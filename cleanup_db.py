import sqlite3
import time

db_path = "/Users/macbook/.gemini/antigravity/scratch/petroleum-ai/well_analyses.db"

def cleanup():
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path, timeout=60)
    cursor = conn.cursor()
    
    print("Finding IDs of massive rows...")
    # We only care about really big ones for now to unblock the app
    cursor.execute("SELECT id FROM knowledge_base WHERE length(fact_description) > 5000")
    ids = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(ids)} massive rows.")
    
    count = 0
    for row_id in ids:
        print(f"Truncating row {row_id}...")
        cursor.execute("UPDATE knowledge_base SET fact_description = substr(fact_description, 1, 5000) || ' [TRUNCATED]' WHERE id = ?", (row_id,))
        conn.commit()
        count += 1
        if count % 10 == 0:
            print(f"Processed {count}/{len(ids)}...")
            
    print("Cleanup complete.")
    conn.close()

if __name__ == "__main__":
    cleanup()
