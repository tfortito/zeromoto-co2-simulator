import streamlit as st
import pandas as pd
from datetime import datetime

# Emission factors
EMISSION_FACTORS = {
    "Petrol Scooter": 0.092,
    "Diesel Car": 0.171,
    "Electric Scooter (Grid Avg)": 0.020,
    "Electric Scooter (Clean Energy)": 0.000
}

BASELINE_VEHICLE = "Petrol Scooter"
BASELINE_FACTOR = EMISSION_FACTORS[BASELINE_VEHICLE]

def get_emission_factor(vehicle_name):
    return EMISSION_FACTORS.get(vehicle_name.strip())

def calculate_emissions(distance, vehicle):
    factor = get_emission_factor(vehicle)
    if factor is None:
        st.warning(f"⚠️ Unknown vehicle: '{vehicle}' — check spelling.")
        return None, None, None
    emitted = round(distance * factor, 3)
    avoided = round(distance * (BASELINE_FACTOR - factor), 3)
    return factor, emitted, avoided

# Initialize trip log
if "trip_data" not in st.session_state:
    st.session_state.trip_data = []

# UI setup
st.set_page_config(page_title="Zeromoto Trip Tracker", layout="wide")
st.title("🔍 Zeromoto Trip Logger – Emissions & Avoidance")

st.caption(f"Baseline vehicle: **{BASELINE_VEHICLE} ({BASELINE_FACTOR} kg/km)**")

# --- CSV Upload ---
st.header("📥 Upload Trip Log (CSV)")
csv = st.file_uploader("CSV format: Date, Scooter ID, Distance (km), Vehicle Type", type="csv")
if csv:
    df = pd.read_csv(csv)
    records = []
    for _, row in df.iterrows():
        vehicle = row["Vehicle Type"]
        distance = row["Distance (km)"]
        factor, emitted, avoided = calculate_emissions(distance, vehicle)
        if factor is not None:
            records.append({
                "Date": row["Date"],
                "Scooter ID": row["Scooter ID"],
                "Distance (km)": distance,
                "Vehicle Type": vehicle,
                "Emission Factor": factor,
                "CO₂ Emitted (kg)": emitted,
                "CO₂ Avoided (kg)": avoided
            })
    st.session_state.trip_data.extend(records)
    st.success(f"{len(records)} trips added!")

# --- Manual Entry ---
st.header("📝 Add Trip Manually")
with st.form("manual_form"):
    date = st.date_input("Trip Date", datetime.today())
    scooter_id = st.text_input("Scooter ID")
    distance = st.number_input("Distance (km)", min_value=0.0, step=0.1)
    vehicle = st.selectbox("Vehicle Type", list(EMISSION_FACTORS.keys()))
    submitted = st.form_submit_button("Add Trip")

    if submitted:
        factor, emitted, avoided = calculate_emissions(distance, vehicle)
        if factor is not None:
            st.session_state.trip_data.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Scooter ID": scooter_id,
                "Distance (km)": distance,
                "Vehicle Type": vehicle,
                "Emission Factor": factor,
                "CO₂ Emitted (kg)": emitted,
                "CO₂ Avoided (kg)": avoided
            })
            st.success("Trip added.")

# --- Show table ---
st.header("📊 Trip Log")
if st.session_state.trip_data:
    df = pd.DataFrame(st.session_state.trip_data)
    st.dataframe(df, use_container_width=True)

    total_emitted = df["CO₂ Emitted (kg)"].sum()
    total_avoided = df["CO₂ Avoided (kg)"].sum()

    st.metric("🔥 Total CO₂ Emitted", f"{total_emitted:.3f} kg")
    st.metric("🌍 Total CO₂ Avoided", f"{total_avoided:.3f} kg")

    st.download_button(
        "📤 Download Trip Log CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="zeromoto_trip_log.csv",
        mime="text/csv"
    )
else:
    st.info("No data yet. Upload CSV or add trips manually.")
