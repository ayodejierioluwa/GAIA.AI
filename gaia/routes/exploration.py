from flask import Blueprint, request, redirect, url_for, session, current_app, json
from .utils import render_gaia_page
import numpy as np

exploration_bp = Blueprint('exploration', __name__)

@exploration_bp.route('/exploration-tools')
def exploration_tools():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = '''
    <div class="glass-panel page-transition">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid var(--glass-border); padding-bottom: 15px;">
            <h2 style="color: var(--neon-teal); font-family: 'Space Grotesk', sans-serif;">🌍 Geological Workstation</h2>
            <div style="display: flex; gap: 10px;">
                <button class="cyber-btn" onclick="switchTab('target')">📍 Target</button>
                <button class="cyber-btn" onclick="switchTab('basin')">📊 Basin</button>
                <button class="cyber-btn" onclick="switchTab('economics')">💰 Economics</button>
                <button class="cyber-btn" onclick="switchTab('grid')">🧠 Grid</button>
                <button class="cyber-btn" onclick="switchTab('simulation')">🏗️ Simulation</button>
            </div>
        </div>

        <!-- Tab: Target Analysis -->
        <div id="tab-target" class="viz-panel active">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                <div class="form-group">
                    <h3>📍 Point Investigation</h3>
                    <p style="color: var(--text-dim); margin-bottom: 20px;">Analyze specific coordinate-based geophysical anomalies.</p>
                    <div style="margin-bottom: 15px;">
                        <label>Latitude</label>
                        <input type="number" step="0.001" id="latInput" value="4.8" class="cyber-input">
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label>Longitude</label>
                        <input type="number" step="0.001" id="lonInput" value="6.5" class="cyber-input">
                    </div>
                    <button class="cyber-btn w-100" onclick="analyzeLocation()">💡 Run Sigma Analysis</button>
                </div>
                <div id="target-results" style="background: rgba(0,0,0,0.2); border-radius: 12px; padding: 20px; border: 1px dashed var(--glass-border); min-height: 400px;">
                    <div style="color: var(--text-dim); text-align: center; margin-top: 50px;">
                        <i class="fas fa-brain fa-pulse" style="font-size: 2rem; margin-bottom: 15px; opacity: 0.3;"></i>
                        <p>Waiting for telemetry...</p>
                        <button class="cyber-btn" onclick="syncFromNeuralCore()" style="margin-top: 20px; font-size: 0.6rem;">
                            <i class="fas fa-sync"></i> SYNC FROM NEURAL CORE
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab: Basin -->
        <div id="tab-basin" class="viz-panel" style="display: none;">
            <div style="display: grid; grid-template-columns: 350px 1fr; gap: 30px;">
                <div class="glass-panel" style="padding: 24px;">
                    <h3 style="color: var(--neon-teal); margin-bottom: 15px;"><i class="fas fa-layer-group"></i> BASIN ARCHITECTURE</h3>
                    <p style="color: var(--text-dim); font-size: 0.8rem; margin-bottom: 25px;">Synthesize regional subsurface data and reservoir trends.</p>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="font-size: 0.7rem; color: var(--text-dim); display: block; margin-bottom: 8px;">TARGET BASIN</label>
                        <select id="basinInput" class="cyber-input" style="width: 100%;">
                            <option value="Niger Delta">Niger Delta (Cenozoic)</option>
                            <option value="Benue Trough">Benue Trough (Cretaceous)</option>
                            <option value="Anambra">Anambra Basin (Coal Measures)</option>
                        </select>
                    </div>

                    <button class="cyber-btn w-100" onclick="analyzeBasin()" style="margin-bottom: 25px;">
                        <i class="fas fa-microchip"></i> EXECUTE SYNTHESIS
                    </button>

                    <div id="basin-hud" style="display: none;">
                        <!-- ... existing HUD content ... -->
                    </div>

                    <!-- GAIA Strategic Intelligence Integration -->
                    <div class="glass-panel" style="margin-top: 20px; border-color: var(--neon-blue); background: rgba(0, 212, 255, 0.05); padding: 15px;">
                        <h4 style="font-size: 0.7rem; color: var(--neon-blue); margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-brain"></i> GAIA STRATEGIC INTELLIGENCE
                        </h4>
                        <div id="basin-neural-feed" style="font-size: 0.7rem; color: var(--text-dim); max-height: 200px; overflow-y: auto;">
                            <div style="text-align: center; padding: 20px; opacity: 0.5;">Awaiting neural assessment...</div>
                        </div>
                    </div>
                </div>
                </div>

                <div class="glass-panel" style="padding: 0; background: #000; position: relative; overflow: hidden; height: 600px; border: 1px solid var(--glass-border);">
                    <!-- View Mode Toggle -->
                    <div style="position: absolute; top: 15px; right: 15px; z-index: 20; display: flex; gap: 10px;">
                        <button id="btn-3d" class="cyber-btn active" style="padding: 5px 12px; font-size: 0.6rem;" onclick="setBasinView('3d')">3D MODEL</button>
                        <button id="btn-seismic" class="cyber-btn" style="padding: 5px 12px; font-size: 0.6rem;" onclick="setBasinView('seismic')">SEISMIC B-B'</button>
                    </div>
                    <div id="basin-plot" style="width: 100%; height: 100%;">
                        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text-dim);">
                            <i class="fas fa-satellite-dish" style="font-size: 2rem; margin-bottom: 15px; opacity: 0.5;"></i>
                            <div style="font-family: 'Roboto Mono'; font-size: 0.8rem; letter-spacing: 2px;">AWAITING BINARY INPUT...</div>
                        </div>
                    </div>
                    <!-- Sync Overlay -->
                    <div id="basin-sync" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; baseline-background: rgba(0,0,0,0.8); display: none; align-items: center; justify-content: center; z-index: 10;">
                        <div style="text-align: center;">
                            <div class="pulse-ring" style="width: 50px; height: 50px; margin: 0 auto 15px;"></div>
                            <div style="font-family: 'Roboto Mono'; color: var(--neon-teal); font-size: 0.7rem; letter-spacing: 2px;">RECONSTRUCTING VOXEL SPACE...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab: Economics -->
        <div id="tab-economics" class="viz-panel" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                <div>
                    <h3 style="color: #FFD700; margin: 0;">💰 Asset Feasibility Audit</h3>
                    <p style="color: var(--text-dim); font-size: 0.75rem;">GEOLOGICAL-FINANCIAL SYNTHESIS ENGINE</p>
                </div>
                <button class="cyber-btn" onclick="syncFromTarget()" style="border-color: var(--neon-teal); color: var(--neon-teal);">
                    <i class="fas fa-sync"></i> SYNC FROM TARGET
                </button>
            </div>

            <div style="display: grid; grid-template-columns: 350px 1fr; gap: 30px;">
                <!-- Economics Parameters -->
                <div class="glass-panel" style="padding: 24px; border-color: rgba(255, 215, 0, 0.3); background: rgba(255, 215, 0, 0.02);">
                    <h4 style="color: #FFD700; margin-bottom: 20px;"><i class="fas fa-sliders-h"></i> Simulation Parameters</h4>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="font-size: 0.6rem; color: var(--text-dim);">EXPECTED FLOW (BPD)</label>
                        <input type="number" id="econ-rate" value="1200" class="cyber-input" style="width: 100%;">
                    </div>

                    <div style="margin-bottom: 15px;">
                        <label style="font-size: 0.6rem; color: var(--text-dim);">TARGET DEPTH (M)</label>
                        <input type="number" id="econ-depth-input" value="3000" class="cyber-input" style="width: 100%;">
                    </div>

                    <div style="margin-bottom: 15px;">
                        <label style="font-size: 0.6rem; color: var(--text-dim);">FORMATION LITHOLOGY</label>
                        <select id="econ-formation-input" class="cyber-btn" style="width: 100%; text-align: left; padding: 10px; background: rgba(0,0,0,0.4);">
                            <optgroup label="Niger Delta / Southern">
                                <option value="Agbada">Agbada (Sandstone)</option>
                                <option value="Akata">Akata (Shale/High Pressure)</option>
                                <option value="Benin">Benin (Standard Sands)</option>
                            </optgroup>
                            <optgroup label="Chad Basin / Northern">
                                <option value="Fika">Fika Shale (High TOC/Hard)</option>
                                <option value="Bima">Bima Sandstone (Basal)</option>
                                <option value="Gombe">Gombe Sandstone (Estuarine)</option>
                                <option value="Gongila">Gongila (Calcareous/Shale)</option>
                            </optgroup>
                            <optgroup label="Anambra / Benue">
                                <option value="Ajali">Ajali Sandstone</option>
                                <option value="Nsukka">Nsukka Formation</option>
                                <option value="Pindiga">Pindiga (Shale/Limestone)</option>
                            </optgroup>
                        </select>
                    </div>

                    <div style="margin-bottom: 25px;">
                        <label style="font-size: 0.6rem; color: var(--text-dim);">SITE ENVIRONMENT</label>
                        <select id="econ-env-input" class="cyber-input" style="width: 100%;">
                            <option value="Onshore">Onshore / Inland</option>
                            <option value="Offshore">Offshore / Deepwater</option>
                        </select>
                    </div>

                    <button class="cyber-btn w-100" onclick="runFeasibility()" style="background: #FFD700; color: #000; font-weight: bold; border: none;">
                        <i class="fas fa-calculator"></i> EXECUTE ASSET AUDIT
                    </button>
                </div>

                <!-- Simulation Output -->
                <div id="economics-results" class="glass-panel" style="min-height: 500px; display: flex; flex-direction: column; justify-content: center; align-items: center; border-style: dashed; border-color: rgba(255, 215, 0, 0.2);">
                    <div style="text-align: center; color: var(--text-dim);">
                        <i class="fas fa-file-invoice-dollar" style="font-size: 3rem; margin-bottom: 15px; opacity: 0.2;"></i>
                        <p>Configure parameters and run audit to view financial feasibility.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tab: Grid -->
        <div id="tab-grid" class="viz-panel" style="display: none;">
            <div style="display: grid; grid-template-columns: 320px 1fr; gap: 20px;">
                <div class="glass-panel" style="padding: 24px;">
                    <h3 style="color: var(--neon-teal); margin-bottom: 20px;"><i class="fas fa-microchip"></i> COMPUTE ENGINE</h3>
                    <p style="color: var(--text-dim); font-size: 0.75rem; margin-bottom: 20px;">Execute a high-resolution parallel scan to identify potential leads across a 10km search area.</p>
                    
                    <button class="cyber-btn w-100" id="grid-scan-btn" onclick="runGrid()" style="margin-bottom: 25px;">
                        <i class="fas fa-search"></i> INITIALIZE GRID SCAN
                    </button>

                    <div id="leads-container" style="display: none;">
                        <div style="font-size: 0.6rem; color: var(--text-dim); text-transform: uppercase; margin-bottom: 12px; letter-spacing: 1px;">Leads Identified</div>
                        <div id="leads-list" style="display: flex; flex-direction: column; gap: 10px;"></div>
                    </div>
                </div>

                <div class="glass-panel" style="padding: 0; background: #000; position: relative; height: 600px; border: 1px solid var(--glass-border); overflow: hidden;">
                    <div id="grid-plot" style="width: 100%; height: 100%;">
                        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text-dim); opacity: 0.5;">
                            <i class="fas fa-th" style="font-size: 3rem; margin-bottom: 15px;"></i>
                            <div style="font-family: 'Roboto Mono'; font-size: 0.8rem; letter-spacing: 2px;">NEURAL GRID OFFLINE</div>
                        </div>
                    </div>
                    <!-- Sync Overlay -->
                    <div id="grid-sync" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; baseline-background: rgba(0,0,0,0.85); display: none; align-items: center; justify-content: center; z-index: 10;">
                        <div style="text-align: center;">
                            <div class="pulse-ring" style="width: 50px; height: 50px; margin: 0 auto 15px;"></div>
                            <div style="font-family: 'Roboto Mono'; color: var(--neon-teal); font-size: 0.7rem; letter-spacing: 2px;">PARALLEL PROCESSING...</div>
                            <div id="grid-progress" style="font-family: 'Roboto Mono'; font-size: 0.5rem; color: var(--text-dim); margin-top: 10px;">MAPPING SUB-VECTOR 0/100</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab: Simulation -->
        <div id="tab-simulation" class="viz-panel" style="display: none;">
            <div style="display: grid; grid-template-columns: 300px 1fr; gap: 20px;">
                <div class="glass-panel" style="padding: 20px;">
                    <h3 style="color: var(--neon-teal); margin-bottom: 15px;"><i class="fas fa-tools"></i> DRILLING CONTROL</h3>
                    <div id="sim-info" style="font-family: 'Roboto Mono', monospace; font-size: 0.7rem; color: var(--text-dim); margin-bottom: 20px;">
                        READY TO INITIALIZE...
                    </div>
                    <button id="start-drill-btn" class="cyber-btn w-100" style="margin-top: 10px;" onclick="startDrilling()">
                        <i class="fas fa-arrow-down"></i> START DRILLING
                    </button>
                    
                    <div class="telemetry-grid" style="margin-top: 25px; display: grid; gap: 10px;">
                        <div class="glass-panel" style="padding: 10px; background: rgba(0,0,0,0.3);">
                            <div style="font-size: 0.5rem; color: var(--text-dim);">HYDROSTATIC PRESSURE</div>
                            <div id="val-pressure" style="color: var(--neon-blue); font-size: 1rem;">-- PSI</div>
                        </div>
                        <div class="glass-panel" style="padding: 10px; background: rgba(0,0,0,0.3);">
                            <div style="font-size: 0.5rem; color: var(--text-dim);">FORMATION TEMP</div>
                            <div id="val-temp" style="color: var(--warning); font-size: 1rem;">-- °C</div>
                        </div>
                        <div class="glass-panel" style="padding: 10px; background: rgba(0,0,0,0.3);">
                            <div style="font-size: 0.5rem; color: var(--text-dim);">RATE OF PENETRATION</div>
                            <div id="val-rop" style="color: var(--neon-teal); font-size: 1rem;">-- m/hr</div>
                        </div>
                    </div>
                    
                    <div class="glass-panel" style="margin-top: 15px; padding: 15px; border: 1px dashed var(--glass-border); background: rgba(0,255,195,0.02);">
                        <div style="font-size: 0.6rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px;">Expected Time of Completion</div>
                        <div id="val-etc" style="color: var(--neon-teal); font-family: 'Space Grotesk'; font-size: 1.1rem; margin-top: 5px;">-- DAYS, -- HOURS</div>
                    </div>
                </div>
                <div id="drill-container" style="background: #000; border-radius: 12px; height: 600px; position: relative; overflow: hidden; border: 1px solid var(--glass-border);">
                    <div class="scanner-line"></div>
                    <div id="drill-hud" style="position: absolute; top: 20px; left: 20px; z-index: 5; font-family: 'Roboto Mono'; pointer-events: none;">
                        <div style="color: var(--neon-teal); font-size: 0.8rem; margin-bottom: 5px;">📍 LOCATION SYNC: ACTIVE</div>
                        <div id="hud-depth" style="font-size: 1.5rem; color: #fff;">DEPTH: 0.0m</div>
                        <div id="hud-formation" style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase;">SURFACE LEVEL</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        var scene, camera, renderer, controls, drillPipe, layers = [];
        var isDrilling = false;
        var currentDepth = 0;
        var animationId;
        var activeFormations = []; // Dynamic storage for current coordinates
        var activeTargetData = null; // Storage for latest Sigma Analysis results
        var ambientParticles, debrisParticles;
        var shakeIntensity = 0;

        function resetSimulation() {
            isDrilling = false;
            currentDepth = 0;
            if (animationId) cancelAnimationFrame(animationId);
            
            if (scene) {
                scene.traverse(object => {
                    if (object.geometry) object.geometry.dispose();
                    if (object.material) {
                        if (Array.isArray(object.material)) {
                            object.material.forEach(mat => mat.dispose());
                        } else {
                            object.material.dispose();
                        }
                    }
                });
                scene = null;
            }

            var container = document.getElementById('drill-container');
            if (container) {
                while (container.firstChild) {
                    container.removeChild(container.firstChild);
                }
                // Refill the HUD as it's lost during clear
                container.innerHTML = `
                    <div id="drill-hud" style="position: absolute; top: 20px; left: 20px; z-index: 5; font-family: 'Roboto Mono'; pointer-events: none;">
                        <div style="color: var(--neon-teal); font-size: 0.8rem; margin-bottom: 5px;">📍 LOCATION SYNC: ACTIVE</div>
                        <div id="hud-depth" style="font-size: 1.5rem; color: #fff;">DEPTH: 0.0m</div>
                        <div id="hud-formation" style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase;">SURFACE LEVEL</div>
                    </div>
                `;
            }

            if (renderer) {
                renderer.dispose();
                renderer = null;
            }
            if (controls) {
                controls.dispose();
                controls = null;
            }
            ambientParticles = null;
            debrisParticles = null;

            // Reset UI labels
            document.getElementById('start-drill-btn').innerHTML = '<i class="fas fa-arrow-down"></i> START DRILLING';
            document.getElementById('sim-info').innerText = 'READY TO INITIALIZE...';
            document.getElementById('val-pressure').innerText = '-- PSI';
            document.getElementById('val-temp').innerText = '-- °C';
            document.getElementById('val-rop').innerText = '-- m/hr';
            // Do not reset val-etc here, it stays for the coordinate point
        }

        function init3D() {
            var container = document.getElementById('drill-container');
            if (!container || scene) return;

            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            // Add OrbitControls for interactivity
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.screenSpacePanning = true; // Fix: Enable vertical/axial panning
            controls.minDistance = 5;
            controls.maxDistance = 150;

            // Lighting
            var ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
            scene.add(ambientLight);
            
            var pointLight = new THREE.PointLight(0x00ffc3, 1, 100);
            pointLight.position.set(10, 10, 10);
            scene.add(pointLight);
            
            var directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(-5, 5, 5);
            scene.add(directionalLight);

            // Create Drill Pipe (Premium Metallic)
            var pipeGeo = new THREE.CylinderGeometry(0.5, 0.5, 50, 32);
            var pipeMat = new THREE.MeshStandardMaterial({ 
                color: 0x888888, 
                metalness: 1.0, 
                roughness: 0.1,
                emissive: 0x000000
            });
            drillPipe = new THREE.Mesh(pipeGeo, pipeMat);
            drillPipe.position.y = 25; // Start above ground
            scene.add(drillPipe);

            // Add Drill Bit Glow (Cyber Pulsing)
            var bitGlowGeo = new THREE.SphereGeometry(1.2, 32, 32);
            var bitGlowMat = new THREE.MeshBasicMaterial({ color: 0x00ffc3, transparent: true, opacity: 0.2 });
            var bitGlow = new THREE.Mesh(bitGlowGeo, bitGlowMat);
            bitGlow.position.y = -25;
            drillPipe.add(bitGlow);

            // Add Neural Particle Field (Ambient Data)
            var particleGeo = new THREE.BufferGeometry();
            var particlesCount = 2000;
            var posArray = new Float32Array(particlesCount * 3);
            for(var i=0; i < particlesCount * 3; i++) {
                posArray[i] = (Math.random() - 0.5) * 100;
            }
            particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
            var particleMat = new THREE.PointsMaterial({ size: 0.05, color: 0x00ffc3, transparent: true, opacity: 0.4 });
            ambientParticles = new THREE.Points(particleGeo, particleMat);
            scene.add(ambientParticles);

            // Drilling Debris Particles (Hidden until drilling)
            var debrisGeo = new THREE.BufferGeometry();
            var debrisCount = 100;
            var debArray = new Float32Array(debrisCount * 3);
            debrisGeo.setAttribute('position', new THREE.BufferAttribute(debArray, 3));
            var debrisMat = new THREE.PointsMaterial({ size: 0.1, color: 0xffffff });
            debrisParticles = new THREE.Points(debrisGeo, debrisMat);
            debrisParticles.visible = false;
            scene.add(debrisParticles);

            camera.position.set(10, 10, 30);
            camera.lookAt(0, 0, 0);

            // Add Formations (Dynamic)
            var formationData = activeFormations.length > 0 ? activeFormations : [
                { name: 'Quaternary Alluvium', depth: [0, 100], rock_type: 'sand', porosity: 0.2 },
                { name: 'Agbada Formation', depth: [100, 2000], rock_type: 'sandstone', porosity: 0.22 },
                { name: 'Akata Shale', depth: [2000, 4000], rock_type: 'shale', porosity: 0.1 },
                { name: 'Basement Complex', depth: [4000, 6000], rock_type: 'granite', porosity: 0.01 }
            ];

            var colors = {
                'sand': 0xd2b48c,
                'sandstone': 0x6495ed,
                'shale': 0x4682b4,
                'granite': 0x696969,
                'limestone': 0xececec
            };

            var yOffset = 0;
            formationData.forEach((f, index) => {
                var height = (f.depth[1] - f.depth[0]) / 50; // Scaling
                var geo = new THREE.CylinderGeometry(15, 15, height, 32);
                var mat = new THREE.MeshPhongMaterial({ 
                    color: colors[f.rock_type] || 0x666666, 
                    transparent: true, 
                    opacity: 0.25, // More transparent for holographic look
                    side: THREE.DoubleSide
                });
                var mesh = new THREE.Mesh(geo, mat);
                mesh.position.y = yOffset - height / 2;
                scene.add(mesh);
                
                // Add Holographic Scanlines (Wireframe inside)
                var holoGeo = new THREE.CylinderGeometry(14.8, 14.8, height, 32);
                var holoMat = new THREE.MeshBasicMaterial({ 
                    color: colors[f.rock_type] || 0x666666, 
                    wireframe: true, 
                    transparent: true, 
                    opacity: 0.1 
                });
                var holoMesh = new THREE.Mesh(holoGeo, holoMat);
                mesh.add(holoMesh);
                
                // Add visible boundary disk (Separator)
                var diskGeo = new THREE.RingGeometry(0.6, 15, 32);
                var diskMat = new THREE.MeshBasicMaterial({ 
                    color: 0x001111, 
                    side: THREE.DoubleSide, 
                    transparent: true, 
                    opacity: 0.8 
                });
                var disk = new THREE.Mesh(diskGeo, diskMat);
                disk.rotation.x = Math.PI / 2;
                disk.position.y = yOffset;
                scene.add(disk);

                // Add Sprite Label (Guaranteed Alignment)
                var sprite = createLabelSprite(f.name.replace('_', ' '));
                sprite.position.set(22, 0, 0); // Position to the side
                mesh.add(sprite);
                
                yOffset -= height;
            });

            animate();
        }

        function createLabelSprite(text) {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            canvas.width = 1024; // Double resolution
            canvas.height = 256;

            // Stylish Opaque Background
            ctx.fillStyle = 'rgba(0, 20, 20, 0.95)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Neon Glow Effect
            ctx.shadowColor = '#00ffc3';
            ctx.shadowBlur = 20;
            
            // Neon Border
            ctx.strokeStyle = '#00ffc3';
            ctx.lineWidth = 15;
            ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);
            
            // Heavy Side Border
            ctx.fillStyle = '#00ffc3';
            ctx.fillRect(0, 0, 60, canvas.height);

            // Text Styling (Sharp & Vibrant)
            ctx.shadowBlur = 10;
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 90px "Space Grotesk", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(text.toUpperCase(), canvas.width / 2 + 30, canvas.height / 2);

            var texture = new THREE.CanvasTexture(canvas);
            texture.magFilter = THREE.LinearFilter;
            texture.minFilter = THREE.LinearFilter;
            
            var spriteMat = new THREE.SpriteMaterial({ 
                map: texture, 
                transparent: true,
                opacity: 1.0,
                depthTest: false // Ensure they stay on top
            });
            var sprite = new THREE.Sprite(spriteMat);
            sprite.scale.set(10, 2.5, 1);
            sprite.renderOrder = 999;
            return sprite;
        }

        function animate() {
            animationId = requestAnimationFrame(animate);
            
            // Ambient Particle Flow
            if(ambientParticles) {
                ambientParticles.rotation.y += 0.001;
                ambientParticles.rotation.x += 0.0005;
            }

            if (isDrilling) {
                currentDepth += 2.5;
                drillPipe.position.y -= 0.05;
                drillPipe.rotation.y += 0.2; // Rapid rotation
                
                // Vibration / Camera Shake
                if (shakeIntensity > 0) {
                    camera.position.x += (Math.random() - 0.5) * shakeIntensity;
                    camera.position.y += (Math.random() - 0.5) * shakeIntensity;
                    shakeIntensity *= 0.9; // Decay
                }

                // Debris Animation
                if(debrisParticles) {
                    debrisParticles.visible = true;
                    debrisParticles.position.y = drillPipe.position.y - 25;
                    var positions = debrisParticles.geometry.attributes.position.array;
                    for(var i=0; i < positions.length; i += 3) {
                        positions[i] += (Math.random() - 0.5) * 0.5;
                        positions[i+1] += Math.random() * 0.5;
                        positions[i+2] += (Math.random() - 0.5) * 0.5;
                        if(positions[i+1] > 5) positions[i+1] = 0;
                    }
                    debrisParticles.geometry.attributes.position.needsUpdate = true;
                }
                
                if (currentDepth % 50 === 0) {
                    updateTelemetry(currentDepth);
                    // Hit detection for shake
                    if(document.getElementById('hud-formation').innerText.includes('Basement') || 
                       document.getElementById('hud-formation').innerText.includes('Shale')) {
                        shakeIntensity = 0.15;
                    }
                }
                
                if (currentDepth >= 5000) {
                    isDrilling = false;
                    debrisParticles.visible = false;
                    document.getElementById('start-drill-btn').innerText = 'DRILLING COMPLETE';
                }
            }
            
            if (!isDrilling && controls) {
                controls.update();
            }
            
            renderer.render(scene, camera);
        }

        function startDrilling() {
            if (isDrilling) return;
            isDrilling = true;
            document.getElementById('start-drill-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> DRILLING IN PROGRESS...';
            document.getElementById('sim-info').innerText = 'PENETRATING STRATA...';
            playSfx();
        }

        function updateTelemetry(depth) {
            fetch(`/api/exploration/telemetry?depth=${depth}`)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('val-pressure').innerText = data.pressure.toLocaleString() + ' PSI';
                    document.getElementById('val-temp').innerText = data.temperature + ' °C';
                    document.getElementById('val-rop').innerText = data.rop + ' m/hr';
                    document.getElementById('hud-depth').innerText = `DEPTH: ${data.depth.toFixed(1)}m`;
                    document.getElementById('hud-formation').innerText = data.formation;
                });
        }

        function switchTab(tab) {
            document.querySelectorAll('.viz-panel').forEach(p => p.style.display = 'none');
            document.getElementById('tab-' + tab).style.display = 'block';
            if (tab === 'simulation') {
                init3D();
            }
            playSfx();
        }

        function analyzeLocation() {
            var lat = parseFloat(document.getElementById('latInput').value);
            var lon = parseFloat(document.getElementById('lonInput').value);
            var res = document.getElementById('target-results');
            
            res.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center;">
                    <div class="fas fa-satellite fa-spin" style="font-size: 2rem; color: var(--neon-teal); margin-bottom: 15px;"></div>
                    <div style="font-family: 'Roboto Mono'; font-size: 0.7rem; letter-spacing: 2px;">SYNCHRONIZING ORBITAL SAR...</div>
                </div>
            `;
            
            fetch('/api/exploration/target', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({lat, lon})
            })
            .then(r => r.json())
            .then(data => {
                if(data.status === 'success') {
                    // Reset simulation variables
                    resetSimulation();
                    activeFormations = data.layers;
                    activeTargetData = data; // Store full results for sync
                    
                    // Display expected time
                    document.getElementById('val-etc').innerText = data.etc.toUpperCase();

                    var matchColor = data.match > 80 ? 'var(--neon-teal)' : data.match > 60 ? 'var(--warning)' : 'var(--error)';
                    
                    var layersHtml = data.layers.map(l => `
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 8px 0; align-items: center;">
                            <div style="display: flex; flex-direction: column;">
                                <span style="color: var(--text-main); font-size: 0.75rem;">${l.name.replace('_', ' ')}</span>
                                <span style="color: var(--text-dim); font-size: 0.6rem; text-transform: uppercase;">${l.rock_type.replace('_', ' ')}</span>
                            </div>
                            <div style="text-align: right;">
                                <span style="color: var(--neon-blue); font-family: 'Roboto Mono'; font-size: 0.7rem;">${l.depth[0]} - ${l.depth[1]}m</span>
                                <div style="font-size: 0.55rem; color: var(--text-dim);">φ: ${Math.round(l.porosity*100)}%</div>
                            </div>
                        </div>
                    `).join('');
                    
                    res.innerHTML = `
                        <div class="page-transition">
                            <!-- Signal & Basin Header -->
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                                <div>
                                    <h4 style="margin: 0; font-size: 0.7rem; color: var(--text-dim); letter-spacing: 1px; text-transform: uppercase;">Signal Integrity</h4>
                                    <div style="font-size: 1.5rem; font-weight: bold; color: ${matchColor}; font-family: 'Space Grotesk';">${data.match}%</div>
                                </div>
                                <div style="text-align: right;">
                                    <span class="badge" style="background: rgba(0, 255, 195, 0.1); color: var(--neon-teal); border: 1px solid var(--neon-teal); font-size: 0.65rem; padding: 4px 10px;">${data.basin_type}</span>
                                    <div style="font-size: 0.6rem; color: var(--text-dim); margin-top: 5px;">COORDS: ${lat}, ${lon}</div>
                                </div>
                            </div>

                            <!-- Confidence Bar -->
                            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-bottom: 25px; overflow: hidden;">
                                <div style="width: ${data.match}%; height: 100%; background: ${matchColor}; box-shadow: 0 0 10px ${matchColor}; transition: width 1s ease-out;"></div>
                            </div>

                            <!-- Primary Target Analysis -->
                            <div style="background: rgba(0,255,195,0.03); border: 1px solid rgba(0,255,195,0.2); padding: 20px; border-radius: 12px; margin-bottom: 20px; position: relative; overflow: hidden;">
                                <div style="position: absolute; right: -10px; top: -10px; font-size: 4rem; opacity: 0.05; color: var(--neon-teal);"><i class="fas fa-bullseye"></i></div>
                                <div style="font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px;">Primary Hydrocarbon Target</div>
                                <div style="font-size: 1.3rem; color: var(--neon-teal); font-weight: bold; font-family: 'Space Grotesk'; margin: 5px 0;">${data.primary_target}</div>
                                <div style="display: flex; gap: 15px; margin-top: 10px;">
                                    <div class="glass-panel" style="padding: 5px 10px; font-size: 0.6rem; background: rgba(0,0,0,0.3);">
                                         <i class="fas fa-mountain" style="color: var(--warning);"></i> ${data.lithology}
                                    </div>
                                    <div class="glass-panel" style="padding: 5px 10px; font-size: 0.6rem; background: rgba(0,0,0,0.3);">
                                         <i class="fas fa-layer-group" style="color: var(--neon-blue);"></i> STRATIGRAPHIC INDEX: #02
                                    </div>
                                </div>
                            </div>

                            <!-- Stratigraphic Stack -->
                            <div style="font-size: 0.65rem; text-transform: uppercase; color: var(--text-dim); margin-bottom: 12px; letter-spacing: 1px;">Analytical Stratigraphy</div>
                            <div style="font-family: 'Roboto Mono'; max-height: 250px; overflow-y: auto; padding-right: 5px;" class="custom-scroll">
                                ${layersHtml}
                            </div>

                            <!-- Oracle Quick-Reason Entry Point -->
                            <div id="oracle-sidebar-trigger" style="margin-top: 20px; border-top: 1px solid var(--glass-border); padding-top: 15px; text-align: center;">
                                <button class="cyber-btn" style="font-size: 0.7rem; width: 100%;" onclick="consultOracle('${data.primary_target}', ${data.match})">
                                    <i class="fas fa-brain"></i> CONSULT ORACLE REASONING
                                </button>
                            </div>
                        </div>
                    `;
                } else {
                    res.innerHTML = `<div style="color: var(--error); padding: 20px; text-align: center; border: 1px solid var(--error); border-radius: 8px;">
                        <i class="fas fa-exclamation-triangle"></i><br>TELEMETRY ERROR: ${data.message}
                    </div>`;
                }
            });
        }

        function syncFromTarget() {
            if (!activeTargetData) {
                alert("Please run a Sigma Analysis (Sigma Analysis button) in the 'Target' tab first.");
                return;
            }

            // Sync Formation
            var formationSelect = document.getElementById('econ-formation-input');
            var targetName = activeTargetData.primary_target.toLowerCase();
            
            // Comprehensive Basin-Aware Mapping
            var mapping = {
                'akata': 'Akata', 'fika': 'Fika', 'shale': 'Akata',
                'agbada': 'Agbada', 'gombe': 'Gombe', 'bima': 'Bima', 'sandstone': 'Agbada',
                'benin': 'Benin', 'chad': 'Bima', 'gongila': 'Gongila',
                'pindiga': 'Pindiga', 'ajali': 'Ajali', 'nsukka': 'Nsukka'
            };

            var matched = false;
            for (var [key, val] of Object.entries(mapping)) {
                if (targetName.includes(key)) {
                    formationSelect.value = val;
                    matched = true;
                    break;
                }
            }
            
            if (!matched) formationSelect.value = 'Agbada'; // Base fallback

            // Sync Depth (Pulling the deepest layer limit)
            var depthInput = document.getElementById('econ-depth-input');
            if (activeTargetData.layers && activeTargetData.layers.length > 0) {
                var maxDepth = Math.max(...activeTargetData.layers.map(l => l.depth[1]));
                depthInput.value = maxDepth;
            } else {
                depthInput.value = 3500;
            }

            // Environment Sync
            var envSelect = document.getElementById('econ-env-input');
            envSelect.value = depthInput.value > 3500 ? 'Offshore' : 'Onshore';
            
            alert(`Exploration data synced: ${activeTargetData.primary_target} at ${depthInput.value}m.`);
        }

        function runFeasibility() {
            var rate = document.getElementById("econ-rate").value;
            var depth = document.getElementById("econ-depth-input").value;
            var formation = document.getElementById("econ-formation-input").value;
            var env = document.getElementById("econ-env-input").value;
            var out = document.getElementById("economics-results");
            
            out.innerHTML = `
                <div style="text-align: center; padding: 50px;">
                    <i class="fas fa-coins fa-spin" style="font-size: 2rem; color: #FFD700;"></i><br><br>
                    <div style="font-family: 'Roboto Mono'; font-size: 0.7rem;">CALCULATING NPV & AUDITING FORMATION COSTS...</div>
                </div>
            `;
            
            fetch("/api/feasibility", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    initial_rate: rate,
                    depth: depth,
                    formation: formation,
                    env_type: env
                })
            })
            .then(r => r.json())
            .then(res => {
                var data = res.result;
                
                var materialsHtml = "";
                data.audit.breakdown.specialized_materials.forEach(m => {
                    materialsHtml += `
                        <div style="padding: 10px; background: rgba(255, 215, 0, 0.05); border: 1px solid rgba(255, 215, 0, 0.2); border-radius: 6px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; font-weight: bold; color: #FFD700; font-size: 0.8rem;">
                                <span>${m.item}</span>
                                <span>$${m.cost.toLocaleString()}</span>
                            </div>
                            <div style="font-size: 0.65rem; color: var(--text-dim); margin-top: 4px;">${m.reason}</div>
                        </div>
                    `;
                });

                out.style.borderStyle = "solid";
                out.style.alignItems = "stretch";
                out.style.justifyContent = "flex-start";
                out.style.padding = "25px";
                
                out.innerHTML = `
                    <div class="page-transition">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid rgba(255, 215, 0, 0.3); padding-bottom: 15px;">
                            <div>
                                <h3 style="color: #FFD700; margin: 0;">ASSET AUDIT: BILL OF MATERIALS</h3>
                                <div style="font-size: 0.6rem; color: var(--text-dim); margin-top: 4px;">SITE: ${env.toUpperCase()} / ${formation.toUpperCase()} REGIME</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 0.6rem; color: var(--text-dim);">ESTIMATED CAPEX</div>
                                <div style="font-size: 1.4rem; color: #FFD700; font-family: 'Space Grotesk'; font-weight: 800;">$${data.financials.total_capex.toLocaleString()}</div>
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                            <div>
                                <h4 style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase;">Financial Viability</h4>
                                <div style="font-size: 0.8rem; line-height: 2;">
                                    <div style="display: flex; justify-content: space-between;"><span>NPV (10% Disc.)</span><span style="color: #FFD700;">$${data.metrics.npv.toLocaleString()}</span></div>
                                    <div style="display: flex; justify-content: space-between;"><span>Project ROI</span><span style="color: var(--neon-teal);">${data.metrics.roi}%</span></div>
                                    <div style="display: flex; justify-content: space-between;"><span>Payback Period</span><span style="color: var(--warning);">${data.metrics.payback_months} Months</span></div>
                                </div>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 15px; border-radius: 8px;">
                                <h4 style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase;">Geological Rationale</h4>
                                <ul style="font-size: 0.75rem; color: var(--text-primary); padding-left: 20px; margin: 0;">
                                    ${data.audit.rationales.map(r => `<li>${r}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                        
                        <h4 style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; margin-bottom: 10px;">Primary Enquiry List</h4>
                        ${materialsHtml}
                    </div>
                `;
            });
        }

        function runGrid() {
            var lat = parseFloat(document.getElementById('latInput').value);
            var lon = parseFloat(document.getElementById('lonInput').value);
            var sync = document.getElementById('grid-sync');
            var btn = document.getElementById('grid-scan-btn');
            
            sync.style.display = 'flex';
            btn.disabled = true;
            playSfx();

            fetch("/api/region-grid", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({lat, lon})
            })
            .then(r => r.json())
            .then(res => {
                if(res.status === 'success') {
                    Plotly.newPlot('grid-plot', res.chart.data, res.chart.layout);
                    
                    var leadsList = document.getElementById('leads-list');
                    leadsList.innerHTML = res.top_leads.map(lead => `
                        <div class="glass-panel" style="padding: 12px; background: rgba(0,0,0,0.2); border-left: 2px solid ${lead.score > 80 ? 'var(--neon-teal)' : 'var(--warning)'};">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-size: 0.6rem; color: var(--text-dim);">${lead.lat.toFixed(3)}N, ${lead.lon.toFixed(3)}E</span>
                                <span style="font-weight: bold; color: var(--neon-teal); font-size: 0.7rem;">${lead.score}% Match</span>
                            </div>
                            <button class="cyber-btn" style="width: 100%; padding: 4px; font-size: 0.5rem;" onclick="setTargetFromGrid(${lead.lat}, ${lead.lon})">SET AS TARGET</button>
                        </div>
                    `).join('');
                    
                    document.getElementById('leads-container').style.display = 'block';
                }
                sync.style.display = 'none';
                btn.disabled = false;
            });
        }

        function setTargetFromGrid(lat, lon) {
            document.getElementById('latInput').value = lat;
            document.getElementById('lonInput').value = lon;
            switchTab('target');
            analyzeLocation();
        }

        function consultOracle(target, match) {
            var sidebar = document.getElementById('oracle-sidebar');
            var content = document.getElementById('oracle-consult-content');
            
            sidebar.style.right = '0'; // Open
            content.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div class="pulse-ring" style="margin: 0 auto 20px;"></div>
                    <div style="color: var(--neon-teal); font-size: 0.7rem; font-family: 'Roboto Mono';">ORACLE IS SYNTHESIZING...</div>
                </div>
            `;
            
            fetch('/api/intelligence/reason', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    query: `Assess the economic and geological risk of the ${target} target with a ${match}% signal match.`,
                    geological_context: { layers: activeFormations } // Pass full context
                })
            })
            .then(r => r.json())
            .then(data => {
                content.innerHTML = `
                    <div class="page-transition">
                        <div style="font-size: 0.8rem; color: var(--neon-teal); margin-bottom: 15px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                            <i class="fas fa-microchip"></i> EXPERT DEDUCTION
                        </div>
                        <div style="font-size: 0.75rem; line-height: 1.6; white-space: pre-wrap;">${data.response}</div>
                    </div>
                `;
            });
        }

        function closeOracle() {
            document.getElementById('oracle-sidebar').style.right = '-400px';
        }

        function analyzeBasin() {
            var basin = document.getElementById('basinInput').value;
            var sync = document.getElementById('basin-sync');
            var hud = document.getElementById('basin-hud');
            
            sync.style.display = 'flex';
            playSfx();

            fetch(`/api/exploration/basin?id=${encodeURIComponent(basin)}`)
                .then(r => r.json())
                .then(data => {
                    Plotly.newPlot('basin-plot', data.chart.data, data.chart.layout);
                    document.getElementById('basin-potential').innerText = (data.potential * 100).toFixed(0) + '%';
                    document.getElementById('basin-maturity').innerText = data.maturity.toUpperCase();
                    document.getElementById('basin-desc').innerText = data.description;
                    
                    // Update G-Risk Matrix
                    var r = data.risk_profile;
                    var updateRisk = (id, val, text) => {
                        var el = document.getElementById(id);
                        el.innerText = `${text}: ${(val * 100).toFixed(0)}%`;
                        el.style.borderColor = val > 0.8 ? 'var(--neon-teal)' : (val > 0.5 ? 'var(--warning)' : 'var(--error)');
                        el.style.color = val > 0.8 ? 'var(--neon-teal)' : '#fff';
                    };
                    updateRisk('risk-source', r.source, 'SOURCE');
                    updateRisk('risk-reservoir', r.reservoir, 'RESERVOIR');
                    updateRisk('risk-seal', r.seal, 'SEAL');
                    updateRisk('risk-charge', r.charge, 'CHARGE');
                    document.getElementById('total-pos').innerText = (r.source * r.reservoir * r.seal * r.charge).toFixed(3);

                    // Render Stratigraphic Column
                    var stratCol = document.getElementById('strat-column');
                    stratCol.innerHTML = data.stratigraphy.map(s => `
                        <div style="background: ${s.color}; padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid rgba(255,255,255,0.2);">
                            <div style="display: flex; flex-direction: column;">
                                <span style="font-size: 0.7rem; font-weight: bold; color: #fff;">${s.name}</span>
                                <span style="font-size: 0.55rem; color: rgba(255,255,255,0.7); text-transform: uppercase;">${s.age} • ${s.type}</span>
                            </div>
                            <span style="font-family: 'Roboto Mono'; font-size: 0.6rem; color: rgba(255,255,255,0.8);">${s.range[0]}-${s.range[1]}m</span>
                        </div>
                    `).join('');

                    sync.style.display = 'none';
                    hud.style.display = 'block';
                });
        }

        var currentBasinView = '3d';
        function setBasinView(mode) {
            currentBasinView = mode;
            document.querySelectorAll('#tab-basin .cyber-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + mode).classList.add('active');
            
            var basin = document.getElementById('basinInput').value;
            var sync = document.getElementById('basin-sync');
            sync.style.display = 'flex';
            
            var url = mode === '3d' ? 
                `/api/exploration/basin?id=${encodeURIComponent(basin)}` : 
                `/api/exploration/seismic?id=${encodeURIComponent(basin)}`;

            fetch(url).then(r => r.json()).then(data => {
                var chart = mode === '3d' ? data.chart : data;
                Plotly.newPlot('basin-plot', chart.data, chart.layout);
                sync.style.display = 'none';
            });
        }

        function syncFromNeuralCore() {
            playSfx();
            fetch('/api/intelligence/latest-thoughts')
                .then(r => r.json())
                .then(data => {
                    if (data.thoughts && data.thoughts.length > 0) {
                        const latest = data.thoughts[0];
                        // Example: "Niger Delta Assessment"
                        alert(`GAIA Recommendation: ${latest.entity.toUpperCase()}\nSyncing coordinates...`);
                        
                        // Default coordinates based on basin if not explicit in thought
                        const basinCoords = {
                            'Niger Delta': {lat: 4.8, lon: 6.5},
                            'Benue Trough': {lat: 9.0, lon: 10.0},
                            'Anambra Basin': {lat: 6.8, lon: 7.2},
                            'Chad Basin': {lat: 12.5, lon: 13.8}
                        };
                        
                        for (let b in basinCoords) {
                            if (latest.entity.includes(b)) {
                                document.getElementById('latInput').value = basinCoords[b].lat;
                                document.getElementById('lonInput').value = basinCoords[b].lon;
                                analyzeLocation();
                                return;
                            }
                        }
                    } else {
                        alert("No recent neural assessments found. Trigger a Growth Cycle in the Neural Thought Stream first.");
                    }
                });
        }

        function fetchNeuralBasinFeed(basin) {
            const feed = document.getElementById('basin-neural-feed');
            feed.innerHTML = '<div style="text-align: center; padding: 20px;"><i class="fas fa-sync fa-spin"></i> Consultating GAIA...</div>';
            
            fetch(`/api/intelligence/thoughts-by-basin?basin=${encodeURIComponent(basin)}`)
                .then(r => r.json())
                .then(data => {
                    if (data.thoughts && data.thoughts.length > 0) {
                        feed.innerHTML = data.thoughts.map(t => `
                            <div class="glass-panel data-stream-item" style="margin-bottom: 10px; border-left-color: var(--neon-blue); background: rgba(0,212,255,0.02);">
                                <div style="display: flex; justify-content: space-between; font-size: 0.55rem; color: var(--neon-blue); margin-bottom: 5px;">
                                    <span>ASSESSMENT</span>
                                    <span>${Math.round(t.confidence * 100)}% CONF</span>
                                </div>
                                <div style="color: var(--text-primary); font-size: 0.65rem; line-height: 1.4;">${t.description}</div>
                            </div>
                        `).join('');
                    } else {
                        feed.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.5;">No basin-specific strategic flags found.</div>';
                    }
                });
        }

        // Hook into basin change
        const basinInput = document.getElementById('basinInput');
        if (basinInput) {
            basinInput.addEventListener('change', (e) => {
                fetchNeuralBasinFeed(e.target.value);
            });
            // Initial load
            setTimeout(() => fetchNeuralBasinFeed(basinInput.value), 500);
        }
    </script>
    
    <!-- Oracle Sidebar UI -->
    <div id="oracle-sidebar" style="position: fixed; top: 0; right: -400px; width: 400px; height: 100vh; background: rgba(0,0,0,0.9); backdrop-filter: blur(20px); border-left: 1px solid var(--neon-teal); z-index: 1000; transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1); padding: 30px; box-shadow: -10px 0 30px rgba(0,0,0,0.5);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
            <h3 style="margin: 0; color: var(--neon-teal); font-family: 'Space Grotesk'; font-size: 1.1rem;">TECHNICAL CONSULTANT</h3>
            <button class="cyber-btn" onclick="closeOracle()" style="padding: 5px 10px;">&times;</button>
        </div>
        <div id="oracle-consult-content"></div>
    </div>
    '''
    return render_gaia_page("Exploration Workstation", content)

