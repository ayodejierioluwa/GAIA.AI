import sqlite3
from werkzeug.security import generate_password_hash
import os

db_path = "well_analyses_v3.db"
password_hash = generate_password_hash("password123", method='pbkdf2:sha256')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)", 
                   ("admin", "admin@gaia.ai", password_hash, "2026-04-24"))
    conn.commit()
    print("User 'admin' created with password 'password123'")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
