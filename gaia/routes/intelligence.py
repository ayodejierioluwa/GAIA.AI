from flask import Blueprint, request, redirect, url_for, session, current_app, json
from .utils import render_gaia_page

intelligence_bp = Blueprint('intelligence', __name__)

@intelligence_bp.route('/intelligence-suite')
def intelligence_suite():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('intelligence.intelligence_dashboard'))

@intelligence_bp.route('/api/economics/simulate', methods=['POST'])
def api_economics_simulate():
    if 'user_id' not in session:
        return json.dumps({'status': 'error', 'message': 'Auth required'})
    
    data = request.json
    depth = float(data.get('depth', 3000))
    formation = data.get('formation', 'Agbada')
    env_type = data.get('env_type', 'Onshore')
    
    economics = current_app.config['economics_engine']
    # We use a dummy 500 bbl/d for simulation flow
    audit_data = economics.assess_well_feasibility(
        initial_rate=500,
        depth=depth,
        formation=formation,
        env_type=env_type
    )
    
    return json.dumps(audit_data)

@intelligence_bp.route('/ai-training')
def ai_training():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Redirect to the new upgraded dashboard
    return redirect(url_for('intelligence.intelligence_dashboard'))

@intelligence_bp.route('/workshop/dashboard')
def intelligence_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = current_app.config['ai_db']
    ml = current_app.config['ml_analyzer']
    
    # Fetch real metrics from DB
    knowledge_facts = db.get_recent_knowledge(limit=10)
    learning_logs = db.get_learning_history(limit=15)
    
    # Fetch Strategic Thoughts (Assessments)
    strategic_thoughts = db.query_knowledge_by_tag("Strategic Opportunity", limit=5)
    
    # Map to UI variables
    facts_count = db.get_knowledge_count()
    # Simulated confidence based on actual R2 (default 0.8) and data density
    from gaia.models.ml import ConfidenceScorer
    avg_confidence = ConfidenceScorer.calculate_confidence(
        last_trained_days=1, 
        r2_score=0.85, 
        data_density=facts_count
    )
    
    from flask import render_template
    # We use our custom template which we created earlier
    # Since we don't have a full template loader setup for 'custom' paths easily, 
    # we can use render_template if we set the folder appropriately, 
    # but for simplicity in this walkthrough we'll use render_template_string
    # and just read the file content.
    template_path = os.path.join(current_app.root_path, 'templates', 'intelligence_dashboard.html')
    with open(template_path, 'r') as f:
        template_content = f.read()

    from .utils import render_gaia_page
    from flask import render_template_string
    content = render_template_string(
        template_content,
        knowledge_count=facts_count,
        confidence=int(avg_confidence * 100),
        learning_rate=round(1.2 + (facts_count * 0.05), 1),
        last_growth=learning_logs[0][4] if learning_logs else "Never",
        logs=[{'timestamp': l[4], 'event_type': l[1], 'description': l[2]} for l in learning_logs],
        facts=[{'entity_name': f[1], 'entity_type': f[2], 'fact_description': f[3], 'confidence_score': f[5], 'source_url': f[4]} for f in knowledge_facts],
        thoughts=[{'entity': t[0], 'description': t[2], 'confidence': t[3]} for t in strategic_thoughts]
    )
    
    return render_gaia_page("Intelligence Dashboard", content)

@intelligence_bp.route('/api/intelligence/reason', methods=['POST'])
def api_reason():
    if 'user_id' not in session:
        return json.dumps({'status': 'error', 'message': 'Auth required'})
    
    data = request.json
    query = data.get('query')
    
    gaia_agent = current_app.config['gaia_agent']
    analyzer = current_app.config['advanced_analyzer']
    
    # prioritize passed context from active workstation sessions
    context = data.get('geological_context')
    
    if not context:
        if "agbada" in query.lower() or "delta" in query.lower():
            layers = analyzer.generate_geological_layers(4.9, 6.5)
            context = {'layers': layers}
        elif "mamu" in query.lower() or "anambra" in query.lower():
            layers = analyzer.generate_geological_layers(7.1, 7.2)
            context = {'layers': layers}
        
    response = gaia_agent.generate_response(query, geological_context=context, session_id=session.get('user_id', 1))
    
    return json.dumps({
        'status': 'success',
        'response': response
    })

