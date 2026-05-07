from flask import Blueprint, request, redirect, url_for, flash, session, current_app
import numpy as np
from datetime import datetime
from .utils import render_gaia_page

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = f'''
    <div class="page-transition">
        <div style="margin-bottom: 40px;">
            <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; margin-bottom: 5px;">Welcome back, <span style="color: var(--neon-teal);">{session.get('username', 'User')}</span></h1>
            <p style="color: var(--text-dim); letter-spacing: 1px;">ORBITAL STATUS: <span style="color: var(--neon-teal);">ONLINE</span> | SUBSURFACE SYNC: ACTIVE</p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            <div class="glass-panel" style="display: flex; flex-direction: column; gap: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <i class="fas fa-chart-pie" style="color: var(--neon-teal); font-size: 1.5rem;"></i>
                    <span style="font-size: 0.7rem; color: var(--text-dim);">HUB-01</span>
                </div>
                <h3>Analysis Hub</h3>
                <p style="font-size: 0.85rem; color: var(--text-dim);">Process well tests, review records, and sync field telemetry.</p>
                <button onclick="navigate(event, '/analysis-hub')" class="cyber-btn" style="margin-top: auto;">Open Terminal</button>
            </div>
            
            <div class="glass-panel" style="display: flex; flex-direction: column; gap: 15px;">
                 <div style="display: flex; justify-content: space-between; align-items: center;">
                    <i class="fas fa-satellite" style="color: var(--neon-blue); font-size: 1.5rem;"></i>
                    <span style="font-size: 0.7rem; color: var(--text-dim);">ORBIT-04</span>
                </div>
                <h3>Geological Studio</h3>
                <p style="font-size: 0.85rem; color: var(--text-dim);">Interactive 4D visualization and basin-wide exploration tools.</p>
                <button onclick="navigate(event, '/exploration-tools')" class="cyber-btn" style="margin-top: auto;">Engage Engine</button>
            </div>

            <div class="glass-panel" style="display: flex; flex-direction: column; gap: 15px;">
                 <div style="display: flex; justify-content: space-between; align-items: center;">
                    <i class="fas fa-brain" style="color: var(--warning); font-size: 1.5rem;"></i>
                    <span style="font-size: 0.7rem; color: var(--text-dim);">NEURAL-08</span>
                </div>
                <h3>Intelligence suite</h3>
                <p style="font-size: 0.85rem; color: var(--text-dim);">AI predictions, autonomous growth cycle, and orbital OSINT.</p>
                <button onclick="navigate(event, '/intelligence-dashboard')" class="cyber-btn" style="margin-top: auto;">Access Core</button>
            </div>
        </div>

        <div class="glass-panel" style="margin-top: 30px; background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 255, 195, 0.1) 100%); border-color: var(--neon-blue);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="color: var(--neon-blue); margin-bottom: 8px;">🚀 Advanced 4D Subsurface Visualizer</h2>
                    <p style="color: var(--text-primary);">New high-fidelity voxel rendering and temporal comparison now live.</p>
                </div>
                <button onclick="navigate(event, '/visualization')" class="cyber-btn" style="background: var(--neon-blue); color: black;">Launch Studio</button>
            </div>
        </div>
    </div>
    '''
    return render_gaia_page("Dashboard", content)