@exploration_bp.route('/api/exploration/target', methods=['POST'])
def api_exploration_target():
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    
    analyzer = current_app.config['advanced_analyzer']
    layers = analyzer.generate_geological_layers(lat, lon)
    match = analyzer.calculate_prospectivity(lat, lon, layers)
    
    # Identify Basin Type for badge
    basin_type = "UNKNOWN BASIN"
    if 4.0 <= lat <= 7.0: basin_type = "NIGER DELTA"
    elif 6.5 <= lat <= 7.5: basin_type = "ANAMBRA BASIN"
    elif 7.5 <= lat <= 10.5: basin_type = "BENUE TROUGH"
    elif 11.0 <= lat <= 14.0: basin_type = "CHAD BASIN"

    from ..visualization.charts import calculate_drilling_etc
    etc = calculate_drilling_etc(layers)

    return json.dumps({
        'status': 'success',
        'primary_target': layers[1]['name'].replace('_', ' '),
        'lithology': layers[1]['rock_type'].replace('_', ' '),
        'match': match,
        'basin_type': basin_type,
        'layers': layers,
        'etc': etc
    })

@exploration_bp.route('/feasibility-assessment')
def feasibility_assessment():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Similar to original feasibility_assessment
    content = '''
    <div class="section-header">
        <h3>💰 Feasibility Assessment Engine</h3>
    </div>
    <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h3>⚙️ Well Parameters</h3>
        <input type="number" id="initial_rate" value="1200">
        <button onclick="runFeasibility()" class="btn btn-success">Run Analysis</button>
        <div id="feasibilityResults"></div>
    </div>
    <script>
        function runFeasibility() {
            var rate = document.getElementById("initial_rate").value;
            fetch("/api/feasibility", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({initial_rate: rate})
            })
            .then(r => r.json())
            .then(res => {
                document.getElementById("feasibilityResults").innerHTML = JSON.stringify(res.result);
            });
        }
    </script>
    '''
    return render_gaia_page("Feasibility Assessment", content)

