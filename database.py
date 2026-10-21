
import sqlite3

DATABASE_NAME = "cold_storage.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS storage_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature_c REAL NOT NULL,
            humidity_pct REAL NOT NULL,
            door_status TEXT NOT NULL,
            predicted_status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

    print("Database and table created successfully!")


if __name__ == "__main__":
    create_database()
