from prophet import Prophet
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

class CrimePredictor:
    def __init__(self):
        self.model = None
        self.last_training_params = None

    def prepare_data(self, data, crime_type):
        """Prepare data for Prophet model"""
        # Group by year and get the specified crime type
        yearly_data = data.groupby('year')[crime_type].sum().reset_index()
        # Prophet requires columns named 'ds' and 'y'
        yearly_data.columns = ['ds', 'y']
        # Convert year to datetime
        yearly_data['ds'] = pd.to_datetime(yearly_data['ds'].astype(str))
        return yearly_data

    def train_and_predict(self, historical_data, crime_type, future_years=100):
        """Train model and make predictions"""
        # Prepare training data
        train_data = self.prepare_data(historical_data, crime_type)
        
        # Initialize and train Prophet model
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            uncertainty_samples=1000
        )
        self.model.fit(train_data)
        
        # Create future dates dataframe
        last_year = train_data['ds'].dt.year.max()
        future_dates = pd.DataFrame({
            'ds': pd.date_range(
                start=datetime.today(),     # Start from current datetime
                periods=future_years,
                freq='YE'                   # Year-end frequency
                )
                })
        
        # Make predictions
        forecast = self.model.predict(future_dates)
        
        return {
            'forecast': forecast,
            'historical': train_data,
            'crime_type': crime_type
        }

    def plot_prediction(self, prediction_data, title_prefix=""):
        """Create visualization of predictions with confidence intervals"""
        forecast = prediction_data['forecast']
        historical = prediction_data['historical']
        crime_type = prediction_data['crime_type']
        
        plt.figure(figsize=(12, 6))
        
        # Plot historical data
        plt.plot(historical['ds'], historical['y'], 
                'k.', label='Historical Data')
        
        # Plot predictions
        plt.plot(forecast['ds'], forecast['yhat'], 
                'b-', label='Predicted')
        
        # Plot confidence intervals
        plt.fill_between(forecast['ds'],
                        forecast['yhat_lower'],
                        forecast['yhat_upper'],
                        color='b', alpha=0.2,
                        label='95% Confidence Interval')
        
        title = f"{title_prefix}Crime Prediction for {crime_type.replace('_', ' ').title()}"
        plt.title(title)
        plt.xlabel('Year')
        plt.ylabel('Number of Cases')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return plt.gcf()  # Return the current figure