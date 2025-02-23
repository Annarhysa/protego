from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from chatbot import CrimeBot
from crime_analyzer import CrimeAnalyzer
from crime_reporter import CrimeReporter

app = Flask(__name__)
CORS(app)

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
    
    analysis_results['plot_path'] = result['plot_path']
    return analysis_results

# API Endpoints
@app.route('/analyze', methods=['GET'])
def analyze():
    result = analyzer.interactive_analysis()
    return jsonify(display_analysis_result(result))

@app.route('/report', methods=['POST'])
def report():
    data = request.json
    reporter.report_crime(data)
    return jsonify({"message": "Crime reported successfully. Remember, you're not alone. Reach out to emergency services if you need immediate help."})

@app.route('/similar', methods=['GET'])
def similar():
    crime_type = request.args.get('crime_type')
    if not crime_type:
        return jsonify({"error": "Please specify a crime type to find similar crimes."}), 400
    
    similar_crimes = bot.get_similar_crimes(crime_type)
    if similar_crimes:
        return jsonify({"similar_crimes": similar_crimes})
    else:
        return jsonify({"message": "No similar crimes found."})

@app.route('/ask', methods=['GET'])
def ask():
    crime_type = request.args.get('crime_type')
    if not crime_type:
        return jsonify({"error": "Please specify a crime type to ask about."}), 400
    
    response, similar_crimes = handle_crime_query(crime_type)
    return jsonify({"response": response, "similar_crimes": similar_crimes})

@app.route('/query', methods=['GET'])
def query():
    user_input = request.args.get('input')
    if not user_input:
        return jsonify({"error": "Please provide an input."}), 400
    
    response, similar_crimes = handle_crime_query(user_input)
    return jsonify({"response": response, "similar_crimes": similar_crimes})

if __name__ == "__main__":
    app.run(debug=True)