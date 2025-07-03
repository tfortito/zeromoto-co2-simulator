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

# Define the baseline vehicle
BASELINE_VEHICLE = "Petrol Scooter"

def normalize_vehicle_name(name):
    return name.strip().lower()

def get_emission_factor(name):
    name = normalize_vehicle_name(name)
    for key in EMISSION_FACTORS:
        if normalize_vehicle_name(key) == name:
            return EMISSION_FACTORS[key]
    return None

def calculate_emissions(distance_km, vehicle_type):
    factor = get_emission_factor(vehicle_type)
    baseline = EMISSION_FACTORS[BASELINE_VEHICLE]
    
    if factor is None:
        st.warning(f"⚠️ Unknown vehicle type: '{vehicle_type}'")
        return 0.0, 0.0

    emitted = round(distance_km * factor, 3)
    avoided = round(distance_km * (baseline - factor), 3)
    return emitted, avoided

# Initialize session state
if "trip_data" not in st.session_state:
    st.session_state.trip_data = []

# UI
st.set_page_config(page_title="Zeromoto CO₂ Tracker", layout="wide")
st.title("📋 Zeromoto Trip Logger")
st.caption(f"Baseline comparison vehicle: **{BASELINE_VEHICLE}** ({EMISSION_FACTORS[BASELINE_VEHICLE]} kg CO₂/km)")

# --- CSV Upload ---
st.header("📥 Upload Trip Log (CSV)")
csv_file = st.file_uploader("Expected columns: Date, Scooter ID, Distance (km), Vehicle Type", type="csv")
if csv_file:
    df = pd.read_csv(csv_file)
    emitted_list = []
    avoided_list = []

    for _, row in df.iterrows():
        emitted, avoided = calculate_emissions(row["Distance (km)"], row["Vehicle Type"])
        emitted_list.append(emitted)
        avoided_list.append(avoided)

    df["CO₂ Emitted (kg)"] = emitted_list
    df["CO₂ Avoided (kg)"] = avoided_list
    st.session_state.trip_data.extend(df.to_dict("records"))
    st.success(f"{len(df)} trips added.")

# --- Manual Trip Form ---
st.header("📝 Add Trip Manually")
with st.form("manual_form"):
    date = st.date_input("Trip Date", value=datetime.today())
    scooter_id = st.text_input("Scooter ID")
    distance = st.number_input("Distance Travelled (km)", min_value=0.0, step=0.1)
    vehicle = st.selectbox("Vehicle Type", list(EMISSION_FACTORS.keys()))
    submitted = st.form_submit_button("Add Trip")

    if submitted:
        emitted, avoided = calculate_emissions(distance, vehicle)
        record = {
            "Date": date.strftime("%Y-%m-%d"),
            "Scooter ID": scooter_id,
            "Distance (km)": distance,
            "Vehicle Type": vehicle,
            "CO₂ Emitted (kg)": emitted,
            "CO₂ Avoided (kg)": avoided
        }
        st.session_state.trip_data.append(record)
        st.success("Trip successfully added!")

# --- Display Trip Table ---
st.header("📊 Trip Log")
if st.session_state.trip_data:
    trip_df = pd.DataFrame(st.session_state.trip_data)
    st.dataframe(trip_df, use_container_width=True)

    total_emitted = trip_df["CO₂ Emitted (kg)"].sum()
    total_avoided = trip_df["CO₂ Avoided (kg)"].sum()

    st.markdown(f"### 🔥 Total CO₂ Emitted: **{round(total_emitted, 3)} kg**")
    st.markdown(f"### 🌍 Total CO₂ Avoided: **{round(total_avoided, 3)} kg**")

    st.download_button(
        label="📤 Download Trip Log as CSV",
        data=trip_df.to_csv(index=False).encode("utf-8"),
        file_name="zeromoto_trip_log.csv",
        mime="text/csv"
    )
else:
    st.info("No trips yet. Upload a CSV or enter manually.")
