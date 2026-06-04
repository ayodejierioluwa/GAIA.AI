from flask import Blueprint, request, session, current_app, json, Response
import os
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/training-status')
def training_status():
    analyzer = current_app.config['advanced_analyzer']
    return json.dumps(analyzer.get_training_status())

@api_bp.route('/api/start-training', methods=['POST'])
def start_training():
    analyzer = current_app.config['advanced_analyzer']
    try:
        result = analyzer.enhanced_training_with_web_data()
        return json.dumps(result)
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@api_bp.route('/api/predict-potential', methods=['POST'])
def predict_potential():
    ml_analyzer = current_app.config['ml_analyzer']
    try:
        data = request.get_json()
        result = ml_analyzer.predict_oil_potential(
            data.get('lat', 4.8), data.get('lon', 6.5), 
            data.get('depth', 3000), data.get('porosity', 0.25), 
            data.get('permeability', 150)
        )
        return json.dumps(result)
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@api_bp.route('/api/feasibility', methods=['POST'])
def feasibility():
    engine = current_app.config['economics_engine']
    try:
        data = request.get_json()
        result = engine.assess_well_feasibility(
            initial_rate=float(data.get('initial_rate', 1000)),
            depth=float(data.get('depth', 3000)),
            formation=data.get('formation', 'Agbada'),
            env_type=data.get('env_type', 'Onshore'),
            project_life_months=int(data.get('project_life', 60))
        )
        return json.dumps({'status': 'success', 'result': result})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@api_bp.route('/api/region-grid', methods=['POST'])
def region_grid():
    precise_ml = current_app.config['precise_ml']
    try:
        data = request.get_json()
        raw_result = precise_ml.analyze_region(
            center_lat=float(data.get('lat', 5.5)),
            center_lon=float(data.get('lon', 6.8)),
            radius_km=float(data.get('radius_km', 10)),
            resolution=int(data.get('resolution', 10))
        )
        
        # Transform for UI expectations
        detailed = raw_result['detailed_results']
        
        # Extract leads (top 15% with probability > 0.7)
        leads = []
        for r in detailed:
            if r['status'] == 'success' and r['result']['probability'] > 0.7:
                leads.append({
                    'lat': r['input']['lat'],
                    'lon': r['input']['lon'],
                    'score': int(r['result']['probability'] * 100)
                })
        
        leads = sorted(leads, key=lambda x: x['score'], reverse=True)[:5]
        
        # Build Heatmap Chart
        lats = sorted(list(set([r['input']['lat'] for r in detailed])))
        lons = sorted(list(set([r['input']['lon'] for r in detailed])))
        
        z_matrix = []
        for lat in lats:
            row = []
            for lon in lons:
                # Find matching result
                val = 0
                for r in detailed:
                    if r['input']['lat'] == lat and r['input']['lon'] == lon:
                        val = r['result']['probability']
                        break
                row.append(val)
            z_matrix.append(row)

        chart = {
            'data': [{
                'z': z_matrix,
                'x': lons,
                'y': lats,
                'type': 'heatmap',
                'colorscale': 'Viridis',
                'showscale': True
            }],
            'layout': {
                'title': 'NEURAL PROBABILITY GRID',
                'xaxis': {'title': 'Longitude'},
                'yaxis': {'title': 'Latitude'},
                'paper_bgcolor': '#000',
                'plot_bgcolor': '#000',
                'font': {'color': '#00ffc3'}
            }
        }
        
        return json.dumps({
            'status': 'success',
            'chart': chart,
            'top_leads': leads,
            'summary': raw_result
        })
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@api_bp.route('/api/chat', methods=['POST'])
def chat():
    chatbot = current_app.config['chatbot']
    gaia_agent = current_app.config['gaia_agent']
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        use_legacy = data.get('legacy', False)
        
        if use_legacy:
            response = chatbot.generate_response(user_message)
        else:
            geological_context = data.get('context', {})
            response = gaia_agent.generate_response(user_message, geological_context, session_id=session.get('user_id', 1))
            
        return json.dumps({'response': response})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@api_bp.route('/api/chat/status')
def chat_status():
    db = current_app.config['ai_db']
    try:
        count = db.get_knowledge_count()
        return json.dumps({'status': 'online', 'node_count': count})
    except Exception:
        return json.dumps({'status': 'offline', 'node_count': 3000})

@api_bp.route('/api/simple-error-log', methods=['POST'])
def simple_error_log():
    try:
        data = request.get_json()
        entry = data.get('entry', '')
        with open('prototype_errors_simple.log', 'a') as f:
            f.write(entry)
        return json.dumps({'status': 'success'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

# ── Visualization API Endpoints ──────────────────────────────
from gaia.visualization.charts import (
    generate_3d_subsurface_chart,
    generate_4d_depletion_comparison,
    generate_nigeria_heatmap,
    generate_geological_cross_section,
)

@api_bp.route('/api/visualization/3d')
def api_viz_3d():
    if 'user_id' not in session:
        return json.dumps({'error': 'Not authenticated'})
    return Response(response=generate_3d_subsurface_chart(), status=200, mimetype='application/json')

@api_bp.route('/api/visualization/4d')
def api_viz_4d():
    if 'user_id' not in session:
        return json.dumps({'error': 'Not authenticated'})
    try:
        lat = float(request.args.get('lat', 4.9))
        lon = float(request.args.get('lon', 6.5))
    except ValueError:
        lat, lon = 4.9, 6.5
    return Response(response=generate_4d_depletion_comparison(lat, lon), status=200, mimetype='application/json')

@api_bp.route('/api/visualization/heatmap')
def api_viz_heatmap():
    if 'user_id' not in session:
        return json.dumps({'error': 'Not authenticated'})
    return Response(response=generate_nigeria_heatmap(), status=200, mimetype='application/json')

@api_bp.route('/api/visualization/cross')
def api_viz_cross():
    if 'user_id' not in session:
        return json.dumps({'error': 'Not authenticated'})
    try:
        lat = float(request.args.get('lat', 4.9))
        lon = float(request.args.get('lon', 6.5))
    except ValueError:
        lat, lon = 4.9, 6.5
    return Response(response=generate_geological_cross_section(lat, lon), status=200, mimetype='application/json')

@api_bp.route('/api/download-report/<filename>')
def download_report(filename):
    from flask import send_from_directory
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