@intelligence_bp.route('/api/intelligence/debate', methods=['POST'])
def api_debate():
    if 'user_id' not in session:
        return json.dumps({'status': 'error', 'message': 'Auth required'})
    
    data = request.json
    query = data.get('query')
    
    gaia_agent = current_app.config['gaia_agent']
    # prioritize passed context from active workstation sessions
    context = data.get('geological_context')
    
    # Run the collaborative debate loop
    collab_data = gaia_agent.collaborate(query, geological_context=context)
    
    return json.dumps({
        'status': 'success',
        **collab_data
    })

@intelligence_bp.route('/api/intelligence/manual-trigger', methods=['POST'])
def manual_trigger():
    if 'user_id' not in session:
        return json.dumps({'status': 'error', 'message': 'Auth required'})
        
    ingestion = current_app.config['ingestion_engine']
    if not ingestion.is_running:
        import threading
        import asyncio
        
        def run_cycle():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(ingestion.run_autonomous_cycle())
            loop.close()
            
        threading.Thread(target=run_cycle, daemon=True).start()
        return json.dumps({"status": "started"})
    return json.dumps({"status": "already_running"})

@intelligence_bp.route('/api/intelligence/growth-status')
def growth_status():
    ingestion_engine = current_app.config['ingestion_engine']
    db = current_app.config['ai_db']
    
    # Refresh the global node count for the telemetry object
    ingestion_engine.telemetry["total_kb_nodes"] = db.get_knowledge_count()
    
    return json.dumps(ingestion_engine.telemetry)

import os
import asyncio

@intelligence_bp.route('/workshop/satellite')
def satellite_analysis():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Load the new control room template we just created
    template_path = os.path.join(current_app.root_path, 'templates', 'satellite_control_room.html')
    with open(template_path, 'r') as f:
        template_content = f.read()

    from .utils import render_gaia_page
    from flask import render_template_string
    content = render_template_string(template_content)
    
    return render_gaia_page("Satellite Control Room", content)

@intelligence_bp.route('/api/satellite/analyze')
def api_satellite_analyze():
    lat = float(request.args.get('lat', 4.9))
    lon = float(request.args.get('lon', 6.5))
    mode = request.args.get('mode', 'TRUE_COLOR')
    live = request.args.get('live', 'false').lower() == 'true'
    
    engine = current_app.config['satellite_engine']
    analysis = engine.analyze_spectral_profile(lat, lon, mode=mode, live=live)
    
    # Convert grid to a Plotly heatmap
    import json
    fig = {
        'data': [{
            'type': 'heatmap',
            'z': analysis['grid'],
            'colorscale': 'Viridis' if mode == 'THERMAL_IR' else 'Greens' if mode == 'NDVI' else [[0, '#000033'], [0.5, '#000080'], [1, '#00bfff']] if mode == 'SAR' else 'Earth',
            'showscale': False
        }],
        'layout': {
            'margin': {'l':0, 'r':0, 'b':0, 't':0},
            'xaxis': {'visible': False}, 'yaxis': {'visible': False},
            'paper_bgcolor': '#000', 'plot_bgcolor': '#000'
        },
        'live_data': analysis.get('live_data', False),
        'timestamp': analysis.get('timestamp', ''),
        'cloud_cover': analysis.get('cloud_cover', 0),
        'platform': analysis.get('platform', '')
    }
    return json.dumps(fig)

@intelligence_bp.route('/api/satellite/compare')
def api_satellite_compare():
    lat = float(request.args.get('lat', 4.9))
    lon = float(request.args.get('lon', 6.5))
    start_year = int(request.args.get('start', 2010))
    end_year = int(request.args.get('end', 2024))
    
    engine = current_app.config['satellite_engine']
    comparison = engine.compare_temporal_signatures(lat, lon, start_year, end_year)
    
    # Generate AI Interpretation
    chatbot = current_app.config['chatbot']
    interp_prompt = f"Interpret a temporal change score of {comparison['change_score']}% between {start_year} and {end_year} for a petroleum basin at lat {lat}, lon {lon}. Focus on exploration implications."
    ai_interpretation = chatbot.generate_response(interp_prompt)
    
    # Side-by-side or difference map
    fig = {
        'data': [
            {'type': 'heatmap', 'z': comparison['start_profile']['grid'], 'xaxis': 'x1', 'colorscale': 'YlOrRd', 'showscale': False},
            {'type': 'heatmap', 'z': comparison['end_profile']['grid'], 'xaxis': 'x2', 'colorscale': 'YlOrRd', 'showscale': False}
        ],
        'layout': {
            'grid': {'rows': 1, 'columns': 2, 'pattern': 'independent'},
            'paper_bgcolor': '#000', 'plot_bgcolor': '#000',
            'margin': {'l': 20, 'r': 20, 'b': 20, 't': 40},
            'title': {'text': f'{start_year} vs {end_year} Surface Delta', 'font': {'color': '#00ffc3'}, 'x': 0.5}
        },
        'change_score': comparison['change_score'],
        'interpretation': ai_interpretation
    }
    return json.dumps(fig)

