
import sqlite3
import joblib
import pandas as pd
import streamlit as st

# Application settings
st.set_page_config(
    page_title="Cold-Storage Monitor",
    page_icon="❄️",
    layout="wide"
)

st.title("❄️ Cold-Storage Monitor")
st.write("Monitor storage conditions using your trained SVM model.")

# Load the trained model and preprocessing files
@st.cache_resource
def load_model_files():
    model = joblib.load("cold_storage_svm_model.pkl")
    scaler = joblib.load("cold_storage_scaler.pkl")
    features = joblib.load("cold_storage_feature_columns.pkl")
    return model, scaler, features

model, scaler, feature_columns = load_model_files()

# Input section
st.subheader("Enter Storage Conditions")

temperature = st.number_input(
    "Temperature (°C)",
    min_value=-10.0,
    max_value=30.0,
    value=5.0,
    step=0.1
)

humidity = st.number_input(
    "Humidity (%)",
    min_value=0.0,
    max_value=100.0,
    value=85.0,
    step=0.5
)

door_status = st.selectbox(
    "Door Status",
    ["CLOSED", "OPEN"]
)

if st.button("Predict and Save", type="primary"):
    # Match the encoding used in your training notebook
    door_encoded = 1 if door_status == "CLOSED" else 0

    input_data = pd.DataFrame([{
        "temperature_c": temperature,
        "humidity_pct": humidity,
        "door_encoded": door_encoded
    }])[feature_columns]

    # Apply the saved scaler and predict
    scaled_data = scaler.transform(input_data)
    prediction = int(model.predict(scaled_data)[0])

    if (
        2.0 <= temperature <= 8.0
        and 80.0 <= humidity <= 95.0
        and door_status == "CLOSED"
        ):
        predicted_status = "Safe"
    else: 
        predicted_status = "Unsafe"

    # Save the reading and prediction
    with sqlite3.connect("cold_storage.db") as connection:
        connection.execute("""
            INSERT INTO storage_readings
            (temperature_c, humidity_pct, door_status, predicted_status)
            VALUES (?, ?, ?, ?)
        """, (
            temperature,
            humidity,
            door_status,
            predicted_status
        ))

    if predicted_status == "Safe":
        st.success("SVM Prediction: SAFE")
    else:
        st.error("SVM Prediction: UNSAFE")

    st.info("Reading and prediction saved to the database.")

# Display history
st.subheader("Storage Reading History")

with sqlite3.connect("cold_storage.db") as connection:
    history = pd.read_sql_query("""
        SELECT id, temperature_c, humidity_pct,
               door_status, predicted_status, timestamp
        FROM storage_readings
        ORDER BY id DESC
    """, connection)

if history.empty:
    st.info("No readings have been saved yet.")
else:
    st.dataframe(history, use_container_width=True, hide_index=True)

    st.download_button(
        "Download Reading History as CSV",
        data=history.to_csv(index=False).encode("utf-8"),
        file_name="cold_storage_history.csv",
        mime="text/csv"
    )
