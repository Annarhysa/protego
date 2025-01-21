from sentence_transformers import SentenceTransformer, util
import json
import torch

class CrimeBot:
    def __init__(self):
        # Load intents and crime descriptions
        with open('./data/intents.json', 'r') as f:
            self.intents = json.load(f)['intents']
        with open('./data/crime_description.json', 'r') as f:
            self.crime_descriptions = json.load(f)

        # Initialize the sentence transformer model
        # Using a lightweight multilingual model that's good for semantic similarity
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

        # Pre-compute embeddings for patterns and crime descriptions
        self.intent_patterns = []
        self.intent_embeddings = []
        self.intent_mapping = []

        # Process intents
        for intent in self.intents:
            for pattern in intent['patterns']:
                self.intent_patterns.append(pattern)
                self.intent_mapping.append(intent)

        # Create embeddings for all patterns
        self.intent_embeddings = self.model.encode(self.intent_patterns, convert_to_tensor=True)

        # Process crime descriptions
        self.crime_queries = list(self.crime_descriptions.keys())
        self.crime_embeddings = self.model.encode(self.crime_queries, convert_to_tensor=True)

    def get_response(self, user_input):
        # Encode user input
        input_embedding = self.model.encode(user_input, convert_to_tensor=True)

        # Find closest intent pattern
        cos_scores_intents = util.cos_sim(input_embedding, self.intent_embeddings)[0]
        best_intent_match = torch.argmax(cos_scores_intents)

        # Find closest crime description
        cos_scores_crimes = util.cos_sim(input_embedding, self.crime_embeddings)[0]
        best_crime_match = torch.argmax(cos_scores_crimes)

        # Get similarity scores
        intent_similarity = cos_scores_intents[best_intent_match].item()
        crime_similarity = cos_scores_crimes[best_crime_match].item()

        # Threshold for considering a match valid
        SIMILARITY_THRESHOLD = 0.6

        # Choose best response based on similarity scores
        if max(intent_similarity, crime_similarity) < SIMILARITY_THRESHOLD:
            return "I'm not sure about that. Could you please rephrase or ask about a specific crime?"

        if intent_similarity > crime_similarity:
            # Return response from matched intent
            matched_intent = self.intent_mapping[best_intent_match]
            return random.choice(matched_intent['responses'])
        else:
            # Return crime description
            matched_crime = self.crime_queries[best_crime_match]
            return self.crime_descriptions[matched_crime]

    def get_similar_crimes(self, crime_type, n=3):
        """Find similar crimes to the given crime type"""
        query_embedding = self.model.encode(crime_type, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.crime_embeddings)[0]

        # Get top N similar crimes
        top_results = torch.topk(cos_scores, k=min(n + 1, len(self.crime_queries)))

        similar_crimes = []
        for score, idx in zip(top_results[0], top_results[1]):
            if self.crime_queries[idx].lower() != crime_type.lower():  # Exclude exact match
                similar_crimes.append({
                    'crime': self.crime_queries[idx],
                    'description': self.crime_descriptions[self.crime_queries[idx]],
                    'similarity': score.item()
                })

        return similar_crimes[:n]