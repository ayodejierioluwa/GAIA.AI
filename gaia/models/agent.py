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

class GAIAAgent:
    """
    GAIA Sovereign Intelligence v2: Neural Reasoning Core.
    Powered by Gemini 1.5 Pro/Flash.
    Handles high-level technical inference, RAG-enhanced geological analysis,
    and autonomous decision-making.
    """
    
    def __init__(self, db_manager=None, model_name="models/gemini-flash-latest"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment.")
            raise ValueError("GEMINI_API_KEY is required for GAIA v2.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.db = db_manager
        self.history = []
        
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

    def _retrieve_context(self, query):
        """Perform RAG: Retrieve relevant geological facts and recent logs."""
        context = ""
        if self.db:
            # 1. Search Knowledge Base by Keywords
            keywords = query.split()
            facts = []
            for kw in keywords[:3]: # Limit to first 3 keywords for broad search
                facts.extend(self.db.query_knowledge_by_tag(kw, limit=5))
            
            if facts:
                context += "### RELEVANT GEOLOGICAL FACTS:\n"
                for fact in facts:
                    context += f"- [{fact[1]}] {fact[0]}: {fact[2]} (Confidence: {fact[3]})\n"
            
            # 2. Get Recent Learning Logs
            logs = self.db.get_learning_history(limit=3)
            if logs:
                context += "\n### RECENT SYSTEM LOGS:\n"
                for log in logs:
                    context += f"- {log[4]}: {log[1]} - {log[2]}\n"
                    
        return context

    def collaborate(self, user_query, geological_context=None):
        """Invoke Multi-Agent Debate and Synthesis."""
        db_context = self._retrieve_context(user_query)
        session_context = json.dumps(geological_context, indent=2) if geological_context else "None"
        
        # 1. Specialist: Geospatial Sentinel
        sentinel_prompt = f"{self.PERSONAS['SENTINEL']}\n[CONTEXT]\n{db_context}\n{session_context}\n[TASK] Analyze the geological risk of: {user_query}"
        sentinel_resp = self.model.generate_content(sentinel_prompt).text
        
        # 2. Specialist: Economic Prophet
        prophet_prompt = f"{self.PERSONAS['PROPHET']}\n[CONTEXT]\n{db_context}\n{session_context}\n[TASK] Analyze the financial feasibility of: {user_query}"
        prophet_resp = self.model.generate_content(prophet_prompt).text
        
        # 3. Arbiter: Synthesis
        arbiter_prompt = f"""
        {self.PERSONAS['ARBITER']}
        
        [DEBATE LOG]
        SENTINEL: {sentinel_resp}
        
        PROPHET: {prophet_resp}
        
        [TASK]
        Provide a final synthesized recommendation for the query: {user_query}
        Format as a professional Executive Brief.
        """
        final_resp = self.model.generate_content(arbiter_prompt).text
        
        return {
            "sentinel": sentinel_resp,
            "prophet": prophet_resp,
            "synthesis": final_resp
        }

    def generate_response(self, user_query, geological_context=None, mode="normal"):
        """High-Fidelity Technical Inference Pipeline."""
        if mode == "collaborative":
            collab_data = self.collaborate(user_query, geological_context)
            return collab_data["synthesis"]
            
        # 1. RAG: Get context from DB
        db_context = self._retrieve_context(user_query)
        
        # 2. Combine with session context
        full_context = f"{db_context}\n\n### ADDITIONAL SESSION CONTEXT:\n{json.dumps(geological_context, indent=2) if geological_context else 'None'}"
        
        # 3. Construct Prompt
        prompt = f"{self.persona}\n\n[CONTEXT]\n{full_context}\n\n[USER QUERY]\n{user_query}\n\n[GAIA RESPONSE]"
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return f"### [SYSTEM ERROR] GAIA Neural Core Offline\nReason: {str(e)}\n\n*Falling back to legacy reasoning matrix...*"

    def analyze_basin_anomaly(self, basin_name, satellite_data):
        """Specialized tool for autonomous basin scouting."""
        prompt = f"""
        {self.persona}
        
        TASK: Perform a Strategic Basin Audit for {basin_name}.
        DATA: {json.dumps(satellite_data, indent=2)}
        
        Analyze the following:
        1. Structural Trap Integrity based on the anomalies.
        2. Surface Seepage Proxy (Spectral heterogeneous variance).
        3. Primary Target Recommendation.
        4. Risk Assessment (Geological & Financial).
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Analysis failed: {e}"
