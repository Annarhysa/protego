from flask import Flask, request, jsonify
from chatbot import CrimeBot
from crime_analyzer import CrimeAnalyzer
#from crime_reporter import CrimeReporter  #Uncomment when you will have crime_reporter.py
import json

app = Flask(__name__)

# Initialize the CrimeBot and CrimeAnalyzer
crime_bot = CrimeBot()
crime_analyzer = CrimeAnalyzer()
#crime_reporter = CrimeReporter() #Uncomment when you will have crime_reporter.py

@app.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    """
    Endpoint for the chatbot.  Handles user input and routes to appropriate
    functionality based on the input.
    """
    try:
        user_input = request.json['message'].strip()
        original_input = user_input
        user_input = user_input.lower()

        if user_input == 'help':
            return jsonify({
                'response': "\nAvailable commands:\n"
                           "- analyze: Start interactive crime analysis\n"
                           "- ask [crime]: Ask about a specific crime\n"
                           "- similar [crime]: Find similar crimes\n"
                           #"- report: Report a crime\n" #Uncomment when you will have crime_reporter.py
                           "- exit: Exit the program"
            })
        #elif user_input == 'report': #Uncomment when you will have crime_reporter.py
        #    #  This is a placeholder; the actual crime reporting logic would need to be implemented.
        #    return jsonify({'response': "Crime reporting functionality is not yet implemented."}) #Uncomment when you will have crime_reporter.py

        elif user_input.startswith('similar'):
            crime_type = original_input[7:].strip()
            if not crime_type:
                return jsonify({'response': "Please specify a crime type to find similar crimes."})
            similar_crimes = crime_bot.get_similar_crimes(crime_type)
            if similar_crimes:
                response_text = "Here are similar crimes:\n"
                for crime in similar_crimes:
                    response_text += f"\n- {crime['crime']}:\n"
                    response_text += f" Description: {crime['description']}\n"
                    response_text += f" Similarity: {crime['similarity']:.2f}\n"
                return jsonify({'response': response_text})
            else:
                return jsonify({'response': "No similar crimes found."})

        elif user_input.startswith('ask'):
            crime_type = original_input[4:].strip()
            if not crime_type:
                return jsonify({'response': "Please specify a crime type to ask about."})
            response = handle_crime_query(crime_bot, crime_type)
            return jsonify({'response': response})

        elif user_input == 'analyze':
            # Start interactive analysis and return the result
            result = crime_analyzer.interactive_analysis()  # This now returns a dictionary
            if isinstance(result, str):  # Check if it's an error string
                return jsonify({'error': result}), 400
            # Include the plot (base64 encoded), data, and other analysis results
            return jsonify(result)
        else:
            # Handle general queries using the chatbot
            response = handle_crime_query(crime_bot, original_input)
            return jsonify({'response': response})


    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/analyze_crime', methods=['POST'])
def analyze_crime_endpoint():
    """
    Endpoint for direct crime analysis (non-interactive).
    Receives analysis parameters and returns analysis results, including a plot.
    """
    try:
        params = request.json  # Expecting a JSON with state, district, years, crimes, predict_years
        result = crime_analyzer.generate_analysis(params)

        if isinstance(result, str):  # Handle case where result is an error message
            return jsonify({'error': result}), 400

        # Include the plot (base64 encoded), data, and other analysis results
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/states', methods=['GET'])
def get_available_states():
    """
    Endpoint to get a list of available states for analysis.
    """
    try:
        states = crime_analyzer.states
        return jsonify({'states': states})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/districts', methods=['GET'])
def get_available_districts():
    """
    Endpoint to get a list of available districts for a given state.
    Requires a 'state' query parameter.
    """
    try:
        state = request.args.get('state')
        if not state:
            return jsonify({'error': 'State parameter is required'}), 400
        districts = crime_analyzer.get_districts(state)
        return jsonify({'districts': districts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_crime_query(bot, query):
    """
    Helper function to get a response from the chatbot and display related crimes.
    Mimics the handle_crime_query function from main.py
    """
    response = bot.get_response(query)
    response_text = f"\nBot: {response}\n"
    similar_crimes = bot.get_similar_crimes(query)
    if similar_crimes:
        response_text += "\nRelated crimes you might want to know about:\n"
        for crime in similar_crimes:
            response_text += f"- {crime['crime']}: {crime['description'][:100]}...\n"
    return response_text

if __name__ == '__main__':
    app.run(debug=True)
