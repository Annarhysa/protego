from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from chatbot import CrimeBot
from crime_analyzer import CrimeAnalyzer
from crime_reporter import CrimeReporter
from recommendation import detect_crime, get_recommendations, filter_similar_suggestions, get_sentiment, elaborate_recommendation
import logging

app = Flask(__name__)
app.static_folder = 'output/plots'
CORS(app)

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

bot = CrimeBot()
analyzer = CrimeAnalyzer()
reporter = CrimeReporter()

def handle_crime_query(query):
    response = bot.get_response(query)
    similar_crimes = bot.get_similar_crimes(query)
    return response, similar_crimes

def display_analysis_result(result):
    if isinstance(result, str):
        return result

    data = result['data']
    df = pd.DataFrame(data)
    crimes = ['murder', 'rape', 'kidnapping_abduction', 'robbery', 'burglary']
    total_crimes = df[crimes].sum()
    
    analysis_results = {
        'total_records': len(data),
        'historical_crime_statistics': {crime.replace('_', ' ').title(): int(count) for crime, count in total_crimes.items()},
        'predictions': {}
    }
    
    if 'predictions' in result and result['predictions']:
        for crime, pred_data in result['predictions'].items():
            forecast = pred_data['forecast']
            analysis_results['predictions'][crime.replace('_', ' ').title()] = [
                {
                    'year': row['ds'].year,
                    'predicted': int(row['yhat']),
                    'confidence_interval': f"{int(row['yhat_lower'])}-{int(row['yhat_upper'])}"
                } for idx, row in forecast.iterrows()
            ]
    
    analysis_results['plot'] = result['plot']
    analysis_results['plot_path'] = result['plot_path']
    return analysis_results

# API Endpoints
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get JSON data from the request
        data = request.json

        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided. Please provide analysis parameters."}), 400

        # Extract parameters
        params = {
            'state': data.get('state'),
            'district': data.get('district'),
            'years': data.get('years', []),
            'crimes': data.get('crimes', []),
            'predict_years': data.get('predict_years', 0)
        }

        # Validate at least one location parameter is provided
        if not params['state'] and not params['district']:
            return jsonify({"error": "You must specify either a state or a district."}), 400

        # Validate years
        available_years = analyzer.get_years(params['state'], params['district'])
        if params['years']:
            # Filter out invalid years
            params['years'] = [year for year in params['years'] if year in available_years]
            if not params['years']:
                params['years'] = available_years  # Use all available years if no valid years are provided
        else:
            params['years'] = available_years  # Use all available years if no years are provided

        # Validate crimes
        prevalent_crimes = analyzer.get_prevalent_crimes(params['state'], params['district'])
        if params['crimes']:
            # Filter out invalid crimes
            params['crimes'] = [crime for crime in params['crimes'] if crime in [c[0] for c in prevalent_crimes]]
            if not params['crimes']:
                params['crimes'] = [crime[0] for crime in prevalent_crimes]  # Use all crimes if no valid crimes are provided
        else:
            params['crimes'] = [crime[0] for crime in prevalent_crimes]  # Use all crimes if no crimes are provided

        # Validate predict_years
        if params['predict_years']:
            if not (1 <= params['predict_years'] <= 100):
                return jsonify({"error": "Prediction years must be between 1 and 100."}), 400

        # Generate analysis
        result = analyzer.generate_analysis(params)
        return jsonify(display_analysis_result(result))

    except Exception as e:
        logger.error(f"Error in /analyze endpoint: {str(e)}")
        return jsonify({"error": "An internal error occurred while processing your request."}), 500

@app.route('/report', methods=['POST'])
def report():
    try:
        data = request.json
        if not data or not data.get('crime'):
            return jsonify({"error": "Please provide crime details."}), 400

        reporter.report_crime(data)  # Pass the data to the report_crime method
        return jsonify({"message": "Crime reported successfully. Remember, you're not alone. Reach out to emergency services if you need immediate help."})

    except Exception as e:
        logger.error(f"Error in /report endpoint: {str(e)}")
        return jsonify({"error": "An internal error occurred while processing your request."}), 500

