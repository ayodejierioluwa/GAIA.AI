from flask import Blueprint, redirect, url_for, session
from .utils import render_gaia_page

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Standalone Developer Auto-Login
    session['user_id'] = 1
    session['username'] = 'Operator'
    return redirect(url_for('analysis.dashboard'))
