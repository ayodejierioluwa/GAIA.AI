import numpy as np
from datetime import datetime

class EconomicFeasibilityEngine:
    """
    Evaluates the commercial viability of petroleum assets.
    Incorporates Arps Decline Curves, Net Present Value (NPV), and ROI metrics.
    """
    def __init__(self, target_roi=0.15, current_oil_price=80.0):
        self.target_roi = target_roi
        self.oil_price = current_oil_price
        
    def arps_decline_curve(self, initial_rate, decline_rate, b_factor, time_months):
        """
        Calculate production over time using the Arps decline equation.
        Models Exponential (b=0), Harmonic (b=1), and Hyperbolic (0<b<1) decline curves.
        Returns a list of monthly production rates (bbl/day).
        """
        production = []
        for t in range(time_months):
            if b_factor == 0:  # Exponential
                rate = initial_rate * np.exp(-decline_rate * t)
            elif b_factor == 1:  # Harmonic
                rate = initial_rate / (1 + decline_rate * t)
            else:  # Hyperbolic
                rate = initial_rate / ((1 + b_factor * decline_rate * t) ** (1 / b_factor))
            production.append(max(0, rate))
        return production
        
    def calculate_npv(self, cash_flows, discount_rate=0.10):
        """Calculate the Net Present Value of a series of cash flows."""
        npv = 0
        for t, cf in enumerate(cash_flows):
            npv += cf / ((1 + discount_rate) ** t)
        return npv

    def detailed_cost_audit(self, depth, formation="Agbada", env_type="Onshore"):
        """
        Calculate a granular CAPEX/OPEX breakdown based on depth and lithology.
        Provides rationales for specific materials and operations.
        """
        # Base Costs per tier
        daily_rate = 45000 if env_type == "Onshore" else 250000 
        drilling_days = max(15, int(depth / 150))
        
        # 1. Drilling CAPEX Breakdown
        rig_cost = daily_rate * drilling_days
        
        # Formation Multipliers (Heuristics)
        # Pressure/Hardness factor
        formation_mult = 1.0
        rationales = []
        materials = []
        
        f_lower = formation.lower()
        if "akata" in f_lower or "fika" in f_lower:
            formation_mult = 1.4
            materials.append({"item": "15K psi BOP Stack", "cost": 1200000, "reason": f"High-pressure regime predicted in {formation}."})
            materials.append({"item": "Synthetic Based Mud (SBM)", "cost": 450000, "reason": "Required for shale stability and hydration prevention."})
            rationales.append(f"{formation} requires high-density mud weights to prevent kick/collapse.")
        elif "agbada" in f_lower or "gombe" in f_lower or "bima" in f_lower:
            formation_mult = 1.1
            materials.append({"item": "Sand Control Screens", "cost": 350000, "reason": "Unconsolidated sands require multi-stage sand exclusion."})
            rationales.append(f"{formation} sands prioritize completion integrity due to sand production risks.")
        elif "pindiga" in f_lower or "gongila" in f_lower:
            formation_mult = 1.25
            materials.append({"item": "PDC Drill Bits", "cost": 180000, "reason": "Calcareous/Limestone content requires high-durability bits."})
            rationales.append(f"Calcareous sequences in {formation} increase bit wear and drilling torque.")
        else:
            materials.append({"item": "Standard 5K BOP", "cost": 400000, "reason": "Standard pressure regime."})
            rationales.append("Normal formation pressure expected; standard drilling parameters applied.")

        # Casing cost (function of depth)
        casing_cost = depth * 450 * formation_mult
        completion_cost = 500000 + (depth * 100)
        
        # 2. Logistics & Operational OPEX
        logistics = rig_cost * 0.15
        personnel = drilling_days * 12000
        
        capex_total = rig_cost + casing_cost + completion_cost + sum(m['cost'] for m in materials)
        opex_per_month = personnel / 12 + (depth * 2) # simplified 
        
        return {
            'breakdown': {
                'rig_operations': round(rig_cost, 2),
                'casing_tubulars': round(casing_cost, 2),
                'completion_fluids': round(completion_cost, 2),
                'specialized_materials': materials,
                'logistics_support': round(logistics, 2)
            },
            'rationales': rationales,
            'capex_total': round(capex_total, 2),
            'opex_monthly': round(opex_per_month, 2),
            'environment': env_type,
            'formation_complexity': formation_mult
        }

    def assess_well_feasibility(self, initial_rate, depth=3000, formation="Agbada", env_type="Onshore", project_life_months=60):
        """
        Hyper-precise feasibility assessment using Formation-Aware logic.
        """
        audit = self.detailed_cost_audit(depth, formation, env_type)
        capex = audit['capex_total']
        opex_per_month = audit['opex_monthly']
        
        # Base logic for production
        decline_rate = 0.08 if "akata" not in formation.lower() else 0.12
        b_factor = 0.5
        
        # Generate production profile
        production_profile = self.arps_decline_curve(initial_rate, decline_rate, b_factor, project_life_months)
        
        # Calculate monthly revenue
        monthly_revenue = [rate * 30 * self.oil_price for rate in production_profile]
        
        # Cash flows
        cash_flows = [-capex]
        for rev in monthly_revenue:
            cash_flows.append(rev - opex_per_month)
            
        npv = self.calculate_npv(cash_flows)
        total_revenue = sum(monthly_revenue)
        total_profit = sum(cash_flows)
        roi = (total_profit / capex) if capex > 0 else 0
        
        payback = self.calculate_payback_period(cash_flows)
        
        return {
            'is_feasible': npv > 0 and roi > self.target_roi,
            'metrics': {
                'npv': round(npv, 2),
                'roi': round(roi * 100, 2),
                'payback_months': payback
            },
            'audit': audit,
            'financials': {
                'total_capex': round(capex, 2),
                'monthly_opex': round(opex_per_month, 2),
                'gross_revenue': round(total_revenue, 2)
            },
            'production_profile': [round(p, 2) for p in production_profile[:12]] # First year
        }

    def calculate_payback_period(self, cash_flows):
        """Returns the month where cumulative cash flows become positive."""
        cumulative_cash_flow = 0
        for t, cf in enumerate(cash_flows):
            cumulative_cash_flow += cf
            if cumulative_cash_flow >= 0 and t > 0:
                return t
        return -1 # Never paid back

    def generate_strategic_plan(self, initial_rate, depth, formation, probability=0.5):
        """
        Phase 3: Strategic Executive Audit.
        Combines geological risk with financial life-cycle modeling.
        Returns a multi-decade strategic deployment roadmap.
        """
        env_type = "Offshore" if depth > 3500 else "Onshore"
        
        # 1. Base Feasibility (240 months = 20 years)
        base_res = self.assess_well_feasibility(initial_rate, depth, formation, env_type, project_life_months=240)
        
        # 2. Risk-Adjusted Economics (EMV - Expected Monetary Value)
        # EMV = (P_success * NPV_success) - (P_failure * Cost_failure)
        p_success = probability
        cost_failure = base_res['financials']['total_capex'] * 0.85 # Dry hole cost estimate
        emv = (p_success * base_res['metrics']['npv']) - ((1 - p_success) * cost_failure)
        
        # 3. Nigerian Fiscal Model (Simplified PIA 2021 Tiers)
        royalty_rate = 0.05 if env_type == "Offshore" else 0.15 
        tax_rate = 0.30 # Hydrocarbon Tax
        
        # Net Take after state shares and taxes
        net_take = base_res['metrics']['npv'] * (1 - royalty_rate) * (1 - tax_rate)
        
        # 4. Strategic Milestones
        milestones = [
            {"phase": "I: Exploration", "duration": "4-6 Months", "task": "Seismic 3D Inversion & Environmental Impact (EIA)."},
            {"phase": "II: Drilling", "duration": f"{max(15, int(depth/150))} Days", "task": f"Mobilize {env_type} rig system for {formation} target."},
            {"phase": "III: Completion", "duration": "45 Days", "task": "Multi-zone smart completion and pressure sync."},
            {"phase": "IV: Production", "duration": "240 Months", "task": f"Life-cycle extraction targeting {initial_rate} BBL/day peak."}
        ]

        return {
            'executive_summary': {
                'emv': round(float(emv), 2),
                'risk_adjusted_roi': round(float((emv / base_res['financials']['total_capex']) * 100), 2),
                'fiscal_regime': "Deepwater PSC" if env_type == "Offshore" else "Onshore JV / Lease (PIA)",
                'net_take_estimate': round(float(net_take), 2)
            },
            'feasibility': base_res,
            'milestones': milestones,
            'strategic_risk': "CRITICAL" if probability < 0.3 else "HIGH" if probability < 0.5 else "MODERATE" if probability < 0.8 else "LOW",
            'timestamp': datetime.now().isoformat()
        }
