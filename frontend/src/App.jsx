import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:5000";

function App() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [message, setMessage] = useState("System Online. Waiting for commands...");
  const [loading, setLoading] = useState(false);

  const callApi = async (endpoint, actionName) => {
    try {
      setLoading(true);
      setMessage(`Starting ${actionName}...`);
      const response = await axios.get(`${API}${endpoint}`);
      setMessage(response.data.message || response.data.status);
    } catch (error) {
      setMessage(`Error connecting to backend for ${actionName}.`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="app-container">
      
      {/* The Floating Glowing Orb */}
      <div 
        className={`orb ${isExpanded ? 'expanded' : ''}`} 
        onClick={toggleExpand}
        title="Toggle Touch AI"
      >
        {isExpanded ? "✖" : "⚡"}
      </div>

      {/* The Glassmorphism Dashboard */}
      <div className={`glass-panel ${isExpanded ? 'show' : ''}`}>
        <div className="header">
          <h1>Touch AI</h1>
          <p>Next-Gen Desktop Assistant</p>
        </div>

        <div className="buttons">
          <button onClick={() => callApi("/api/status", "System Check")}>
            📊 Check System Status
          </button>

          <button onClick={() => callApi("/api/start-gesture", "Gestures")}>
            ✋ Start Gesture Engine (Smooth)
          </button>

          <button onClick={() => callApi("/api/start-voice", "Voice Assistant")}>
            🎤 Start Voice Assistant
          </button>
          
          <button onClick={() => {
            setMessage("Hold 🤙 (Shaka sign) to enter Lens Mode, pinch to select.");
          }}>
            🔍 How to use Google Lens Mode
          </button>
        </div>

        <div className="status-box">
          {loading ? "Processing request..." : message}
        </div>
      </div>

    </div>
  );
}

export default App;