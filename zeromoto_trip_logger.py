import streamlit as st
import pandas as pd
from datetime import datetime

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

# Initialize session state
if "trip_data" not in st.session_state:
    st.session_state.trip_data = []

# UI layout
st.set_page_config(page_title="Zeromoto Trip Logger", layout="wide")
st.title("📋 Zeromoto Trip Logger & CO₂ Tracker")

# --- Upload CSV ---
st.header("📥 Upload Trip Log (CSV)")
csv_file = st.file_uploader("Upload a CSV (Date, Scooter ID, Distance (km), Vehicle Type)", type="csv")
if csv_file:
    df = pd.read_csv(csv_file)
    df["CO₂ Emitted (kg)"] = df.apply(lambda row: calculate_emissions(row["Distance (km)"], row["Vehicle Type"]), axis=1)
    st.session_state.trip_data.extend(df.to_dict("records"))
    st.success(f"{len(df)} trips added from file.")

# --- Manual Entry ---
st.header("📝 Add Trip Manually")
with st.form("manual_entry"):
    date = st.date_input("Trip Date", value=datetime.today())
    scooter_id = st.text_input("Scooter ID")
    distance = st.number_input("Distance Travelled (km)", min_value=0.0, step=0.1)
    vehicle = st.selectbox("Vehicle Type", list(EMISSION_FACTORS.keys()))
    submitted = st.form_submit_button("Add Trip")

    if submitted:
        co2 = calculate_emissions(distance, vehicle)
        record = {
            "Date": date.strftime("%Y-%m-%d"),
            "Scooter ID": scooter_id,
            "Distance (km)": distance,
            "Vehicle Type": vehicle,
            "CO₂ Emitted (kg)": co2
        }
        st.session_state.trip_data.append(record)
        st.success("Trip added!")

# --- Trip Log Table ---
st.header("📊 Logged Trips")
if st.session_state.trip_data:
    trip_df = pd.DataFrame(st.session_state.trip_data)
    st.dataframe(trip_df, use_container_width=True)

    total = trip_df["CO₂ Emitted (kg)"].sum()
    st.markdown(f"### 🌍 Total CO₂ Avoided: **{round(total, 3)} kg**")

    st.download_button(
        label="📤 Download Trip Log as CSV",
        data=trip_df.to_csv(index=False).encode("utf-8"),
        file_name="zeromoto_trip_log.csv",
        mime="text/csv"
    )
else:
    st.info("No trips logged yet. Upload a CSV or add trips manually.")
