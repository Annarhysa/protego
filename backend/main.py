import sys
import random
import pandas as pd
from chatbot import CrimeBot
from crime_analyzer import CrimeAnalyzer
from crime_reporter import CrimeReporter

def handle_crime_query(bot, query):
    response = bot.get_response(query)
    print(f"\nBot: {response}")
    
    similar_crimes = bot.get_similar_crimes(query)
    if similar_crimes:
        print("\nRelated crimes you might want to know about:")
        for crime in similar_crimes:
            print(f"- {crime['crime']}: {crime['description'][:100]}...")

def display_analysis_result(result):
    if isinstance(result, str):
        print(f"\nBot: {result}")
        return

    print("\nAnalysis Results:")
    data = result['data']
    print(f"Total records found: {len(data)}")
    
    # Display summary statistics
    df = pd.DataFrame(data)
    crimes = ['murder', 'rape', 'kidnapping_abduction', 'robbery', 'burglary']
    total_crimes = df[crimes].sum()
    
    print("\nHistorical Crime Statistics:")
    for crime, count in total_crimes.items():
        print(f"- {crime.replace('_', ' ').title()}: {int(count)}")
    
    # Display predictions if available
    if 'predictions' in result and result['predictions']:
        print("\nPredicted Crime Rates:")
        for crime, pred_data in result['predictions'].items():
            forecast = pred_data['forecast']
            print(f"\n{crime.replace('_', ' ').title()}:")
            for idx, row in forecast.iterrows():
                year = row['ds'].year
                predicted = int(row['yhat'])
                lower = int(row['yhat_lower'])
                upper = int(row['yhat_upper'])
                print(f"  {year}: {predicted} cases (95% CI: {lower}-{upper})")
    
    # The plot has been generated and saved
    print(f"\nVisualization has been saved to: {result['plot_path']}")

def main():
    print("Welcome to Crime Awareness and Reporting Portal")
    print("Type 'exit' to quit, 'help' for commands")

    bot = CrimeBot()
    analyzer = CrimeAnalyzer()
    reporter = CrimeReporter()

    while True:
        try:
            user_input = input("\nYou: ").strip()
            original_input = user_input
            user_input = user_input.lower()

            if user_input == 'exit':
                print("Thank you for using our service. Stay safe!")
                break
            elif user_input == 'help':
                print("\nAvailable commands:")
                print("- analyze: Start interactive crime analysis")
                print("- ask [crime]: Ask about a specific crime")
                print("- similar [crime]: Find similar crimes")
                print("- report: Report a crime")
                print("- exit: Exit the program")
                continue

            if user_input.startswith('analyze'):
                result = analyzer.interactive_analysis()
                display_analysis_result(result)
            elif user_input.startswith('report'):
                reporter.report_crime()
            elif user_input.startswith('similar'):
                crime_type = original_input[7:].strip()
                if not crime_type:
                    print("\nBot: Please specify a crime type to find similar crimes.")
                    continue
                
                similar_crimes = bot.get_similar_crimes(crime_type)
                if similar_crimes:
                    print("\nBot: Here are similar crimes:")
                    for crime in similar_crimes:
                        print(f"\n- {crime['crime']}:")
                        print(f"  Description: {crime['description']}")
                        print(f"  Similarity: {crime['similarity']:.2f}")
                else:
                    print("\nBot: No similar crimes found.")
            elif user_input.startswith('ask'):
                crime_type = original_input[4:].strip()
                if not crime_type:
                    print("\nBot: Please specify a crime type to ask about.")
                    continue
                
                handle_crime_query(bot, crime_type)
            else:
                handle_crime_query(bot, original_input)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again or type 'help' for available commands.")

if __name__ == "__main__":
    main()