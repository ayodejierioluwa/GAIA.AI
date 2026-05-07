import os
import json
from datetime import datetime
from fpdf import FPDF

class GeologicalAuditor:
    """
    Autonomous Tool: Generates high-fidelity petroleum technical reports.
    Synthesizes ML results, geological context, and neural reasoning.
    """
    
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf_report(self, well_name, basin, ml_results, neural_assessment, collab_data=None):
        """Creates a professional PDF audit of a prospect."""
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(0, 100, 100)
        pdf.cell(0, 20, "GAIA STRATEGIC AUDIT", ln=True, align="C")
        
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | GAIA v2 Neural Core", ln=True, align="C")
        pdf.ln(10)
        
        # Well Details
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Prospect: {well_name}", ln=True)
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Basin: {basin}", ln=True)
        pdf.ln(5)
        
        # 1. Collaborative Domain Debate (If available)
        if collab_data:
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(0, 100, 200)
            pdf.cell(0, 10, "1. COLLABORATIVE DOMAIN DEBATE", ln=True)
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(0, 150, 100)
            pdf.cell(0, 8, "[GEOSPATIAL SENTINEL]", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, collab_data.get('sentinel', 'No data.'))
            pdf.ln(4)
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(200, 100, 0)
            pdf.cell(0, 8, "[ECONOMIC PROPHET]", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, collab_data.get('prophet', 'No data.'))
            pdf.ln(8)
            
            # Synthesis
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, "2. STRATEGIC ARBITER SYNTHESIS", ln=True)
            pdf.set_font("Helvetica", "I", 10)
            pdf.multi_cell(0, 7, collab_data.get('synthesis', neural_assessment))
            pdf.ln(10)
        else:
            # Fallback to single assessment
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "1. NEURAL STRATEGIC ASSESSMENT", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 8, neural_assessment)
            pdf.ln(10)

        # ML Metrics
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "3. PROBABILISTIC ML METRICS" if collab_data else "2. PROBABILISTIC ML METRICS", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for key, val in ml_results.items():
            if isinstance(val, dict): continue
            pdf.cell(0, 8, f"- {key.replace('_', ' ').title()}: {val}", ln=True)
        pdf.ln(10)
        
        # Footer
        pdf.set_y(-30)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 10, "CONFIDENTIAL - PROPERTY OF GAIA SOVEREIGN INTELLIGENCE", align="C")
        
        filename = f"GAIA_AUDIT_{well_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        print(f"--- GEOLOGICAL AUDIT REPORT GENERATED: {filepath} ---")
        return filepath

    def generate_executive_briefing(self, analysis_data, recommendation):
        """
        Generates a high-level briefing for executive stakeholders using FPDF.
        """
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="GAIA STRATEGIC EXECUTIVE BRIEFING", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(10)
        
        # Verdict
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="STRATEGIC VERDICT:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, txt=recommendation)
        pdf.ln(5)
        
        # Metrics
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="KEY ASSET METRICS:", ln=True)
        pdf.set_font("Arial", size=10)
        for key, val in analysis_data.items():
            pdf.cell(200, 8, txt=f"- {key.upper()}: {val}", ln=True)
            
        filename = f"EXECUTIVE_BRIEF_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        return filepath

class EconomicForecaster:
    """
    Autonomous Tool: Runs NPV/IRR sensitivity analysis based on market proxies.
    """
    def __init__(self, oil_price_proxy=75.0):
        self.oil_price = oil_price_proxy

    def run_npv_sensitivity(self, reserves_p50, depth, capex_multiplier=1.0):
        """Simulate economic viability."""
        # Simple heuristic: $40M base capex + depth escalation
        base_capex = 40 * (1 + (depth / 5000)**2) * capex_multiplier
        revenue = reserves_p50 * self.oil_price * 0.4 # Assuming 40% net take after tax/opex
        npv = revenue - base_capex
        irr = (revenue / base_capex) * 100 if base_capex > 0 else 0
        
        return {
            "estimated_npv_mm": round(npv, 2),
            "estimated_irr_percent": round(irr, 2),
            "break_even_price": round(base_capex / (reserves_p50 * 0.4), 2) if reserves_p50 > 0 else 999
        }

class NewsEngine:
    """
    OSINT Tool: Simulates real-time energy market and regulatory intelligence.
    """
    def __init__(self):
        self.categories = ["REGULATORY", "MARKET", "SECURITY", "TECHNICAL"]

    def get_latest_headlines(self, limit=5):
        headlines = [
            {"category": "REGULATORY", "title": "NUPRC issues new Deepwater Lease guidelines.", "impact": "HIGH"},
            {"category": "MARKET", "title": "Bonny Light crude holds at $82.40/bbl amid supply shifts.", "impact": "MEDIUM"},
            {"category": "SECURITY", "title": "Neural Pulse detects vessel anomaly in OML 130.", "impact": "CRITICAL"},
            {"category": "TECHNICAL", "title": "New seismic interpretation suggests deeper reservoir in Anambra Basin.", "impact": "HIGH"},
            {"category": "REGULATORY", "title": "PIA 2021 fiscal terms update expected in Q3.", "impact": "LOW"},
            {"category": "MARKET", "title": "Regional gas pipeline expansion project reaches 70% completion.", "impact": "MEDIUM"}
        ]
        import random
        return random.sample(headlines, min(limit, len(headlines)))
