import sys
import os

# Align python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gaia.models.ingestion_utils import WellDataParser

def test_las_parsing():
    las_path = os.path.join(os.path.dirname(__file__), 'sample_well.las')
    with open(las_path, 'r') as f:
        content = f.read()
    
    data = WellDataParser.parse_file(content, 'sample_well.las')
    print("Parsed Data:")
    for k, v in data.items():
        print(f"  {k}: {v}")
        
    assert data['well_name'] == 'GAIA-APPRAISAL-01', f"Expected well name 'GAIA-APPRAISAL-01', got '{data['well_name']}'"
    assert abs(data['latitude'] - 5.4851) < 0.001, f"Expected latitude ~5.4851, got {data['latitude']}"
    assert abs(data['longitude'] - 6.8214) < 0.001, f"Expected longitude ~6.8214, got {data['longitude']}"
    assert data['depth'] == 1520.0, f"Expected max depth 1520.0, got {data['depth']}"
    assert 0.20 < data['porosity'] < 0.30, f"Expected average porosity ~0.24, got {data['porosity']}"
    assert data['permeability'] > 0.0, f"Expected permeability to be calculated, got {data['permeability']}"
    assert data['formation'] == 'Agbada', f"Expected formation 'Agbada' from Niger Delta offshore context, got '{data['formation']}'"
    
    print("\nLAS Parser Verification: SUCCESS!")

if __name__ == '__main__':
    test_las_parsing()
