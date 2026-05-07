"""
gaia/visualization/charts.py
Interactive 4D/3D Plotly chart generators for GAIA.
Includes Dual-Mode (Scatter/Voxel) 3D maps and Temporal Subsurface Comparison.
"""
import numpy as np
import json

# ─────────────────────────────────────────────────────────────
#  Nigerian Basin Reference Data
# ─────────────────────────────────────────────────────────────
BASINS = {
    'Niger Delta':  {'lat': 4.9,  'lon': 6.5,  'color': '#27ae60', 'potential': 0.92},
    'Benue Trough': {'lat': 8.5,  'lon': 8.2,  'color': '#f39c12', 'potential': 0.65},
    'Anambra':      {'lat': 6.2,  'lon': 7.0,  'color': '#3498db', 'potential': 0.40},
    'Chad Basin':   {'lat': 12.0, 'lon': 13.0, 'color': '#e74c3c', 'potential': 0.18},
}

FORMATIONS = [
    {'name': 'Quaternary Alluvium',  'top':    0, 'bottom':  100, 'color': 'rgba(210,180,140,0.5)'},
    {'name': 'Agbada Formation',     'top':  100, 'bottom': 2000, 'color': 'rgba(100,149,237,0.5)'},
    {'name': 'Akata Shale',          'top': 2000, 'bottom': 4000, 'color': 'rgba(70,130,180,0.6)'},
    {'name': 'Basement Complex',     'top': 4000, 'bottom': 6000, 'color': 'rgba(105,105,105,0.7)'},
]

def _oil_probability(lat, lon, depth=3000):
    """Simple, fast, deterministic potential score (0-1)."""
    niger_delta_dist = ((lat - 4.9) ** 2 + (lon - 6.5) ** 2) ** 0.5
    benue_dist       = ((lat - 8.5) ** 2 + (lon - 8.2) ** 2) ** 0.5
    basin_factor     = float(np.exp(-min(niger_delta_dist, benue_dist) / 2))
    depth_factor     = float(np.exp(-((depth - 3000) / 1200) ** 2))
    return round(basin_factor * 0.6 + depth_factor * 0.4, 3)

# ─────────────────────────────────────────────────────────────
#  1.  3D Subsurface Chart (Dual-Mode: Scatter/Voxel)
# ─────────────────────────────────────────────────────────────
def generate_3d_subsurface_chart(center_lat=5.5, center_lon=6.8, 
                                  radius_deg=2.0, n_points=300, mode='scatter') -> str:
    rng = np.random.default_rng(seed=42)
    
    if mode == 'voxel':
        grid_res = 12
        lats_g  = np.linspace(center_lat - radius_deg/2, center_lat + radius_deg/2, grid_res)
        lons_g  = np.linspace(center_lon - radius_deg/2, center_lon + radius_deg/2, grid_res)
        depths_g = np.linspace(500, 5000, grid_res)
        
        x, y, z, p = [], [], [], []
        for lo in lons_g:
            for la in lats_g:
                for d in depths_g:
                    prob = _oil_probability(la, lo, d)
                    if prob > 0.4:
                        x.append(lo); y.append(la); z.append(-d); p.append(prob)
        
        main_trace = {
            'type': 'scatter3d',
            'x': x, 'y': y, 'z': z,
            'mode': 'markers',
            'marker': {
                'size': 14,
                'symbol': 'square',
                'color': p,
                'colorscale': 'Viridis',
                'opacity': 0.7,
                'colorbar': {'title': 'Hydrocarbon Prob', 'tickfont': {'color': '#00ffc3'}}
            },
            'name': 'Voxels'
        }
    else:
        lats  = rng.uniform(center_lat - radius_deg, center_lat + radius_deg, n_points)
        lons  = rng.uniform(center_lon - radius_deg, center_lon + radius_deg, n_points)
        depths = rng.uniform(500, 5000, n_points)
        probs = np.array([_oil_probability(la, lo, d) for la, lo, d in zip(lats, lons, depths)])
        
        main_trace = {
            'type': 'scatter3d',
            'x': lons.tolist(), 'y': lats.tolist(), 'z': (-depths).tolist(),
            'mode': 'markers',
            'marker': {
                'size': 6,
                'color': probs.tolist(),
                'colorscale': 'RdYlGn',
                'opacity': 0.85,
                'colorbar': {'title': 'Oil Potential', 'tickfont': {'color': '#00ffc3'}}
            },
            'name': 'Sensor Data'
        }

    basin_traces = []
    for basin_name, bd in BASINS.items():
        basin_traces.append({
            'type': 'scatter3d',
            'x': [bd['lon']], 'y': [bd['lat']], 'z': [-2500],
            'mode': 'markers+text',
            'marker': {'size': 12, 'color': bd['color'], 'symbol': 'diamond', 'line': {'width': 2, 'color': '#fff'}},
            'text': [basin_name],
            'textposition': 'top center',
            'name': basin_name,
        })

    figure = {
        'data': [main_trace] + basin_traces,
        'layout': {
            'title': {'text': f'🧭 GAIA 3D Subsurface - {mode.upper()} ANALYSIS', 'font': {'color': '#00ffc3', 'size': 20}},
            'scene': {
                'xaxis': {'title': 'Longitude', 'gridcolor': '#222'},
                'yaxis': {'title': 'Latitude', 'gridcolor': '#222'},
                'zaxis': {'title': 'Depth (m)', 'tickvals': [-1000, -3000, -5000], 'gridcolor': '#222'},
                'bgcolor': '#080c12',
                'camera': {'eye': {'x': 1.8, 'y': 1.8, 'z': 1.2}}
            },
            'paper_bgcolor': '#080c12',
            'font': {'color': '#00ffc3'},
            'template': 'plotly_dark',
            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 50}
        }
    }
    return json.dumps(figure)

