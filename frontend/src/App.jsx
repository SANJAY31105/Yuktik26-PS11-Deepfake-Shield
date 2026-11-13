import React, { useState, useEffect } from 'react';

export default function App() {
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchIncident();
  }, []);

  const fetchIncident = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/incident/scenario-demo');
      const data = await res.json();
      setIncident(data.correlated_intelligence);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-black tracking-wide text-white">SatyaShield AI · Real-Time Threat Intelligence</h1>
          <p className="text-sm text-slate-400">Autonomous Multimodal Deepfake & Disinformation Defense Platform</p>
        </div>
        <button
          onClick={fetchIncident}
          className="bg-red-600 hover:bg-red-500 text-white font-bold py-2 px-4 rounded-lg shadow-lg"
        >
          {loading ? 'Correlating...' : '⚡ Trigger Dam Collapse Demo'}
        </button>
      </header>

      {incident && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-red-900/60 p-6 rounded-2xl">
            <div className="flex justify-between items-center mb-2">
              <span className="text-red-400 font-mono font-bold uppercase">{incident.overall_verdict}</span>
              <span className="text-slate-400 font-mono">Confidence: {(incident.overall_confidence * 100).toFixed(1)}%</span>
            </div>
            <h2 className="text-xl font-bold mb-2">{incident.title}</h2>
            <p className="text-slate-300 text-sm leading-relaxed">{incident.explainable_summary}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
              <h3 className="font-bold text-lg mb-4">Cross-Modal Contradictions Detected</h3>
              <div className="space-y-3">
                {incident.cross_modal_contradictions?.map((c, i) => (
                  <div key={i} className="p-3 bg-slate-950 rounded-lg border border-red-900/40">
                    <span className="text-xs font-bold text-red-400 block mb-1">[{c.type}]</span>
                    <p className="text-xs text-slate-300">{c.description}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
              <h3 className="font-bold text-lg mb-4">Incident Propagation Timeline</h3>
              <div className="space-y-3">
                {incident.timeline?.map((t, i) => (
                  <div key={i} className="flex gap-4 items-start text-xs">
                    <span className="font-mono text-blue-400 font-bold w-16">{t.time}</span>
                    <div>
                      <span className="text-slate-400 font-mono">[{t.status}]</span>
                      <p className="text-slate-200 mt-0.5">{t.event}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

