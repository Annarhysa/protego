import pandas as pd
import json
from datetime import datetime
import geocoder
from location import get_location

class CrimeReporter:
    def __init__(self):
        self.report_file = './data/reported_crimes.csv'
        self.load_attack_types()

    def load_attack_types(self):
        # Load attack types from your data
        self.attack_types = [
            "Armed Assault", "Bombing/Explosion", "Assassination",
            "Hostage Taking", "Facility Attack", "Unarmed Assault"
        ]

    def report_crime(self, data):
        current_date = datetime.now()
        try:
            lat, lon, location = get_location()
        except Exception as e:
            print("Could not get location automatically. Please provide city name:")
            location = data.get('location', 'Unknown')  # Use location from data if automatic detection fails
            lat, lon = None, None

        attack_type = data.get('attack_type', 'Unknown')  # Get attack type from data
        summary = data.get('summary', 'No description provided')  # Get summary from data

        report = {
            'iyear': current_date.year,
            'imonth': current_date.month,
            'iday': current_date.day,
            'location': location,
            'latitude': lat,
            'longitude': lon,
            'summary': summary,
            'attacktype1_txt': attack_type
        }

        df = pd.DataFrame([report])
        df.to_csv(self.report_file, mode='a', header=False, index=False)

        return report