@exploration_bp.route('/region-grid-analysis')
def region_grid_analysis():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = '''
    <div class="section-header">
        <h3>🧠 Regional Grid Analysis</h3>
    </div>
    <div style="background:white; padding:25px; border-radius:15px;">
        <button onclick="runGrid()" class="btn btn-success">Start Parallel Compute</button>
        <div id="gridResults"></div>
    </div>
    <script>
        function runGrid() {
            var lat = parseFloat(document.getElementById('latInput').value);
            var lon = parseFloat(document.getElementById('lonInput').value);
            var sync = document.getElementById('grid-sync');
            var btn = document.getElementById('grid-scan-btn');
            
            sync.style.display = 'flex';
            btn.disabled = true;
            playSfx();

            fetch("/api/region-grid", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({lat, lon})
            })
            .then(r => r.json())
            .then(res => {
                if(res.status === 'success') {
                    Plotly.newPlot('grid-plot', res.chart.data, res.chart.layout);
                    
                    // Render Leads List
                    var leadsList = document.getElementById('leads-list');
                    leadsList.innerHTML = res.top_leads.map(lead => `
                        <div class="glass-panel" style="padding: 12px; background: rgba(0,0,0,0.2); border-left: 2px solid ${lead.score > 80 ? 'var(--neon-teal)' : 'var(--warning)'};">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-size: 0.6rem; color: var(--text-dim);">${lead.lat.toFixed(3)}N, ${lead.lon.toFixed(3)}E</span>
                                <span style="font-weight: bold; color: var(--neon-teal); font-size: 0.7rem;">${lead.score}% Match</span>
                            </div>
                            <button class="cyber-btn" style="width: 100%; padding: 4px; font-size: 0.5rem;" onclick="setTargetFromGrid(${lead.lat}, ${lead.lon})">SET AS TARGET</button>
                        </div>
                    `).join('');
                    
                    document.getElementById('leads-container').style.display = 'block';
                }
                sync.style.display = 'none';
                btn.disabled = false;
            });
        }

        function setTargetFromGrid(lat, lon) {
            document.getElementById('latInput').value = lat;
            document.getElementById('lonInput').value = lon;
            switchTab('target');
            analyzeLocation();
        }
    </script>
    '''
    return render_gaia_page("Region Grid Analysis", content)