@app.route('/similar', methods=['GET'])
def similar():
    try:
        crime_type = request.args.get('crime_type')
        if not crime_type:
            return jsonify({"error": "Please specify a crime type to find similar crimes."}), 400
        
        similar_crimes = bot.get_similar_crimes(crime_type)
        if similar_crimes:
            return jsonify({"similar_crimes": similar_crimes})
        else:
            return jsonify({"message": "No similar crimes found."})

    except Exception as e:
        logger.error(f"Error in /similar endpoint: {str(e)}")
        return jsonify({"error": "An internal error occurred while processing your request."}), 500

@app.route('/ask', methods=['GET'])
def ask():
    try:
        crime_type = request.args.get('crime_type')
        if not crime_type:
            return jsonify({"error": "Please specify a crime type to ask about."}), 400
        
        response, similar_crimes = handle_crime_query(crime_type)
        return jsonify({"response": response, "similar_crimes": similar_crimes})

    except Exception as e:
        logger.error(f"Error in /ask endpoint: {str(e)}")
        return jsonify({"error": "An internal error occurred while processing your request."}), 500

@app.route('/query', methods=['GET'])
def query():
    try:
        user_input = request.args.get('input')
        if not user_input:
            return jsonify({"error": "Please provide an input."}), 400
        
        response, similar_crimes = handle_crime_query(user_input)
        return jsonify({"response": response, "similar_crimes": similar_crimes})

    except Exception as e:
        logger.error(f"Error in /query endpoint: {str(e)}")
        return jsonify({"error": "An internal error occurred while processing your request."}), 500

@app.route('/states', methods=['GET'])
def get_available_states():
    try:
        states = analyzer.states
        return jsonify({'states': states})
    except Exception as e:
        logger.error(f"Error in /states endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/districts', methods=['GET'])
def get_available_districts():
    try:
        state = request.args.get('state')
        if not state:
            return jsonify({'error': 'State parameter is required'}), 400
        districts = analyzer.get_districts(state)
        return jsonify({'districts': districts})
    except Exception as e:
        logger.error(f"Error in /districts endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/years', methods=['GET'])
def get_years():
    try:
        state = request.args.get('state')
        district = request.args.get('district')
        
        years = analyzer.get_years(state, district)
        return jsonify({"years": years})
    except Exception as e:
        logger.error(f"Error in /years endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/prevalent-crimes', methods=['GET'])
def get_prevalent_crimes():
    try:
        state = request.args.get('state')
        district = request.args.get('district')
        
        prevalent_crimes = analyzer.get_prevalent_crimes(state, district)
        return jsonify({"prevalent_crimes": prevalent_crimes})
    except Exception as e:
        logger.error(f"Error in /prevalent-crimes endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.json.get("query", "").strip()
    if not user_query:
        return "Please provide a valid query."

    # Detect multiple potential crimes
    detected_crimes = detect_crime(user_query)
    
    # Get all recommendations across detected crimes
    all_recommendations = get_recommendations(detected_crimes)
    
    if not all_recommendations:
        return f"Detected potential crimes: {', '.join(detected_crimes)}.\n No recommendations found."

    # Get user sentiment
    user_sentiment = get_sentiment(user_query)
    
    # Score and sort recommendations
    scored_recs = []
    for rec in all_recommendations:
        rec_sentiment = get_sentiment(rec)
        sentiment_diff = abs(user_sentiment - rec_sentiment)
        scored_recs.append((rec, sentiment_diff))
    
    # Get top 3 recommendations by sentiment match
    top_recommendations = sorted(scored_recs, key=lambda x: x[1])[:3]

    
    # Generate detailed versions
    detailed_recommendations = [
        elaborate_recommendation(rec[0]) for rec in top_recommendations
    ]

    unique_recommendations = filter_similar_suggestions(detailed_recommendations)

    
    return f"Based on your query, I identified the crime as {', '.join(detected_crimes)}.\n Here is my suggestion: {' '.join(unique_recommendations)}"

if __name__ == "__main__":
    app.run(debug=True)