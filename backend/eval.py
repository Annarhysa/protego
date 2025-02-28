import json
import requests  # To make requests to your Flask API

# Load test cases
with open("./data/test_queries.json", "r") as f:
    data = json.load(f)

# Extract test cases correctly
test_cases = data["test_cases"]

# API URL
API_URL = "http://127.0.0.1:5000/chat"  # Update this if your Flask app runs elsewhere

# Initialize evaluation metrics
total_cases = len(test_cases)
correct_crime_predictions = 0
correct_recommendations = 0

for entry in test_cases:
    query = entry["query"]
    expected_crime = entry["expected_crime"]
    expected_recommendation = entry["expected_recommendation"]

    # Send request to your Flask API
    response = requests.post(API_URL, json={"query": query})
    
    if response.status_code == 200:
        result = response.text  # Assuming response contains crime & recommendation text
        
        # Extract crime detected from the response
        detected_crime = None
        if "identified the crime as" in result:
            detected_crime = result.split("identified the crime as")[1].split(".")[0].strip()

        # Extract recommendation from the response
        detected_recommendation = result.split("Here is my suggestion:")[-1].strip()

        # Evaluate crime detection
        if detected_crime and detected_crime.lower() == expected_crime.lower():
            correct_crime_predictions += 1

        # Evaluate recommendation
        if detected_recommendation and expected_recommendation.lower() in detected_recommendation.lower():
            correct_recommendations += 1

    else:
        print(f"Error: Received status code {response.status_code} for query: {query}")

# Calculate accuracy
crime_accuracy = correct_crime_predictions / total_cases * 100
recommendation_accuracy = correct_recommendations / total_cases * 100

print(f"Crime Detection Accuracy: {crime_accuracy:.2f}%")
print(f"Recommendation Accuracy: {recommendation_accuracy:.2f}%")