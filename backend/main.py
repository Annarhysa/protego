from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import CrimeBot
from crime_analyzer import CrimeAnalyzer
from crime_reporter import CrimeReporter

app = Flask(__name__)
CORS(app)
bot = CrimeBot()
analyzer = CrimeAnalyzer()
reporter = CrimeReporter()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data['message'].lower()

    if user_input == 'help':
        return jsonify({"message": "Available commands: analyze, ask [crime], similar [crime], report"})
    elif user_input.startswith('analyze'):
        result = analyzer.interactive_analysis()
        return jsonify({"message": str(result)})
    elif user_input.startswith('report'):
        report = reporter.report_crime()
        return jsonify({"message": "Crime reported successfully. Stay safe."})
    elif user_input.startswith('similar'):
        crime_type = user_input[7:].strip()
        similar_crimes = bot.get_similar_crimes(crime_type)
        response = "Similar crimes:\n" + "\n".join([f"- {crime['crime']}" for crime in similar_crimes])
        return jsonify({"message": response})
    elif user_input.startswith('ask'):
        crime_type = user_input[4:].strip()
        response = bot.get_response(crime_type)
        return jsonify({"message": response})
    else:
        response = bot.get_response(user_input)
        return jsonify({"message": response})

if __name__ == '__main__':
    app.run(debug=True)
