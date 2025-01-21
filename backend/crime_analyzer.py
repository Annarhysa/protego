import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

class CrimeAnalyzer:
    def __init__(self):
        self.crime_data = pd.read_csv('/data/crime_data.csv')

    def analyze_crime(self, query):
        parts = query.split()
        if len(parts) < 2:
            return "Please specify a state/city and optionally a year"

        location = parts[1]
        year = parts[2] if len(parts) > 2 else None

        filtered_data = self.crime_data
        if location:
            filtered_data = filtered_data[
                (filtered_data['state_ut'].str.contains(location, case=False)) |
                (filtered_data['district'].str.contains(location, case=False))
            ]
        if year:
            filtered_data = filtered_data[filtered_data['year'] == int(year)]

        if filtered_data.empty:
            return "No data found for the specified criteria"

        # Create visualizations
        plt.figure(figsize=(12, 6))
        crimes = ['murder', 'rape', 'kidnapping_abduction', 'robbery', 'burglary']
        filtered_data[crimes].sum().plot(kind='bar')
        plt.title(f'Crime Statistics for {location}')
        plt.tight_layout()

        # Save plot to string
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png)

        return {
            'data': filtered_data.to_dict('records'),
            'plot': graphic
        }
