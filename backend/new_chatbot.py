import json
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from flask import Flask, request

# Load Sentence-BERT for better crime detection
sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load DistilRoBERTa for paraphrasing
paraphrase_pipeline = pipeline("text2text-generation", model="t5-small")

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

# Function to paraphrase response using DistilRoBERTa
def paraphrase_text(text):
    paraphrased = paraphrase_pipeline(text, max_length=200, truncation=True)
    return paraphrased[0]["generated_text"].strip()

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
        return paraphrase_text(f"I found that your concern is related to {detected_crime}, but I don't have any recommendations at the moment.")
    
    # Generate response
    response_text = f"Based on your query, I identified the crime as {detected_crime}. Here are my suggestions:\n"
    for scenario in scenarios:
        response_text += f"\nScenario: {scenario['scenario']}\n"
        for rec in scenario["recommendations"]:
            response_text += f"- {rec}\n"
    
    # Paraphrase the final response
    return paraphrase_text(response_text.strip())

if __name__ == "__main__":
    app.run(debug=True)
