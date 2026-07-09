"""
generate_sample_data.py
HemaGrid AI - Synthetic Telemetry Data Generator

Generates a mock CSV dataset simulating historical blood demand patterns,
epidemiological outbreak metrics (dengue cases), and seasonal weather data.
"""

import os
import pandas as pd
import numpy as np

def generate_dataset(num_records=1000):
    np.random.seed(42)

    # Categories
    blood_types = ['A_POS', 'A_NEG', 'B_POS', 'B_NEG', 'AB_POS', 'AB_NEG', 'O_POS', 'O_NEG']
    hospital_types = ['General', 'Trauma', 'Clinic']
    
    # Generate random features
    hospital_ids = np.random.randint(1, 10, size=num_records)
    h_type_choice = np.random.choice(hospital_types, size=num_records, p=[0.5, 0.3, 0.2])
    b_type_choice = np.random.choice(blood_types, size=num_records)
    
    temperatures = np.random.uniform(22.0, 38.0, size=num_records)
    dengue_cases = np.random.randint(0, 300, size=num_records)
    
    day_of_week = np.random.randint(1, 8, size=num_records)
    month = np.random.randint(1, 13, size=num_records)
    
    # Calculate baseline demand with dependencies (the ground truth rules)
    demand = np.zeros(num_records)
    for i in range(num_records):
        base = 10.0
        # Trauma centers need more blood
        if h_type_choice[i] == 'Trauma':
            base += 15.0
        elif h_type_choice[i] == 'General':
            base += 5.0
            
        # O-Neg is universal, highly demanded
        if b_type_choice[i] == 'O_NEG':
            base += 8.0
            
        # Summer heat / outbreaks drive up demand (especially dengue which limits platelets)
        if temperatures[i] > 32.0:
            base += 4.0
        if dengue_cases[i] > 150:
            base += 12.0
            
        # Add random noise
        noise = np.random.normal(0.0, 2.0)
        demand[i] = max(1.0, round(base + noise))

    # Construct dataframe
    df = pd.DataFrame({
        "hospital_id": hospital_ids,
        "hospital_type": h_type_choice,
        "blood_type": b_type_choice,
        "temperature_c": np.round(temperatures, 1),
        "dengue_cases_weekly": dengue_cases,
        "day_of_week": day_of_week,
        "month": month,
        "units_demanded": demand.astype(int)
    })

    # Save to file
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sample_blood_data.csv")
    df.to_csv(out_path, index=False)
    print(f"Successfully generated {num_records} sample records at: {out_path}")

if __name__ == "__main__":
    generate_dataset()
