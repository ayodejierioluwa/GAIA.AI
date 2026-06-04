import sys
import os

# DEEP PATCH: Protobuf compatibility for Python 3.14
sys.modules['google._upb'] = None
sys.modules['google.protobuf.pyext'] = None

import json
import logging
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class MockGenerativeModel:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate_content(self, prompt):
        class MockResponse:
            def __init__(self, text):
                self.text = text
        
        # Extract the user query section specifically to avoid context leaks
        query_text = prompt.lower()
        if "[user query]" in query_text:
            query_text = query_text.split("[user query]")[-1]
            
        # Analyze query keywords to produce customized mock parameters
        well_name = "DHB-01"
        if "om" in query_text or "130" in query_text:
            well_name = "OML-130 Appraisal"
        elif "benue" in query_text:
            well_name = "GB-04 (Benue Trough)"
        elif "anambra" in query_text:
            well_name = "FB-08 (Anambra)"
            
        prob = 84.2
        confidence = 0.91
        npv = 42.5
        irr = 24.5
        status = "GO"
        
        if "benue" in query_text:
            prob = 62.5
            confidence = 0.81
            npv = 12.8
            irr = 16.2
            status = "RE-AUDIT"
        elif "anambra" in query_text:
            prob = 48.0
            confidence = 0.78
            npv = -2.4
            irr = 8.5
            status = "NO-GO"
            
        text = f"### 📡 GAIA Sovereign Intelligence [DEMO MODE]\n\n"
        text += "Geological & Geospatial inference simulated successfully. To enable live neural reasoning, please configure `GEMINI_API_KEY` in your environment variables.\n\n"
        
        text += f"### 1. **VERDICT SUMMARY**: [{status}]\n"
        if status == "GO":
            text += f"- **Recommendation**: Proceed with appraisal drilling. Rollover anticline trap integrity is high.\n"
            text += f"- **Key Justification**: Confirmed structural closure with sandstone reservoir facies matching proven Niger Delta play analogues.\n"
        elif status == "RE-AUDIT":
            text += f"- **Recommendation**: Suspend immediate drilling; execute high-resolution 3D seismic reprocessing.\n"
            text += f"- **Key Justification**: Fault seals are questionable, risking reservoir leakage despite reasonable ML charge indicators.\n"
        else:
            text += f"- **Recommendation**: Do not lease or drill target area.\n"
            text += f"- **Key Justification**: Thin structural reservoir pay thickness combined with excessive cap rock fracturing yields negative NPV risk.\n"
            
        text += "\n### 2. **GEOLOGICAL AUDIT**\n"
        text += "| Formation | Top Depth (m) | Thickness (m) | Lithology | Porosity (avg) |\n"
        text += "| :--- | :--- | :--- | :--- | :--- |\n"
        if "benue" in query_text:
            text += "| Awgu Shale | 0 | 1200 | Marine Shale / Seal | 0.08 |\n"
            text += "| Eze-Aku | 1200 | 1800 | Tight Sandstone | 0.14 |\n"
            text += "| Asu River | 3000 | 1500 | Dense Siltstone | 0.11 |\n"
        elif "anambra" in query_text:
            text += "| Nsukka | 0 | 800 | Sandy Mudstone | 0.16 |\n"
            text += "| Mamu | 800 | 1200 | Coal Measures | 0.12 |\n"
            text += "| Ajali | 2000 | 1500 | Unconsolidated Sands | 0.22 |\n"
        else:
            text += "| Benin | 0 | 1500 | Continental Sands | 0.30 |\n"
            text += "| Agbada | 1500 | 2500 | Interbedded Sand/Shale | 0.24 |\n"
            text += "| Akata | 4000 | 2000 | Overpressured Shale | 0.15 |\n"
            
        text += f"\n### 3. **PREDICTIVE MACHINE LEARNING**\n"
        text += f"- **Oil Presence Probability**: `{prob}%` (Averaged Ensemble: Random Forest & Gradient Boosting)\n"
        text += f"- **Estimation Confidence**: `{confidence}` (Based on historical spatial data density and model validation parameters)\n"
        text += f"- **Model Output Recommendation**: "
        if prob >= 80:
            text += "EXCELLENT - Highly recommended for exploration and target testing.\n"
        elif prob >= 60:
            text += "GOOD - Promising target with moderate risk profile.\n"
        else:
            text += "POOR - High risk target, seek alternative locations.\n"
            
        text += f"\n### 4. **FINANCIAL FEASIBILITY**\n"
        text += f"- **CAPEX / OPEX**: $18.5M (Est. Drilling & Completion) / $3.2M (Annual Operating Logistics)\n"
        text += f"- **Net Present Value (NPV)**: `${npv}M` (Calculated at 10% discount rate, $75/bbl Brent)\n"
        text += f"- **Internal Rate of Return (IRR)**: `{irr}%` | Payback Period: `{3.2 if status=='GO' else 5.8} Years`\n"
        
        text += f"\n### 5. **ENGINEERING TASK MANDATES**\n"
        if "benue" in query_text:
            text += f"- Implement mud weight monitoring program (11.5 - 12.2 ppg) to manage fractured shale sloughing.\n"
            text += f"- Plan mud motor directional assembly for rifting dip angles.\n"
        elif "anambra" in query_text:
            text += f"- Design heavy core capture for coal-bed methane extraction options.\n"
            text += f"- Deploy high-pressure sand screening for Ajali sandstone intervals.\n"
        else:
            text += f"- Deploy sand control screens (sandstone core filtration) for the Agbada sands.\n"
            text += f"- Maintain casing weight thresholds during transition into overpressured Akata seals.\n"
            
        return MockResponse(text)

