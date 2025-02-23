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
        
        # Convert numpy.int64 to Python int
        years = sorted(data['year'].unique().tolist())
        return years

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

    def interactive_analysis(self, params):
        """Perform analysis based on provided parameters."""
    # Validate parameters
        if not params:
            raise ValueError("No parameters provided.")

        # Validate at least one location parameter is provided
        if not params.get('state') and not params.get('district'):
            raise ValueError("You must specify either a state or a district.")

        # Validate years
        available_years = self.get_years(params.get('state'), params.get('district'))
        if params.get('years'):
            params['years'] = [year for year in params['years'] if year in available_years]
            if not params['years']:
                params['years'] = available_years  # Use all available years if no valid years are provided
        else:
            params['years'] = available_years  # Use all available years if no years are provided

        # Validate crimes
        prevalent_crimes = self.get_prevalent_crimes(params.get('state'), params.get('district'))
        if params.get('crimes'):
            params['crimes'] = [crime for crime in params['crimes'] if crime in [c[0] for c in prevalent_crimes]]
            if not params['crimes']:
                params['crimes'] = [crime[0] for crime in prevalent_crimes]  # Use all crimes if no valid crimes are provided
        else:
            params['crimes'] = [crime[0] for crime in prevalent_crimes]  # Use all crimes if no crimes are provided

        # Validate predict_years
        if params.get('predict_years'):
            if not (1 <= params['predict_years'] <= 100):
                raise ValueError("Prediction years must be between 1 and 100.")

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