import json
import nltk
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import torch
import os
from sentence_transformers import SentenceTransformer

# 1. Resolve NLTK punkt Download Error
try:
    nltk.download('punkt')
except Exception as e:
    print(f"Error downloading nltk punkt resource: {e}")
    print("Please check your internet connection and try again.")
    exit()

# 2. Data Loading and Preprocessing
def load_data(intents_file, crime_descriptions_file, recommendations_file):
    with open(intents_file, 'r') as f:
        intents_data = json.load(f)
    with open(crime_descriptions_file, 'r') as f:
        crime_descriptions_data = json.load(f)
    with open(recommendations_file, 'r') as f:
        recommendations_data = json.load(f)
    return intents_data, crime_descriptions_data, recommendations_data

# 3. Intent Recognition using SentenceTransformer
class IntentRecognizer:
    def __init__(self, intents_data):
        self.intents = intents_data['intents']
        self.tags = [i['tag'] for i in self.intents]
        self.patterns = [i['patterns'] for i in self.intents]

        # Load SentenceTransformer model
        try:
            self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading SentenceTransformer model: {e}")
            print("Please check your internet connection and ensure the sentence-transformers library is installed.")
            exit()

        self.pattern_embeddings = self.encode_patterns()

    def encode_patterns(self):
        embeddings = []
        for pattern_list in self.patterns:
            embeddings.extend(self.model.encode(pattern_list))  # Encode all patterns in the list
        return embeddings

    def recognize_intent(self, text):
        text_embedding = self.encode_text(text)
        max_similarity = -1
        predicted_intent_index = -1

        for i, pattern_embedding in enumerate(self.pattern_embeddings):
            similarity = cosine_similarity([text_embedding], [pattern_embedding.reshape(1, -1)])[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                predicted_intent_index = i

        # Determine the correct intent tag based on the index
        pattern_index = 0
        intent_index = 0
        for i, pattern_list in enumerate(self.patterns):
            if pattern_index + len(pattern_list) > predicted_intent_index:
                intent_index = i
                break
            pattern_index += len(pattern_list)

        if predicted_intent_index != -1:
            return self.tags[intent_index]
        else:
            return None

    def encode_text(self, text):
        return self.model.encode(text)

# 4. Crime Description Matching
def match_crime_description(crime_descriptions_data, intent):
    if intent in crime_descriptions_data:
        return crime_descriptions_data[intent]
    else:
        return "Description not found."

# 5. Sentiment Analysis
class SentimentAnalyzer:
    def __init__(self):
        # Load emotion-based sentiment analysis pipeline
        try:
            self.sentiment_pipeline = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base")
        except Exception as e:
            print(f"Error loading sentiment analysis pipeline: {e}")
            print("Please check your internet connection and ensure the transformers library is installed.")
            exit()

    def analyze_sentiment(self, text):
        result = self.sentiment_pipeline(text)[0]
        return result['label'], result['score']

# 6. Recommendation Retrieval and Paraphrasing
class RecommendationSystem:
    def __init__(self, recommendations_data):
        self.recommendations_data = recommendations_data["crime_prevention_recommendations"]
        self.paraphraser = pipeline("text2text-generation", model="t5-base") #Or MiniLM as in architecture

    def get_recommendations(self, crime, scenario):
        for crime_data in self.recommendations_data:
            if crime_data["crime"] == crime:
                for scenario_data in crime_data["scenarios"]:
                    if scenario_data["scenario"].lower() in scenario.lower():
                        return scenario_data["recommendations"]
        return ["No specific recommendations found for this scenario."]

    def paraphrase_text(self, text):
        paraphrased_text = self.paraphraser(text, max_length=150, num_return_sequences=1)[0]['generated_text']
        return paraphrased_text

# 7. Chatbot Logic
class CrimeChatbot:
    def __init__(self, intents_file, crime_descriptions_file, recommendations_file):
        self.intents_data, self.crime_descriptions_data, self.recommendations_data = load_data(intents_file, crime_descriptions_file, recommendations_file)
        self.intent_recognizer = IntentRecognizer(self.intents_data)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.recommendation_system = RecommendationSystem(self.recommendations_data)

    def respond_to_user(self, user_input):
        intent = self.intent_recognizer.recognize_intent(user_input)
        sentiment, score = self.sentiment_analyzer.analyze_sentiment(user_input)

        if intent:
            crime_description = match_crime_description(self.crime_descriptions_data, intent)
            recommendations = self.recommendation_system.get_recommendations(intent, user_input)

            response = f"I understand you're dealing with a situation related to {intent}.\n"
            response += f"Here's a brief description of {intent}: {crime_description}\n\n"
            response += "Based on your situation, here are some recommendations:\n"

            for i, recommendation in enumerate(recommendations):
                paraphrased_recommendation = self.recommendation_system.paraphrase_text(recommendation)
                response += f"{i+1}. {paraphrased_recommendation}\n"

            response += f"\n(Sentiment of your message: {sentiment} - {score:.2f})"
            return response
        else:
            return "I'm sorry, I didn't understand your situation. Can you please provide more details?"

# 8. Main Function and Chatbot Interaction
if __name__ == "__main__":
    intents_file = './data/intents.json'
    crime_descriptions_file = './data/crime_description.json'
    recommendations_file = './data/recommendations.json'

    chatbot = CrimeChatbot(intents_file, crime_descriptions_file, recommendations_file)

    print("Welcome to the Crime Assistance Chatbot! How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye, and stay safe!")
            break
        response = chatbot.respond_to_user(user_input)
        print("Chatbot:", response)
