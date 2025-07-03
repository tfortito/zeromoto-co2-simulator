import streamlit as st
import pandas as pd
from datetime import datetime

# Emission factors (kg CO₂/km) — standardized names
EMISSION_FACTORS = {
    "petrol scooter": 0.092,
    "diesel car": 0.171,
    "electric scooter (grid avg)": 0.020,
    "electric scooter (clean energy)": 0.000
}

# Baseline for comparison (used to calculate avoided emissions)
BASELINE_VEHICLE = "petrol scooter"

# Normalize vehicle name to match dictionary keys
def normalize_vehicle_name(name):
    return name.strip().lower()

# Calculate CO₂ avoided using baseline - project vehicle
def calculate_avoided_emissions(distance_km, project_vehicle_raw):
    project_vehicle = normalize_vehicle_name(project_vehicle_raw)
    baseline = EMISSION_FACTORS.get(BASELINE_VEHICLE)
    project = EMISSION_FACTORS.get(project_vehicle)

    if project is None:
        st.warning(f"⚠️ Unknown vehicle type: '{project_vehicle_raw}' — no CO₂ savings calculated.")
        return 0.0

    avoided = distance_km * (baseline - project)
    return round(avoided, 3)

# Initialize session
if "trip_data" not in st.session_state:
    st.session_state.trip_data = []

# Page setup
st.set_page_config(page_title="Zeromoto Trip Logger", layout="wide")
st.title("📋 Zeromoto Trip Logger & CO₂ Avoided Tracker")
st.caption(f"Baseline vehicle for comparison: **{BASELINE_VEHICLE.title()}** ({EMISSION_FACTORS[BASELINE_VEHICLE]} kg/km)")

# --- Upload CSV File ---
st.header("📥 Upload Trip Log (CSV)")
csv_file = st.file_uploader("Upload CSV with: Date, Scooter ID, Distance (km), Vehicle Type", type="csv")

if csv_file:
    df = pd.read_csv(csv_file)
    df["CO₂ Avoided (kg)"] = df.apply(
        lambda row: calculate_avoided_emissions(row["Distance (km)"], row["Vehicle Type"]),
        axis=1
    )
    st.session_state.trip_data.extend(df.to_dict("records"))
    st.success(f"{len(df)} trip entries added successfully.")

# --- Manual Trip Entry ---
st.header("📝 Add a Trip Manually")
with st.form("manual_trip_form"):
    date = st.date_input("Trip Date", value=datetime.today())
    scooter_id = st.text_input("Scooter ID")
    distance = st.number_input("Distance Travelled (km)", min_value=0.0, step=0.1)
    vehicle_type = st.selectbox("Vehicle Type", list(EMISSION_FACTORS.keys()))
    submitted = st.form_submit_button("Add Trip")

    if submitted:
        avoided = calculate_avoided_emissions(distance, vehicle_type)
        new_entry = {
            "Date": date.strftime("%Y-%m-%d"),
            "Scooter ID": scooter_id,
            "Distance (km)": distance,
            "Vehicle Type": vehicle_type,
            "CO₂ Avoided (kg)": avoided
        }
        st.session_state.trip_data.append(new_entry)
        st.success("Trip successfully added.")

# --- Display Trip Log ---
st.header("📊 Logged Trips")
if st.session_state.trip_data:
    log_df = pd.DataFrame(st.session_state.trip_data)
    st.dataframe(log_df, use_container_width=True)

    total_avoided = log_df["CO₂ Avoided (kg)"].sum()
    st.markdown(f"### 🌍 Total CO₂ Avoided: **{round(total_avoided, 3)} kg**")

    st.download_button(
        label="📤 Download Trip Log as CSV",
        data=log_df.to_csv(index=False).encode("utf-8"),
        file_name="zeromoto_trip_log.csv",
        mime="text/csv"
    )
else:
    st.info("No trip data yet. Upload a CSV or add manually to begin.")
