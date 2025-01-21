import sys
from chatbot import CrimeBot
from crime_analyzer import CrimeAnalyzer
from crime_reporter import CrimeReporter

def main():
    print("Welcome to Crime Awareness and Reporting Portal")
    print("Type 'exit' to quit, 'help' for commands")

    bot = CrimeBot()
    analyzer = CrimeAnalyzer()
    reporter = CrimeReporter()

    while True:
        try:
            user_input = input("\nYou: ").strip().lower()

            if user_input == 'exit':
                print("Thank you for using our service. Stay safe!")
                break
            elif user_input == 'help':
                print("\nAvailable commands:")
                print("- ask [crime]: Ask about a specific crime")
                print("- report: Report a crime")
                print("- analyze [state/city] [year]: Get crime statistics")
                print("- exit: Exit the program")
                continue

            if user_input.startswith('analyze'):
                result = analyzer.analyze_crime(user_input)
                print(result)
            elif user_input.startswith('report'):
                reporter.report_crime()
            else:
                response = bot.get_response(user_input)
                print(f"\nBot: {response}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()