@exploration_bp.route('/visualization')
def visualization():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = '''
    <div class="page-transition">
        <!-- Header: Volumetric Lab -->
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; border-bottom: 1px solid var(--glass-border); padding-bottom: 20px;">
            <div>
                <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; margin-bottom: 0;">VOLUMETRIC <span style="color: var(--neon-teal);">STUDIO</span></h1>
                <p style="color: var(--text-dim); letter-spacing: 2px; font-size: 0.8rem;">4D SUBSURFACE MODELING • TEMPORAL DEPLETION AUDIT</p>
            </div>
            <div class="glass-panel" style="padding: 10px 20px; display: flex; gap: 20px; font-family: 'Roboto Mono'; font-size: 0.7rem;">
                <div><span style="color: var(--text-dim);">ENGINE:</span> <span style="color: var(--neon-teal);">VOXEL-SYNAPSE v4</span></div>
                <div><span style="color: var(--text-dim);">LATENCY:</span> <span style="color: var(--neon-blue);" id="render-latency">--ms</span></div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 320px 1fr; gap: 20px;">
            <!-- Left: Rendering Workbench -->
            <div class="glass-panel workbench" style="padding: 25px;">
                <h3 style="color: var(--neon-teal); margin-bottom: 20px; font-size: 1rem;"><i class="fas fa-microchip"></i> RENDER MASTER</h3>
                
                <div style="margin-bottom: 20px;">
                    <label style="font-size: 0.7rem; color: var(--text-dim); display: block; margin-bottom: 8px;">VISUALIZATION MODE</label>
                    <select id="render-mode" class="cyber-input" style="width: 100%;" onchange="loadView('subsurface')">
                        <option value="scatter">High-Precision Scatter</option>
                        <option value="voxel">Solid Voxel Volume</option>
                    </select>
                </div>

                <div style="margin-bottom: 30px;">
                    <label style="font-size: 0.7rem; color: var(--text-dim); display: block; margin-bottom: 8px;">4D TEMPORAL DYNAMICS</label>
                    <button class="cyber-btn" style="width: 100%; color: var(--warning); border-color: var(--warning);" onclick="loadView('comparison')">
                        <i class="fas fa-history"></i> RUN 2010 v 2024 AUDIT
                    </button>
                    <p style="font-size: 0.6rem; color: var(--text-dim); margin-top: 10px;">Compares initial discovery pressure vs current depletion estimates.</p>
                </div>

                <div class="glass-panel" style="margin-top: 30px; background: rgba(0,0,0,0.3); padding: 15px;">
                    <h4 style="font-size: 0.6rem; color: var(--text-dim); text-transform: uppercase; margin-bottom: 10px;">Voxel Attributes</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.7rem;">
                        <div><i class="fas fa-tint" style="color: var(--neon-blue);"></i> POR: 24%</div>
                        <div><i class="fas fa-wind" style="color: var(--neon-teal);"></i> PERM: 140mD</div>
                    </div>
                </div>
            </div>

            <!-- Right: Dynamic Viewport -->
            <div class="glass-panel" style="padding: 0; min-height: 650px; position: relative; background: #000; overflow: hidden; border-color: var(--neon-teal);">
                <!-- 3D HUD Elements -->
                <div style="position: absolute; top: 20px; left: 20px; z-index: 5; font-family: 'Roboto Mono'; pointer-events: none;">
                    <div style="color: var(--neon-teal); font-size: 0.7rem; letter-spacing: 2px;">VOXEL DENSITY: <span id="voxel-density">OPTIMAL</span></div>
                    <div style="color: var(--text-dim); font-size: 0.6rem;">GRID RESOLUTION: 50m³</div>
                </div>

                <div id="plot-area" style="width: 100%; height: 700px;"></div>
                
                <!-- Lab Sync Overlay -->
                <div id="lab-sync" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(8, 10, 15, 0.9); display: flex; align-items: center; justify-content: center; z-index: 10; pointer-events: none;">
                    <div style="text-align: center;">
                        <div class="pulse-ring" style="width: 60px; height: 60px; margin: 0 auto 20px; border-color: var(--neon-teal);"></div>
                        <div style="font-family: 'Roboto Mono'; color: var(--neon-teal); font-size: 0.8rem; letter-spacing: 3px;">RECONSTRUCTING SUBSURFACE MESH...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadView(type) {
            playSfx();
            var mode = document.getElementById('render-mode').value;
            var startTime = performance.now();
            var sync = document.getElementById('lab-sync');
            sync.style.display = 'flex';
            
            var url = type === 'comparison' ? '/api/viz/comparison' : `/api/viz/3d?mode=${mode}`;
            
            fetch(url).then(r => r.json()).then(fig => {
                Plotly.newPlot('plot-area', fig.data, fig.layout);
                sync.style.display = 'none';
                var diff = Math.round(performance.now() - startTime);
                document.getElementById('render-latency').innerText = diff + 'ms';
            });
        }

        // Forced Immediate Multi-Stage Load
        setTimeout(() => loadView('subsurface'), 100);
    </script>
    '''
    return render_gaia_page("Volumetric Laboratory", content)

