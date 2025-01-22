from sentence_transformers import SentenceTransformer, util
import json
import torch
import random
from transformers import pipeline

class CrimeBot:
    def __init__(self):
        # Load intents and crime descriptions
        with open('./data/intents.json', 'r') as f:
            self.intents = json.load(f)['intents']
        with open('./data/crime_description.json', 'r') as f:
            self.crime_descriptions = json.load(f)

        # Initialize the sentence transformer model
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

        # Initialize sentiment analysis pipeline
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base")

        # Pre-compute embeddings for patterns and crime descriptions
        self.intent_patterns = []
        self.intent_embeddings = []
        self.intent_mapping = []

        for intent in self.intents:
            for pattern in intent['patterns']:
                self.intent_patterns.append(pattern)
                self.intent_mapping.append(intent)

        self.intent_embeddings = self.model.encode(self.intent_patterns, convert_to_tensor=True)
        self.crime_queries = list(self.crime_descriptions.keys())
        self.crime_embeddings = self.model.encode(self.crime_queries, convert_to_tensor=True)

    def analyze_sentiment(self, user_input):
        """
        Analyze sentiment of the user input using Hugging Face's model.
        """
        analysis = self.sentiment_analyzer(user_input)
        return analysis[0]['label'], analysis[0]['score']

    def get_response(self, user_input):
        # Analyze user sentiment
        sentiment, confidence = self.analyze_sentiment(user_input)
        is_distressed = sentiment in ['sadness', 'fear', 'anger']

        # Encode user input for similarity checks
        input_embedding = self.model.encode(user_input, convert_to_tensor=True)

        # Find closest intent and crime description
        cos_scores_intents = util.cos_sim(input_embedding, self.intent_embeddings)[0]
        best_intent_match = torch.argmax(cos_scores_intents)
        cos_scores_crimes = util.cos_sim(input_embedding, self.crime_embeddings)[0]
        best_crime_match = torch.argmax(cos_scores_crimes)

        intent_similarity = cos_scores_intents[best_intent_match].item()
        crime_similarity = cos_scores_crimes[best_crime_match].item()
        SIMILARITY_THRESHOLD = 0.6

        # Provide comforting responses for distressed users
        if is_distressed and confidence > 0.8:
            comforting_responses = [
                "I'm here to assist you. Please take a deep breath and share as much or as little as you're comfortable with.",
                "I understand this might be hard to talk about. You're not alone. Let me guide you.",
                "It's okay to feel this way. Please let me know how I can help."
            ]
            return random.choice(comforting_responses)

        # Choose best response based on similarity
        if max(intent_similarity, crime_similarity) < SIMILARITY_THRESHOLD:
            return "I'm not sure about that. Could you please rephrase or ask about a specific crime?"

        if intent_similarity > crime_similarity:
            matched_intent = self.intent_mapping[best_intent_match]
            return random.choice(matched_intent['responses'])
        else:
            matched_crime = self.crime_queries[best_crime_match]
            return self.crime_descriptions[matched_crime]

    def get_similar_crimes(self, crime_type, n=3):
        query_embedding = self.model.encode(crime_type, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.crime_embeddings)[0]
        top_results = torch.topk(cos_scores, k=min(n + 1, len(self.crime_queries)))

        similar_crimes = []
        for score, idx in zip(top_results[0], top_results[1]):
            if self.crime_queries[idx].lower() != crime_type.lower():
                similar_crimes.append({
                    'crime': self.crime_queries[idx],
                    'description': self.crime_descriptions[self.crime_queries[idx]],
                    'similarity': score.item()
                })

        return similar_crimes[:n]