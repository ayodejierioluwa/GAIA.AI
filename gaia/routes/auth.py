from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
import hashlib
from .utils import render_gaia_page

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/sso-verify', methods=['POST'])
def sso_verify():
    from flask import current_app
    ai_db = current_app.config['ai_db']
    
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 400
        
    user_id = ai_db.verify_user(username, password)
    if user_id:
        token = hashlib.sha256(f"{username}:{current_app.config['SECRET_KEY']}".encode()).hexdigest()
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user_id,
                "username": username
            }
        })
    return jsonify({"success": False, "message": "Invalid username or password"}), 401

@auth_bp.route('/api/auth/sso-login', methods=['POST'])
def sso_login():
    from flask import current_app
    ai_db = current_app.config['ai_db']
    
    data = request.get_json() or {}
    username = data.get('username')
    token = data.get('token')
    
    if not username or not token:
        return jsonify({"success": False, "message": "Missing authentication parameters"}), 400
        
    expected_token = hashlib.sha256(f"{username}:{current_app.config['SECRET_KEY']}".encode()).hexdigest()
    if token != expected_token:
        return jsonify({"success": False, "message": "Invalid session token"}), 403
        
    user_id = 1
    try:
        conn = ai_db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            user_id = row[0]
        conn.close()
    except Exception:
        pass
        
    session['user_id'] = user_id
    session['username'] = username
    return jsonify({"success": True})

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from flask import current_app
    ai_db = current_app.config['ai_db']
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if ai_db.create_user(username, email, password):
            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))
        else:
            flash('Username or email already exists')
    
    content = '''
    <div style="max-width: 500px; margin: 40px auto;">
        <div class="glass-panel" style="padding: 40px;">
            <h2 style="font-family: 'Space Grotesk', sans-serif; color: var(--neon-teal); margin-bottom: 10px;"><i class="fas fa-user-plus"></i> Initialize Node</h2>
            <p style="color: var(--text-dim); margin-bottom: 30px; font-size: 0.9rem;">Register your access credentials for the GAIA orbital network.</p>
            
            <form method="post" style="display: flex; flex-direction: column; gap: 20px;">
                <div>
                    <label style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; display: block;">Username</label>
                    <input type="text" name="username" class="cyber-input" placeholder="Operator Designation" required style="width: 100%;">
                </div>
                <div>
                    <label style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; display: block;">Email</label>
                    <input type="email" name="email" class="cyber-input" placeholder="Secure Comm Channel" required style="width: 100%;">
                </div>
                <div>
                    <label style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; display: block;">Password</label>
                    <input type="password" name="password" class="cyber-input" placeholder="Encryption Key" required style="width: 100%;">
                </div>
                <div style="margin-top: 10px;">
                    <button type="submit" class="cyber-btn" style="width: 100%;"><i class="fas fa-satellite-dish"></i> Register Node</button>
                </div>
            </form>
            <div style="margin-top: 20px; text-align: center;">
                <a href="/login" onclick="window.location.href='/login'; return false;" style="color: var(--neon-blue); text-decoration: none; font-size: 0.9rem;">Login instead</a>
            </div>
        </div>
    </div>
    '''
    return render_gaia_page("Register", content)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from flask import current_app
    ai_db = current_app.config['ai_db']
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = ai_db.verify_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            flash('Login successful! Welcome back.')
            return redirect(url_for('analysis.dashboard'))
        else:
            flash('Invalid username or password')
            
    content = '''
    <div style="max-width: 500px; margin: 40px auto;">
        <div class="glass-panel" style="padding: 40px; border-color: var(--neon-blue); box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);">
            <h2 style="font-family: 'Space Grotesk', sans-serif; color: var(--neon-blue); margin-bottom: 10px;"><i class="fas fa-fingerprint"></i> System Login</h2>
            <p style="color: var(--text-dim); margin-bottom: 30px; font-size: 0.9rem;">Authenticate to access the orbital intelligence grid.</p>
            
            <form method="post" style="display: flex; flex-direction: column; gap: 20px;">
                <div>
                    <label style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; display: block;">Username</label>
                    <input type="text" name="username" class="cyber-input" placeholder="Operator Designation" required style="width: 100%;">
                </div>
                <div>
                    <label style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; display: block;">Password</label>
                    <input type="password" name="password" class="cyber-input" placeholder="Encryption Key" required style="width: 100%;">
                </div>
                <div style="margin-top: 10px;">
                    <button type="submit" class="cyber-btn" style="width: 100%;"><i class="fas fa-lock-open"></i> Authenticate</button>
                </div>
            </form>
            <div style="margin-top: 20px; text-align: center;">
                <a href="/register" onclick="window.location.href='/register'; return false;" style="color: var(--neon-teal); text-decoration: none; font-size: 0.9rem;">Request Access</a>
            </div>
        </div>
    </div>
    
    <script>
        (function() {
            if (window.self !== window.top) {
                console.log("GAIA SSO: Embedded context detected, sending session request...");
                window.parent.postMessage({ type: "REQUEST_SSO_SESSION" }, "*");
                
                var overlay = document.createElement('div');
                overlay.style.position = 'fixed';
                overlay.style.inset = '0';
                overlay.style.background = '#050507';
                overlay.style.display = 'flex';
                overlay.style.flexDirection = 'column';
                overlay.style.alignItems = 'center';
                overlay.style.justifyContent = 'center';
                overlay.style.zIndex = '99999';
                overlay.innerHTML = '<div style="width: 40px; height: 40px; border: 3px solid rgba(0, 212, 255, 0.2); border-top-color: #00d4ff; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem;"></div><div style="color: #94a3b8; font-family: monospace; font-size: 11px; letter-spacing: 2px;">SYNCHRONIZING SECURE NODE IDENTITY...</div><style>@keyframes spin { to { transform: rotate(360deg); } }</style>';
                document.body.appendChild(overlay);
                
                window.addEventListener('message', async function(event) {
                    if (event.data.type === 'SSO_SESSION_RESPONSE') {
                        if (event.data.session) {
                            console.log("GAIA SSO: Handshake verified. Authenticating with local backend...");
                            try {
                                const response = await fetch('/api/auth/sso-login', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                        username: event.data.session.username,
                                        token: event.data.session.token
                                    })
                                });
                                const result = await response.json();
                                if (result.success) {
                                    console.log("GAIA SSO: Authenticated successfully! Redirecting...");
                                    window.location.href = '/dashboard';
                                    return;
                                }
                            } catch (err) {
                                console.error("GAIA SSO: Failed backend sync", err);
                            }
                        }
                        console.log("GAIA SSO: No active session. Rendering login form.");
                        document.body.removeChild(overlay);
                    }
                });
            }
        })();
    </script>
    '''
    return render_gaia_page("Login", content)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully')
    return redirect(url_for('main.index'))
