// frontend/src/App.jsx
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm' // <-- NEW: Imports table support
import './App.css'

function App() {
  const [formData, setFormData] = useState({
    starting_location: '',
    destination: '',
    travel_days: 1,
    travelers: 1,
    total_budget: 10000,
    travel_preferences: ''
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const isNumberField = ['travel_days', 'travelers', 'total_budget'].includes(name);
    const parsedValue = isNumberField ? Number(value) : value;
    
    setFormData({ ...formData, [name]: parsedValue });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/plan-trip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMsg = Array.isArray(data.detail) 
          ? data.detail[0].msg 
          : data.detail;       
        throw new Error(errorMsg || "An error occurred");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>TripSmith</h1>
      <h2>AI Travel Feasibility & Itinerary Planner</h2>

      <form onSubmit={handleSubmit} className="trip-form">
        <div className="form-group">
          <label>Starting Location:</label>
          <input type="text" name="starting_location" value={formData.starting_location} onChange={handleChange} required placeholder="e.g. Mumbai" />
        </div>

        <div className="form-group">
          <label>Destination (in Kerala):</label>
          <input type="text" name="destination" value={formData.destination} onChange={handleChange} required placeholder="e.g. Munnar" />
        </div>

        <div className="form-group">
          <label>Travel Days:</label>
          <input type="number" name="travel_days" min="1" max="30" value={formData.travel_days} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label>Number of Travelers:</label>
          <input type="number" name="travelers" min="1" max="20" value={formData.travelers} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label>Total Budget (INR):</label>
          <input type="number" name="total_budget" min="1" value={formData.total_budget} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label>Travel Preferences:</label>
          <input type="text" name="travel_preferences" value={formData.travel_preferences} onChange={handleChange} placeholder="e.g. Adventure, Relaxing, Nature" />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing Trip Feasibility..." : "Plan My Trip"}
        </button>
      </form>

      {error && (
        <div className="error-box">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="success-box" style={{ marginTop: '2rem', textAlign: 'left' }}>
          <h3>Feasibility Status: <span style={{ color: result.feasibility_status === "Feasible" ? "green" : "red" }}>{result.feasibility_status}</span></h3>
          
          {result.warnings && result.warnings.length > 0 && (
            <div className="warning-box" style={{ backgroundColor: '#fff3cd', padding: '10px', borderRadius: '5px', marginBottom: '15px' }}>
              <strong>⚠️ Warnings:</strong>
              <ul style={{ margin: 0 }}>
                {result.warnings.map((warn, index) => (
                  <li key={index}>{warn}</li>
                ))}
              </ul>
            </div>
          )}

          <hr />
          
          <div className="markdown-body">
            {/* NEW: remarkPlugins prop added here to render tables properly */}
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {result.itinerary}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}

export default App