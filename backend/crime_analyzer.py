import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import os
from datetime import datetime

class CrimeAnalyzer:
    def __init__(self):
        self.crime_data = pd.read_csv('./data/crime_data.csv')
        self.states = sorted(self.crime_data['state_ut'].unique())
        self.crimes = ['murder', 'rape', 'kidnapping_abduction', 'robbery', 'burglary']
        self.output_dir = './output/plots'
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
        """Interactive analysis with step-by-step input"""
        # Initialize parameters
        params = {
            'state': None,
            'district': None,
            'years': [],
            'crimes': []
        }

        # 1. State selection
        print("\nAvailable states:")
        for i, state in enumerate(self.states, 1):
            print(f"{i}. {state}")
        while True:
            state_input = input("\nEnter state number (or press Enter to skip): ").strip()
            if not state_input:
                break
            try:
                state_idx = int(state_input) - 1
                if 0 <= state_idx < len(self.states):
                    params['state'] = self.states[state_idx]
                    break
                else:
                    print("Invalid state number. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        # 2. District selection (if state was selected)
        if params['state']:
            districts = self.get_districts(params['state'])
            print(f"\nAvailable districts in {params['state']}:")
            for i, district in enumerate(districts, 1):
                print(f"{i}. {district}")
            district_input = input("\nEnter district number (or press Enter to skip): ").strip()
            if district_input:
                try:
                    district_idx = int(district_input) - 1
                    if 0 <= district_idx < len(districts):
                        params['district'] = districts[district_idx]
                except ValueError:
                    print("Invalid input. Proceeding without district filter.")

        # 3. Year selection
        available_years = self.get_years(params['state'], params['district'])
        print("\nAvailable years:", ', '.join(map(str, available_years)))
        year_input = input("Enter years (comma-separated, or press Enter to skip): ").strip()
        if year_input:
            try:
                params['years'] = [int(y.strip()) for y in year_input.split(',')
                                 if int(y.strip()) in available_years]
            except ValueError:
                print("Invalid year input. Proceeding without year filter.")

        # 4. Crime type selection
        prevalent_crimes = self.get_prevalent_crimes(params['state'], params['district'])
        print("\nCrimes (sorted by prevalence in selected location):")
        for i, (crime, count) in enumerate(prevalent_crimes, 1):
            print(f"{i}. {crime.replace('_', ' ').title()} ({int(count)} cases)")
        crime_input = input("\nEnter crime numbers (comma-separated, or press Enter for all): ").strip()
        if crime_input:
            try:
                selected_indices = [int(i.strip()) - 1 for i in crime_input.split(',')]
                params['crimes'] = [prevalent_crimes[i][0] for i in selected_indices
                                  if 0 <= i < len(prevalent_crimes)]
            except (ValueError, IndexError):
                print("Invalid crime selection. Using all crimes.")

        # Generate analysis
        return self.generate_analysis(params)

    def generate_analysis(self, params):
        """Generate analysis based on selected parameters"""
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

        # Create visualization
        plt.figure(figsize=(12, 6))
        
        if len(params['years']) <= 1:  # Single year or no year specified
            data_to_plot = filtered_data[crimes_to_analyze].sum()
            data_to_plot.plot(kind='bar')
            title = 'Crime Statistics'
        else:  # Multiple years - show trends
            data_to_plot = filtered_data.groupby('year')[crimes_to_analyze].sum()
            data_to_plot.plot(kind='line', marker='o')
            title = 'Crime Trends'

        # Add location info to title
        if params['state']:
            title += f" for {params['state']}"
            if params['district']:
                title += f" - {params['district']}"
        if params['years']:
            title += f" ({', '.join(map(str, params['years']))})"

        plt.title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crime_analysis_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        
        # Save for web display
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
            'parameters': params
        }