import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path="well_analyses.db"):
        self.db_path = db_path
        self.use_sqlalchemy = False
        self.engine = None
        
        if db_path.startswith(("postgresql://", "mysql://", "sqlite:///")):
            self.use_sqlalchemy = True
            if HAS_SQLALCHEMY:
                self.engine = create_engine(db_path)
            else:
                if db_path.startswith("sqlite:///"):
                    self.db_path = db_path.replace("sqlite:///", "")
                else:
                    self.db_path = "well_analyses_v3.db"
                self.use_sqlalchemy = False
        
        self.init_database()

    def _get_connection(self):
        if self.use_sqlalchemy and self.engine:
            return self.engine.connect()
        return sqlite3.connect(self.db_path, timeout=30)

    def init_database(self):
        try:
            if self.use_sqlalchemy:
                self._init_sqlalchemy_db()
            else:
                self._init_sqlite_db()
        except Exception as e:
            if "malformed" in str(e) and not self.use_sqlalchemy:
                if os.path.exists(self.db_path):
                    os.rename(self.db_path, f"{self.db_path}.corrupted_{int(datetime.now().timestamp())}")
                self._init_sqlite_db()

    def _init_sqlite_db(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, well_name TEXT, flow_rate REAL, initial_pressure REAL, final_pressure REAL, productivity_index REAL, skin_factor REAL, analysis_date TEXT, report_text TEXT, depth REAL DEFAULT 0, api_gravity REAL DEFAULT 32.0, gor REAL DEFAULT 500, water_cut REAL DEFAULT 0, temperature REAL DEFAULT 180, diagnostic_insight TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS geological_data (id INTEGER PRIMARY KEY AUTOINCREMENT, well_name TEXT, latitude REAL, longitude REAL, depth REAL, formation TEXT, porosity REAL, permeability REAL, oil_presence BOOLEAN, source TEXT, last_updated TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge_base (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_name TEXT, entity_type TEXT, fact_description TEXT, source_url TEXT, confidence_score REAL, date_extracted TEXT)''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entity_name ON knowledge_base(entity_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entity_type ON knowledge_base(entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_extracted ON knowledge_base(date_extracted)')
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT, description TEXT, accuracy_improvement REAL, timestamp TEXT)''')
        conn.commit()
        conn.close()

    def _init_sqlalchemy_db(self):
        # Full schema for Cloud SQL
        with self.engine.begin() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(255) UNIQUE, email VARCHAR(255) UNIQUE, password_hash TEXT, created_at TEXT)"))
            conn.execute(text("CREATE TABLE IF NOT EXISTS analyses (id SERIAL PRIMARY KEY, user_id INTEGER, well_name TEXT, flow_rate REAL, initial_pressure REAL, final_pressure REAL, productivity_index REAL, skin_factor REAL, analysis_date TEXT, report_text TEXT, depth REAL, api_gravity REAL, gor REAL, water_cut REAL, temperature REAL, diagnostic_insight TEXT)"))
            conn.execute(text("CREATE TABLE IF NOT EXISTS knowledge_base (id SERIAL PRIMARY KEY, entity_name TEXT, entity_type TEXT, fact_description TEXT, source_url TEXT, confidence_score REAL, date_extracted TEXT)"))
            conn.execute(text("CREATE TABLE IF NOT EXISTS learning_logs (id SERIAL PRIMARY KEY, event_type TEXT, description TEXT, accuracy_improvement REAL, timestamp TEXT)"))

    def create_user(self, username, email, password):
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            if self.use_sqlalchemy:
                with self.engine.begin() as conn:
                    result = conn.execute(text("INSERT INTO users (username, email, password_hash, created_at) VALUES (:u, :e, :p, :c) RETURNING id"), {"u": username, "e": email, "p": password_hash, "c": datetime.now().strftime("%Y-%m-%d")})
                    return result.fetchone()[0]
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)", (username, email, password_hash, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                uid = cursor.lastrowid
                conn.close()
                return uid
        except Exception: return None

    def verify_user(self, username, password):
        try:
            if self.use_sqlalchemy:
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT id, password_hash FROM users WHERE username = :u"), {"u": username}).fetchone()
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
                result = cursor.fetchone()
                conn.close()
            if result:
                user_id, pwd_hash = result
                if check_password_hash(pwd_hash, password): return user_id
        except Exception: pass
        return None

    def save_analysis(self, user_id, well_data, report_text="", pi=0, skin_factor=0, diagnostic=""):
        params = {"uid": user_id, "wn": well_data.get('well_name', 'Unknown'), "fr": well_data.get('flow_rate', 0), "ip": well_data.get('initial_pressure', 0), "fp": well_data.get('final_pressure', 0), "pi": pi, "sf": skin_factor, "ad": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "rt": report_text, "dp": well_data.get('depth', 0), "api": well_data.get('api_gravity', 32.0), "gor": well_data.get('gor', 500), "wc": well_data.get('water_cut', 0), "temp": well_data.get('temperature', 180), "di": diagnostic}
        try:
            if self.use_sqlalchemy:
                with self.engine.begin() as conn:
                    conn.execute(text("INSERT INTO analyses (user_id, well_name, flow_rate, initial_pressure, final_pressure, productivity_index, skin_factor, analysis_date, report_text, depth, api_gravity, gor, water_cut, temperature, diagnostic_insight) VALUES (:uid, :wn, :fr, :ip, :fp, :pi, :sf, :ad, :rt, :dp, :api, :gor, :wc, :temp, :di)"), params)
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO analyses (user_id, well_name, flow_rate, initial_pressure, final_pressure, productivity_index, skin_factor, analysis_date, report_text, depth, api_gravity, gor, water_cut, temperature, diagnostic_insight) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(params.values()))
                conn.commit()
                conn.close()
        except Exception: pass

    def get_user_analyses(self, user_id):
        try:
            if self.use_sqlalchemy:
                with self.engine.connect() as conn:
                    return conn.execute(text("SELECT * FROM analyses WHERE user_id = :u ORDER BY analysis_date DESC"), {"u": user_id}).fetchall()
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM analyses WHERE user_id = ? ORDER BY analysis_date DESC', (user_id,))
                res = cursor.fetchall()
                conn.close()
                return res
        except Exception: return []

    def get_analysis_by_id(self, analysis_id, user_id):
        try:
            if self.use_sqlalchemy:
                with self.engine.connect() as conn:
                    return conn.execute(text("SELECT * FROM analyses WHERE id = :aid AND user_id = :uid"), {"aid": analysis_id, "uid": user_id}).fetchone()
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM analyses WHERE id = ? AND user_id = ?', (analysis_id, user_id))
                res = cursor.fetchone()
                conn.close()
                return res
        except Exception: return None

    def save_geological_data(self, data):
        params = {"wn": data.get('well_name'), "lat": data.get('latitude'), "lon": data.get('longitude'), "dp": data.get('depth'), "fm": data.get('formation'), "po": data.get('porosity'), "pe": data.get('permeability'), "op": data.get('oil_presence'), "src": data.get('source'), "upd": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        try:
            if self.use_sqlalchemy:
                with self.engine.begin() as conn:
                    conn.execute(text("INSERT INTO geological_data (well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence, source, last_updated) VALUES (:wn, :lat, :lon, :dp, :fm, :po, :pe, :op, :src, :upd)"), params)
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO geological_data (well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence, source, last_updated) VALUES (?,?,?,?,?,?,?,?,?,?)", tuple(params.values()))
                conn.commit()
                conn.close()
        except Exception: pass

    def add_knowledge_fact(self, entity_name, entity_type, fact, source_url, confidence=0.8):
        try:
            if self.use_sqlalchemy:
                with self.engine.begin() as conn:
                    conn.execute(text("INSERT INTO knowledge_base (entity_name, entity_type, fact_description, source_url, confidence_score, date_extracted) VALUES (:n, :t, :f, :u, :c, :d)"), {"n": entity_name, "t": entity_type, "f": fact, "u": source_url, "c": confidence, "d": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM knowledge_base WHERE entity_name = ? AND fact_description = ? LIMIT 1", (entity_name, fact))
                if cursor.fetchone(): 
                    conn.close()
                    return
                cursor.execute("INSERT INTO knowledge_base (entity_name, entity_type, fact_description, source_url, confidence_score, date_extracted) VALUES (?, ?, ?, ?, ?, ?)", (entity_name, entity_type, fact, source_url, confidence, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
        except Exception: pass

    def log_learning_event(self, event_type, description, improvement=0.0):
        try:
            if self.use_sqlalchemy:
                with self.engine.begin() as conn:
                    conn.execute(text("INSERT INTO learning_logs (event_type, description, accuracy_improvement, timestamp) VALUES (:t, :d, :i, :ts)"), {"t": event_type, "d": description, "i": improvement, "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO learning_logs (event_type, description, accuracy_improvement, timestamp) VALUES (?, ?, ?, ?)", (event_type, description, improvement, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
        except Exception: pass

    def get_knowledge_count(self):
        try:
            if self.use_sqlalchemy:
                with self.engine.connect() as conn:
                    return conn.execute(text("SELECT COUNT(*) FROM knowledge_base")).scalar() or 0
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM knowledge_base')
                count = cursor.fetchone()[0]
                conn.close()
                return count
        except Exception: return 0

    def get_recent_knowledge(self, limit=10):
        query = "SELECT id, entity_name, entity_type, CASE WHEN length(fact_description) > 2000 THEN substr(fact_description, 1, 2000) || ' [TRUNCATED]' ELSE fact_description END, source_url, confidence_score, date_extracted FROM knowledge_base ORDER BY date_extracted DESC LIMIT :l"
        try:
            if self.use_sqlalchemy:
                with self.engine.connect() as conn:
                    return conn.execute(text(query), {"l": limit}).fetchall()
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(query.replace(':l', '?'), (limit,))
                res = cursor.fetchall()
                conn.close()
                return res
        except Exception: return []

    def get_learning_history(self, limit=20):
        try:
            if self.use_sqlalchemy:
                with self.engine.connect() as conn:
                    return conn.execute(text("SELECT * FROM learning_logs ORDER BY timestamp DESC LIMIT :l"), {"l": limit}).fetchall()
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM learning_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
                res = cursor.fetchall()
                conn.close()
                return res
        except Exception: return []

    def query_knowledge_by_tag(self, tag, limit=3):
        search = f"%{tag}%"
        query = "SELECT entity_name, entity_type, fact_description, confidence_score FROM knowledge_base WHERE entity_name LIKE :s OR entity_type LIKE :s OR fact_description LIKE :s ORDER BY confidence_score DESC LIMIT :l"
        try:
            if self.use_sqlalchemy:
                with self.engine.connect() as conn:
                    return conn.execute(text(query), {"s": search, "l": limit}).fetchall()
            else:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(query.replace(':l', '?').replace(':s', '?'), (search, search, search, limit))
                res = cursor.fetchall()
                conn.close()
                return res
        except Exception: return []
