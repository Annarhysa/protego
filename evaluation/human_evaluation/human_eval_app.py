from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "crime_prevention_evaluation_secret"  # Change in production

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
AUTOMATED_RESULTS_FILE = os.path.join(RESULTS_DIR, "automated_results.json")
HUMAN_RESULTS_FILE = os.path.join(RESULTS_DIR, "human_results.json")

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_data():
    """Load test queries and automated results"""
    # Load test queries
    with open(os.path.join(DATA_DIR, "test_queries.json"), "r") as f:
        queries = json.load(f)
    
    # Load ground truth
    with open(os.path.join(DATA_DIR, "ground_truth.json"), "r") as f:
        ground_truth = json.load(f)
    
    # Map ground truth by query_id
    ground_truth_map = {item["query_id"]: item for item in ground_truth}
    
    # Load automated results if they exist
    automated_results = []
    if os.path.exists(AUTOMATED_RESULTS_FILE):
        with open(AUTOMATED_RESULTS_FILE, "r") as f:
            automated_data = json.load(f)
            automated_results = automated_data.get("individual_results", [])
    
    # Map automated results by query_id
    automated_results_map = {item["query_id"]: item for item in automated_results}
    
    # Combine data
    evaluation_items = []
    for query in queries:
        query_id = query["query_id"]
        item = {
            "query_id": query_id,
            "query_text": query["query_text"],
            "expected_crime": ground_truth_map.get(query_id, {}).get("crime", "unknown")
        }
        
        # Add automated results if available
        auto_result = automated_results_map.get(query_id, {})
        if auto_result:
            item["detected_crime"] = auto_result.get("detected_crime", "unknown")
            item["recommendation"] = auto_result.get("recommendation", "No recommendation found")
            item["crime_detected_correctly"] = auto_result.get("crime_detected_correctly", False)
        
        evaluation_items.append(item)
    
    return evaluation_items

def load_human_evaluations():
    """Load existing human evaluations"""
    if os.path.exists(HUMAN_RESULTS_FILE):
        with open(HUMAN_RESULTS_FILE, "r") as f:
            data = json.load(f)
            return data.get("evaluations", [])
    return []

def save_human_evaluations(evaluations):
    """Save human evaluations to file"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "evaluations": evaluations
    }
    with open(HUMAN_RESULTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    """Home page with instructions"""
    return render_template("index.html")

@app.route("/evaluate", methods=["GET", "POST"])
def evaluate():
    """Evaluation page for human evaluators"""
    if "evaluator_name" not in session:
        return redirect(url_for("login"))
    
    # Load data
    evaluation_items = load_data()
    existing_evaluations = load_human_evaluations()
    
    # Map existing evaluations by query_id and evaluator
    existing_map = {}
    for eval_item in existing_evaluations:
        key = f"{eval_item.get('evaluator')}_{eval_item.get('query_id')}"
        existing_map[key] = eval_item
    
    # Get evaluator name
    evaluator = session["evaluator_name"]
    
    if request.method == "POST":
        # Process evaluation form submission
        query_id = int(request.form.get("query_id"))
        
        # Create evaluation data
        evaluation = {
            "evaluator": evaluator,
            "query_id": query_id,
            "timestamp": datetime.now().isoformat(),
            "relevance": int(request.form.get("relevance", 0)),
            "helpfulness": int(request.form.get("helpfulness", 0)),
            "clarity": int(request.form.get("clarity", 0)),
            "overall": int(request.form.get("overall", 0)),
            "comments": request.form.get("comments", "")
        }
        
        # Find and update existing evaluation or add new one
        key = f"{evaluator}_{query_id}"
        if key in existing_map:
            # Update existing evaluation
            for i, item in enumerate(existing_evaluations):
                if item.get("evaluator") == evaluator and item.get("query_id") == query_id:
                    existing_evaluations[i] = evaluation
                    break
        else:
            # Add new evaluation
            existing_evaluations.append(evaluation)
        
        # Save updated evaluations
        save_human_evaluations(existing_evaluations)
        
        flash("Evaluation saved successfully!", "success")
        return redirect(url_for("evaluate"))
    
    # Get query ID to evaluate - prioritize queries without evaluations
    unevaluated_queries = []
    for item in evaluation_items:
        key = f"{evaluator}_{item['query_id']}"
        if key not in existing_map:
            unevaluated_queries.append(item)
    
    if unevaluated_queries:
        # Pick a random unevaluated query
        query_to_evaluate = random.choice(unevaluated_queries)
    else:
        # All queries evaluated, pick a random one
        query_to_evaluate = random.choice(evaluation_items)
    
    # Check if query has an existing evaluation
    query_id = query_to_evaluate["query_id"]
    key = f"{evaluator}_{query_id}"
    existing_evaluation = existing_map.get(key, {})
    
    return render_template(
        "evaluate.html",
        query=query_to_evaluate,
        existing=existing_evaluation,
        progress={
            "evaluated": len([k for k in existing_map.keys() if k.startswith(f"{evaluator}_")]),
            "total": len(evaluation_items)
        }
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page for evaluators"""
    if request.method == "POST":
        evaluator_name = request.form.get("evaluator_name", "").strip()
        if evaluator_name:
            session["evaluator_name"] = evaluator_name
            return redirect(url_for("evaluate"))
        else:
            flash("Please enter your name", "error")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for("index"))

@app.route("/results")
def results():
    """View evaluation results summary"""
    if "evaluator_name" not in session:
        return redirect(url_for("login"))
    
    # Load evaluation data
    evaluations = load_human_evaluations()
    
    # Calculate summary statistics
    total_evaluations = len(evaluations)
    evaluators = set(e.get("evaluator") for e in evaluations)
    
    # Calculate average scores
    avg_scores = {"relevance": 0, "helpfulness": 0, "clarity": 0, "overall": 0}
    for metric in avg_scores.keys():
        values = [e.get(metric, 0) for e in evaluations if e.get(metric, 0) > 0]
        if values:
            avg_scores[metric] = sum(values) / len(values)
    
    # Group evaluations by query
    query_scores = {}
    for e in evaluations:
        query_id = e.get("query_id")
        if query_id not in query_scores:
            query_scores[query_id] = []
        query_scores[query_id].append(e)
    
    # Load query texts
    evaluation_items = load_data()
    query_texts = {item["query_id"]: item["query_text"] for item in evaluation_items}
    
    return render_template(
        "results.html",
        evaluations=evaluations,
        total_evaluations=total_evaluations,
        evaluator_count=len(evaluators),
        avg_scores=avg_scores,
        query_scores=query_scores,
        query_texts=query_texts
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Use a different port from main app