@intelligence_bp.route('/predictive-analytics')
def predictive_analytics():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_gaia_page("Predictive Analytics", "<p>Predictive modeling interface...</p>")

@intelligence_bp.route('/data-integration')
def data_integration():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_gaia_page("Data Integration", "<p>External data connectivity hub...</p>")
@intelligence_bp.route('/workshop/geospatial')
def geospatial_3d():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    basin = request.args.get('basin', 'niger_delta')
    
    template_path = os.path.join(current_app.root_path, 'templates', 'geospatial_3d.html')
    with open(template_path, 'r') as f:
        template_content = f.read()

    from .utils import render_gaia_page
    from flask import render_template_string
    import numpy as np
    
    # Restoring the EXACT mathematical model from first request
    x = np.linspace(0, 10, 50)
    y = np.linspace(0, 10, 50)
    X, Y = np.meshgrid(x, y)
    
    # Base formula from first request: Z = np.sin(X/2) * np.cos(Y/2) * 2000
    if basin == 'niger_delta':
        Z = np.sin(X/2) * np.cos(Y/2) * 2000
        title = "Niger Delta Depocenter"
        metrics = {"rate": "-4.2%", "reserves": "37.5B BBL"}
    elif basin == 'benue_trough':
        Z = np.sin(X/1.8) * np.cos(Y/2.2) * 1800
        title = "Benue Trough Rift"
        metrics = {"rate": "Frontier", "reserves": "8.2B BBL (EST.)"}
    elif basin == 'anambra':
        Z = np.sin(X/2.5) * np.cos(Y/1.5) * 1600
        title = "Anambra Fault Blocks"
        metrics = {"rate": "+1.2%", "reserves": "5.4B BBL"}
    else:
        Z = np.sin(X/2) * np.cos(Y/2) * 2000
        title = "Regional Overview"
        metrics = {"rate": "Stable", "reserves": "N/A"}
    
    # Add the EXACT noise factor from first request
    Z += np.random.normal(0, 50, Z.shape)
    
    # NEW: Fetch real satellite data for side-by-side correlation
    sat_engine = current_app.config['satellite_engine']
    # Approximate basin centers
    centers = {'niger_delta': (4.9, 6.5), 'benue_trough': (8.5, 8.2), 'anambra': (6.2, 7.0)}
    lat, lon = centers.get(basin, (4.9, 6.5))
    
    sat_mode = request.args.get('sat_mode', 'SAR')
    sat_analysis = sat_engine.analyze_spectral_profile(lat, lon, mode=sat_mode)
    
    # NEW: Generate Anomaly Markers for Agent Annotations
    # These are mock "high-potential" spots identified by GAIA
    anomaly_x = [2, 5, 8]
    anomaly_y = [3, 7, 4]
    anomaly_z = [Z[20, 10] + 200, Z[35, 25] + 200, Z[20, 40] + 200]
    
    fig_data = [{
        'type': 'surface',
        'z': Z.tolist(),
        'colorscale': 'Viridis',
        'showscale': False,
        'scene': 'scene1'
    }]
    
    sat_data = [{
        'type': 'heatmap',
        'z': sat_analysis['grid'],
        'colorscale': 'Viridis' if sat_mode == 'THERMAL_IR' else 'Greens' if sat_mode == 'NDVI' else 'Earth',
        'showscale': False,
        'xaxis': 'x2',
        'yaxis': 'y2'
    }]
    
    anomalies = [{
        'type': 'scatter3d',
        'x': anomaly_x,
        'y': anomaly_y,
        'z': anomaly_z,
        'mode': 'markers',
        'marker': {
            'size': 10,
            'color': '#00ffc3',
            'symbol': 'diamond',
            'line': {'color': 'white', 'width': 2},
            'opacity': 0.8
        },
        'name': 'Neural Anomaly',
        'text': ['Anambra-A1: Potential Trap', 'Anambra-A2: Seepage Proxy', 'Anambra-A3: Structural High'],
        'hoverinfo': 'text'
    }]
    
    fig_data.extend(anomalies)
    
    # Specialist Quick-Takes (Mock data for annotations)
    quick_takes = {
        'Anambra-A1': {'sentinel': 'Structural trap confirmed via 3D seismic proxy.', 'prophet': 'NPV looks promising if pipeline infra is shared.'},
        'Anambra-A2': {'sentinel': 'High spectral heterogeneity suggests active seepage.', 'prophet': 'Frontier risk is high; JV structure recommended.'},
        'Anambra-A3': {'sentinel': 'Major fault block uplift detected.', 'prophet': 'Low cost of entry; high exploration upside.'}
    }

    content = render_template_string(
        template_content, 
        plot_data=json.dumps(fig_data),
        sat_data=json.dumps(sat_data),
        basin_title=title,
        metrics=metrics,
        active_basin=basin,
        active_sat_mode=sat_mode,
        quick_takes=json.dumps(quick_takes)
    )
    return render_gaia_page("Geospatial 3D Studio", content)

