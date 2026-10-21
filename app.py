import sqlite3
import joblib
import pandas as pd
import streamlit as st

# 1. Application Configuration
st.set_page_config(
    page_title="Cold-Storage Monitor",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for Modern, Stylish UI
st.markdown("""
<style>
    /* Global Styling Adjustments */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Card Container Styling */
    div[data-testid="stVerticalBlock"] > div.css-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }

    /* Headings */
    h1, h2, h3 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    
    /* Custom Primary Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        border-radius: 10px;
        padding: 12px 28px;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(2, 132, 199, 0.39);
        width: 100%;
    }
    
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        box-shadow: 0 6px 20px 0 rgba(56, 189, 248, 0.5);
        transform: translateY(-2px);
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 3. Model & Cache Loading
@st.cache_resource
def load_model_files():
    model = joblib.load("cold_storage_svm_model.pkl")
    scaler = joblib.load("cold_storage_scaler.pkl")
    features = joblib.load("cold_storage_feature_columns.pkl")
    return model, scaler, features

try:
    model, scaler, feature_columns = load_model_files()
except Exception as e:
    st.sidebar.error("⚠️ Model files not found. Ensure .pkl files exist in the directory.")

# 4. Sidebar Content
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/snowflake.png", width=64)
    st.title("Control Panel")
    st.markdown("Monitor real-time cold-storage climate parameters powered by **Support Vector Machine (SVM)** classifier models.")
    st.divider()
    st.caption("⚙️ **System Status**: Active")
    st.caption("💾 **Database**: SQLite3 Connected")

# 5. Dashboard Header
st.title("❄️ Cold-Storage Monitoring Dashboard")
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Real-time AI surveillance for optimal environmental conditions.</p>", unsafe_allow_html=True)
st.divider()

# 6. Main Dashboard Layout: Left Input Panel, Right Live Metrics/Status
col_inputs, col_status = st.columns([1.2, 1], gap="large")

with col_inputs:
    st.markdown("### 🎛️ Live Sensor Parameters")
    
    with st.container():
        sub_col1, sub_col2 = st.columns(2)
        
        with sub_col1:
            temperature = st.number_input(
                "Temperature (°C)",
                min_value=-10.0,
                max_value=30.0,
                value=5.0,
                step=0.1,
                help="Optimal Range: 2.0°C to 8.0°C"
            )
            
        with sub_col2:
            humidity = st.number_input(
                "Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=85.0,
                step=0.5,
                help="Optimal Range: 80.0% to 95.0%"
            )

        door_status = st.selectbox(
            "Door Position",
            ["CLOSED", "OPEN"],
            help="Door must remain closed to ensure storage safety."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("⚡ Evaluate & Log Reading", type="primary")

with col_status:
    st.markdown("### 📊 Active Metrics Preview")
    
    # Real-time quick metric badges
    m1, m2, m3 = st.columns(3)
    
    # Dynamic styling for metrics display
    temp_delta = "Optimal" if 2.0 <= temperature <= 8.0 else "Out of bounds"
    hum_delta = "Optimal" if 80.0 <= humidity <= 95.0 else "Out of bounds"
    door_delta = "Secure" if door_status == "CLOSED" else "Alert!"
    
    m1.metric("Temp", f"{temperature} °C", delta=temp_delta, delta_color="normal" if temp_delta == "Optimal" else "inverse")
    m2.metric("Humidity", f"{humidity} %", delta=hum_delta, delta_color="normal" if hum_delta == "Optimal" else "inverse")
    m3.metric("Door", door_status, delta=door_delta, delta_color="normal" if door_delta == "Secure" else "inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # Prediction Logic Execution
    if predict_btn:
        door_encoded = 1 if door_status == "CLOSED" else 0

        input_data = pd.DataFrame([{
            "temperature_c": temperature,
            "humidity_pct": humidity,
            "door_encoded": door_encoded
        }])[feature_columns]

        # Scaler transformation & Model inference
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

        # Save to Database
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

        # Result Display Banner
        if predicted_status == "Safe":
            st.success("🟢 **SVM Evaluation: SAFE**\n\nConditions are within specified safe parameters.")
        else:
            st.error("🔴 **SVM Evaluation: UNSAFE**\n\nEnvironmental thresholds violated or door open!")

        st.toast("Reading logged to SQLite database successfully!", icon="✅")

st.divider()

# 7. Database History Section
st.markdown("### 📜 Storage Log History")

with sqlite3.connect("cold_storage.db") as connection:
    history = pd.read_sql_query("""
        SELECT id, temperature_c, humidity_pct,
               door_status, predicted_status, timestamp
        FROM storage_readings
        ORDER BY id DESC
    """, connection)

if history.empty:
    st.info("No storage records found in database. Use the input panel above to log data.")
else:
    # Column styling configuration for Streamlit dataframe
    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "temperature_c": st.column_config.NumberColumn("Temp (°C)", format="%.1f °C"),
            "humidity_pct": st.column_config.NumberColumn("Humidity (%)", format="%.1f %%"),
            "door_status": st.column_config.TextColumn("Door Status"),
            "predicted_status": st.column_config.TextColumn("SVM Prediction"),
            "timestamp": st.column_config.DatetimeColumn("Logged Timestamp", format="YYYY-MM-DD HH:mm:ss")
        }
    )

    col_dl1, col_dl2 = st.columns([1, 4])
    with col_dl1:
        st.download_button(
            "📥 Export Logs as CSV",
            data=history.to_csv(index=False).encode("utf-8"),
            file_name="cold_storage_history.csv",
            mime="text/csv",
            use_container_width=True
        )
