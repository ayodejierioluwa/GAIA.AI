import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from gaia.models.satellite import SatelliteSpectralEngine

def test_live_satellite():
    engine = SatelliteSpectralEngine()
    
    # Bounding coordinates for Anambra Basin (lat=6.2, lon=7.0)
    lat = 6.2
    lon = 7.0
    
    print("Testing live satellite data retrieval for Anambra Basin...")
    res = engine.analyze_spectral_profile(lat, lon, mode="NDVI", live=True)
    
    print("\n--- RESULTS ---")
    print(f"Latitude: {res.get('lat')}")
    print(f"Longitude: {res.get('lon')}")
    print(f"Mode: {res.get('mode')}")
    print(f"Live Data Flag: {res.get('live_data', False)}")
    print(f"Platform: {res.get('platform', 'N/A')}")
    
    if res.get('live_data'):
        print(f"Acquisition Date: {res.get('timestamp')}")
        print(f"Cloud Cover: {res.get('cloud_cover')}%")
        grid = res.get('grid')
        print(f"Grid shape: {len(grid)}x{len(grid[0]) if grid else 0}")
        print(f"First row: {grid[0][:5]}...")
    else:
        print("Live data search failed or fell back to simulation.")
        
if __name__ == '__main__':
    test_live_satellite()
