import sqlite3
import os

db_path = "db/media.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    filepath TEXT,
    media_type TEXT,
    date_taken TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database schema initialized successfully.")