class GAIAAgent:
    """
    GAIA Sovereign Intelligence v2: Neural Reasoning Core.
    Powered by Gemini 1.5/3.5 models.
    Supports native tool calling / function calling to interface with:
    - NigeriaOilMLAnalyzer (Machine Learning potential predictions)
    - SubsurfaceGeologicalAnalyzer (Dynamic stratigraphy & seismic profiles)
    - EconomicFeasibilityEngine (NPV / IRR evaluations)
    - SatelliteSpectralEngine (MODIS/Sentinel-2 remote sensing seeps detection)
    - DatabaseManager (Historical knowledge database lookups)
    """
    
    def __init__(self, db_manager=None, model_name="models/gemini-flash-latest",
                 ml_analyzer=None, geological_analyzer=None, economics_engine=None, satellite_engine=None):
        self.db = db_manager
        self.ml_analyzer = ml_analyzer
        self.geological_analyzer = geological_analyzer
        self.economics_engine = economics_engine
        self.satellite_engine = satellite_engine
        self.history = []
        self.chats = {}
        
        # System Persona Definitions
        self.PERSONAS = {
            "SENTINEL": """
            You are 'Geospatial Sentinel' (Dr. Geofinder), a Structural Geology and Remote Sensing Specialist.
            Your focus: Stratigraphic trap integrity, lithology, spectral heterogeneity, and seismic proxy analysis.
            Tone: Academic, Detail-Oriented, Cautious.
            """,
            "PROPHET": """
            You are 'Economic Prophet' (The Capitalist Oracle), a Senior Petroleum Economist.
            Your focus: NPV, IRR, fiscal regimes (PSC/JV), market volatility, and infrastructure cost-benefit.
            Tone: Strategic, Profit-Focused, Pragmatic.
            """,
            "ARBITER": """
            You are GAIA Core (The Strategic Arbiter). 
            Your role is to synthesize the findings of the 'Sentinel' and the 'Prophet' into a single, high-fidelity Executive Summary.
            Highlight contradictions and provide a final 'Go/No-Go' recommendation.
            """
        }
        
        self.persona = self.PERSONAS["ARBITER"]

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment. Initializing in DEMO/MOCK mode.")
            self.model = MockGenerativeModel(model_name)
            self.live = False
        else:
            genai.configure(api_key=api_key)
            self.live = True
            
            # Define structural callable tools to link Gemini to our Python engines
            self.tools = [
                self.predict_well_prospectivity,
                self.get_subsurface_seismic,
                self.calculate_well_economics,
                self.scan_satellite_seeps,
                self.query_historical_geological_knowledge,
                self.query_well_geological_measurements,
                self.list_workspace_geological_files,
                self.read_geological_dataset_file,
                self.trigger_ai_model_retraining
            ]
            self.model = genai.GenerativeModel(model_name, tools=self.tools)

    # --- AGENT TOOLS / PLUGINS ---

    def predict_well_prospectivity(self, latitude: float, longitude: float, depth: float = 3000.0, porosity: float = 0.20, permeability: float = 100.0) -> str:
        """
        Runs machine learning models (Random Forest and Gradient Boosting) to estimate the oil prospectivity potential, confidence level, and recommendation at specific coordinates.
        Use this tool when the user queries prospectivity, oil presence probability, reservoir quality parameters, or needs recommendations on drilling specific coordinate points.
        """
        if not self.ml_analyzer:
            return "Error: Machine Learning Analyzer is offline."
        try:
            res = self.ml_analyzer.predict_oil_potential(latitude, longitude, depth, porosity, permeability)
            return json.dumps(res)
        except Exception as e:
            return f"Error executing ML analysis: {e}"

    def get_subsurface_seismic(self, latitude: float, longitude: float, depth_min: float = 0.0, depth_max: float = 5000.0) -> str:
        """
        Retrieves dynamic geological stratigraphy (layers, formations, rock types) and simulates a seismic wave velocity reflection profile at specific coordinates.
        Use this tool when the query asks about geological formations, stratigraphic layers (e.g. Agbada, Akata, Mamu), seismic velocities, velocity models, traps, or hydrocarbon anomalies.
        """
        if not self.geological_analyzer:
            return "Error: Geological Analyzer is offline."
        try:
            res = self.geological_analyzer.process_seismic_data(latitude, longitude, (depth_min, depth_max))
            return json.dumps(res)
        except Exception as e:
            return f"Error executing seismic/stratigraphy retrieval: {e}"

    def calculate_well_economics(self, initial_rate: float, depth: float, formation: str, env_type: str) -> str:
        """
        Runs Net Present Value (NPV), Internal Rate of Return (IRR), payback period, and break-even calculations for a target well.
        Use this tool when the user asks for well economics, profitability, NPV, IRR, CAPEX, OPEX, or financial feasibility of a well.
        """
        if not self.economics_engine:
            return "Error: Economics Engine is offline."
        try:
            res = self.economics_engine.assess_well_feasibility(initial_rate, depth, formation, env_type)
            return json.dumps(res)
        except Exception as e:
            return f"Error executing economic simulation: {e}"

    def scan_satellite_seeps(self, latitude: float, longitude: float, mode: str = "SAR") -> str:
        """
        Triggers a spectral remote sensing scan (Sentinel-2/MODIS proxy) to detect oil seeps or vegetation stress at coordinates.
        Modes: 'TRUE_COLOR', 'NDVI' (vegetation stress), 'THERMAL_IR' (heat anomalies), 'SAR' (subsurface structural indicators).
        Use this tool when the user asks for satellite, remote sensing, seeps, NDVI, or thermal anomalies.
        """
        if not self.satellite_engine:
            return "Error: Satellite Spectral Engine is offline."
        try:
            res = self.satellite_engine.analyze_spectral_profile(latitude, longitude, mode=mode, live=True)
            return json.dumps(res)
        except Exception as e:
            return f"Error executing remote sensing scan: {e}"

    def query_historical_geological_knowledge(self, tag: str) -> str:
        """
        Queries the database for historical well reports and geological knowledge tags.
        Use this tool when the user asks about specific wells, historical audits, or previous exploration reports.
        """
        if not self.db:
            return "Error: Database Manager is offline."
        try:
            res = self.db.query_knowledge_by_tag(tag, limit=5)
            facts = [f"- [{f[1]}] {f[0]}: {f[2]} (Confidence: {f[3]})" for f in res]
            return "\n".join(facts) if facts else "No historical records found for this tag."
        except Exception as e:
            return f"Error querying database: {e}"

    def query_well_geological_measurements(self, well_name: str = None, formation: str = None) -> str:
        """
        Queries the database for raw well measurements and parameters such as porosity, permeability, depth, and oil presence.
        Parameters:
        - well_name: Optional name of the well (e.g. 'DHB-01', 'OML-130').
        - formation: Optional geological formation name (e.g. 'Agbada', 'Akata', 'Benin').
        Use this tool when the query asks for actual rock measurements, coordinates, porosity, permeability, or well depths.
        """
        if not self.db:
            return "Error: Database Manager is offline."
        try:
            conn = self.db._get_connection()
            if hasattr(conn, 'cursor'):
                cursor = conn.cursor()
                if well_name and formation:
                    cursor.execute("SELECT well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence FROM geological_data WHERE well_name LIKE ? AND formation LIKE ?", (f"%{well_name}%", f"%{formation}%"))
                elif well_name:
                    cursor.execute("SELECT well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence FROM geological_data WHERE well_name LIKE ?", (f"%{well_name}%",))
                elif formation:
                    cursor.execute("SELECT well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence FROM geological_data WHERE formation LIKE ?", (f"%{formation}%",))
                else:
                    cursor.execute("SELECT well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence FROM geological_data ORDER BY last_updated DESC LIMIT 10")
                res = cursor.fetchall()
                conn.close()
            else:
                from sqlalchemy import text
                if well_name and formation:
                    res = conn.execute(text("SELECT well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence FROM geological_data WHERE well_name LIKE :w AND formation LIKE :f"), {"w": f"%{well_name}%", "f": f"%{formation}%"}).fetchall()
                elif well_name:
                    res = conn.execute(text("SELECT well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence FROM geological_data WHERE well_name LIKE :w"), {"w": f"%{well_name}%"}).fetchall()
                elif formation:
                    res = conn.execute(text("SELECT well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence FROM geological_data WHERE formation LIKE :f"), {"f": f"%{formation}%"}).fetchall()
                else:
                    res = conn.execute(text("SELECT well_name, latitude, longitude, depth, formation, porosity, permeability, oil_presence FROM geological_data ORDER BY last_updated DESC LIMIT 10")).fetchall()
                conn.close()
                
            if not res:
                return "No raw geological measurements found matching the criteria."
                
            lines = []
            for r in res:
                oil = "Yes" if r[7] else "No"
                lines.append(f"- Well: {r[0]} | Location: [{r[1]}, {r[2]}] | Depth: {r[3]}m | Formation: {r[4]} | Porosity: {r[5]:.2f} | Permeability: {r[6]}mD | Oil Presence: {oil}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error querying geological measurements: {e}"

    def list_workspace_geological_files(self) -> str:
        """
        Lists all geological datasets (CSV files and databases) present in the active workspace and uploads folders.
        Use this tool when the user asks about available data files, datasets, what files are in the directory, or where files are stored.
        """
        import os
        workspace_dir = "/Users/macbook/.gemini/antigravity-ide/scratch"
        uploads_dir = os.path.join(workspace_dir, "petroleum-ai", "uploads")
        
        files = []
        if os.path.exists(workspace_dir):
            for f in os.listdir(workspace_dir):
                if f.endswith(('.csv', '.db', '.las', '.txt')) and os.path.isfile(os.path.join(workspace_dir, f)):
                    size = os.path.getsize(os.path.join(workspace_dir, f)) / 1024
                    files.append(f"- [Workspace] {f} ({size:.1f} KB)")
                    
        if os.path.exists(uploads_dir):
            for f in os.listdir(uploads_dir):
                if f.endswith(('.csv', '.db', '.las', '.txt')) and os.path.isfile(os.path.join(uploads_dir, f)):
                    size = os.path.getsize(os.path.join(uploads_dir, f)) / 1024
                    files.append(f"- [Uploads] {f} ({size:.1f} KB)")
                    
        if not files:
            return "No geological datasets or database files were found in the workspace."
            
        return "Available geological datasets in workspace:\n" + "\n".join(files)

    def read_geological_dataset_file(self, filename: str, num_rows: int = 5) -> str:
        """
        Reads a specific geological dataset (CSV or text file) from the workspace, returning column headers, shape, statistical summary, and first N rows.
        Parameters:
        - filename: The name of the file (e.g., 'drilling_processed.csv' or 'washouts_and_vibrations.csv').
        - num_rows: The number of preview rows to return (default is 5).
        Use this tool when the user queries data from a specific file, asks to inspect a dataset, or needs statistics about a workspace table.
        """
        import os
        workspace_dir = "/Users/macbook/.gemini/antigravity-ide/scratch"
        path1 = os.path.join(workspace_dir, filename)
        path2 = os.path.join(workspace_dir, "petroleum-ai", "uploads", filename)
        
        file_path = None
        if os.path.exists(path1):
            file_path = path1
        elif os.path.exists(path2):
            file_path = path2
            
        if not file_path:
            return f"Error: Dataset '{filename}' not found in the workspace or uploads directory."
            
        try:
            if filename.endswith('.db'):
                import sqlite3
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                return f"SQLite Database File: {filename}\nTables present: {', '.join([t[0] for t in tables])}"
                
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                total_rows = len(df)
                columns = list(df.columns)
                summary = df.describe().to_string()
                preview = df.head(num_rows).to_string()
                
                return (
                    f"### DATASET PROFILE: {filename}\n"
                    f"- **Total Scanned Rows**: {total_rows}\n"
                    f"- **Columns**: {', '.join(columns)}\n\n"
                    f"**Descriptive Statistics Summary**:\n{summary}\n\n"
                    f"**First {num_rows} Preview Rows**:\n{preview}"
                )
            except ImportError:
                import csv
                with open(file_path, 'r') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    rows = []
                    for _ in range(num_rows):
                        try:
                            rows.append(next(reader))
                        except StopIteration:
                            break
                return f"Dataset Profile: {filename} (No pandas fallback)\nColumns: {header}\nRows:\n" + "\n".join([str(r) for r in rows])
        except Exception as e:
            return f"Error reading dataset file: {e}"

    def trigger_ai_model_retraining(self) -> str:
        """
        Manually triggers the scikit-learn ML training sequence from the active geological database measurements.
        Use this tool when the user explicitly requests to retrain the models, update model weights, or learn from the latest well uploads.
        """
        if not self.ml_analyzer:
            return "Error: Machine Learning Analyzer is offline."
        try:
            res = self.ml_analyzer.train_models_with_real_data()
            if res.get('status') == 'success':
                return f"Success: Models retrained successfully. Ingested {res['training_samples']} samples. Metrics: R2 Score = {res['metrics']['random_forest']['r2']:.4f}"
            return f"Failure: Retraining encountered errors: {res.get('message')}"
        except Exception as e:
            return f"Error executing retraining: {e}"

    # --- CORE REASONING METHODS ---

    def _retrieve_context(self, query):
        """Perform RAG: Retrieve relevant geological facts and recent logs."""
        context = ""
        if self.db:
            keywords = query.split()
            facts = []
            for kw in keywords[:3]:
                facts.extend(self.db.query_knowledge_by_tag(kw, limit=5))
            
            if facts:
                context += "### RELEVANT GEOLOGICAL FACTS:\n"
                for fact in facts:
                    context += f"- [{fact[1]}] {fact[0]}: {fact[2]} (Confidence: {fact[3]})\n"
            
            logs = self.db.get_learning_history(limit=3)
            if logs:
                context += "\n### RECENT SYSTEM LOGS:\n"
                for log in logs:
                    context += f"- {log[4]}: {log[1]} - {log[2]}\n"
                    
        return context

    def collaborate(self, user_query, geological_context=None):
        """Invoke Multi-Agent Debate and Synthesis."""
        if not self.live:
            db_context = self._retrieve_context(user_query)
            session_context = json.dumps(geological_context, indent=2) if geological_context else "None"
            
            sentinel_prompt = f"{self.PERSONAS['SENTINEL']}\n[CONTEXT]\n{db_context}\n{session_context}\n[TASK] Analyze the geological risk of: {user_query}"
            sentinel_resp = self.model.generate_content(sentinel_prompt).text
            
            prophet_prompt = f"{self.PERSONAS['PROPHET']}\n[CONTEXT]\n{db_context}\n{session_context}\n[TASK] Analyze the financial feasibility of: {user_query}"
            prophet_resp = self.model.generate_content(prophet_prompt).text
            
            arbiter_prompt = f"""
            {self.PERSONAS['ARBITER']}
            [DEBATE LOG]
            SENTINEL: {sentinel_resp}
            PROPHET: {prophet_resp}
            [TASK] Provide a final synthesized recommendation for the query: {user_query}
            Format as a professional Executive Brief.
            """
            final_resp = self.model.generate_content(arbiter_prompt).text
            
            return {
                "sentinel": sentinel_resp,
                "prophet": prophet_resp,
                "synthesis": final_resp
            }
        
        try:
            # Live multi-agent debate runs
            sentinel_prompt = f"{self.PERSONAS['SENTINEL']}\n[TASK] Analyze the structural geology / geospatial profiles for: {user_query}"
            sentinel_resp = self.model.generate_content(sentinel_prompt).text

            prophet_prompt = f"{self.PERSONAS['PROPHET']}\n[TASK] Analyze the economics and capex feasibility for: {user_query}"
            prophet_resp = self.model.generate_content(prophet_prompt).text

            arbiter_prompt = f"""
            {self.PERSONAS['ARBITER']}
            
            [DEBATE INPUTS]
            GEOSPATIAL SENTINEL: {sentinel_resp}
            ECONOMIC PROPHET: {prophet_resp}
            
            [TASK] Synthesize these positions and issue the final executive brief recommendation for: {user_query}
            """
            final_resp = self.model.generate_content(arbiter_prompt).text

            return {
                "sentinel": sentinel_resp,
                "prophet": prophet_resp,
                "synthesis": final_resp
            }
        except Exception as e:
            logger.error(f"Gemini API Debate Error: {e}")
            return {
                "sentinel": "Error running live Sentinel",
                "prophet": "Error running live Prophet",
                "synthesis": f"Collaborative synthesis failed: {e}"
            }

    def generate_response(self, user_query, geological_context=None, mode="normal", session_id=1):
        """High-Fidelity Technical Inference Pipeline with Tool Invocation."""
        if not self.live:
            # Fallback to mock model
            db_context = self._retrieve_context(user_query)
            full_context = f"{db_context}\n\n### ADDITIONAL SESSION CONTEXT:\n{json.dumps(geological_context, indent=2) if geological_context else 'None'}"
            prompt = f"{self.persona}\n\n[CONTEXT]\n{full_context}\n\n[USER QUERY]\n{user_query}\n\n[GAIA RESPONSE]"
            response = self.model.generate_content(prompt)
            return response.text
            
        if mode == "collaborative":
            collab_data = self.collaborate(user_query, geological_context)
            return collab_data["synthesis"]
            
        # RAG context pre-retrieval
        db_context = self._retrieve_context(user_query)
        full_context = f"{db_context}\n\n### ACTIVE GEOLOGICAL CONTEXT:\n{json.dumps(geological_context, indent=2) if geological_context else 'None'}"
        
        system_instruction = """
        You are GAIA Core (The Strategic Arbiter), the primary artificial intelligence module for XXII Group.
        You have direct access to structural, machine learning, database, and financial modeling tools.
        Use these tools when queries ask for geological layering, seismic profiles, well measurements, NPV/IRR evaluations, satellite seeps, or ML predictions.
        
        Mandatory Output Structure:
        Always format your responses as a clean, comprehensive Technical Briefing using markdown tables, bullet points, and equations:
        1. **VERDICT SUMMARY**: Highlight the prospect status (e.g., [GO / NO-GO / RE-AUDIT]) with bulleted key justifications.
        2. **GEOLOGICAL AUDIT**: Include a markdown table of stratigraphic layers (Formations, depths, thicknesses, lithology).
        3. **PREDICTIVE MACHINE LEARNING**: State the oil presence probability (%), confidence, and model-based recommendations.
        4. **FINANCIAL FEASIBILITY**: Break down CAPEX/OPEX, NPV, IRR, and payback period.
        5. **ENGINEERING TASK MANDATES**: List specific, highly accurate operational mitigation steps (e.g., sand control screens for Agbada sands, fault seals, or seismic reprocessing).
        
        Ensure all information is easily comprehensible to stakeholders, mathematically consistent, and technically correct.
        """
        
        prompt = f"{system_instruction}\n\n[CONTEXT]\n{full_context}\n\n[USER QUERY]\n{user_query}\n\n[GAIA RESPONSE]"
        
        try:
            if session_id not in self.chats:
                self.chats[session_id] = self.model.start_chat(enable_automatic_function_calling=True)
            chat = self.chats[session_id]
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return f"### [SYSTEM ERROR] GAIA Neural Core Offline\nReason: {str(e)}\n\n*Falling back to legacy reasoning matrix...*"

    def analyze_basin_anomaly(self, basin_name, satellite_data):
        """Specialized tool for autonomous basin scouting."""
        if not self.live:
            prompt = f"{self.persona}\n\nTASK: Perform a Strategic Basin Audit for {basin_name}.\nDATA: {json.dumps(satellite_data, indent=2)}"
            response = self.model.generate_content(prompt)
            return response.text
            
        prompt = f"""
        {self.persona}
        
        TASK: Perform a Strategic Basin Audit for {basin_name}.
        DATA: {json.dumps(satellite_data, indent=2)}
        
        Use your tools as necessary to run simulations for this basin.
        Analyze the following:
        1. Structural Trap Integrity based on the anomalies.
        2. Surface Seepage Proxy (Spectral heterogeneous variance).
        3. Primary Target Recommendation.
        4. Risk Assessment (Geological & Financial).
        """
        try:
            chat = self.model.start_chat(enable_automatic_function_calling=True)
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Analysis failed: {e}"
