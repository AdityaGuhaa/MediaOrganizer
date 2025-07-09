import sqlite3
import os

# Use absolute path
db_path = "C:/Media Organizer/db/media.db"

# Make sure the folder exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Create or connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add missing columns safely
try:
    cursor.execute("ALTER TABLE media ADD COLUMN duration REAL")
    print("✅ 'duration' column added.")
except sqlite3.OperationalError:
    print("⚠️ 'duration' column already exists.")

try:
    cursor.execute("ALTER TABLE media ADD COLUMN resolution TEXT")
    print("✅ 'resolution' column added.")
except sqlite3.OperationalError:
    print("⚠️ 'resolution' column already exists.")

conn.commit()
conn.close()
