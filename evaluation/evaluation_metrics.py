import json
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, accuracy_score
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

class RecommendationEvaluator:
    def __init__(self, model_path="../backend/data/recommendations.json"):
        # Load the recommendation data
        with open(model_path, "r") as f:
            self.recommendations_data = json.load(f)
        
        # Initialize models that mirror the main application
        self.sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.paraphrase_pipeline = pipeline("text2text-generation", model="t5-small")
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        
        # Lists of all crimes for reference
        self.crime_labels = [entry["crime"] for entry in self.recommendations_data["crime_prevention_recommendations"]]
        
        # Metrics storage
        self.results = {
            "crime_detection": {
                "accuracy": 0,
                "precision": 0,
                "recall": 0,
                "f1_score": 0,
                "confusion_matrix": None
            },
            "sentiment_match": {
                "mae": 0,
                "rmse": 0,
                "correlation": 0
            },
            "paraphrase_quality": {
                "semantic_similarity": 0,
                "novelty": 0
            },
            "response_time": {
                "avg_ms": 0,
                "max_ms": 0,
                "percentile_95_ms": 0
            }
        }
    
    def detect_crime(self, query):
        """Mirror of the application's crime detection function"""
        query_embedding = self.sbert_model.encode(query, convert_to_tensor=True)
        crime_embeddings = self.sbert_model.encode(self.crime_labels, convert_to_tensor=True)
        similarity_scores = util.pytorch_cos_sim(query_embedding, crime_embeddings)[0]
        best_match_index = torch.argmax(similarity_scores).item()
        return self.crime_labels[best_match_index]
    
    def get_sentiment(self, text):
        """Mirror of the application's sentiment analysis function"""
        result = self.sentiment_pipeline(text)[0]
        label = result["label"]
        score = result["score"] if label == "POSITIVE" else -result["score"]
        return score
    
    def paraphrase_text(self, text):
        """Simplified version of the paraphrase function"""
        paraphrased = self.paraphrase_pipeline(
            "Paraphrase this text in English only: " + text, 
            max_length=200, 
            truncation=True,
            do_sample=False
        )
        return paraphrased[0]["generated_text"].strip()
    
    def evaluate_crime_detection(self, test_data):
        """
        Evaluate the crime detection accuracy
        
        Args:
            test_data: List of dicts with 'query' and 'expected_crime' fields
        """
        y_true = [item["expected_crime"] for item in test_data]
        y_pred = self.predict_crime_labels([item["query"] for item in test_data])  

        # Ensure crime labels align with y_true
        valid_labels = list(set(self.crime_labels) & set(y_true))
        
        # Handle case where no valid labels are found
        if not valid_labels:
            raise ValueError("No valid labels in y_true match self.crime_labels")
        
        # Compute confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=valid_labels)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        
        # Store results
        self.results["crime_detection"]["accuracy"] = accuracy
        self.results["crime_detection"]["precision"] = precision
        self.results["crime_detection"]["recall"] = recall
        self.results["crime_detection"]["f1_score"] = f1
        self.results["crime_detection"]["confusion_matrix"] = cm
        
        return accuracy
    
    def evaluate_sentiment_matching(self, test_data):
        """
        Evaluate how well the sentiment matching works
        
        Args:
            test_data: List of dicts with 'query', 'recommendation', and 'expected_sentiment_similarity' fields
        """
        true_similarities = []
        pred_similarities = []
        
        for item in tqdm(test_data, desc="Evaluating sentiment matching"):
            query_sentiment = self.get_sentiment(item['query'])
            rec_sentiment = self.get_sentiment(item['recommendation'])
            
            # Calculate sentiment similarity (1 - absolute difference normalized to [0,1])
            predicted_similarity = 1 - min(abs(query_sentiment - rec_sentiment) / 2, 1)
            
            true_similarities.append(item['expected_sentiment_similarity'])
            pred_similarities.append(predicted_similarity)
        
        # Calculate metrics
        mae = np.mean(np.abs(np.array(true_similarities) - np.array(pred_similarities)))
        rmse = np.sqrt(np.mean(np.square(np.array(true_similarities) - np.array(pred_similarities))))
        correlation = np.corrcoef(true_similarities, pred_similarities)[0, 1]
        
        # Store results
        self.results["sentiment_match"]["mae"] = mae
        self.results["sentiment_match"]["rmse"] = rmse
        self.results["sentiment_match"]["correlation"] = correlation
        
        return correlation
    
    def evaluate_paraphrase_quality(self, test_data):
        """
        Evaluate paraphrase quality
        
        Args:
            test_data: List of dicts with 'original_text' fields
        """
        similarities = []
        novelties = []
        
        for item in tqdm(test_data, desc="Evaluating paraphrase quality"):
            original = item['original_text']
            paraphrased = self.paraphrase_text(original)
            
            # Calculate semantic similarity
            original_emb = self.sbert_model.encode(original, convert_to_tensor=True)
            paraphrased_emb = self.sbert_model.encode(paraphrased, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(original_emb, paraphrased_emb).item()
            
            # Calculate lexical novelty (1 - Jaccard similarity)
            original_tokens = set(original.lower().split())
            paraphrased_tokens = set(paraphrased.lower().split())
            jaccard = len(original_tokens.intersection(paraphrased_tokens)) / len(original_tokens.union(paraphrased_tokens))
            novelty = 1 - jaccard
            
            similarities.append(similarity)
            novelties.append(novelty)
        
        # Store results
        self.results["paraphrase_quality"]["semantic_similarity"] = np.mean(similarities)
        self.results["paraphrase_quality"]["novelty"] = np.mean(novelties)
        
        return np.mean(similarities)
    
    def evaluate_response_time(self, test_data):
        """
        Evaluate response times
        
        Args:
            test_data: List of dicts with 'query' fields
        """
        import time
        response_times = []
        
        for item in tqdm(test_data, desc="Evaluating response time"):
            start_time = time.time()
            
            # Simulate full pipeline
            crime = self.detect_crime(item['query'])
            sentiment = self.get_sentiment(item['query'])
            
            # Just getting a sample recommendation to test paraphrasing
            sample_recommendation = next(iter(self.recommendations_data["crime_prevention_recommendations"]))
            if "scenarios" in sample_recommendation and sample_recommendation["scenarios"]:
                if "recommendations" in sample_recommendation["scenarios"][0]:
                    text_to_paraphrase = sample_recommendation["scenarios"][0]["recommendations"][0]
                    _ = self.paraphrase_text(text_to_paraphrase)
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            response_times.append(response_time_ms)
        
        # Store results
        self.results["response_time"]["avg_ms"] = np.mean(response_times)
        self.results["response_time"]["max_ms"] = np.max(response_times)
        self.results["response_time"]["percentile_95_ms"] = np.percentile(response_times, 95)
        
        return np.mean(response_times)
    
    def plot_confusion_matrix(self, save_path="confusion_matrix.png"):
        """Plot and save the confusion matrix"""
        if self.results["crime_detection"]["confusion_matrix"] is None:
            print("No confusion matrix data available. Run evaluate_crime_detection first.")
            return
        
        plt.figure(figsize=(12, 10))
        cm = self.results["crime_detection"]["confusion_matrix"]
        
        # Normalize the confusion matrix
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        sns.heatmap(
            cm_normalized, 
            annot=True, 
            fmt='.2f', 
            cmap='Blues',
            xticklabels=self.crime_labels,
            yticklabels=self.crime_labels
        )
        
        plt.title('Crime Detection Confusion Matrix')
        plt.ylabel('True Crime')
        plt.xlabel('Predicted Crime')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
        return save_path
    
    def run_full_evaluation(self, test_data_path="./data/test_data.json"):
        """Run all evaluations with data from the test file"""
        print(f"Loading test data from {test_data_path}")
        
        with open(test_data_path, "r") as f:
            test_data = json.load(f)
            
        print(f"Loaded {len(test_data['crime_detection'])} crime detection test cases")
        print(f"Loaded {len(test_data['sentiment_matching'])} sentiment matching test cases")
        print(f"Loaded {len(test_data['paraphrase_quality'])} paraphrase quality test cases")
        
        # Run all evaluations
        self.evaluate_crime_detection(test_data["crime_detection"])
        self.evaluate_sentiment_matching(test_data["sentiment_matching"])
        self.evaluate_paraphrase_quality(test_data["paraphrase_quality"])
        self.evaluate_response_time(test_data["crime_detection"])  # Reuse crime detection queries
        
        # Plot the confusion matrix
        self.plot_confusion_matrix()
        
        return self.results
    
    def generate_report(self, output_path="evaluation_report.html"):
        """Generate an HTML report of the evaluation results"""
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crime Prevention Recommendation Engine Evaluation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ margin-bottom: 10px; }}
                .section {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                h1, h2 {{ color: #2c3e50; }}
                .good {{ color: green; }}
                .average {{ color: orange; }}
                .poor {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                table, th, td {{ border: 1px solid #ddd; }}
                th, td {{ padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Crime Prevention Recommendation Engine Evaluation Report</h1>
            <p>Generated on {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="section">
                <h2>Crime Detection Performance</h2>
                <div class="metric">Accuracy: <span class="{self._get_rating_class(self.results['crime_detection']['accuracy'], 0.7, 0.9)}">{self.results['crime_detection']['accuracy']:.4f}</span></div>
                <div class="metric">Precision: <span class="{self._get_rating_class(self.results['crime_detection']['precision'], 0.7, 0.9)}">{self.results['crime_detection']['precision']:.4f}</span></div>
                <div class="metric">Recall: <span class="{self._get_rating_class(self.results['crime_detection']['recall'], 0.7, 0.9)}">{self.results['crime_detection']['recall']:.4f}</span></div>
                <div class="metric">F1 Score: <span class="{self._get_rating_class(self.results['crime_detection']['f1_score'], 0.7, 0.9)}">{self.results['crime_detection']['f1_score']:.4f}</span></div>
                <p>See confusion matrix image for detailed classification performance.</p>
            </div>
            
            <div class="section">
                <h2>Sentiment Matching Performance</h2>
                <div class="metric">Mean Absolute Error: <span class="{self._get_rating_class(1-self.results['sentiment_match']['mae'], 0.7, 0.9)}">{self.results['sentiment_match']['mae']:.4f}</span></div>
                <div class="metric">Root Mean Square Error: <span class="{self._get_rating_class(1-self.results['sentiment_match']['rmse'], 0.7, 0.9)}">{self.results['sentiment_match']['rmse']:.4f}</span></div>
                <div class="metric">Correlation: <span class="{self._get_rating_class(self.results['sentiment_match']['correlation'], 0.7, 0.9)}">{self.results['sentiment_match']['correlation']:.4f}</span></div>
            </div>
            
            <div class="section">
                <h2>Paraphrase Quality</h2>
                <div class="metric">Semantic Similarity: <span class="{self._get_rating_class(self.results['paraphrase_quality']['semantic_similarity'], 0.7, 0.9)}">{self.results['paraphrase_quality']['semantic_similarity']:.4f}</span></div>
                <div class="metric">Novelty: <span class="{self._get_rating_class(self.results['paraphrase_quality']['novelty'], 0.3, 0.6)}">{self.results['paraphrase_quality']['novelty']:.4f}</span></div>
                <p>Good paraphrasing should maintain high semantic similarity while introducing some novelty in word choice.</p>
            </div>
            
            <div class="section">
                <h2>Response Time</h2>
                <div class="metric">Average Response Time: <span class="{self._get_rating_class(1000/self.results['response_time']['avg_ms'], 0.002, 0.01)}">{self.results['response_time']['avg_ms']:.2f} ms</span></div>
                <div class="metric">Maximum Response Time: <span class="{self._get_rating_class(2000/self.results['response_time']['max_ms'], 0.002, 0.01)}">{self.results['response_time']['max_ms']:.2f} ms</span></div>
                <div class="metric">95th Percentile Response Time: <span class="{self._get_rating_class(1500/self.results['response_time']['percentile_95_ms'], 0.002, 0.01)}">{self.results['response_time']['percentile_95_ms']:.2f} ms</span></div>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <p>Based on the evaluation results, here are some recommendations for improvement:</p>
                <ul>
                    {self._generate_recommendations()}
                </ul>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, "w") as f:
            f.write(report)
            
        print(f"Evaluation report saved to {output_path}")
        return output_path
    
    def _get_rating_class(self, value, threshold_average, threshold_good):
        """Helper to determine CSS class for metric values"""
        if value >= threshold_good:
            return "good"
        elif value >= threshold_average:
            return "average"
        return "poor"
    
    def _generate_recommendations(self):
        """Generate improvement recommendations based on metrics"""
        recommendations = []
        
        # Crime detection recommendations
        if self.results["crime_detection"]["accuracy"] < 0.8:
            recommendations.append("<li>Consider fine-tuning the Sentence-BERT model on domain-specific crime data to improve detection accuracy.</li>")
        
        # Sentiment matching recommendations
        if self.results["sentiment_match"]["correlation"] < 0.7:
            recommendations.append("<li>The sentiment matching could be improved by using a specialized sentiment model trained on crime-related content.</li>")
        
        # Paraphrase recommendations
        if self.results["paraphrase_quality"]["semantic_similarity"] < 0.8:
            recommendations.append("<li>The paraphrasing model could benefit from fine-tuning to better preserve meaning while rewording recommendations.</li>")
        
        if self.results["paraphrase_quality"]["novelty"] < 0.3:
            recommendations.append("<li>The paraphrasing model is not introducing enough variation. Consider adjusting the generation parameters.</li>")
        
        # Response time recommendations
        if self.results["response_time"]["avg_ms"] > 500:
            recommendations.append("<li>Response times could be improved by model quantization or using smaller models.</li>")
        
        # If everything looks good
        if not recommendations:
            recommendations.append("<li>All metrics look good! Consider expanding the test dataset to ensure robustness.</li>")
        
        return "".join(recommendations)

def create_sample_test_data():
    """Create a sample test data file if one doesn't exist"""
    sample_data = {
        "crime_detection": [
            {"query": "Someone broke into my car last night", "expected_crime": "burglary"},
            {"query": "I received threatening messages", "expected_crime": "harassment"},
            {"query": "My wallet was stolen at the mall", "expected_crime": "theft"}
        ],
        "sentiment_matching": [
            {"query": "I'm terrified after my house was broken into", "recommendation": "Install security cameras", "expected_sentiment_similarity": 0.7},
            {"query": "My neighbor keeps making noise at night", "recommendation": "Try talking to them calmly", "expected_sentiment_similarity": 0.8}
        ],
        "paraphrase_quality": [
            {"original_text": "Make sure to lock all doors and windows before leaving."},
            {"original_text": "Report suspicious activities to local authorities immediately."}
        ]
    }
    
    with open("./data/test_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("Sample test data created at ./data/test_data.json")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate Crime Prevention Recommendation Engine")
    parser.add_argument("--model", default="../backend/data/recommendations.json", help="Path to recommendations JSON file")
    parser.add_argument("--test-data", default="./data/test_data.json", help="Path to test data JSON file")
    parser.add_argument("--create-sample", action="store_true", help="Create a sample test data file")
    parser.add_argument("--output", default="./result/evaluation_report.html", help="Output path for evaluation report")
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_test_data()
    
    try:
        evaluator = RecommendationEvaluator(model_path=args.model)
        results = evaluator.run_full_evaluation(test_data_path=args.test_data)
        
        # Print summary to console
        print("\n===== Evaluation Summary =====")
        print(f"Crime Detection Accuracy: {results['crime_detection']['accuracy']:.4f}")
        print(f"Sentiment Matching Correlation: {results['sentiment_match']['correlation']:.4f}")
        print(f"Paraphrase Semantic Similarity: {results['paraphrase_quality']['semantic_similarity']:.4f}")
        print(f"Average Response Time: {results['response_time']['avg_ms']:.2f} ms")
        
        # Generate HTML report
        report_path = evaluator.generate_report(output_path=args.output)
        print(f"\nDetailed evaluation report saved to: {report_path}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("If test data is missing, use --create-sample to generate a sample test file.")