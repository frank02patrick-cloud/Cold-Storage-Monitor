
import sqlite3

connection = sqlite3.connect("cold_storage.db")

# Insert one test reading
connection.execute("""
    INSERT INTO storage_readings
    (temperature_c, humidity_pct, door_status, predicted_status)
    VALUES (?, ?, ?, ?)
""", (5.0, 60.0, "CLOSED", "Unsafe"))

connection.commit()

# Retrieve saved readings
cursor = connection.execute("""
    SELECT id, temperature_c, humidity_pct,
           door_status, predicted_status, timestamp
    FROM storage_readings
""")

for row in cursor.fetchall():
    print(row)

connection.close()
