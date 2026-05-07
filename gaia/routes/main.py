from flask import Blueprint, redirect, url_for, session
from .utils import render_gaia_page

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('analysis.dashboard'))
    content = '''
    <div style="text-align: center; max-width: 900px; margin: 80px auto;" class="page-transition">
        <i class="fas fa-satellite-dish" style="font-size: 5rem; color: var(--neon-teal); margin-bottom: 30px; filter: drop-shadow(0 0 20px var(--neon-teal));"></i>
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 3.5rem; letter-spacing: -2px; margin-bottom: 20px;">GAIA <span style="color: var(--neon-teal);">ORBITAL</span></h1>
        <p style="font-size: 1.2rem; color: var(--text-dim); margin-bottom: 50px;">Autonomous Petroleum Intelligence & 4D Subsurface Exploration for Nigerian Basins.</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 60px;">
            <div class="glass-panel" style="padding: 20px;">
                <i class="fas fa-brain" style="color: var(--neon-teal); margin-bottom: 10px;"></i>
                <h4 style="font-size: 0.9rem;">Adaptive ML</h4>
            </div>
            <div class="glass-panel" style="padding: 20px;">
                <i class="fas fa-globe-africa" style="color: var(--neon-blue); margin-bottom: 10px;"></i>
                <h4 style="font-size: 0.9rem;">Subsurface 4D</h4>
            </div>
            <div class="glass-panel" style="padding: 20px;">
                <i class="fas fa-satellite" style="color: var(--warning); margin-bottom: 10px;"></i>
                <h4 style="font-size: 0.9rem;">OSINT Spectral</h4>
            </div>
        </div>
        
        <div style="display: flex; gap: 20px; justify-content: center;">
            <a href="/register" class="cyber-btn" style="padding: 15px 40px; font-size: 1.1rem; text-decoration: none;">Initialize System</a>
            <a href="/login" class="nav-item" style="color: var(--text-dim); text-decoration: none; display: flex; align-items: center; gap: 8px;">
                <i class="fas fa-key"></i> System Access
            </a>
        </div>
    </div>
    '''
    return render_gaia_page("Terminal entry", content)
