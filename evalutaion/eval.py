import pandas as pd
import numpy as np
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize

# Read test and actual data from CSV files
test_data = pd.read_csv('../backend/output/test_data/test.csv')
actual_data = pd.read_csv('../backend/output/test_data/protego.csv')

def calculate_jaccard_similarity(set1, set2):
    """Calculate Jaccard similarity between two sets (case-insensitive)"""
    set1 = set1.lower()
    set2 = set2.lower()
    
    intersection = set(set1.split()).intersection(set(set2.split()))
    union = set(set1.split()).union(set(set2.split()))
    
    return len(intersection) / len(union)

def calculate_recommendation_similarity(reference, hypothesis):
    """Calculate similarity of recommendations based on conveyed message"""
    # Tokenize and remove stopwords for better comparison
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
    
    reference_tokens = [word for word in word_tokenize(reference.lower()) if word not in stop_words]
    hypothesis_tokens = [word for word in word_tokenize(hypothesis.lower()) if word not in stop_words]
    
    # Calculate cosine similarity using TF-IDF
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([reference.lower(), hypothesis.lower()])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2]).flatten()[0]
    
    return similarity

from sklearn.metrics.pairwise import cosine_similarity

def evaluate_performance(test_data, actual_data):
    """Evaluate performance across crime detection, sentiment score, and recommendation quality"""
    total_crime_similarity = 0
    total_sentiment_diff = 0
    total_recommendation_similarity = 0
    
    for index, row in test_data.iterrows():
        actual_row = actual_data.iloc[index]
        
        # Crime detection similarity
        crime_similarity = calculate_jaccard_similarity(row['crime'], actual_row['crime'])
        total_crime_similarity += crime_similarity
        
        # Sentiment score difference
        sentiment_diff = abs(row['sentiment_score'] - actual_row['sentiment_score'])
        total_sentiment_diff += sentiment_diff
        
        # Recommendation quality (similarity of conveyed message)
        recommendation_similarity = calculate_recommendation_similarity(row['recommendations'], actual_row['recommendations'])
        total_recommendation_similarity += recommendation_similarity
    
    # Average scores
    avg_crime_similarity = total_crime_similarity / len(test_data)
    avg_sentiment_diff = total_sentiment_diff / len(test_data)
    avg_recommendation_similarity = total_recommendation_similarity / len(test_data)
    
    # Overall performance score (example: weighted average)
    performance_score = (avg_crime_similarity * 0.4) + (1 - avg_sentiment_diff) * 0.3 + (avg_recommendation_similarity * 0.3)
    
    return {
        "crime_detection_similarity": avg_crime_similarity,
        "sentiment_score_accuracy": 1 - avg_sentiment_diff,
        "recommendation_quality_similarity": avg_recommendation_similarity,
        "overall_performance_score": performance_score
    }

# Evaluate performance
performance_results = evaluate_performance(test_data, actual_data)
print(performance_results)
