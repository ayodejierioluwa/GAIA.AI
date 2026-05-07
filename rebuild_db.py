import sqlite3
import os
import time

old_db = "/Users/macbook/.gemini/antigravity/scratch/petroleum-ai/well_analyses.db"
new_db = "/Users/macbook/.gemini/antigravity/scratch/petroleum-ai/well_analyses_new.db"

def rebuild():
    if os.path.exists(new_db):
        os.remove(new_db)
        
    print(f"Connecting to old database: {old_db}...")
    conn_old = sqlite3.connect(old_db)
    cursor_old = conn_old.cursor()
    
    print(f"Creating new database: {new_db}...")
    conn_new = sqlite3.connect(new_db)
    cursor_new = conn_new.cursor()
    
    # Create tables
    print("Creating tables in new database...")
    cursor_new.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT
    )''')
    cursor_new.execute('''CREATE TABLE analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        well_name TEXT,
        flow_rate REAL,
        initial_pressure REAL,
        final_pressure REAL,
        productivity_index REAL,
        skin_factor REAL,
        analysis_date TEXT,
        report_text TEXT,
        depth REAL DEFAULT 0,
        api_gravity REAL DEFAULT 32.0,
        gor REAL DEFAULT 500,
        water_cut REAL DEFAULT 0,
        temperature REAL DEFAULT 180,
        diagnostic_insight TEXT
    )''')
    cursor_new.execute('''CREATE TABLE geological_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        well_name TEXT,
        latitude REAL,
        longitude REAL,
        depth REAL,
        formation TEXT,
        porosity REAL,
        permeability REAL,
        oil_presence BOOLEAN,
        source TEXT,
        last_updated TEXT
    )''')
    cursor_new.execute('''CREATE TABLE knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_name TEXT,
        entity_type TEXT,
        fact_description TEXT,
        source_url TEXT,
        confidence_score REAL,
        date_extracted TEXT
    )''')
    cursor_new.execute('''CREATE TABLE learning_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        description TEXT,
        accuracy_improvement REAL,
        timestamp TEXT
    )''')
    
    # Copy data
    tables = ['users', 'analyses', 'geological_data', 'learning_logs']
    for table in tables:
        print(f"Copying table: {table}...")
        cursor_old.execute(f"SELECT * FROM {table}")
        rows = cursor_old.fetchall()
        if rows:
            placeholders = ', '.join(['?'] * len(rows[0]))
            cursor_new.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
            conn_new.commit()
            
    # Copy and Truncate knowledge_base
    print("Copying and Truncating knowledge_base (this involves reading the massive file)...")
    cursor_old.execute("SELECT * FROM knowledge_base")
    count = 0
    while True:
        row = cursor_old.fetchone()
        if not row:
            break
            
        # row: (id, entity_name, entity_type, fact_description, source_url, confidence_score, date_extracted)
        # index 3 is fact_description
        desc = row[3]
        if desc and len(desc) > 5000:
            desc = desc[:5000] + " [TRUNCATED]"
            
        new_row = list(row)
        new_row[3] = desc
        
        cursor_new.execute("INSERT INTO knowledge_base VALUES (?, ?, ?, ?, ?, ?, ?)", new_row)
        count += 1
        if count % 100 == 0:
            print(f"Processed {count} nodes...")
            conn_new.commit()
            
    conn_new.commit()
    
    # Create indices
    print("Creating indices...")
    cursor_new.execute('CREATE INDEX idx_entity_name ON knowledge_base(entity_name)')
    cursor_new.execute('CREATE INDEX idx_entity_type ON knowledge_base(entity_type)')
    cursor_new.execute('CREATE INDEX idx_date_extracted ON knowledge_base(date_extracted)')
    
    conn_old.close()
    conn_new.close()
    print("Rebuild complete.")

if __name__ == "__main__":
    rebuild()