# ─────────────────────────────────────────────────────────────
#  2.  4D Temporal Comparison (2010 vs 2024)
# ─────────────────────────────────────────────────────────────
def generate_4d_depletion_comparison(lat=4.9, lon=6.5, years=[2010, 2024]) -> str:
    rng = np.random.default_rng(seed=42)
    traces = []
    x_coords = np.linspace(lon - 0.5, lon + 0.5, 12)
    y_coords = np.linspace(lat - 0.5, lat + 0.5, 12)
    xv, yv = np.meshgrid(x_coords, y_coords)
    
    for i, year in enumerate(years):
        shift = i * 35 
        z = (np.sin(xv*10) * np.cos(yv*10) * 150) - 3000 - shift
        traces.append({
            'type': 'surface',
            'x': x_coords.tolist(), 'y': y_coords.tolist(), 'z': z.tolist(),
            'name': f'Formation ({year})',
            'colorscale': 'YlOrBr' if i == 0 else 'Cividis',
            'opacity': 0.5 if i == 1 else 0.8,
            'showscale': False,
        })

    figure = {
        'data': traces,
        'layout': {
            'title': {'text': f'⏳ Subsurface Temporal Comparison ({years[0]} vs {years[1]})', 'font': {'color': '#00ffc3', 'size': 18}},
            'scene': {
                'xaxis': {'title': 'Lon', 'gridcolor': '#222'},
                'yaxis': {'title': 'Lat', 'gridcolor': '#222'},
                'zaxis': {'title': 'Depth (m)', 'gridcolor': '#222'},
                'bgcolor': '#080c12',
                'camera': {'eye': {'x': 2.0, 'y': 1.5, 'z': 1.0}}
            },
            'paper_bgcolor': '#080c12',
            'font': {'color': '#00ffc3'},
            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 60}
        }
    }
    return json.dumps(figure)

# ─────────────────────────────────────────────────────────────
#  3.  Nigeria Basin 2D Heatmap (overview)
# ─────────────────────────────────────────────────────────────
def generate_nigeria_heatmap() -> str:
    lats = np.linspace(4.0, 14.0, 40)
    lons = np.linspace(2.5, 15.0, 40)
    z = [[_oil_probability(la, lo) for lo in lons] for la in lats]
    
    figure = {
        'data': [
            {'type': 'heatmap', 'x': lons.tolist(), 'y': lats.tolist(), 'z': z, 'colorscale': 'RdYlGn', 'zmin': 0, 'zmax': 1},
            {'type': 'scatter', 'x': [bd['lon'] for bd in BASINS.values()], 'y': [bd['lat'] for bd in BASINS.values()], 
             'mode': 'markers+text', 'text': list(BASINS.keys()), 'marker': {'size': 14, 'color': '#fff'}}
        ],
        'layout': {
            'title': {'text': '🗺️ Nigeria Oil Potential Heatmap', 'font': {'color': '#ecf0f1'}},
            'paper_bgcolor': '#0d1117', 'plot_bgcolor': '#0d1117', 'font': {'color': '#ecf0f1'},
            'xaxis': {'title': 'Longitude'}, 'yaxis': {'title': 'Latitude'}
        }
    }
    return json.dumps(figure)

# ─────────────────────────────────────────────────────────────
#  4.  Geological Layer Cross-Section
# ─────────────────────────────────────────────────────────────
def generate_geological_cross_section(lat=4.9, lon=6.5) -> str:
    traces = []
    for f in FORMATIONS:
        traces.append({
            'type': 'bar', 'name': f['name'], 'x': [f['name']], 'y': [f['bottom'] - f['top']], 'base': [-f['bottom']],
            'marker': {'color': f['color']}
        })
    figure = {
        'data': traces,
        'layout': {
            'title': {'text': f'🪨 Geological Cross-Section — Lat {lat}, Lon {lon}', 'font': {'color': '#ecf0f1'}},
            'barmode': 'stack', 'paper_bgcolor': '#0d1117', 'plot_bgcolor': '#0d1117', 'font': {'color': '#ecf0f1'},
            'yaxis': {'title': 'Depth (m)', 'tickvals': [0, -2000, -4000, -6000]}
        }
    }
    return json.dumps(figure)