@intelligence_bp.route('/api/intelligence/latest-thoughts')
def api_latest_thoughts():
    db = current_app.config['ai_db']
    strategic_thoughts = db.query_knowledge_by_tag("Strategic Opportunity", limit=5)
    return json.dumps({
        'status': 'success',
        'thoughts': [{'entity': t[0], 'description': t[2], 'confidence': t[3]} for t in strategic_thoughts]
    })

@intelligence_bp.route('/api/intelligence/thoughts-by-basin')
def api_thoughts_by_basin():
    basin = request.args.get('basin', '')
    db = current_app.config['ai_db']
    # Search for thoughts mentioning the basin
    thoughts = db.query_knowledge_by_tag(basin, limit=5)
    # Filter for Strategic Opportunity type if possible, or just return relevant ones
    return json.dumps({
        'status': 'success',
        'thoughts': [{'entity': t[0], 'description': t[2], 'confidence': t[3]} for t in thoughts if 'Strategic' in t[1] or 'Assessment' in t[2]]
    })

@intelligence_bp.route('/api/intelligence/news')
def api_news():
    news_engine = current_app.config['news_engine']
    headlines = news_engine.get_latest_headlines(limit=4)
    return json.dumps({
        'status': 'success',
        'headlines': headlines
    })
@intelligence_bp.route('/workshop/mission-control')
def mission_control():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = current_app.config['ai_db']
    facts_count = db.get_knowledge_count()
    from gaia.models.ml import ConfidenceScorer
    avg_confidence = ConfidenceScorer.calculate_confidence(
        last_trained_days=1, 
        r2_score=0.85, 
        data_density=facts_count
    )

    template_path = os.path.join(current_app.root_path, 'templates', 'mission_control.html')
    with open(template_path, 'r') as f:
        template_content = f.read()

    from .utils import render_gaia_page
    from flask import render_template_string
    content = render_template_string(
        template_content,
        confidence=int(avg_confidence * 100)
    )
    
    return render_gaia_page("Mission Control", content)

@intelligence_bp.route('/api/intelligence/generate-brief')
def generate_brief():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    from gaia.models.tools import GeologicalAuditor
    import os
    
    # We use some dynamic metrics combined with the simulated strategic advice
    analysis_data = {
        "OML 130 Target": "Deepwater Reservoir Extension",
        "Estimated Upside": "15% Volumetric Increase",
        "Geospatial Confidence": "High (Spectral Match)",
        "Economic Feasibility": "IRR > 22%",
        "Primary Risk": "Regulatory Approval Delay"
    }
    
    recommendation = (
        "Based on multi-spectral satellite analysis and the current neural consensus, "
        "GAIA recommends immediate appraisal drilling in the OML 130 extension block. "
        "The estimated internal rate of return exceeds the 20% threshold at current Brent pricing."
    )
    
    auditor = GeologicalAuditor(output_dir=os.path.join(current_app.root_path, 'static', 'reports'))
    pdf_path = auditor.generate_executive_briefing(analysis_data, recommendation)
    
    # Serve the generated PDF to the user
    from flask import send_file
    return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')