@exploration_bp.route('/api/viz/3d')
def api_viz_3d():
    mode = request.args.get('mode', 'scatter')
    from ..visualization.charts import generate_3d_subsurface_chart
    return generate_3d_subsurface_chart(mode=mode)

@exploration_bp.route('/api/viz/comparison')
def api_viz_comparison():
    from ..visualization.charts import generate_4d_depletion_comparison
    return generate_4d_depletion_comparison()

@exploration_bp.route('/api/exploration/basin')
def api_exploration_basin():
    basin_id = request.args.get('id', 'Niger Delta')
    from ..visualization.charts import BASINS, generate_3d_subsurface_chart
    
    basin_data = BASINS.get(basin_id, BASINS['Niger Delta'])
    
    # Generate 3D Chart
    chart_json = generate_3d_subsurface_chart(
        center_lat=basin_data['lat'], 
        center_lon=basin_data['lon'],
        radius_deg=1.5,
        mode='voxel'
    )
    
    # Advanced Geological Data
    stratigraphies = {
        'Niger Delta': [
            {'name': 'Benin Formation', 'age': 'Oligocene', 'type': 'SEAL', 'range': [0, 1500], 'color': 'rgba(210,180,140,0.3)'},
            {'name': 'Agbada Formation', 'age': 'Eocene', 'type': 'RESERVOIR', 'range': [1500, 3500], 'color': 'rgba(100,149,237,0.4)'},
            {'name': 'Akata Formation', 'age': 'Paleocene', 'type': 'SOURCE', 'range': [3500, 6000], 'color': 'rgba(70,130,180,0.5)'}
        ],
        'Benue Trough': [
            {'name': 'Gombe Sandstone', 'age': 'Maastrichtian', 'type': 'RESERVOIR', 'range': [0, 800], 'color': 'rgba(243,156,18,0.3)'},
            {'name': 'Pindiga Fm', 'age': 'Turonian', 'type': 'SEAL/SOURCE', 'range': [800, 2500], 'color': 'rgba(52,152,219,0.4)'},
            {'name': 'Bima Sandstone', 'age': 'Albian', 'type': 'RESERVOIR', 'range': [2500, 5000], 'color': 'rgba(46,204,113,0.5)'}
        ],
        'Anambra': [
            {'name': 'Nsukka Formation', 'age': 'Paleocene', 'type': 'CAP ROCK', 'range': [0, 400], 'color': 'rgba(149,165,166,0.3)'},
            {'name': 'Ajali Sandstone', 'age': 'Maastrichtian', 'type': 'RESERVOIR', 'range': [400, 1200], 'color': 'rgba(231,76,60,0.4)'},
            {'name': 'Mamu Formation', 'age': 'Campanian', 'type': 'COAL/SOURCE', 'range': [1200, 3000], 'color': 'rgba(52,73,94,0.5)'}
        ]
    }

    maturities = {
        'Niger Delta': 'Late Oil Window (110°C AVG)',
        'Benue Trough': 'Early Gas Window (135°C AVG)',
        'Anambra': 'Main Gas Window (155°C AVG)'
    }

    # G-Risk Assessment profiles (Source, Reservoir, Seal, Charge)
    risk_profiles = {
        'Niger Delta': {'source': 0.95, 'reservoir': 0.88, 'seal': 0.90, 'charge': 0.98},
        'Benue Trough': {'source': 0.75, 'reservoir': 0.82, 'seal': 0.65, 'charge': 0.70},
        'Anambra': {'source': 0.82, 'reservoir': 0.75, 'seal': 0.78, 'charge': 0.85}
    }

    descriptions = {
        'Niger Delta': 'Major tertiary prograding delta. Features expansive Agbada reservoirs and deep-water turbidites. Primary source: Akata Shale.',
        'Benue Trough': 'Intracontinental rift system. Cretaceous sandstone reservoirs with significant structural trapping potential.',
        'Anambra': 'Transition basin featuring thick coal measures and sandstone sequences. High gas potential in lower Campanian strata.',
        'Chad Basin': 'Interior cratonic basin. Exploration targets focus on Bima sandstone sequences with variable maturation levels.'
    }

    return json.dumps({
        'status': 'success',
        'basin': basin_id,
        'potential': basin_data['potential'],
        'maturity': maturities.get(basin_id, 'Undefined Thermal State'),
        'risk_profile': risk_profiles.get(basin_id, {'source': 0.5, 'reservoir': 0.5, 'seal': 0.5, 'charge': 0.5}),
        'stratigraphy': stratigraphies.get(basin_id, []),
        'description': descriptions.get(basin_id, 'Regional geological assessment in progress.'),
        'chart': json.loads(chart_json)
    })

