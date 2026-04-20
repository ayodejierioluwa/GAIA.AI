# Copyright (c) 2026. All Rights Reserved.
# Proprietary and confidential. Do not distribute.

"""
run_gaia.py
Your single entry point for GAIA AI.
Just run: python3 run_gaia.py
"""
import sys
import os
import threading
import asyncio
import time
from gaia.app import create_app
from gaia.utils.processing import MAX_WORKERS

# Initialize the application
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting GAIA AI — Nigerian Petroleum Intelligence Platform (Modular)...")
    
    # Apply CPU throttling
    precise_ml = app.config['precise_ml']
    try:
        precise_ml.supercomputer.num_cores = MAX_WORKERS
        print(f"⚡ Supercomputer throttled to {MAX_WORKERS} cores (Mac-safe)")
    except Exception:
        pass

    # Start Autonomous Growth Service (Background)
    def start_autonomous_service(flask_app):
        # Allow time for flask to start
        time.sleep(10)
        engine = flask_app.config['ingestion_engine']
        db = flask_app.config['ai_db']
        
        while True:
            try:
                # We use a context to run the async cycle
                asyncio.run(engine.run_autonomous_cycle())
                # Sleep for 6 hours before next automatic scan (or 10 mins for demo)
                time.sleep(3600 * 6) 
            except Exception as e:
                print(f"⚠️ Background Growth Error: {e}")
                time.sleep(60)

    print("🧠 Starting GAIA Autonomous Growth Service...")
    growth_thread = threading.Thread(target=start_autonomous_service, args=(app,), daemon=True)
    growth_thread.start()

    # Pre-train ML models
    ml_analyzer = app.config['ml_analyzer']
    try:
        train_result = ml_analyzer.train_models_with_real_data()
        if train_result.get('status') == 'success':
            print(f"✅ ML models ready — {train_result['training_samples']} training samples")
        else:
            print(f"⚠️  Training issues: {train_result.get('message', '')}")
    except Exception as e:
        print(f"⚠️  Error during ML init: {e} — using fallback demo mode")

    print(f"\n   GAIA AI is running at: http://127.0.0.1:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
