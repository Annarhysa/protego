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

    def report_crime(self):
        print("\nCrime Reporting System")
        print("----------------------")

        current_date = datetime.now()
        try:
            lat, lon, location = get_location()
        except Exception as e:
            print("Could not get location automatically. Please provide city name:")
            location = input()
            lat, lon = None, None

        print("\nSelect type of crime:")
        for i, attack_type in enumerate(self.attack_types, 1):
            print(f"{i}. {attack_type}")

        type_index = int(input("Enter number: ")) - 1
        attack_type = self.attack_types[type_index]

        print("\nPlease provide a brief description of the incident:")
        summary = input()

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

        print("\nReport submitted successfully. Please contact emergency services if immediate help is needed.")
        print("\nHere are some resources for you:")
        print("- National Helpline: 112")
        print("- Local Police: 100 or your regional number")
        print("- Emotional Support: Visit www.support.com for guidance")
        print("- Stay indoors, and ensure you're in a safe environment.")
        return report
