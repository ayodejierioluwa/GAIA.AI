import os
import sys
import json
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from gaia.app import create_app

def test_coordinate_api():
    app = create_app()
    db_path = app.config['DATABASE']
    print(f"Active database: {db_path}")
    
    with app.test_client() as client:
        # Mock session login
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = "Operator"
            
        data = {
            'latitude': 6.2,
            'longitude': 7.0,
            'depth': 1500.0,
            'basin': 'anambra'
        }
        
        print("Sending POST request to /api/exploration/predict-coordinate...")
        res = client.post('/api/exploration/predict-coordinate', 
                          data=json.dumps(data), 
                          content_type='application/json')
        
        print("Status Code:", res.status_code)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        res_data = json.loads(res.data.decode('utf-8'))
        print("\n--- API RESPONSE ---")
        print(f"Status: {res_data.get('status')}")
        print(f"Latitude: {res_data.get('latitude')}")
        print(f"Longitude: {res_data.get('longitude')}")
        print(f"Formation: {res_data.get('formation')}")
        
        # Check ML prediction fields
        ml = res_data.get('ml_prediction', {})
        print(f"ML Oil Prob: {ml.get('oil_presence_probability')}")
        print(f"ML Rec: {ml.get('recommendation')}")
        
        # Check Discovery prediction fields
        disc = res_data.get('discovery_prediction', {})
        print(f"Discovery Prob: {disc.get('probability')}")
        
        # Check Economics fields
        econ = res_data.get('economics', {})
        print(f"NPV (10%): ${econ.get('metrics', {}).get('npv'):,}")
        print(f"IRR: {econ.get('metrics', {}).get('irr')}%")
        
        # Check Diagnostic
        diag = res_data.get('diagnostic')
        print(f"Diagnostic: {diag}")
        
        # Check Synthesis
        synthesis = res_data.get('synthesis')
        print(f"Synthesis snippet: {synthesis[:120]}...")
        
        assert res_data['status'] == 'success'
        assert res_data['formation'] == 'Mamu'
        assert 'ml_prediction' in res_data
        assert 'discovery_prediction' in res_data
        assert 'economics' in res_data
        assert 'diagnostic' in res_data
        assert 'synthesis' in res_data
        
        print("\nCoordinate Prediction API Verification: SUCCESS!")

if __name__ == '__main__':
    test_coordinate_api()
