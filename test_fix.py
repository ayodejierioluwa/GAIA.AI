import sys
import os
import time

# Add the current directory to sys.path so we can import gaia
sys.path.append(os.getcwd())

from gaia.database import DatabaseManager

def test():
    print("Initializing DatabaseManager...")
    db = DatabaseManager(db_path="well_analyses.db")
    
    print("Calling get_recent_knowledge(limit=1)...")
    start = time.time()
    results = db.get_recent_knowledge(limit=1)
    end = time.time()
    
    print(f"Query took {end - start:.4f} seconds.")
    if results:
        fact = results[0][3]
        print(f"Fact length: {len(fact)}")
        print(f"Fact content preview: {fact[:100]}...")
    else:
        print("No results found.")

if __name__ == "__main__":
    test()