@analysis_bp.route('/analysis-hub')
def analysis_hub():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    ai_db = current_app.config['ai_db']
    analyses = ai_db.get_user_analyses(session['user_id'])
    latest = analyses[0] if analyses else None
    
    # Latest Audit Summary for the 3rd panel
    econ_summary = "Awaiting first analysis..."
    if latest:
        import json
        report_text = latest[9]
        if "||ECON_AUDIT||" in report_text:
            feasibility = json.loads(report_text.split("||ECON_AUDIT||")[1])
            econ_summary = f'''
            <div style="font-size: 1.5rem; color: #FFD700; font-family: 'Space Grotesk';">${feasibility['financials']['total_capex']:,.0f}</div>
            <div style="font-size: 0.7rem; color: var(--text-dim);">LATEST WELL: {latest[2]}</div>
            <div style="margin-top: 10px; font-size: 0.65rem; color: var(--neon-teal);">ROI: {feasibility['metrics']['roi']}% • PAYBACK: {feasibility['metrics']['payback_months']} MO</div>
            '''

    latest_id = latest[0] if latest else 0
    audit_url = url_for('analysis.economics_audit', analysis_id=latest_id) if latest else '#'

    content = f'''
    <div class="page-transition">
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px;">
            <div>
                <h2 style="font-family: 'Space Grotesk', sans-serif; color: var(--neon-teal); margin-bottom: 5px;">📊 Analysis Hub</h2>
                <p style="color: var(--text-dim);">ASSET LEAD COMMAND & CONTROL DASHBOARD</p>
            </div>
            <div style="font-family: 'Roboto Mono'; font-size: 0.7rem; color: var(--text-dim); background: rgba(255, 215, 0, 0.05); padding: 5px 15px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.2);">
                <i class="fas fa-coins" style="color: #FFD700;"></i> FINANCIAL SYNC: ACTIVE
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0;">
            <!-- Panel 1: Ingestion -->
            <div class="glass-panel" style="padding: 25px; border-color: var(--neon-teal); background: rgba(0, 255, 195, 0.02); display: flex; flex-direction: column;">
                <i class="fas fa-file-upload" style="font-size: 1.5rem; color: var(--neon-teal); margin-bottom: 15px;"></i>
                <h3 style="font-size: 1.1rem; margin-bottom: 10px;">📤 Data Ingestion</h3>
                <p style="color: var(--text-dim); font-size: 0.8rem; margin-bottom: 20px;">Upload test data, reports, or seismic logs.</p>
                <button onclick="navigate(event, '/upload')" class="cyber-btn" style="width: 100%; margin-top: auto;">Initialize Ingestion</button>
            </div>
            
            <!-- Panel 2: Economics Hub (THE NEW FRONT-AND-CENTER SECTION) -->
            <div class="glass-panel" style="padding: 25px; border-color: #FFD700; background: rgba(255, 215, 0, 0.02); display: flex; flex-direction: column;">
                <i class="fas fa-vault" style="font-size: 1.5rem; color: #FFD700; margin-bottom: 15px;"></i>
                <h3 style="font-size: 1.1rem; margin-bottom: 10px;">💰 Asset Economics Hub</h3>
                <div style="margin-bottom: 20px;">
                    {econ_summary}
                </div>
                <button onclick="navigate(event, '{audit_url}')" class="cyber-btn" style="width: 100%; border-color: #FFD700; color: #FFD700; margin-top: auto;">View Full Audit</button>
            </div>

            <!-- Panel 3: Mission History -->
            <div class="glass-panel" style="padding: 25px; display: flex; flex-direction: column;">
                <i class="fas fa-history" style="font-size: 1.5rem; color: var(--neon-blue); margin-bottom: 15px;"></i>
                <h3 style="font-size: 1.1rem; margin-bottom: 10px;">📜 Mission History</h3>
                <p style="color: var(--text-dim); font-size: 0.8rem; margin-bottom: 20px;">Review previous analytical cycles and neural extraction results.</p>
                <button onclick="navigate(event, '/history')" class="cyber-btn" style="width: 100%; margin-top: auto;">Access Records</button>
            </div>
        </div>
    </div>
    '''
    return render_gaia_page("Analysis Hub", content)

