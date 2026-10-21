
import joblib
import os

model_file = "cold_storage_svm_model.pkl"
scaler_file = "cold_storage_scaler.pkl"
features_file = "cold_storage_feature_columns.pkl"

for file in [model_file, scaler_file, features_file]:
    if not os.path.exists(file):
        raise FileNotFoundError(f"Missing file: {file}")

model = joblib.load(model_file)
scaler = joblib.load(scaler_file)
feature_columns = joblib.load(features_file)

print("Model loaded successfully!")
print("Scaler loaded successfully!")
print("Feature columns loaded successfully!")
print("Expected input features:", feature_columns)
