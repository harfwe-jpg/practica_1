# vehicle_detector.py
from flask import Flask, render_template_string, jsonify, request, Response
from ultralytics import YOLO
import cv2
import json
import time
from datetime import datetime
import threading
import torch
from collections import defaultdict

app = Flask(__name__)

# ==========================================
# INTERFAZ DE USUARIO (HTML/CSS/JS PREMIUM)
# ==========================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Vehicle Analytics</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0b0f19;
            --bg-card: #131a26;
            --border-color: #1f293d;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --accent: #06b6d4;
            --danger: #ef4444;
            --success: #10b981;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-main); color: var(--text-primary); min-height: 100vh; padding: 24px; }

        .container { max-width: 1600px; margin: 0 auto; }

        .header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 20px 32px; background: var(--bg-card); border-radius: 16px;
            border: 1px solid var(--border-color); margin-bottom: 24px;
        }
        .header h1 { font-size: 1.8rem; font-weight: 700; letter-spacing: -0.025em; color: var(--text-primary); }
        .header h1 span { color: var(--accent); }

        .main-grid { display: grid; grid-template-columns: 9fr 4fr; gap: 24px; }

        .card {
            background: var(--bg-card); border: 1px solid var(--border-color);
            border-radius: 16px; padding: 24px; display: flex; flex-direction: column;
        }
        .card h2 { font-size: 1.2rem; font-weight: 600; margin-bottom: 20px; color: var(--text-secondary); display: flex; align-items: center; gap: 8px; }

        .video-container { background: #000; border-radius: 12px; overflow: hidden; position: relative; aspect-ratio: 4/3; }
        #video-stream { width: 100%; height: 100%; object-fit: contain; }

        .control-group { margin-bottom: 20px; }
        .control-group label { display: block; font-size: 0.85rem; font-weight: 500; color: var(--text-secondary); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }

        select, input[type="range"] {
            width: 100%; padding: 12px; background: var(--bg-main); border: 1px solid var(--border-color);
            border-radius: 8px; color: var(--text-primary); font-size: 0.95rem; outline: none; transition: all 0.2s;
        }
        select:focus { border-color: var(--primary); }

        .btn {
            width: 100%; padding: 14px; border: none; border-radius: 8px; font-weight: 600;
            font-size: 0.95rem; cursor: pointer; transition: all 0.2s; display: inline-flex; justify-content: center; align-items: center; gap: 8px;
        }
        .btn-start { background: var(--primary); color: white; }
        .btn-start:hover { background: var(--primary-hover); }
        .btn-stop { background: #261b24; color: var(--danger); border: 1px solid rgba(239,68,68,0.2); }
        .btn-stop:hover { background: rgba(239,68,68,0.1); }

        .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 24px; }
        .stat-box { background: var(--bg-main); border: 1px solid var(--border-color); padding: 16px; border-radius: 12px; text-align: center; }
        .stat-label { font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 4px; }
        .stat-value { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); }
        .stat-value.highlight { color: var(--accent); }

        .status-badge { display: inline-flex; align-items: center; gap: 6px; font-size: 0.85rem; font-weight: 600; padding: 6px 12px; border-radius: 20px; }
        .status-running { background: rgba(16,185,129,0.1); color: var(--success); }
        .status-stopped { background: rgba(239,64,64,0.1); color: var(--danger); }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }

        #detections-log { max-height: 350px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .log-item { background: var(--bg-main); border-left: 4px solid var(--primary); padding: 12px; border-radius: 4px 8px 8px 4px; display: flex; justify-content: space-between; font-size: 0.9rem; }
        .log-time { color: var(--text-secondary); font-size: 0.8rem; }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>VisionX <span>Vehicle Detector</span></h1>
            <div id="status-container" class="status-badge status-stopped">
                <span class="dot"></span><span id="status-text">DISPOSITIVO OFFLINE</span>
            </div>
        </div>

        <div class="main-grid">
            <div class="card">
                <h2>📹 Feed Analítico en Tiempo Real</h2>
                <div class="video-container">
                    <img id="video-stream" src="" alt="Esperando transmisión...">
                </div>
            </div>

            <div class="card">
                <h2>⚙️ Panel de Configuración</h2>
                <div class="control-group">
                    <label>Origen de captura</label>
                    <select id="camera-select">
                        <option value="0">Cámara Integrada (0)</option>
                        <option value="1">Cámara Externa (1)</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>Umbral de confianza: <span id="conf-val" style="color:var(--accent)">50%</span></label>
                    <input type="range" id="confidence-slider" min="0.2" max="1" step="0.05" value="0.5">
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
                    <button class="btn btn-start" onclick="startSystem()">Activar</button>
                    <button class="btn btn-stop" onclick="stopSystem()">Detener</button>
                </div>

                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-label">Total Detectados</div>
                        <div class="stat-value highlight" id="stat-total">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Automóviles</div>
                        <div class="stat-value" id="stat-car">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Camiones</div>
                        <div class="stat-value" id="stat-truck">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Motocicletas</div>
                        <div class="stat-value" id="stat-motorcycle">0</div>
                    </div>
                </div>

                <h2 style="margin-top:24px; margin-bottom:12px;">📋 Eventos Recientes</h2>
                <div id="detections-log"></div>
            </div>
        </div>
    </div>

    <script>
        let running = false;

        document.getElementById('confidence-slider').addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            document.getElementById('conf-val').textContent = Math.round(val * 100) + '%';
            fetch('/set-confidence', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({confidence: val})
            });
        });

        async function startSystem() {
            const cam = document.getElementById('camera-select').value;
            const conf = document.getElementById('confidence-slider').value;

            const res = await fetch('/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({camera: parseInt(cam), confidence: parseFloat(conf)})
            });
            const data = await res.json();
            if(data.success) {
                running = true;
                document.getElementById('status-container').className = "status-badge status-running";
                document.getElementById('status-text').textContent = "SISTEMA ACTIVO";
                document.getElementById('video-stream').src = "/video-feed";
                pollData();
            }
        }

        async function stopSystem() {
            const res = await fetch('/stop', {method: 'POST'});
            const data = await res.json();
            if(data.success) {
                running = false;
                document.getElementById('status-container').className = "status-badge status-stopped";
                document.getElementById('status-text').textContent = "DISPOSITIVO OFFLINE";
                document.getElementById('video-stream').src = "";
            }
        }

        function pollData() {
            if (!running) return;
            fetch('/get-detections')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('stat-total').textContent = data.total;
                    document.getElementById('stat-car').textContent = data.stats.car || 0;
                    document.getElementById('stat-truck').textContent = data.stats.truck || 0;
                    document.getElementById('stat-motorcycle').textContent = data.stats.motorcycle || 0;

                    const log = document.getElementById('detections-log');
                    log.innerHTML = data.recent.map(item => `
                        <div class="log-item">
                            <strong>${item.class.toUpperCase()}</strong>
                            <span class="log-time">${item.time}</span>
                        </div>
                    `).join('');

                    setTimeout(pollData, 1000);
                });
        }
    </script>
