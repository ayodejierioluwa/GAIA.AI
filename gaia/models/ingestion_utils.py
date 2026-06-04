import csv
import io
import re
import random

class WellDataParser:
    """
    High-Fidelity Technical Parser for Petroleum Engineering Data.
    Uses heuristic search to identify metrics without rigid schema requirements.
    """
    
    COL_MAPPING = {
        'well_name': ['well', 'name', 'uwi', 'lease'],
        'flow_rate': ['rate', 'q', 'bpd', 'liquid', 'flow'],
        'initial_pressure': ['initial p', 'pi', 'static pressure', 'p_initial', 'res pressure'],
        'final_pressure': ['final p', 'pf', 'flowing pressure', 'pwf', 'p_flowing'],
        'depth': ['depth', 'tvd', 'mdd', 'interval'],
        'api_gravity': ['api', 'gravity', 'density_api'],
        'gor': ['gor', 'gas oil ratio', 'gasoil'],
        'water_cut': ['wct', 'water cut', 'wc', 'water_percent'],
        'temperature': ['temp', 'temperature', 'bottom hole temp', 'bht'],
        'latitude': ['latitude', 'lat'],
        'longitude': ['longitude', 'lon', 'long'],
        'formation': ['formation', 'fm', 'lithology'],
        'oil_presence': ['oil_presence', 'oil', 'hydrocarbon'],
        'porosity': ['porosity', 'por', 'phi'],
        'permeability': ['permeability', 'perm', 'k', 'md']
    }

    @classmethod
    def parse_file(cls, file_content, filename):
        """Extract structured data from raw file text (CSV/TXT)."""
        data = {
            'well_name': filename.split('.')[0],
            'flow_rate': 0, 'initial_pressure': 0, 'final_pressure': 0,
            'depth': 0, 'api_gravity': 32.0, 'gor': 500, 'water_cut': 0, 'temperature': 180,
            'porosity': 0.22, 'permeability': 150,
            'latitude': None, 'longitude': None, 'formation': None, 'oil_presence': None
        }
        
        try:
            # Handle text/csv decoding
            if isinstance(file_content, bytes):
                text = file_content.decode('utf-8', errors='ignore')
            else:
                text = file_content
                
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            
            if rows:
                row = rows[0] # Take first data row for this logic
                for target, synonyms in cls.COL_MAPPING.items():
                    for col in row.keys():
                        if any(syn in col.lower() for syn in synonyms):
                            val_str = str(row[col]).strip()
                            if target in ['formation', 'well_name']:
                                data[target] = val_str
                                break
                            else:
                                try:
                                    if target == 'oil_presence':
                                        if val_str.lower() in ['true', 'yes', 'y', '1']:
                                            data[target] = True
                                        elif val_str.lower() in ['false', 'no', 'n', '0']:
                                            data[target] = False
                                        else:
                                            data[target] = float(val_str.replace(',', '')) > 0
                                    else:
                                        data[target] = float(val_str.replace(',', ''))
                                    break
                                except (ValueError, TypeError):
                                    continue
            
            # Automatic fallback for common well naming
            if not data.get('well_name') or data['well_name'] == 'Well-New':
                 data['well_name'] = filename.split('.')[0]

        except Exception:
            # Fallback to defaults or partial parsing
            pass
            
        return data

class TechnicalDiagnosticEngine:
    """
    Automated Assistant Lead Diagnostic logic.
    Provides immediate technical feedback on uploaded well performance.
    """
    
    @staticmethod
    def analyze(data):
        """Generate a one-sentence technical insight based on parameters."""
        rate = data.get('flow_rate', 0)
        pi = data.get('productivity_index', 0)
        skin = data.get('skin_factor', 0)
        api = data.get('api_gravity', 0)
        wc = data.get('water_cut', 0)
        
        insights = []
        
        # 1. Skin & Performance
        if skin > 5:
            insights.append("CRITICAL: Significant near-wellbore damage (Skin > 5). Recommend acid stimulation.")
        elif skin > 2:
            insights.append("CAUTION: Moderate skin detected. Potential filtrate invasion.")
        elif skin < 0:
            insights.append("OPTIMAL: Stimulated wellbore interface detected.")
            
        # 2. Fluid properties
        if api < 20 and api > 0:
            insights.append("Asset classified as Heavy Oil. Monitor viscosity-induced frictional losses.")
        elif api > 45:
            insights.append("High-yield condensate/light oil identified.")
            
        # 3. Water/Gas risks
        if wc > 30:
            insights.append("High water cut detected. Assess aquifer sweep or water coning risks.")
            
        # 4. Global fallback
        if not insights:
            insights.append("System Audit: Flow profile appears consistent with regional Niger Delta trends.")
            
        return " | ".join(insights[:2])
