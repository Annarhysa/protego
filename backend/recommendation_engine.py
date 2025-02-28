import json
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from flask import Flask, request

# Load Sentence-BERT for crime detection
sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load T5 for paraphrasing (with explicit English instruction)
paraphrase_pipeline = pipeline("text2text-generation", model="t5-small")

# Load DistilBERT for sentiment analysis
sentiment_pipeline = pipeline("sentiment-analysis")

# Load recommendations JSON
with open("./data/recommendations.json", "r") as f:
    recommendations_data = json.load(f)

app = Flask(__name__)

# Function to find the crime mentioned in the query
def detect_crime(query):
    crime_labels = [entry["crime"] for entry in recommendations_data["crime_prevention_recommendations"]]
    query_embedding = sbert_model.encode(query, convert_to_tensor=True)
    crime_embeddings = sbert_model.encode(crime_labels, convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(query_embedding, crime_embeddings)[0]
    best_match_index = torch.argmax(similarity_scores).item()
    return crime_labels[best_match_index]

# Function to get relevant recommendations
def get_recommendations(crime):
    for crime_entry in recommendations_data["crime_prevention_recommendations"]:
        if crime_entry["crime"] == crime:
            return crime_entry["scenarios"]
    return []

# Function to identify and remove instruction phrases
def remove_instruction_phrases(text):
    """
    Identifies and removes common instruction phrases from paraphrased text.
    
    Args:
        text (str): The paraphrased text that may contain unwanted instruction phrases
    
    Returns:
        str: The cleaned text with instruction phrases removed
    """
    # List of common instruction phrases to check for and remove
    instruction_phrases = [
        "Paraphrase this text in English only and elaborate little:",
        "Paraphrase this text in English only:",
        "Paraphrase this in English:",
        "paraphrase this text:",
        "paraphrase this:",
        "paraphrase:",
    ]
    
    # Check if any of the phrases appear at the beginning of the text
    cleaned_text = text.strip()
    
    for phrase in instruction_phrases:
        if cleaned_text.lower().startswith(phrase.lower()):
            # Remove the phrase from the beginning of the text
            cleaned_text = cleaned_text[len(phrase):].strip()
    
    # Also check for phrases that might appear with slight variations
    if "in english only" in cleaned_text.lower() and "paraphrase" in cleaned_text.lower()[:30]:
        # Find the position after the instruction phrase
        possible_end = cleaned_text.lower().find(":")
        if possible_end != -1 and possible_end < 50:  # Only if the colon appears near the beginning
            cleaned_text = cleaned_text[possible_end + 1:].strip()
    
    return cleaned_text

# Function to paraphrase text - modified to ensure English output
def paraphrase_text(text):
    # Explicitly instruct the model to paraphrase in English
    paraphrased = paraphrase_pipeline(
        "Paraphrase this text in English only: " + text, 
        max_length=200, 
        truncation=True,
        do_sample=False  # Deterministic generation
    )
    
    result = paraphrased[0]["generated_text"].strip()
    
    # Clean any instruction phrases from the result
    cleaned_result = remove_instruction_phrases(result)
    
    # If the cleaning removed everything or almost everything, return the original
    if len(cleaned_result) < 10 or len(cleaned_result) < len(result) * 0.5:
        return text
    
    # Add a fallback mechanism if the response still isn't in English
    # This is a simple check - you might want to use a more robust language detection
    if not all(ord(c) < 128 for c in cleaned_result.replace(' ', '')):
        # If non-ASCII characters detected, use a simpler approach
        return f"My recommendation: {text}"
    
    return cleaned_result

# Function to get sentiment score
def get_sentiment(text):
    result = sentiment_pipeline(text)[0]
    label = result["label"]
    score = result["score"] if label == "POSITIVE" else -result["score"]
    return score

@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.json.get("query", "").strip()
   
    if not user_query:
        return "Please provide a valid query."
   
    # Detect the crime
    detected_crime = detect_crime(user_query)
   
    # Get recommendations
    scenarios = get_recommendations(detected_crime)
    if not scenarios:
        return f"I found that your concern is related to {detected_crime}, but I don't have any recommendations at the moment."
   
    # Get user sentiment
    user_sentiment = get_sentiment(user_query)
   
    # Find the recommendation with the closest sentiment match
    best_match = None
    best_sentiment_diff = float("inf")
   
    for scenario in scenarios:
        for rec in scenario["recommendations"]:
            rec_sentiment = get_sentiment(rec)
            sentiment_diff = abs(user_sentiment - rec_sentiment)
            if sentiment_diff < best_sentiment_diff:
                best_sentiment_diff = sentiment_diff
                best_match = rec
   
    if best_match:
        refined_response = paraphrase_text(best_match)
        return f"Based on your query, I identified the crime as {detected_crime}. Here is my suggestion: {refined_response}"
    else:
        return f"I found that your concern is related to {detected_crime}, but I don't have a matching recommendation."

if __name__ == "__main__":
    app.run(debug=True)