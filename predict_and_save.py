
import sqlite3
import joblib
import pandas as pd

# Load the trained model and preprocessing files
model = joblib.load("cold_storage_svm_model.pkl")
scaler = joblib.load("cold_storage_scaler.pkl")
feature_columns = joblib.load("cold_storage_feature_columns.pkl")


def predict_and_save(temperature_c, humidity_pct, door_status):
    # Convert door status into a number
    door_status = door_status.strip().upper()

    if door_status == "CLOSED":
        door_encoded = 1
    elif door_status == "OPEN":
        door_encoded = 0
    else:
        raise ValueError("Door status must be OPEN or CLOSED.")

    # Arrange inputs in the model's expected feature order
    input_data = pd.DataFrame([{
        "temperature_c": temperature_c,
        "humidity_pct": humidity_pct,
        "door_encoded": door_encoded
    }])[feature_columns]

    # Apply the saved scaler
    scaled_data = scaler.transform(input_data)

    # Predict using the trained SVM
    prediction = int(model.predict(scaled_data)[0])

    predicted_status = "Safe" if prediction == 1 else "Unsafe"

    # Save the reading and prediction in SQLite
    with sqlite3.connect("cold_storage.db") as connection:
        connection.execute("""
            INSERT INTO storage_readings
            (temperature_c, humidity_pct, door_status, predicted_status)
            VALUES (?, ?, ?, ?)
        """, (
            temperature_c,
            humidity_pct,
            door_status,
            predicted_status
        ))

    print(f"Temperature: {temperature_c} °C")
    print(f"Humidity: {humidity_pct}%")
    print(f"Door: {door_status}")
    print(f"SVM prediction: {predicted_status}")
    print("Reading saved to database.")


if __name__ == "__main__":
    predict_and_save(
        temperature_c=5.0,
        humidity_pct=60.0,
        door_status="CLOSED"
    )
