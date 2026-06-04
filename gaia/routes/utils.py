from flask import render_template_string, session, request, current_app
import os

TEMPLATE = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GAIA — Orbital Intelligence Platform</title>
    <link rel="stylesheet" href="/static/css/index.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Space+Grotesk:wght@700&family=Roboto+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div class="neural-node-bg"></div>
    <div class="neural-pulse-overlay" id="global-loader">
        <div class="pulse-ring"></div>
    </div>

    <div class="app-shell">
        <!-- Sidebar -->
        <aside class="shell-sidebar" id="sidebar">
            <div class="sidebar-brand">
                <i class="fas fa-satellite-dish" style="color: var(--neon-teal); font-size: 1.5rem;"></i>
                <span>GAIA AI</span>
            </div>
            <nav class="sidebar-nav">
                {% if session.user_id %}
                    <div class="nav-category">GAIA.AI SYSTEM</div>
                    <a href="/dashboard" class="nav-item" id="nav-dashboard">
                        <i class="fas fa-brain" style="color: var(--neon-teal);"></i> <span>GAIA.AI Workspace</span>
                    </a>
                    
                    <div class="nav-category">GAIA WORKSHOP (LAB)</div>
                    <a href="/workshop/dashboard" class="nav-item" id="nav-intelligence">
                        <i class="fas fa-sliders-h" style="color: var(--neon-blue);"></i> <span>Control Dashboard</span>
                    </a>
                    <a href="/workshop/satellite" class="nav-item" id="nav-satellite">
                        <i class="fas fa-satellite"></i> <span>Satellite Command</span>
                    </a>
                    <a href="/workshop/geospatial" class="nav-item" id="nav-geospatial">
                        <i class="fas fa-cubes"></i> <span>Geospatial Studio</span>
                    </a>
                    <a href="/workshop/mission-control" class="nav-item" id="nav-mission">
                        <i class="fas fa-chess-king" style="color: #FFD700;"></i> <span>Mission Control</span>
                    </a>

                    <div class="nav-category">TECHNICAL SERVICES</div>
                    <a href="/analysis-hub" class="nav-item" id="nav-analysis">
                        <i class="fas fa-microscope"></i> <span>Analysis Hub</span>
                    </a>
                    <a href="/predictive-analytics" class="nav-item" id="nav-foresight">
                        <i class="fas fa-chart-area"></i> <span>Predictive Foresight</span>
                    </a>

                    <a href="#" class="nav-item oracle-trigger" onclick="toggleOracle(event)" style="border-top: 1px solid var(--glass-border); margin-top: 20px;">
                        <i class="fas fa-robot" style="color: var(--neon-teal);"></i> <span style="color: var(--neon-teal);">GAIA ORACLE</span>
                    </a>
                    
                    <div style="margin-top: auto; border-top: 1px solid var(--glass-border);">
                        <a href="/logout" class="nav-item logout-btn">
                            <i class="fas fa-power-off"></i> <span>System Offline</span>
                        </a>
                    </div>
                {% else %}
                    <a href="/login" class="nav-item">
                        <i class="fas fa-sign-in-alt"></i> <span>System Login</span>
                    </a>
                {% endif %}
            </nav>
            <div style="padding: 10px; border-top: 1px solid var(--glass-border);">
                <button onclick="toggleSidebar()" class="cyber-btn w-100" style="font-size: 0.7rem;">
                   <i class="fas fa-arrows-left-right"></i>
                </button>
            </div>
        </aside>

        <!-- Main Workspace -->
        <main id="main-content">
            <header class="shell-topbar">
                <div class="telemetry-ticker" id="telemetry-ticker">
                    SYSTEM STATUS: OPTIMAL | NEURAL LINKS ACTIVE
                </div>
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div class="glass-panel" style="padding: 5px 15px; border-color: var(--neon-blue); background: rgba(0, 212, 255, 0.1); border-radius: 4px; font-family: 'Space Grotesk'; font-size: 0.75rem;">
                        <i class="fas fa-brain" style="color: var(--neon-blue);"></i> 
                        NODES: <span id="shell-node-count" style="color: var(--text-primary); margin-left: 5px;">{{ node_count }}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-bolt" style="color: var(--warning); font-size: 0.8rem;"></i>
                        <span id="load-timer" style="font-family: 'Roboto Mono'; font-size: 0.7rem; color: var(--text-dim);">0ms</span>
                    </div>
                </div>
            </header>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div style="padding: 20px 30px 0 30px;">
                        {% for message in messages %}
                            <div class="glass-panel" style="padding: 15px; border-left: 4px solid var(--neon-blue); margin-bottom: 10px; background: rgba(0, 212, 255, 0.05);">
                                <i class="fas fa-info-circle" style="color: var(--neon-blue); margin-right: 10px;"></i>
                                {{ message }}
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            <div id="dynamic-content" class="page-transition" style="padding: 30px;">
                {{ content|safe }}
            </div>
        </main>

        <!-- Oracle AI Drawer -->
        <aside class="oracle-drawer" id="oracle">
            <div class="oracle-header">
                <div>
                    <h3 style="color: var(--neon-teal); font-family: 'Space Grotesk';">ASSET LEAD ORACLE</h3>
                    <small style="color: var(--text-dim);">INTELLIGENT ASSET COMPANION</small>
                </div>
                <i class="fas fa-times" onclick="toggleOracle()" style="cursor: pointer;"></i>
            </div>
            
            <div class="oracle-body-split">
                <!-- LEFT PANEL: Dynamic Stratigraphy Column -->
                <div class="oracle-strat-pane">
                    <div style="font-size: 0.7rem; color: var(--neon-teal); font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                        <i class="fas fa-layer-group"></i> Stratigraphy
                    </div>
                    <div style="font-size: 0.8rem; font-weight: bold; margin-bottom: 15px; font-family: 'Space Grotesk'; color: white;" id="strat-basin-name">Benin Formation</div>
                    
                    <div id="strat-svg-container" style="flex: 1; min-height: 400px; background: rgba(0,0,0,0.4); border: 1px solid var(--glass-border); border-radius: 8px; position: relative; overflow: hidden; padding: 10px; display: flex; flex-direction: column; justify-content: space-between;">
                        <!-- SVG Column -->
                        <svg id="strat-column-svg" width="100%" height="320" viewBox="0 0 200 320" style="flex: 1; max-height: 320px;">
                            <defs>
                                <!-- Sandstone texture: dotted pattern -->
                                <pattern id="pat-sandstone" width="10" height="10" patternUnits="userSpaceOnUse">
                                    <circle cx="2" cy="2" r="1.2" fill="#FFD700" opacity="0.6"/>
                                    <circle cx="6" cy="6" r="1.5" fill="#FFD700" opacity="0.8"/>
                                </pattern>
                                <!-- Shale texture: horizontal lines -->
                                <pattern id="pat-shale" width="20" height="10" patternUnits="userSpaceOnUse">
                                    <line x1="0" y1="5" x2="20" y2="5" stroke="#00d4ff" stroke-width="1" opacity="0.5"/>
                                </pattern>
                                <!-- Limestone texture: brick pattern -->
                                <pattern id="pat-limestone" width="20" height="20" patternUnits="userSpaceOnUse">
                                    <rect width="20" height="20" fill="none" stroke="#2eec73" stroke-width="0.5" opacity="0.2"/>
                                    <line x1="0" y1="10" x2="20" y2="10" stroke="#2eec73" stroke-width="0.8" opacity="0.4"/>
                                    <line x1="10" y1="0" x2="10" y2="10" stroke="#2eec73" stroke-width="0.8" opacity="0.4"/>
                                </pattern>
                            </defs>
                            
                            <!-- Geological Columns -->
                            <g id="strat-layers">
                                <!-- Benin Formation (0 - 100) -->
                                <rect id="layer-benin" x="20" y="10" width="110" height="80" fill="url(#pat-sandstone)" stroke="rgba(255,255,255,0.1)"/>
                                <text x="140" y="55" fill="#8b949e" font-size="9" font-family="monospace">Benin</text>
                                
                                <!-- Agbada Formation (100 - 200) -->
                                <rect id="layer-agbada" x="20" y="90" width="110" height="110" fill="url(#pat-limestone)" stroke="rgba(255,255,255,0.1)"/>
                                <text x="140" y="150" fill="#8b949e" font-size="9" font-family="monospace">Agbada</text>
                                
                                <!-- Akata Formation (200 - 300) -->
                                <rect id="layer-akata" x="20" y="200" width="110" height="100" fill="url(#pat-shale)" stroke="rgba(255,255,255,0.1)"/>
                                <text x="140" y="255" fill="#8b949e" font-size="9" font-family="monospace">Akata</text>
                            </g>
                            
                            <!-- Glowing Depth Laser Pointer -->
                            <g id="strat-laser-pointer" style="transition: transform 0.8s cubic-bezier(0.19, 1, 0.22, 1); transform: translateY(0px);">
                                <line x1="5" y1="10" x2="195" y2="10" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="2,2"/>
                                <polygon points="5,5 12,10 5,15" fill="#ef4444"/>
                                <circle cx="5" cy="10" r="3" fill="#ef4444" opacity="0.8"/>
                            </g>
                        </svg>
                        
                        <!-- Dynamic overlay details -->
                        <div style="background: rgba(0,0,0,0.5); padding: 10px; border-radius: 6px; border: 1px solid var(--glass-border); font-family: 'Roboto Mono', monospace; font-size: 0.65rem;">
                            <div style="margin-bottom: 4px; display: flex; justify-content: space-between;"><span>TARGET DEPTH:</span> <span style="color:#ef4444; font-weight: bold;" id="strat-depth-val">1,500 ft</span></div>
                            <div style="display: flex; justify-content: space-between;"><span>LITHOLOGY:</span> <span style="color:var(--neon-teal); font-weight: bold;" id="strat-lithology-val">Consolidated Sands</span></div>
                        </div>
                    </div>
                </div>
                
                <!-- RIGHT PANEL: Existing Oracle Chat UI -->
                <div class="oracle-chat-pane">
                    <div class="oracle-messages" id="chat-box" style="line-height: 1.6;">
                        <div class="msg msg-ai">Oracle initialized. I am your Integrated Asset Lead. Ask me about **Agbada**, **Akata**, **Benin** formations, or request a basin risk assessment.</div>
                    </div>
                    <div class="oracle-input">
                        <div style="display: flex; gap: 10px;">
                            <input type="text" id="user-input" class="cyber-input" placeholder="Query Asset Lead..." onkeypress="if(event.key==='Enter') sendQuery()">
                            <button class="cyber-btn" onclick="sendQuery()"><i class="fas fa-paper-plane"></i></button>
                        </div>
                    </div>
                </div>
            </div>
        </aside>
        
        <!-- Command Palette Modal -->
        <div id="command-palette" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 5000; background: rgba(8, 10, 15, 0.9); backdrop-filter: blur(10px); justify-content: center; align-items: flex-start; padding-top: 15vh;">
            <div class="glass-panel" style="width: 600px; padding: 0; overflow: hidden; border-color: var(--neon-blue); box-shadow: 0 0 50px rgba(0, 212, 255, 0.2);">
                <div style="padding: 20px; border-bottom: 1px solid var(--glass-border); display: flex; align-items: center; gap: 15px;">
                    <i class="fas fa-search" style="color: var(--neon-blue); font-size: 1.2rem;"></i>
                    <input type="text" id="command-input" placeholder="Search knowledge base or jump to module (Cmd+K)..." style="background: transparent; border: none; color: white; width: 100%; outline: none; font-family: 'Space Grotesk'; font-size: 1.1rem;">
                    <span class="cyber-badge" style="font-size: 0.6rem;">ESC TO CLOSE</span>
                </div>
                <div id="command-results" style="max-height: 400px; overflow-y: auto; padding: 10px;">
                    <!-- Results injected here -->
                    <div style="padding: 15px; color: var(--text-dim); font-size: 0.8rem; text-align: center;">Type to begin neural lookup...</div>
                </div>
            </div>
        </div>
    </div>

    <audio id="beep-nav" src="https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3"></audio>

    <script>
        // Update Page Indicator
        function updateActiveNav() {
            const path = window.location.pathname;
            document.querySelectorAll('.nav-item').forEach(item => {
                const href = item.getAttribute('href');
                if (href && path.startsWith(href) && href !== '/') {
                    item.classList.add('active');
                } else if (path === '/' && href === '/dashboard') {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }
        updateActiveNav();

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('collapsed');
            playSfx();
        }

        function toggleOracle(e) {
            if(e) e.preventDefault();
            document.getElementById('oracle').classList.toggle('open');
            playSfx();
        }

        function playSfx() {
            const audio = document.getElementById('beep-nav');
            audio.volume = 0.1;
            audio.play().catch(() => {});
        }

        function navigate(e, url) {
            // Deprecated SPA navigate, using hard reload for stability
            window.location.href = url;
        }

        async function sendQuery() {
            const input = document.getElementById('user-input');
            const box = document.getElementById('chat-box');
            if(!input.value.trim()) return;

            const userMsg = input.value;
            input.value = '';
            box.innerHTML += `<div class="msg msg-user">${userMsg}</div>`;
            
            // Multi-stage Thinking Simulation
            const thinkingId = 'thinking-' + Date.now();
            box.innerHTML += `<div class="msg msg-ai" id="${thinkingId}"><i class="fas fa-microchip fa-spin"></i> Initializing domain audit...</div>`;
            box.scrollTop = box.scrollHeight;
            playSfx();

            const taskSteps = [
                "Consulting technical taxonomy...",
                "Synthesizing reservoir physics...",
                "Auditing active mission database...",
                "Finalizing lead-level assessment..."
            ];
            
            var step = 0;
            const stepInterval = setInterval(() => {
                if(step < taskSteps.length) {
                    document.getElementById(thinkingId).innerHTML = `<i class="fas fa-brain fa-pulse"></i> ${taskSteps[step]}`;
                    step++;
                } else {
                    clearInterval(stepInterval);
                }
            }, 800);

            const aiRes = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: userMsg})
            }).then(r => r.json());

            clearInterval(stepInterval);
            const thinkingEl = document.getElementById(thinkingId);
            thinkingEl.innerHTML = '';
            
            // Professional Formatting Typing
            var i = 0;
            const rawText = aiRes.response || "Neural link unstable. Please re-submit query.";
            // Basic Markdown handler for bolding
            const text = rawText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            function typeWriter() {
                if (i < text.length) {
                    if (text.substr(i, 8) === '<strong>') {
                        const end = text.indexOf('</strong>', i) + 9;
                        thinkingEl.innerHTML += text.substring(i, end);
                        i = end;
                    } else {
                        thinkingEl.innerHTML += text.charAt(i);
                        i++;
                    }
                    box.scrollTop = box.scrollHeight;
                    setTimeout(typeWriter, 12);
                }
            }
            typeWriter();

            // Dynamic Stratigraphy Laser Pointer Updates
            const queryLower = (userMsg + " " + rawText).toLowerCase();
            let targetY = 30; // default Benin
            let targetName = "Benin Formation";
            let depthText = "1,500 ft";
            let lithology = "Consolidated Sands";
            
            if (queryLower.includes("agbada") || queryLower.includes("reservoir") || queryLower.includes("oil")) {
                targetY = 135; 
                targetName = "Agbada Formation";
                depthText = "8,450 ft";
                lithology = "Interbedded Sands & Shales";
            } else if (queryLower.includes("akata") || queryLower.includes("shale") || queryLower.includes("source")) {
                targetY = 240; 
                targetName = "Akata Formation";
                depthText = "14,800 ft";
                lithology = "Deep Marine Shales";
            } else if (queryLower.includes("mamu") || queryLower.includes("coal") || queryLower.includes("silt") || queryLower.includes("anambra")) {
                targetY = 175;
                targetName = "Mamu Formation";
                depthText = "7,200 ft";
                lithology = "Siltstone & Coal Seams";
            }
            
            const pointer = document.getElementById('strat-laser-pointer');
            const stratDepth = document.getElementById('strat-depth-val');
            const stratLithology = document.getElementById('strat-lithology-val');
            const basinHeader = document.getElementById('strat-basin-name');
            
            if (pointer) {
                pointer.style.transform = `translateY(${targetY}px)`;
            }
            if (stratDepth) stratDepth.innerText = depthText;
            if (stratLithology) stratLithology.innerText = lithology;
            if (basinHeader) basinHeader.innerText = targetName;
        }

        setInterval(() => {
            const ticker = document.getElementById('telemetry-ticker');
            const statuses = ["SYSTEM STATUS: OPTIMAL", "NEURAL LINKS ACTIVE", "SCANNING FOR DEEPWATER ANOMALIES...", "ORACLE ONLINE"];
            ticker.innerText = statuses[Math.floor(Math.random() * statuses.length)];
            
            // Sync Node Count from Status API
            fetch('/api/intelligence/growth-status')
                .then(r => r.json())
                .then(data => {
                    // This is a placeholder since the growth-status doesn't return total count yet
                    // But we could add it to the status API
                });
        }, 10000);

        function updateGlobalNodes() {
            fetch('/api/chat/status').then(r => r.json()).then(data => {
                if(data.node_count) {
                    document.getElementById('shell-node-count').innerText = data.node_count;
                }
            }).catch(() => {});
        }
        setInterval(updateGlobalNodes, 30000);
        updateGlobalNodes();

        // FAIL-SAFE: Ensure loader is hidden once DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            var loader = document.getElementById('global-loader');
            if(loader) {
                setTimeout(function() {
                    loader.style.display = 'none';
                }, 200);
            }
        });
        
        // Secondary fail-safe for Safari cache transitions
        window.onload = function() {
            var loader = document.getElementById('global-loader');
            if(loader) loader.style.display = 'none';
        };
        // Command Palette Logic
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                toggleCommandPalette();
            }
            if (e.key === 'Escape') {
                closeCommandPalette();
            }
        });

        function toggleCommandPalette() {
            const palette = document.getElementById('command-palette');
            palette.style.display = palette.style.display === 'flex' ? 'none' : 'flex';
            if (palette.style.display === 'flex') {
                document.getElementById('command-input').focus();
            }
        }

        function closeCommandPalette() {
            document.getElementById('command-palette').style.display = 'none';
        }

        const commandInput = document.getElementById('command-input');
        commandInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length < 3) return;
            
            fetch(`/api/intelligence/reason`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: "Summary of: " + query })
            })
            .then(r => r.json())
            .then(data => {
                const results = document.getElementById('command-results');
                results.innerHTML = `
                    <div style="padding: 15px; border-bottom: 1px solid var(--glass-border);">
                        <div style="font-size: 0.6rem; color: var(--neon-blue); margin-bottom: 5px;">NEURAL LOOKUP RESULT</div>
                        <div style="font-size: 0.85rem; line-height: 1.4;">${data.response}</div>
                    </div>
                    <div style="padding: 10px; font-size: 0.7rem; color: var(--text-dim);">Navigate to:</div>
                    <div class="nav-item" onclick="location.href='/workshop/dashboard'" style="padding: 10px; cursor: pointer;"><i class="fas fa-brain"></i> Neural Thought Stream</div>
                    <div class="nav-item" onclick="location.href='/workshop/geospatial'" style="padding: 10px; cursor: pointer;"><i class="fas fa-cubes"></i> Geospatial Studio</div>
                `;
            });
        });
    </script>
</body>
</html>
'''

def render_gaia_page(title, content):
    """Wrapper to render a page within the redesigned SPA shell."""
    if request.args.get('partial') == 'true':
        return content
    
    db = current_app.config['ai_db']
    node_count = db.get_knowledge_count()
    return render_template_string(TEMPLATE, title=title, content=content, node_count=node_count)
