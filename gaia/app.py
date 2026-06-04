"""
gaia/app.py
Flask application factory for GAIA AI.
"""
import os
from flask import Flask
from .database import DatabaseManager

# Import blueprints
from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.analysis import analysis_bp
from .routes.exploration import exploration_bp
from .routes.intelligence import intelligence_bp
from .routes.api import api_bp

# Import models
from .models.ml import EnhancedNigeriaOilMLAnalyzer, AdvancedPreciseModel, ReservoirDiscoveryModel, NigeriaOilExplorer
from .models.geological import SubsurfaceGeologicalAnalyzer
from .models.economics import EconomicFeasibilityEngine
from .models.data_intelligence import AutonomousDataScraper, AutomatedDataAcquisition
from .models.chatbot import PetroleumChatbot
from .models.agent import GAIAAgent
from .models.tools import GeologicalAuditor, EconomicForecaster, NewsEngine
from .models.ingestion_engine import IngestionEngine
from .models.satellite import SatelliteSpectralEngine

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # DATABASE & STORAGE CONFIGURATION
    # Priority: Environment Variable (Cloud Migration) > Volume Mount (/data) > Default Local File
    db_url = os.environ.get('DATABASE_URL')
    volume_dir = "/data"
    
    # Check if persistent volume is mounted at /data (standard Railway volume mount)
    if os.path.exists(volume_dir) and os.path.isdir(volume_dir):
        upload_dir = os.path.join(volume_dir, 'uploads')
        if not db_url:
            db_url = os.path.join(volume_dir, 'well_analyses_v3.db')
            logger_msg = f"Using Volume SQLite: {db_url}"
        else:
            logger_msg = f"Using Configured DB with Volume Uploads: {db_url.split('@')[-1] if '@' in db_url else db_url}"
    else:
        upload_dir = os.path.join(app.root_path, '..', 'uploads')
        if not db_url:
            db_url = os.path.join(app.root_path, '..', 'well_analyses_v3.db')
            logger_msg = f"Using Local SQLite: {db_url}"
        else:
            logger_msg = f"Connecting to Cloud Database: {db_url.split('@')[-1] if '@' in db_url else db_url}"
            
    app.config.from_mapping(
        SECRET_KEY='petroleum-secret-key',
        DATABASE=db_url,
        UPLOAD_FOLDER=upload_dir,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,
    )
    print(f"📡 GAIA {logger_msg}")

    if test_config:
        app.config.from_mapping(test_config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize components
    ai_db = DatabaseManager(app.config['DATABASE'])
    ml_analyzer = EnhancedNigeriaOilMLAnalyzer()
    precise_ml = AdvancedPreciseModel()
    geological_analyzer = SubsurfaceGeologicalAnalyzer()
    economics_engine = EconomicFeasibilityEngine()
    data_scraper = AutonomousDataScraper()
    data_acquisition = AutomatedDataAcquisition()
    geological_auditor = GeologicalAuditor(output_dir=app.config['UPLOAD_FOLDER'])
    economic_forecaster = EconomicForecaster()
    satellite_engine = SatelliteSpectralEngine()
    discovery_model = ReservoirDiscoveryModel(db=ai_db, sat_engine=satellite_engine)
    news_engine = NewsEngine()

    explorer = NigeriaOilExplorer()
    chatbot = PetroleumChatbot(
        ml_analyzer=ml_analyzer,
        explorer=explorer,
        subsurface_analyzer=geological_analyzer,
        db=ai_db
    )
    gaia_agent = GAIAAgent(
        db_manager=ai_db,
        ml_analyzer=ml_analyzer,
        geological_analyzer=geological_analyzer,
        economics_engine=economics_engine,
        satellite_engine=satellite_engine
    )
    ingestion_engine = IngestionEngine(db_manager=ai_db, gaia_agent=gaia_agent)

    # Store in config for blueprints to access
    app.config['ai_db'] = ai_db
    app.config['ml_analyzer'] = ml_analyzer
    app.config['precise_ml'] = precise_ml
    app.config['advanced_analyzer'] = geological_analyzer
    app.config['economics_engine'] = economics_engine
    app.config['data_scraper'] = data_scraper
    app.config['data_acquisition'] = data_acquisition
    app.config['chatbot'] = chatbot
    app.config['gaia_agent'] = gaia_agent
    app.config['geological_auditor'] = geological_auditor
    app.config['economic_forecaster'] = economic_forecaster
    app.config['ingestion_engine'] = ingestion_engine
    app.config['satellite_engine'] = satellite_engine
    app.config['discovery_model'] = discovery_model
    app.config['news_engine'] = news_engine

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(exploration_bp)
    app.register_blueprint(intelligence_bp)
    app.register_blueprint(api_bp)

    @app.before_request
    def handle_preflight():
        from flask import request, make_response
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
            return response

    @app.after_request
    def add_header(response):
        response.headers['Content-Security-Policy'] = "frame-ancestors *"
        if 'X-Frame-Options' in response.headers:
            del response.headers['X-Frame-Options']
        
        # Manual CORS compliance for cross-origin orchestrator requests
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'

        # Rewrite redirect location headers for single-domain compatibility
        location = response.headers.get('Location')
        if location and location.startswith('/') and not location.startswith('/apps/gaia/'):
            response.headers['Location'] = '/apps/gaia' + location

        # Rewrite HTML and JS response bodies to include the /apps/gaia prefix on absolute paths
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type or 'application/javascript' in content_type:
            try:
                data = response.get_data(as_text=True)
                # Absolute static, navigation, and API endpoints replacements
                replacements = [
                    ('href="/', 'href="/apps/gaia/'),
                    ('src="/', 'src="/apps/gaia/'),
                    ('action="/', 'action="/apps/gaia/'),
                    ("window.location.href = '/", "window.location.href = '/apps/gaia/"),
                    ('window.location.href = "/', 'window.location.href = "/apps/gaia/'),
                    ("window.location.href='/", "window.location.href='/apps/gaia/"),
                    ('window.location.href="/', 'window.location.href="/apps/gaia/'),
                    ("location.href = '/", "location.href = '/apps/gaia/"),
                    ('location.href = "/', 'location.href = "/apps/gaia/'),
                    ("location.href='/", "location.href='/apps/gaia/"),
                    ('location.href="/', 'location.href="/apps/gaia/'),
                    ("location.href = `/", "location.href = `/apps/gaia/"),
                    ("location.href=`/", "location.href=`/apps/gaia/"),
                    ("fetch('/", "fetch('/apps/gaia/"),
                    ('fetch("/', 'fetch("/apps/gaia/'),
                    ("url: '/", "url: '/apps/gaia/"),
                    ('url: "/', 'url: "/apps/gaia/'),
                    ('"/api/', '"/apps/gaia/api/'),
                    ("'/api/", "'/apps/gaia/api/"),
                ]
                for old, new in replacements:
                    data = data.replace(old, new)
                response.set_data(data)
            except Exception as e:
                print(f"Error rewriting HTML response paths: {e}")

        return response

    # START AUTONOMOUS PULSE (1 Hour Interval)
    def start_pulse():
        import time
        import asyncio
        from datetime import datetime, timedelta
        
        while True:
            # Update telemetry with next sync time
            next_sync = datetime.now() + timedelta(hours=1)
            ingestion_engine.telemetry["next_sync"] = next_sync.isoformat()
            
            # Wait for interval
            time.sleep(3600)
            
            # Trigger growth
            if not ingestion_engine.is_running:
                 # Create a new loop for the thread if needed
                 try:
                     loop = asyncio.new_event_loop()
                     asyncio.set_event_loop(loop)
                     loop.run_until_complete(ingestion_engine.run_autonomous_cycle())
                     loop.close()
                 except Exception as e:
                     print(f"Background Sync Error: {e}")

    import threading
    pulse_thread = threading.Thread(target=start_pulse, daemon=True)
    pulse_thread.start()

    return app
