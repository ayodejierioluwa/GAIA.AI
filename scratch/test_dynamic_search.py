import os
import sys
import json
import sqlite3

# Align python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gaia.models.agent import GAIAAgent
from gaia.database import DatabaseManager

def test_dynamic_search():
    db_path = "well_analyses_v3.db"
    db = DatabaseManager(db_path)
    
    agent = GAIAAgent(db_manager=db)
    
    # 1. Capture counts before search
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    kb_count_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM learning_logs")
    log_count_before = cursor.fetchone()[0]
    
    print(f"Before search: KB count = {kb_count_before}, Logs count = {log_count_before}")
    
    # 2. Run the tool
    query = "Anambra Basin coal measures"
    result_str = agent.search_and_ingest_web_geology(query)
    result = json.loads(result_str)
    
    print("Tool Output:")
    print(json.dumps(result, indent=2))
    
    # 3. Assert outputs
    assert result['status'] == 'success', f"Expected success status, got {result['status']}"
    assert 'query' in result
    assert result['facts_ingested'] > 0, "Expected at least 1 fact to be ingested via live search or local fallback archive"
    
    # 4. Assert database persistence
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    kb_count_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM learning_logs")
    log_count_after = cursor.fetchone()[0]
    
    print(f"After search: KB count = {kb_count_after}, Logs count = {log_count_after}")
    
    assert kb_count_after > kb_count_before, "Knowledge base count should have increased"
    assert log_count_after > log_count_before, "Learning logs count should have increased"
    
    # Check that Anambra or Mamu facts are in the KB
    cursor.execute("SELECT entity_name, fact_description FROM knowledge_base WHERE entity_name LIKE '%Anambra%' OR entity_name LIKE '%Mamu%' ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    print("\nRecent Ingested Facts:")
    for r in rows:
        print(f"  Entity: {r[0]} | Fact: {r[1][:100]}...")
        
    conn.close()
    print("\nDynamic Web Search and Ingestion: SUCCESS!")

if __name__ == '__main__':
    test_dynamic_search()