# ─────────────────────────────────────────────────────────────
#  5.  Drilling Telemetry Simulation
# ─────────────────────────────────────────────────────────────
def get_drilling_telemetry(depth_m):
    """
    Simulates real-time drilling telemetry (pressure, temp, etc.) 
    based on the current depth and soil characteristics.
    """
    # Find active formation
    formation = FORMATIONS[0]
    for f in FORMATIONS:
        if f['top'] <= depth_m <= f['bottom']:
            formation = f
            break
            
    # Base physics
    # Hydrostatic Pressure: P = 0.052 * MudWeight * TrueVerticalDepth
    # Assuming avg MudWeight of 10.5 ppg
    pressure = 0.052 * 10.5 * (depth_m * 3.281) # PSI
    
    # Geothermal Gradient: ~2.5 deg C per 100m
    temperature = 25 + (depth_m / 100) * 2.5
    
    # Rate of Penetration (ROP) - slower in harder formations
    base_rop = 30 # m/hr
    if 'Shale' in formation['name']:
        base_rop = 15
    elif 'Basement' in formation['name']:
        base_rop = 5
    
    rop = base_rop + np.random.uniform(-2, 2)
    
    return {
        'status': 'success',
        'depth': round(depth_m, 1),
        'formation': formation['name'],
        'pressure': round(pressure, 0),
        'temperature': round(temperature, 1),
        'rop': round(rop, 1),
        'torque': round(15 + (depth_m / 100) * 1.5, 1) # kft-lb
    }

def calculate_drilling_etc(layers):
    """
    Calculates the expected time of completion (ETC) based on 
    the thickness and rock type of each geological layer.
    """
    # ROP (meters per hour) based on rock type
    rop_map = {
        'sand': 40,
        'sandstone': 25,
        'shale': 12,
        'limestone': 15,
        'granite': 4
    }
    
    total_hours = 0
    for layer in layers:
        height = layer['depth'][1] - layer['depth'][0]
        rop = rop_map.get(layer['rock_type'], 10) # Default to 10 m/hr
        total_hours += (height / rop)
    
    days = int(total_hours // 24)
    hours = int(total_hours % 24)
    
    if days > 0:
        return f"{days} Days, {hours} Hours"
    return f"{hours} Hours"

# ─────────────────────────────────────────────────────────────
#  6.  Synthetic Seismic Sub-Slice Generator
# ─────────────────────────────────────────────────────────────
def generate_seismic_slice(lat=4.9, lon=6.5, width_km=10, depth_m=6000) -> str:
    """
    Generates a 2D synthetic seismic profile (Acoustic Impedance).
    Mimics vertical reflections at stratigraphic boundaries.
    """
    res_x, res_y = 100, 150
    x = np.linspace(0, width_km, res_x)
    z = np.linspace(0, depth_m, res_y)
    
    # Base background noise (low frequency)
    data = np.random.normal(0, 0.05, (res_y, res_x))
    
    # Simple folding/dipping effect
    dip = np.sin(x / width_km * np.pi) * 10 
    
    # Reflection coefficients at "Formation" boundaries
    boundaries = [100, 1500, 3500, 5000]
    for b in boundaries:
        # Create a "Wave" reflection at the boundary
        layer_idx = int((b / depth_m) * res_y)
        if layer_idx < res_y:
            for i in range(res_x):
                offset = int(dip[i])
                idx = layer_idx + offset
                if 0 <= idx < res_y:
                    # Ricker-like wavelet pulse
                    pulse = [1.0, -0.8, 0.4] 
                    for p_i, p_val in enumerate(pulse):
                        if idx + p_i < res_y:
                            data[idx + p_i, i] += p_val * (1.0 + np.random.uniform(-0.1, 0.1))

    figure = {
        'data': [{
            'type': 'heatmap',
            'x': x.tolist(), 'y': (-z).tolist(), 'z': data.tolist(),
            'colorscale': 'RdBu',
            'zmid': 0,
            'showscale': False,
            'reversescale': True
        }],
        'layout': {
            'title': {'text': f'〰️ Synthetic Seismic Section — Cross-Section A-A\' (Lat {lat})', 'font': {'color': '#00ffc3', 'size': 16}},
            'paper_bgcolor': '#000', 'plot_bgcolor': '#000',
            'font': {'color': '#00ffc3'},
            'xaxis': {'title': 'Distance (km)', 'showgrid': False, 'zeroline': False},
            'yaxis': {'title': 'Depth (m)', 'showgrid': True, 'gridcolor': '#111'},
            'margin': {'l': 60, 'r': 20, 'b': 40, 't': 50}
        }
    }
    return json.dumps(figure)