@exploration_bp.route('/api/exploration/seismic')
def api_exploration_seismic():
    basin_id = request.args.get('id', 'Niger Delta')
    from ..visualization.charts import BASINS, generate_seismic_slice
    basin_data = BASINS.get(basin_id, BASINS['Niger Delta'])
    return generate_seismic_slice(lat=basin_data['lat'], lon=basin_data['lon'])

@exploration_bp.route('/api/exploration/telemetry')
def api_exploration_telemetry():
    depth = float(request.args.get('depth', 0))
    from ..visualization.charts import get_drilling_telemetry
    return json.dumps(get_drilling_telemetry(depth))
@exploration_bp.route('/api/region-grid', methods=['POST'])
def api_region_grid():
    data = request.json
    seed_lat = data.get('lat', 4.8)
    seed_lon = data.get('lon', 6.5)
    
    analyzer = current_app.config['advanced_analyzer']
    
    # Generate 10x10 Grid (10km coverage)
    grid_size = 10
    step = 0.05 # ~5km spacing
    
    lats = np.linspace(seed_lat - 0.25, seed_lat + 0.25, grid_size)
    lons = np.linspace(seed_lon - 0.25, seed_lon + 0.25, grid_size)
    
    z_data = []
    points = []
    
    for lat in lats:
        row = []
        for lon in lons:
            layers = analyzer.generate_geological_layers(lat, lon)
            score = analyzer.calculate_prospectivity(lat, lon, layers)
            row.append(score)
            points.append({'lat': float(lat), 'lon': float(lon), 'score': float(score)})
        z_data.append(row)
    
    # Sort for Top Leads
    top_leads = sorted(points, key=lambda x: x['score'], reverse=True)[:5]
    
    # Create Heatmap Chart
    figure = {
        'data': [{
            'type': 'heatmap',
            'x': lons.tolist(),
            'y': lats.tolist(),
            'z': z_data,
            'colorscale': 'Viridis',
            'showscale': True,
            'colorbar': {'title': 'Signal Match %', 'tickfont': {'color': '#00ffc3'}}
        }],
        'layout': {
            'title': {'text': '🧠 Regional Prospectivity Grid Scan', 'font': {'color': '#00ffc3', 'size': 16}},
            'paper_bgcolor': '#080c12',
            'plot_bgcolor': '#080c12',
            'font': {'color': '#00ffc3'},
            'xaxis': {'title': 'Longitude', 'gridcolor': '#222'},
            'yaxis': {'title': 'Latitude', 'gridcolor': '#222'},
            'margin': {'l': 50, 'r': 50, 'b': 50, 't': 50}
        }
    }

    return json.dumps({
        'status': 'success',
        'grid_points_analyzed': grid_size * grid_size,
        'top_leads': top_leads,
        'chart': figure
    })

@exploration_bp.route('/strategic-mission-control')
def strategic_mission_control():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from flask import render_template_string
    import os
    
    template_path = os.path.join(current_app.root_path, 'templates', 'strategic_mission_control.html')
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    return render_gaia_page("Strategic Mission Control", render_template_string(template_content))

@exploration_bp.route('/api/strategy/generate')
def api_strategy_generate():
    depth = float(request.args.get('depth', 3000))
    formation = request.args.get('formation', 'Agbada')
    flow = float(request.args.get('flow', 1500))
    prob = float(request.args.get('prob', 0.5))
    
    economics = current_app.config['economics_engine']
    strategy = economics.generate_strategic_plan(
        initial_rate=flow,
        depth=depth,
        formation=formation,
        probability=prob
    )
    
    return json.dumps(strategy)
