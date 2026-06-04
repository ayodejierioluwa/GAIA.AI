import os
import sys
import io
import sqlite3
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from gaia.app import create_app

def test_las_upload_integration():
    app = create_app()
    db_path = app.config['DATABASE']
    print(f"Active database: {db_path}")
    
    # 1. Clean up old test data if present
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM geological_data WHERE well_name = 'GAIA-APPRAISAL-01'")
    cursor.execute("DELETE FROM learning_logs WHERE description LIKE '%GAIA-APPRAISAL-01%'")
    conn.commit()
    conn.close()
    
    # 2. Build test client
    with app.test_client() as client:
        # Mock session login
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = "Operator"
            
        las_file_path = os.path.join(os.path.dirname(__file__), "sample_well.las")
        with open(las_file_path, "rb") as f:
            las_content = f.read()
            
        data = {
            'file': (io.BytesIO(las_content), 'sample_well.las')
        }
        
        print("Sending POST request to /upload with sample_well.las...")
        res = client.post('/upload', data=data, content_type='multipart/form-data')
        print("Upload response status code (Expected 302 redirect):", res.status_code)
        
        # 3. Assert database inserts
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query geological_data
        cursor.execute("SELECT well_name, latitude, longitude, depth, porosity, permeability, formation, oil_presence FROM geological_data WHERE well_name = 'GAIA-APPRAISAL-01'")
        geo_row = cursor.fetchone()
        print("\n--- Ingested LAS Geological Row in DB ---")
        if geo_row:
            print(f"Well: {geo_row[0]}")
            print(f"Location: [{geo_row[1]}, {geo_row[2]}]")
            print(f"Depth: {geo_row[3]}m")
            print(f"Porosity: {geo_row[4]} | Perm: {geo_row[5]} mD")
            print(f"Formation: {geo_row[6]}")
            print(f"Oil Presence: {geo_row[7]}")
            
            assert geo_row[0] == 'GAIA-APPRAISAL-01'
            assert abs(geo_row[1] - 5.4851) < 0.001
            assert abs(geo_row[2] - 6.8214) < 0.001
            assert geo_row[3] == 1520.0
            assert abs(geo_row[4] - 0.2453) < 0.001
            assert geo_row[6] == 'Agbada'
            assert geo_row[7] == 1 # SQLite stores boolean as 1 (True)
        else:
            print("FAILED: No well log record found in geological_data table for GAIA-APPRAISAL-01!")
            assert False, "Record not found in database"
            
        # Query learning_logs
        cursor.execute("SELECT event_type, description, accuracy_improvement, timestamp FROM learning_logs WHERE description LIKE '%GAIA-APPRAISAL-01%' ORDER BY timestamp DESC LIMIT 1")
        log_row = cursor.fetchone()
        print("\n--- Recent System Learning Log ---")
        if log_row:
            print(f"Event: {log_row[0]}")
            print(f"Desc: {log_row[1]}")
            print(f"Improvement: +{log_row[2]}%")
            print(f"Time: {log_row[3]}")
        else:
            print("FAILED: No training logs found in learning_logs table for GAIA-APPRAISAL-01!")
            assert False, "Training log not found"
            
        conn.close()
        print("\nEnd-to-End LAS Upload Integration Test: SUCCESS!")

if __name__ == "__main__":
    test_las_upload_integration()
