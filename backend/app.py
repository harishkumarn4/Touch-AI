from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
import os
import sys

from gestures.hand_tracker import start_gesture_control
from voice.assistant import start_voice_assistant, speak
from vision.analyzer import analyze_image

app = Flask(__name__)
CORS(app)

# Global flag to stop background threads if needed
running = True

def vision_monitor():
    """Watches for the trigger file from hand_tracker and runs vision analysis."""
    trigger_file = os.path.join(os.path.dirname(__file__), 'vision', 'trigger_analysis.txt')
    while running:
        if os.path.exists(trigger_file):
            try:
                with open(trigger_file, 'r') as f:
                    img_path = f.read().strip()
                # Delete the trigger file immediately to prevent duplicate runs
                os.remove(trigger_file)
                
                if img_path and os.path.exists(img_path):
                    # Play a sound or speak a prompt
                    speak("Analyzing selection...")
                    
                    # Analyze
                    result = analyze_image(img_path)
                    
                    # Speak the result
                    speak(result)
            except Exception as e:
                print(f"Vision Monitor Error: {e}")
        
        time.sleep(1) # Check every second

@app.route('/')
def home():
    return "Touch AI Backend is Running!"

@app.route('/api/status')
def status():
    return jsonify({
        "status": "Touch AI backend running successfully 🚀",
        "project": "Touch AI - Next Gen Desktop Assistant"
    })

@app.route('/api/start-gesture')
def start_gesture():
    # Run gesture control in a separate thread so it doesn't block the API
    threading.Thread(target=start_gesture_control, daemon=True).start()
    return jsonify({"message": "Gesture control started in background"})

@app.route('/api/start-voice')
def start_voice():
    # Run voice in a separate thread
    threading.Thread(target=start_voice_assistant, daemon=True).start()
    return jsonify({"message": "Voice assistant started"})

if __name__ == '__main__':
    # Start the vision monitor thread
    threading.Thread(target=vision_monitor, daemon=True).start()
    
    # Run Flask
    app.run(debug=True, port=5000, use_reloader=False)