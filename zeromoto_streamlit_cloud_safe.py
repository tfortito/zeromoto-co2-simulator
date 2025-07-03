import streamlit as st
from datetime import datetime
import pandas as pd

# Emission factors (kg CO₂/km)
EMISSION_FACTORS = {
    "Petrol Scooter": 0.092,
    "Diesel Car": 0.171,
    "Electric Scooter (Grid Avg)": 0.020,
    "Electric Scooter (Clean Energy)": 0.000
}

def calculate_emissions(distance_km, vehicle_type):
    if vehicle_type not in EMISSION_FACTORS:
        raise ValueError(f"Unknown vehicle type: {vehicle_type}")
    return round(distance_km * EMISSION_FACTORS[vehicle_type], 3)

def compare_emissions(distance_km):
    return {v: round(distance_km * f, 3) for v, f in EMISSION_FACTORS.items()}

# --- Streamlit UI ---
st.set_page_config(page_title="Zeromoto CO₂ Calculator", layout="centered")
st.title("🛵 Zeromoto CO₂ Emission Simulator")

with st.form("emission_form"):
    date = st.date_input("Trip Date", value=datetime.today())
    scooter_id = st.text_input("Scooter ID (e.g. ZM-001)")
    distance = st.number_input("Distance Travelled (in km)", min_value=0.0, step=0.1)
    vehicle = st.selectbox("Vehicle Type", list(EMISSION_FACTORS.keys()))
    submitted = st.form_submit_button("Calculate Emissions")

    if submitted:
        co2_emitted = calculate_emissions(distance, vehicle)
        st.success(f"📉 Estimated CO₂ Emitted: {co2_emitted} kg")

        # Display comparison chart
        comparison = compare_emissions(distance)
        df = pd.DataFrame(list(comparison.items()), columns=["Vehicle Type", "CO₂ (kg)"])
        st.bar_chart(df.set_index("Vehicle Type"))

        # Prepare downloadable CSV from memory
        record = {
            "Date": date.strftime("%Y-%m-%d"),
            "Scooter ID": scooter_id,
            "Vehicle Type": vehicle,
            "Distance (km)": distance,
            "CO₂ Emitted (kg)": co2_emitted
        }

        result_df = pd.DataFrame([record])
        csv_data = result_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download CO₂ Record (CSV)",
            data=csv_data,
            file_name=f"Zeromoto_CO2_Record_{date}.csv",
            mime="text/csv"
        )