@analysis_bp.route('/technical-report/<int:analysis_id>')
def technical_report(analysis_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    ai_db = current_app.config['ai_db']
    analysis = ai_db.get_analysis_by_id(analysis_id, session['user_id'])
    
    if not analysis:
        return "Extraction record not found.", 404

    from .utils import render_gaia_page
    from flask import render_template_string
    import os
    
    template_path = os.path.join(current_app.root_path, 'templates', 'technical_report.html')
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    content = render_template_string(
        template_content,
        analysis=analysis
    )
    
    return render_gaia_page("Technical Extraction Report", content)

@analysis_bp.route('/economics-audit/<int:analysis_id>')
def economics_audit(analysis_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    ai_db = current_app.config['ai_db']
    analysis = ai_db.get_analysis_by_id(analysis_id, session['user_id'])
    
    if not analysis:
        return "Audit signature not found.", 404

    # Extract JSON audit from report_text (Index 9)
    import json
    report_text = analysis[9]
    try:
        if "||ECON_AUDIT||" in report_text:
            audit_json = report_text.split("||ECON_AUDIT||")[1]
            feasibility = json.loads(audit_json)
        else:
            # Fallback for old records
            economics = current_app.config['economics_engine']
            feasibility = economics.assess_well_feasibility(
                initial_rate=analysis[3], # flow_rate
                depth=analysis[10] if len(analysis) > 10 else 3000,
                formation="Agbada"
            )
    except Exception as e:
        return f"Economic Synthesis Error: {str(e)}", 500

    from .utils import render_gaia_page
    from flask import render_template_string
    import os
    
    template_path = os.path.join(current_app.root_path, 'templates', 'economics_audit.html')
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    content = render_template_string(
        template_content,
        audit=feasibility['audit'],
        feasibility=feasibility
    )
    
    return render_gaia_page("Asset Lead: Economic Audit", content)

@analysis_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    ai_db = current_app.config['ai_db']
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        # --- TECHNICAL INGESTION & ECONOMIC AUDIT ---
        from gaia.models.ingestion_utils import WellDataParser, TechnicalDiagnosticEngine
        import json
        
        file_content = file.read()
        well_data = WellDataParser.parse_file(file_content, file.filename)
        
        # 1. Engineering Metrics
        pressure_drop = well_data['initial_pressure'] - well_data['final_pressure']
        well_data['productivity_index'] = well_data['flow_rate'] / pressure_drop if pressure_drop > 0 else 0
        well_data['skin_factor'] = round(4.5 + (np.random.normal(0, 1.5)), 2)
        
        # 2. AI Diagnostics
        diagnostic = TechnicalDiagnosticEngine.analyze(well_data)
        
        # 3. Formation-Aware Economics
        economics = current_app.config['economics_engine']
        formation = well_data.get('formation', 'Agbada') 
        env_type = 'Offshore' if well_data['depth'] > 3500 else 'Onshore'
        
        feasibility = economics.assess_well_feasibility(
            initial_rate=well_data['flow_rate'],
            depth=well_data['depth'],
            formation=formation,
            env_type=env_type
        )
        
        audit_tag = f"||ECON_AUDIT||{json.dumps(feasibility)}"
        report_text = f"TECHNICAL AUDIT REPORT\nWell: {well_data['well_name']}\nPI: {well_data['productivity_index']:.4f}\n{audit_tag}"
        
        try:
            analysis_id = ai_db.save_analysis(
                session['user_id'], 
                well_data, 
                report_text, 
                well_data['productivity_index'], 
                well_data['skin_factor'],
                diagnostic=diagnostic
            )
            flash('High-Fidelity Ingestion & Extraction Complete.')
            return redirect(url_for('analysis.technical_report', analysis_id=analysis_id))
        except Exception as e:
            flash(f'Ingestion Error: {str(e)}')
            return redirect(url_for('analysis.history'))
    
    content = '''
    <div class="glass-panel page-transition" style="max-width: 600px; margin: 40px auto; text-align: center;">
        <h3 style="color: var(--neon-teal); margin-bottom: 10px;">📤 Portal: Data Ingestion</h3>
        <p style="color: var(--text-dim); margin-bottom: 30px;">Accepts CSV, TXT, PDF, or DOCX formats.</p>
        
        <form method="post" enctype="multipart/form-data">
            <div style="margin: 20px 0; padding: 50px; border: 2px dashed rgba(0, 255, 195, 0.2); border-radius: 12px; background: rgba(0,0,0,0.2);">
                <input type="file" name="file" accept=".csv,.txt,.pdf,.docx" style="color: var(--text-dim);" required>
            </div>
            <button type="submit" class="cyber-btn" style="width: 100%; padding: 15px;">Analyze & Ingest</button>
        </form>
    </div>
    '''
    return render_gaia_page("Data Ingestion", content)

@analysis_bp.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    ai_db = current_app.config['ai_db']
    analyses = ai_db.get_user_analyses(session['user_id'])
    
    table_rows = ""
    for analysis in analyses:
        # analysis indices: 3:well_name, 4:flow, 5:init_p, 6:final_p, 7:pi, 8:skin, 10:depth, 11:api, 13:wc, 15:diagnostic
        # Note: Analysis indices change based on the updated schema
        well_name = analysis[2]
        flow = analysis[3]
        pi = analysis[6]
        skin = analysis[7]
        date = analysis[8]
        depth = analysis[10]
        api = analysis[11]
        diagnostic = analysis[15] or "No issues detected"
        
        table_rows += f'''
        <tr style="border-bottom: 1px solid var(--glass-border);">
            <td style="padding: 15px; color: var(--neon-teal); font-weight: bold;">{well_name}</td>
            <td style="padding: 15px;">{depth} m</td>
            <td style="padding: 15px;">{api} API</td>
            <td style="padding: 15px; font-family: 'Roboto Mono'; color: var(--neon-blue);">{pi:.4f}</td>
            <td style="padding: 15px;">{skin}</td>
            <td style="padding: 15px;"><span style="font-size: 0.7rem; background: rgba(0,255,195,0.1); padding: 4px 8px; border-radius: 4px; color: var(--neon-teal); border: 1px solid rgba(0,255,195,0.2);">{diagnostic}</span></td>
            <td style="padding: 15px; color: var(--text-dim); font-size: 0.8rem;">{date}</td>
            <td style="padding: 15px; display: flex; gap: 8px;">
                <a href="/technical-report/{analysis[0]}" class="cyber-btn" style="padding: 5px 10px; text-decoration: none; font-size: 0.7rem; border-color: var(--neon-teal); color: var(--neon-teal);">VIEW</a>
                <a href="/economics-audit/{analysis[0]}" class="cyber-btn" style="padding: 5px 10px; text-decoration: none; font-size: 0.7rem; border-color: #FFD700; color: #FFD700;">AUDIT</a>
            </td>
        </tr>
        '''
    
    content = f'''
    <div class="glass-panel page-transition">
        <div style="margin-bottom: 25px;">
            <h3 style="color: var(--neon-blue);">📜 System Extraction History</h3>
            <p style="color: var(--text-dim);">Historical analysis results stored in neural memory.</p>
        </div>
        
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead style="background: rgba(255,255,255,0.03); color: var(--text-dim); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px;">
                    <tr>
                        <th style="padding: 15px; border-bottom: 1px solid var(--neon-blue);">Well Name</th>
                        <th style="padding: 15px; border-bottom: 1px solid var(--neon-blue);">Depth</th>
                        <th style="padding: 15px; border-bottom: 1px solid var(--neon-blue);">API</th>
                        <th style="padding: 15px; border-bottom: 1px solid var(--neon-blue);">PI</th>
                        <th style="padding: 15px; border-bottom: 1px solid var(--neon-blue);">Skin</th>
                        <th style="padding: 15px; border-bottom: 1px solid var(--neon-blue);">AI Diagnostic</th>
                        <th style="padding: 15px; border-bottom: 1px solid var(--neon-blue);">Date</th>
                        <th style="padding: 15px; border-bottom: 1px solid var(--neon-blue);">Actions</th>
                    </tr>
                </thead>
                <tbody style="font-size: 0.9rem;">
                    {table_rows or '<tr><td colspan="8" style="padding: 50px; text-align: center; color: var(--text-dim);">No analytical logs found.</td></tr>'}
                </tbody>
            </table>
    </div>
    '''
    return render_gaia_page("Mission History", content)

@analysis_bp.route('/predictive-analytics')
def predictive_analytics():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from flask import render_template_string
    import os
    
    template_path = os.path.join(current_app.root_path, 'templates', 'predictive_analytics.html')
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    return render_gaia_page("Reservoir Foresight", render_template_string(template_content))

@analysis_bp.route('/api/ml/predict-discovery')
def api_ml_predict_discovery():
    lat = float(request.args.get('lat', 4.9))
    lon = float(request.args.get('lon', 6.5))
    depth = float(request.args.get('depth', 3000))
    formation = request.args.get('formation', 'Agbada')
    
    discovery_model = current_app.config['discovery_model']
    prediction = discovery_model.predict_discovery_probability(lat, lon, depth, formation)
    
    import json
    return json.dumps(prediction)
