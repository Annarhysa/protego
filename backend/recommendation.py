import json
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# Load Sentence-BERT for crime detection
sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load T5 for paraphrasing (with explicit English instruction)
paraphrase_pipeline = pipeline("text2text-generation", model="t5-small")

# Load generative model for elaboration (using FLAN-T5 for better generation)
generation_pipeline = pipeline("text2text-generation", model="google/flan-t5-large")

# Load DistilBERT for sentiment analysis
sentiment_pipeline = pipeline("sentiment-analysis")

# Load recommendations JSON
with open("./data/recommendations.json", "r") as f:
    recommendations_data = json.load(f)


# Function to find the crime mentioned in the query
def detect_crime(query):
    """Enhanced detection using both crime labels and their associated prompts"""
    crime_data = recommendations_data["crime_prevention_recommendations"]
    
    # Create combined text of crime + prompts for better matching
    crime_texts = [
        f"{entry['crime']} {' '.join(entry.get('prompts', []))}" 
        for entry in crime_data
    ]
    
    # Get embeddings for all crimes
    query_embedding = sbert_model.encode(query, convert_to_tensor=True)
    crime_embeddings = sbert_model.encode(crime_texts, convert_to_tensor=True)
    
    # Find top 3 matches
    similarity_scores = util.pytorch_cos_sim(query_embedding, crime_embeddings)[0]
    top_indices = torch.topk(similarity_scores, k=3).indices.tolist()
    
    return [crime_data[i]["crime"] for i in top_indices]

def get_recommendations(crimes):
    """Get recommendations across multiple detected crimes"""
    recommendations = []
    for crime in crimes:
        for entry in recommendations_data["crime_prevention_recommendations"]:
            if entry["crime"] == crime:
                for scenario in entry["scenarios"]:
                    recommendations.extend(scenario["recommendations"])
    return recommendations


def elaborate_recommendation(text):
    """Generate detailed recommendations using FLAN-T5"""
    generated = generation_pipeline(
        f"Elaborate this recommendation with detailed steps and examples: {text}",
        max_length=300,
        num_beams=4,
        repetition_penalty=2.5,
        temperature=0.7
    )
    return generated[0]["generated_text"].strip()

# Function to get sentiment score
def get_sentiment(text):
    result = sentiment_pipeline(text)[0]
    label = result["label"]
    score = result["score"] if label == "POSITIVE" else -result["score"]
    return score

def calculate_similarity(text1, text2):
    """Calculate cosine similarity between two texts"""
    embeddings = sbert_model.encode([text1, text2], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return similarity

def filter_similar_suggestions(suggestions, threshold=0.7):
    """Filter out similar suggestions based on a threshold"""
    filtered_suggestions = []
    
    for suggestion in suggestions:
        is_unique = True
        for existing in filtered_suggestions:
            similarity = calculate_similarity(suggestion, existing)
            if similarity > threshold:
                is_unique = False
                break
        
        if is_unique:
            filtered_suggestions.append(suggestion)
    
    return filtered_suggestions