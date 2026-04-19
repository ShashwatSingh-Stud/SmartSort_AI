from flask import Flask, render_template, Response, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from config import Config
import os
import cv2
import threading
import time

# Blueprints
from routes.overview import overview_bp
from routes.cityos import cityos_bp
from routes.analytics_routes import analytics_bp
from routes.bins import bins_bp
from routes.detection_route import detection_route_bp
from routes.report import report_bp
from routes.history import history_bp
from routes.impact import impact_bp
from routes.ai_insights import ai_insights_bp
from routes.data_api import data_api_bp

# Flask Setup
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register Blueprints
app.register_blueprint(overview_bp, url_prefix='/api/overview')
app.register_blueprint(cityos_bp, url_prefix='/api/cityos')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(bins_bp, url_prefix='/api/bins')
app.register_blueprint(detection_route_bp, url_prefix='/api/detect')
app.register_blueprint(report_bp, url_prefix='/api/report')
app.register_blueprint(history_bp, url_prefix='/api/history')
app.register_blueprint(impact_bp, url_prefix='/api/impact')
app.register_blueprint(ai_insights_bp, url_prefix='/api/insights')
app.register_blueprint(data_api_bp, url_prefix='/api/data')

# Credentials
users = {"admin": "admin123", "guest": "guest123"}

@app.before_request
def require_login():
    # List of open endpoints
    allowed = ['login', 'static', 'video_feed']
    # If the user is requesting an endpoint not in the allowed list and not logged in
    # (API endpoints are already handling their own logic usually, but let's protect them too if needed)
    if 'user' not in session and request.endpoint not in allowed and not request.path.startswith('/api'):
        return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if u in users and users[u] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', user=session['user'])

# Multi-page routes
@app.route('/features')
def cityos(): return render_template('features.html')

@app.route('/map')
def map_page(): return render_template('map.html')

@app.route('/analytics')
def analytics(): return render_template('analytics.html')

@app.route('/insights')
def insights(): return render_template('insights.html')

@app.route('/impact')
def impact(): return render_template('impact.html')

@app.route('/history')
def history(): return render_template('history.html')

@app.route('/report')
def report_page(): return render_template('report.html')

@app.route('/category/<cat>')
def category(cat): return render_template('category.html', category=cat)

# Camera / Video Logic (Existing Detection Integration)
from detection import SmartWasteDetector
detector = SmartWasteDetector()

def gen_frames():
    while True:
        frame, results = detector.read()
        if frame is None: break
        
        # If detection found, update via socket
        if results and results.get("confidence", 0) > 0.8:
            socketio.emit('new_detection', {
                "category": results["category"],
                "confidence": results["confidence"],
                "ts": time.time()
            })
            
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Socket events
@socketio.on('connect')
def handle_connect():
    print("Dashboard Connected")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
