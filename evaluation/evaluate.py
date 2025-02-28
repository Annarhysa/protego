import json
import time
import requests
import os
import argparse
from datetime import datetime

def load_test_data(queries_path, ground_truth_path):
    """Load test queries and ground truth data from JSON files"""
    with open(queries_path, 'r') as f:
        test_queries = json.load(f)
    
    with open(ground_truth_path, 'r') as f:
        ground_truth = json.load(f)
    
    # Ensure data is properly aligned by query_id
    aligned_data = []
    for query in test_queries:
        query_id = query["query_id"]
        truth = next((t for t in ground_truth if t["query_id"] == query_id), None)
        if truth:
            aligned_data.append((query, truth))
    
    return aligned_data

def system_function(query_text, api_url="http://localhost:5000/chat"):
    """Call the system API and parse the response"""
    start_time = time.time()
    
    try:
        response = requests.post(
            api_url,
            json={"query": query_text},
            timeout=10  # Set a reasonable timeout
        )
        
        if response.status_code != 200:
            return {
                "error": f"API returned status code {response.status_code}",
                "response_time": time.time() - start_time
            }
        
        response_text = response.text
        
        # Extract detected crime and recommendation
        # Note: This parsing logic may need adjustment based on your API's actual response format
        try:
            detected_crime = response_text.split("I identified the crime as ")[1].split(".")[0].strip()
        except IndexError:
            detected_crime = "unknown"
        
        try:
            recommendation = response_text.split("Here is my suggestion: ")[1].strip()
        except IndexError:
            recommendation = response_text
        
        return {
            "full_response": response_text,
            "detected_crime": detected_crime,
            "recommendation": recommendation,
            "response_time": time.time() - start_time
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Request failed: {str(e)}",
            "response_time": time.time() - start_time
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "response_time": time.time() - start_time
        }

def calculate_accuracy_metrics(results):
    """Calculate accuracy metrics from evaluation results"""
    total_queries = len(results)
    if total_queries == 0:
        return {"crime_detection_accuracy": 0}
    
    correct_detections = sum(1 for r in results if r.get("crime_detected_correctly", False))
    
    return {
        "crime_detection_accuracy": (correct_detections / total_queries) * 100,
        "total_queries": total_queries,
        "correct_detections": correct_detections
    }

def calculate_performance_metrics(results):
    """Calculate performance metrics from evaluation results"""
    response_times = [r.get("response_time", 0) for r in results]
    
    if not response_times:
        return {"avg_response_time": 0}
    
    response_times.sort()
    
    return {
        "avg_response_time": sum(response_times) / len(response_times),
        "median_response_time": response_times[len(response_times) // 2],
        "min_response_time": min(response_times),
        "max_response_time": max(response_times),
        "90th_percentile_time": response_times[int(len(response_times) * 0.9)]
    }

def evaluate_system(test_data, api_url, output_dir):
    """Evaluate the system using the test data"""
    individual_results = []
    
    for i, (query, truth) in enumerate(test_data):
        query_text = query["query_text"]
        query_id = query["query_id"]
        
        print(f"Processing query {i+1}/{len(test_data)}: {query_text[:50]}...")
        
        # Call the system API
        response = system_function(query_text, api_url)
        
        # Create individual result
        result = {
            "query_id": query_id,
            "query_text": query_text,
            "expected_crime": truth["crime"],
            "detected_crime": response.get("detected_crime", "error"),
            "recommendation": response.get("recommendation", ""),
            "full_response": response.get("full_response", ""),
            "response_time": response.get("response_time", 0),
            "crime_detected_correctly": response.get("detected_crime", "") == truth["crime"],
            "error": response.get("error", None)
        }
        
        individual_results.append(result)
    
    # Calculate aggregated metrics
    accuracy_metrics = calculate_accuracy_metrics(individual_results)
    performance_metrics = calculate_performance_metrics(individual_results)
    
    # Combine all metrics
    evaluation_results = {
        "timestamp": datetime.now().isoformat(),
        "accuracy_metrics": accuracy_metrics,
        "performance_metrics": performance_metrics,
        "individual_results": individual_results
    }
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results to file
    output_file = os.path.join(output_dir, "automated_results.json")
    with open(output_file, 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    return evaluation_results

def print_summary(results):
    """Print a summary of the evaluation results"""
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    
    accuracy = results.get("accuracy_metrics", {})
    performance = results.get("performance_metrics", {})
    
    print(f"Total queries evaluated: {accuracy.get('total_queries', 0)}")
    print(f"Crime detection accuracy: {accuracy.get('crime_detection_accuracy', 0):.2f}%")
    print(f"Average response time: {performance.get('avg_response_time', 0):.4f} seconds")
    print(f"90th percentile response time: {performance.get('90th_percentile_time', 0):.4f} seconds")
    
    # Count error cases
    error_count = sum(1 for r in results.get("individual_results", []) if r.get("error"))
    print(f"Queries with errors: {error_count}")
    
    print("="*50)

def main():
    parser = argparse.ArgumentParser(description="Evaluate crime prevention recommendation system")
    parser.add_argument("--queries", default="test_data/test_queries.json", help="Path to test queries JSON file")
    parser.add_argument("--ground-truth", default="test_data/ground_truth.json", help="Path to ground truth JSON file")
    parser.add_argument("--api-url", default="http://localhost:5000/chat", help="URL of the system API endpoint")
    parser.add_argument("--output-dir", default="results", help="Directory to save evaluation results")
    args = parser.parse_args()
    
    print("Loading test data...")
    test_data = load_test_data(args.queries, args.ground_truth)
    print(f"Loaded {len(test_data)} test cases")
    
    print(f"Starting evaluation using API at {args.api_url}")
    results = evaluate_system(test_data, args.api_url, args.output_dir)
    
    print_summary(results)

if __name__ == "__main__":
    main()