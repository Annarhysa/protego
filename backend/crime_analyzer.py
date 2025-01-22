import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import os
from datetime import datetime
from crime_predictor import CrimePredictor

class CrimeAnalyzer:
    def __init__(self):
        self.crime_data = pd.read_csv('./data/crime_data.csv')
        self.states = sorted(self.crime_data['state_ut'].unique())
        self.crimes = ['murder', 'rape', 'kidnapping_abduction', 'robbery', 'burglary']
        self.output_dir = './output/plots'
        self.predictor = CrimePredictor()
        os.makedirs(self.output_dir, exist_ok=True)

    def get_districts(self, state):
        """Get districts for a given state"""
        return sorted(self.crime_data[
            self.crime_data['state_ut'].str.contains(state, case=False)
        ]['district'].unique())

    def get_years(self, state=None, district=None):
        """Get available years for given state/district"""
        data = self.crime_data
        if state:
            data = data[data['state_ut'].str.contains(state, case=False)]
        if district:
            data = data[data['district'].str.contains(district, case=False)]
        return sorted(data['year'].unique())

    def get_prevalent_crimes(self, state=None, district=None):
        """Get crimes sorted by prevalence for location"""
        data = self.crime_data
        if state:
            data = data[data['state_ut'].str.contains(state, case=False)]
        if district:
            data = data[data['district'].str.contains(district, case=False)]
        
        totals = data[self.crimes].sum()
        return sorted([(crime, count) for crime, count in totals.items()], 
                     key=lambda x: x[1], reverse=True)

    def interactive_analysis(self):
        """Interactive analysis with step-by-step input and prediction option"""
        params = {
            'state': None,
            'district': None,
            'years': [],
            'crimes': [],
            'predict_years': 0
        }

        # Keep asking for location until either state or district is provided
        while not params['state'] and not params['district']:
            # 1. State selection
            print("\nAvailable states:")
            for i, state in enumerate(self.states, 1):
                print(f"{i}. {state}")
            state_input = input("\nEnter state number (or press Enter to skip): ").strip()
            
            if state_input:
                try:
                    state_idx = int(state_input) - 1
                    if 0 <= state_idx < len(self.states):
                        params['state'] = self.states[state_idx]
                    else:
                        print("Invalid state number. Please try again.")
                        continue
                except ValueError:
                    print("Please enter a valid number.")
                    continue

            # 2. District selection
            districts = self.get_districts(params['state']) if params['state'] else self.crime_data['district'].unique()
            print(f"\nAvailable districts:")
            for i, district in enumerate(sorted(districts), 1):
                print(f"{i}. {district}")
            district_input = input("\nEnter district number (or press Enter to skip): ").strip()
            
            if district_input:
                try:
                    district_idx = int(district_input) - 1
                    if 0 <= district_idx < len(districts):
                        params['district'] = sorted(districts)[district_idx]
                except ValueError:
                    print("Invalid input. Please try again.")
                    continue

            # Check if at least one location parameter is provided
            if not params['state'] and not params['district']:
                print("\nError: You must specify either a state or a district. Please try again.")
                continue

        # 3. Year selection
        available_years = self.get_years(params['state'], params['district'])
        print("\nAvailable years:", ', '.join(map(str, available_years)))
        year_input = input("Enter years (comma-separated, or press Enter for all years): ").strip()
        if year_input:
            try:
                params['years'] = [int(y.strip()) for y in year_input.split(',')
                                 if int(y.strip()) in available_years]
                if not params['years']:
                    print("No valid years entered. Using all available years.")
                    params['years'] = available_years
            except ValueError:
                print("Invalid year input. Using all available years.")
                params['years'] = available_years
        else:
            # If no year input, use all available years
            params['years'] = available_years

        # 4. Crime type selection
        prevalent_crimes = self.get_prevalent_crimes(params['state'], params['district'])
        print("\nCrimes (sorted by prevalence in selected location):")
        for i, (crime, count) in enumerate(prevalent_crimes, 1):
            print(f"{i}. {crime.replace('_', ' ').title()} ({count} cases)")
        crime_input = input("\nEnter crime numbers (comma-separated, or press Enter for all): ").strip()
        if crime_input:
            try:
                selected_indices = [int(i.strip()) - 1 for i in crime_input.split(',')]
                params['crimes'] = [prevalent_crimes[i][0] for i in selected_indices
                                  if 0 <= i < len(prevalent_crimes)]
                if not params['crimes']:
                    print("No valid crimes selected. Using all crimes.")
                    params['crimes'] = [crime for crime, _ in prevalent_crimes]
            except (ValueError, IndexError):
                print("Invalid crime selection. Using all crimes.")
                params['crimes'] = [crime for crime, _ in prevalent_crimes]

        # 5. Prediction option
        predict_input = input("\nWould you like to see future predictions? (y/n): ").strip().lower()
        if predict_input == 'y':
            while True:
                try:
                    years = input("Enter number of years to predict (1-10): ").strip()
                    years = int(years)
                    if 1 <= years <= 10:
                        params['predict_years'] = years
                        break
                    print("Please enter a number between 1 and 10.")
                except ValueError:
                    print("Please enter a valid number.")

        # Generate analysis
        return self.generate_analysis(params)

    def generate_analysis(self, params):
        """Generate analysis and predictions based on selected parameters"""
        filtered_data = self.crime_data.copy()
        
        if params['state']:
            filtered_data = filtered_data[
                filtered_data['state_ut'].str.contains(params['state'], case=False)
            ]
        if params['district']:
            filtered_data = filtered_data[
                filtered_data['district'].str.contains(params['district'], case=False)
            ]
        if params['years']:
            filtered_data = filtered_data[filtered_data['year'].isin(params['years'])]
        
        crimes_to_analyze = params['crimes'] if params['crimes'] else self.crimes
        
        if filtered_data.empty:
            return "No data found for the specified criteria"

        # Create visualization with predictions if requested
        plt.figure(figsize=(12, 6))
        
        # Plot historical data
        data_to_plot = filtered_data.groupby('year')[crimes_to_analyze].sum()
        data_to_plot.plot(kind='line', marker='o')

        # Add predictions if requested
        predictions = {}
        if params['predict_years'] > 0:
            for crime in crimes_to_analyze:
                try:
                    pred_result = self.predictor.train_and_predict(
                        filtered_data, 
                        crime, 
                        future_years=params['predict_years']
                    )
                    predictions[crime] = pred_result
                    
                    # Plot prediction line
                    forecast = pred_result['forecast']
                    plt.plot(forecast['ds'].dt.year, forecast['yhat'], 
                            '--', label=f'{crime} (predicted)')
                    
                    # Plot confidence intervals
                    plt.fill_between(
                        forecast['ds'].dt.year,
                        forecast['yhat_lower'],
                        forecast['yhat_upper'],
                        alpha=0.2
                    )
                except Exception as e:
                    print(f"Warning: Could not generate prediction for {crime}: {str(e)}")
        
        # Create title
        title = 'Crime Trends'
        if params['state']:
            title += f" for {params['state']}"
        if params['district']:
            title += f" - {params['district']}"
        if params['predict_years'] > 0:
            title += f"\n(with {params['predict_years']}-year prediction)"

        plt.title(title)
        plt.xlabel('Year')
        plt.ylabel('Number of Cases')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()

        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crime_analysis_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        
        # Save to buffer for web display
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()

        return {
            'data': filtered_data.to_dict('records'),
            'plot': base64.b64encode(image_png).decode('utf-8'),
            'plot_path': filepath,
            'parameters': params,
            'years_analyzed': sorted(filtered_data['year'].unique()),
            'predictions': predictions
        }