import json
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# Load Sentence-BERT for crime detection
sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

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
    top_indices = torch.topk(similarity_scores, k=2).indices.tolist()
    
    return [crime_data[i]["crime"] for i in top_indices]


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

def get_recommendations(crimes):
    """Get recommendations across multiple detected crimes"""
    recommendations = []
    for crime in crimes:
        for entry in recommendations_data["crime_prevention_recommendations"]:
            if entry["crime"] == crime:
                for scenario in entry["scenarios"]:
                    recommendations.extend(scenario["recommendations"])
    

    return recommendations

def score_and_sort_recommendations(user_query, all_recommendations):
    """Score and sort recommendations based on sentiment similarity"""
    user_sentiment = get_sentiment(user_query)
    
    scored_recs = []
    for rec in all_recommendations:
        rec_sentiment = get_sentiment(rec)
        sentiment_diff = abs(user_sentiment - rec_sentiment)
        scored_recs.append((rec, sentiment_diff))
    
    # Get top 3 recommendations by sentiment match
    top_recommendations = sorted(scored_recs, key=lambda x: x[1])[:3]
    
    print(f"Sentiment score: {round(user_sentiment, 2)}")
    return [rec[0] for rec in top_recommendations]

def elaborate_recommendations(recommendations):
    """Elaborate recommendations using FLAN-T5"""

    text_improver = pipeline(
        "text2text-generation", 
        model="google/flan-t5-small",
        device=0 if torch.cuda.is_available() else -1
    )

    elaborated_recommendations = []
    for rec in recommendations:
        prompt = f"Write a proper sentence for this recommendation: {rec}"
        generated = text_improver(
            prompt,
            max_length=200,
            num_beams=4,
            repetition_penalty=5.0,
            temperature=0.7
        )
        elaborated_recommendations.append(generated[0]["generated_text"].strip())
    
    return elaborated_recommendations

def batch_improve_recommendations(recommendations_list):
    """Process all recommendations in a single batch for better performance"""
    
    text_improver = pipeline(
        "text2text-generation", 
        model="google/flan-t5-small",
        device=0 if torch.cuda.is_available() else -1
    )
    
    # Create prompts for each recommendation
    prompts = [f"Convert this note into a helpful, complete sentence: {rec}" 
              for rec in recommendations_list]
    
    # Process all prompts in one batch
    results = text_improver(
        prompts,
        max_length=400,
        num_beams=2,
        temperature=0.7
    )
    
    # Extract generated texts
    improved_recommendations = [result["generated_text"] for result in results]
    
    # Combine into a coherent paragraph
    final_response = ' '.join(improved_recommendations)
    
    return final_response