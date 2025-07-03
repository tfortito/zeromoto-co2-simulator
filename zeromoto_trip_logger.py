# Generate a clean version of the trip logger Streamlit app (with no file writing)

trip_logger_clean_code = """
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

# Session state init
if "trip_data" not in st.session_state:
    st.session_state.trip_data = []

st.set_page_config(page_title="Zeromoto Trip Logger", layout="wide")
st.title("📋 Zeromoto Trip Logger & CO₂ Tracker")

# --- CSV Upload Section ---
st.header("📥 Upload Trip Log (CSV)")
csv_file = st.file_uploader("Upload CSV File (Date, Scooter ID, Distance (km), Vehicle Type)", type="csv")
if csv_file is not None:
    df = pd.read_csv(csv_file)
    df["CO₂ Emitted (kg)"] = df.apply(lambda row: calculate_emissions(row["Distance (km)"], row["Vehicle Type"]), axis=1)
    st.session_state.trip_data.extend(df.to_dict("records"))
    st.success(f"{len(df)} trips added from CSV")

# --- Manual Entry Section ---
st.header("📝 Add Trip Manually")
with st.form("manual_trip_form"):
    date = st.date_input("Trip Date", value=datetime.today())
    scooter_id = st.text_input("Scooter ID")
    distance = st.number_input("Distance Travelled (km)", min_value=0.0, step=0.1)
    vehicle_type = st.selectbox("Vehicle Type", list(EMISSION_FACTORS.keys()))
    submitted = st.form_submit_button("Add Trip")

    if submitted:
        co2 = calculate_emissions(distance, vehicle_type)
        record = {
            "Date": date.strftime("%Y-%m-%d"),
            "Scooter ID": scooter_id,
            "Distance (km)": distance,
            "Vehicle Type": vehicle_type,
            "CO₂ Emitted (kg)": co2
        }
        st.session_state.trip_data.append(record)
        st.success("Trip added!")

# --- Display & Export Table ---
st.header("📊 Logged Trips")
if st.session_state.trip_data:
    trip_df = pd.DataFrame(st.session_state.trip_data)
    st.dataframe(trip_df, use_container_width=True)

    total_co2 = trip_df["CO₂ Emitted (kg)"].sum()
    st.markdown(f"### 🌍 Total CO₂ Avoided: **{round(total_co2, 3)} kg**")

    st.download_button(
        label="📤 Download Full Log as CSV",
        data=trip_df.to_csv(index=False).encode("utf-8"),
        file_name="zeromoto_trip_log.csv",
        mime="text/csv"
    )
else:
    st.info("No trips logged yet. Upload a CSV or add manually.")
"""

# Save the clean version to file
clean_trip_logger_file = "/mnt/data/zeromoto_trip_logger_clean.py"
with open(clean_trip_logger_file, "w", encoding="utf-8") as file:
    file.write(trip_logger_clean_code)

clean_trip_logger_file