</body>
</html>
'''

# ==========================================
# CÓDIGO CORE DE PROCESAMIENTO (MÁXIMO RENDIMIENTO)
# ==========================================
class VideoDetectorEngine:
    def __init__(self):
        self.running = False
        self.camera_index = 0
        self.confidence = 0.5
        self.model = None
        self.recent_detections = []
        self.stats = defaultdict(int)
        self.lock = threading.Lock()
        self.current_frame = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def load_model(self):
        try:
            self.model = YOLO('yolov8n.pt')
            print(f"✅ YOLOv8 cargado en hardware: [{self.device.upper()}]")
            return True
        except Exception as e:
            print(f"❌ Error crítico cargando modelo: {e}")
            return False

    def process_thread(self):
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        target_classes = ['car', 'truck', 'bus', 'motorcycle']

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            results = self.model(frame, conf=self.confidence, device=self.device, verbose=False)
            annotated_frame = frame.copy()

            if results:
                annotated_frame = results[0].plot()

                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    cls_name = results[0].names[cls_id]

                    if cls_name in target_classes:
                        with self.lock:
                            self.stats[cls_name] += 1
                            now = datetime.now().strftime('%H:%M:%S')
                            self.recent_detections.append({'class': cls_name, 'time': now})
                            if len(self.recent_detections) > 100:
                                self.recent_detections.pop(0)

            ret, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if ret:
                with self.lock:
                    self.current_frame = buffer.tobytes()

            time.sleep(0.01)

        cap.release()

engine = VideoDetectorEngine()

# ==========================================
# RUTAS FLASK (CONTROLADORES)
# ==========================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    engine.camera_index = data.get('camera', 0)
    engine.confidence = data.get('confidence', 0.5)

    if not engine.running:
        with engine.lock:
            engine.recent_detections = []
            engine.stats = defaultdict(int)
        engine.running = True
        threading.Thread(target=engine.process_thread, daemon=True).start()
    return jsonify({'success': True})

@app.route('/stop', methods=['POST'])
def stop():
    engine.running = False

    # Salvar el JSON para que el analyzer.py tenga datos inmediatamente
    with engine.lock:
        if engine.recent_detections:
            filename = f"detecciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(engine.recent_detections, f, indent=4, ensure_ascii=False)
            print(f"💾 [Historial] Datos de sesión respaldados en: {filename}")

    return jsonify({'success': True})

def generate_stream():
    while True:
        if not engine.running:
            time.sleep(0.2)
            continue
        with engine.lock:
            frame = engine.current_frame
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03)

@app.route('/video-feed')
def video_feed():
    return Response(generate_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get-detections')
def get_detections():
    with engine.lock:
        total_detections = sum(engine.stats.values())
        return jsonify({
            'total': total_detections,
            'stats': dict(engine.stats),
            'recent': list(reversed(engine.recent_detections))[:15]
        })

@app.route('/set-confidence', methods=['POST'])
def set_confidence():
    data = request.json
    engine.confidence = data.get('confidence', 0.5)
    return jsonify({'success': True})

if __name__ == '__main__':
    if engine.load_model():
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
