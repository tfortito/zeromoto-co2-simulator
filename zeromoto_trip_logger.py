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

BASELINE_VEHICLE = "Petrol Scooter"

def calculate_avoided_emissions(distance_km, project_vehicle):
    baseline = EMISSION_FACTORS[BASELINE_VEHICLE]
    project = EMISSION_FACTORS[project_vehicle]
    return round(distance_km * (baseline - project), 3)

# Init session
if "trip_data" not in st.session_state:
    st.session_state.trip_data = []

st.set_page_config(page_title="Zeromoto Trip Logger", layout="wide")
st.title("📋 Zeromoto Trip Logger & CO₂ Avoided Tracker")
st.caption(f"Baseline vehicle: **{BASELINE_VEHICLE} ({EMISSION_FACTORS[BASELINE_VEHICLE]} kg/km)**")

# --- Upload CSV ---
st.header("📥 Upload Trip Log (CSV)")
csv_file = st.file_uploader("CSV Format: Date, Scooter ID, Distance (km), Vehicle Type", type="csv")
if csv_file:
    df = pd.read_csv(csv_file)
    df["CO₂ Avoided (kg)"] = df.apply(lambda row: calculate_avoided_emissions(row["Distance (km)"], row["Vehicle Type"]), axis=1)
    st.session_state.trip_data.extend(df.to_dict("records"))
    st.success(f"{len(df)} trips added.")

# --- Manual Entry ---
st.header("📝 Add Trip Manually")
with st.form("manual_entry"):
    date = st.date_input("Trip Date", value=datetime.today())
    scooter_id = st.text_input("Scooter ID")
    distance = st.number_input("Distance Travelled (km)", min_value=0.0, step=0.1)
    vehicle = st.selectbox("Vehicle Type", list(EMISSION_FACTORS.keys()))
    submitted = st.form_submit_button("Add Trip")

    if submitted:
        avoided = calculate_avoided_emissions(distance, vehicle)
        record = {
            "Date": date.strftime("%Y-%m-%d"),
            "Scooter ID": scooter_id,
            "Distance (km)": distance,
            "Vehicle Type": vehicle,
            "CO₂ Avoided (kg)": avoided
        }
        st.session_state.trip_data.append(record)
        st.success("Trip added!")

# --- Table Display ---
st.header("📊 Logged Trips")
if st.session_state.trip_data:
    trip_df = pd.DataFrame(st.session_state.trip_data)
    st.dataframe(trip_df, use_container_width=True)

    total = trip_df["CO₂ Avoided (kg)"].sum()
    st.markdown(f"### 🌍 Total CO₂ Avoided: **{round(total, 3)} kg**")

    st.download_button(
        label="📤 Download Trip Log (CSV)",
        data=trip_df.to_csv(index=False).encode("utf-8"),
        file_name="zeromoto_trip_log.csv",
        mime="text/csv"
    )
else:
    st.info("No trips yet. Upload or enter data to get started.")
