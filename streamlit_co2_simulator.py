import streamlit as st
import pandas as pd
from datetime import datetime

# Emission factors (kg CO₂/km)
emission_factors = {
    "Petrol Scooter": 0.092,
    "Diesel Car": 0.171,
    "Electric Scooter (Clean Energy)": 0.0,
    "Electric Scooter (Grid Avg)": 0.020
}

st.title("🛵 Zeromoto CO₂ Emission Simulator")

vehicle = st.selectbox("Select Vehicle Type", list(emission_factors.keys()))
distance = st.number_input("Enter Distance Travelled (in km)", min_value=0.0, step=0.1)

if st.button("Calculate CO₂ Emission"):
    co2 = round(distance * emission_factors[vehicle], 3)
    st.success(f"Estimated CO₂ Emitted: {co2} kg")

    # Save result
    result = {
        "Date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "Vehicle Type": vehicle,
        "Distance (km)": distance,
        "CO₂ Emitted (kg)": co2
    }
    df = pd.DataFrame([result])
    csv_path = f"CO2_Simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    st.download_button("📥 Download Result as CSV", data=df.to_csv(index=False), file_name=csv_path, mime="text/csv")
