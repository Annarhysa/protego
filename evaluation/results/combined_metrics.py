import json
import os
import argparse
from datetime import datetime

def load_json_file(file_path):
    """Load data from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def combine_metrics(automated_results_path, human_results_path, output_path):
    """Combine automated and human evaluation metrics into a single report"""
    # Load results
    automated_results = load_json_file(automated_results_path)
    human_results = load_json_file(human_results_path)
    
    if not automated_results or not human_results:
        print("Failed to load required result files.")
        return False
    
    # Initialize combined metrics
    combined_metrics = {
        "timestamp": datetime.now().isoformat(),
        "automated_metrics": {
            "accuracy": automated_results.get("accuracy_metrics", {}),
            "performance": automated_results.get("performance_metrics", {})
        },
        "human_metrics": {
            "average_scores": {}
        },
        "combined_metrics": {},
        "individual_results": []
    }
    
    # Process human evaluation metrics
    human_scores = human_results.get("evaluations", [])
    avg_scores = {"relevance": 0, "helpfulness": 0, "clarity": 0, "overall": 0}
    score_counts = {"relevance": 0, "helpfulness": 0, "clarity": 0, "overall": 0}
    
    for evaluation in human_scores:
        for metric in avg_scores.keys():
            if metric in evaluation and evaluation[metric] is not None:
                avg_scores[metric] += evaluation[metric]
                score_counts[metric] += 1
    
    # Calculate averages
    for metric in avg_scores.keys():
        if score_counts[metric] > 0:
            avg_scores[metric] /= score_counts[metric]
    
    combined_metrics["human_metrics"]["average_scores"] = avg_scores
    
    # Combine individual results
    auto_results = {r["query_id"]: r for r in automated_results.get("individual_results", [])}
    human_evals = {e["query_id"]: e for e in human_scores}
    
    all_query_ids = set(auto_results.keys()) | set(human_evals.keys())
    
    for query_id in all_query_ids:
        auto_result = auto_results.get(query_id, {})
        human_eval = human_evals.get(query_id, {})
        
        combined_result = {
            "query_id": query_id,
            "query_text": auto_result.get("query_text", human_eval.get("query_text", "")),
            "expected_crime": auto_result.get("expected_crime", ""),
            "detected_crime": auto_result.get("detected_crime", ""),
            "crime_detected_correctly": auto_result.get("crime_detected_correctly", False),
            "recommendation": auto_result.get("recommendation", ""),
            "human_scores": {
                "relevance": human_eval.get("relevance"),
                "helpfulness": human_eval.get("helpfulness"),
                "clarity": human_eval.get("clarity"),
                "overall": human_eval.get("overall")
            },
            "human_comments": human_eval.get("comments", "")
        }
        
        combined_metrics["individual_results"].append(combined_result)
    
    # Calculate overall combined metrics
    overall_score = 0
    components = 0
    
    # Add automated accuracy to overall score
    accuracy = automated_results.get("accuracy_metrics", {}).get("crime_detection_accuracy", 0)
    if accuracy > 0:
        overall_score += accuracy
        components += 1
    
    # Add human overall score to overall score
    if avg_scores["overall"] > 0:
        # Convert from 1-5 scale to 0-100 scale
        human_overall = (avg_scores["overall"] - 1) / 4 * 100
        overall_score += human_overall
        components += 1
    
    # Calculate final combined score
    if components > 0:
        combined_metrics["combined_metrics"]["overall_score"] = overall_score / components
    else:
        combined_metrics["combined_metrics"]["overall_score"] = 0
    
    # Save combined metrics to file
    try:
        with open(output_path, 'w') as f:
            json.dump(combined_metrics, f, indent=2)
        print(f"Combined metrics saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving combined metrics: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Combine automated and human evaluation metrics")
    parser.add_argument("--automated", default="results/automated_results.json", 
                      help="Path to automated evaluation results JSON file")
    parser.add_argument("--human", default="results/human_results.json", 
                      help="Path to human evaluation results JSON file")
    parser.add_argument("--output", default="results/combined_metrics.json", 
                      help="Path to save combined metrics JSON file")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    print(f"Combining metrics from {args.automated} and {args.human}...")
    success = combine_metrics(args.automated, args.human, args.output)
    
    if success:
        # Load the combined metrics to print a summary
        combined_metrics = load_json_file(args.output)
        if combined_metrics:
            print("\n" + "="*50)
            print("COMBINED METRICS SUMMARY")
            print("="*50)
            print(f"Overall system score: {combined_metrics['combined_metrics']['overall_score']:.2f}/100")
            print(f"Crime detection accuracy: {combined_metrics['automated_metrics']['accuracy'].get('crime_detection_accuracy', 0):.2f}%")
            
            human_scores = combined_metrics['human_metrics']['average_scores']
            print(f"Average human ratings (1-5 scale):")
            print(f"  Relevance: {human_scores.get('relevance', 0):.2f}")
            print(f"  Helpfulness: {human_scores.get('helpfulness', 0):.2f}")
            print(f"  Clarity: {human_scores.get('clarity', 0):.2f}")
            print(f"  Overall: {human_scores.get('overall', 0):.2f}")
            print("="*50)

if __name__ == "__main__":
    main()