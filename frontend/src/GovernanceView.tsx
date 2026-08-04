import React, { useState } from 'react';

export const GovernanceView: React.FC = () => {
  const [artifactId, setArtifactId] = useState("");
  const [severity, setSeverity] = useState("MINOR");
  const [slaHours, setSlaHours] = useState(24);
  const [alertVisible, setAlertVisible] = useState(false);

  const handleEvaluate = (e: React.FormEvent) => {
    e.preventDefault();
    if (severity === "BREAKING") {
      setSlaHours(8);
      setAlertVisible(true);
    } else if (severity === "MAJOR") {
      setSlaHours(12);
      setAlertVisible(true);
    } else {
      setSlaHours(24);
      setAlertVisible(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <h1 className="text-2xl font-bold text-indigo-400 mb-6">EKOS Compliance & Governance Dashboard</h1>
      
      <div className="grid grid-cols-2 gap-8">
        {/* Policy Evaluator Form */}
        <form 
          data-testid="policy-evaluator-form" 
          onSubmit={handleEvaluate} 
          className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col gap-4 shadow-xl"
        >
          <h2 className="text-lg font-semibold">Evaluate Artifact SLA Policy</h2>
          
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Artifact ID</label>
            <input 
              data-testid="input-artifact-id"
              type="text" 
              value={artifactId}
              onChange={(e) => setArtifactId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-slate-100" 
              placeholder="e.g. DOC-BRD-001"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Change Severity</label>
            <select 
              data-testid="select-severity"
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-slate-100"
            >
              <option value="MINOR">MINOR</option>
              <option value="MAJOR">MAJOR</option>
              <option value="BREAKING">BREAKING</option>
            </select>
          </div>

          <button 
            data-testid="evaluate-btn"
            type="submit"
            className="w-full py-2 bg-indigo-600 font-semibold rounded hover:bg-indigo-500 transition text-sm shadow-md"
          >
            Evaluate Approval Policy
          </button>
        </form>

        {/* SLA Status Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col gap-4 justify-between shadow-xl">
          <div>
            <h2 className="text-lg font-semibold mb-2">Computed Governance SLA</h2>
            <div data-testid="sla-badge" className="inline-block bg-indigo-950 border border-indigo-700 text-indigo-300 px-3 py-1 rounded text-sm font-bold">
              {slaHours} Hours SLA Limit
            </div>
          </div>

          {alertVisible && (
            <div data-testid="escalation-alert-banner" className="bg-red-950/40 border border-red-700/50 p-4 rounded text-red-200 text-sm">
              ⚠️ <strong>High Risk Escalation Pathway Triggered:</strong> Action required by Enterprise Arch & Security Officers.
            </div>
          )}

          <button 
            data-testid="approve-policy-button"
            className="w-full py-2 bg-emerald-600 font-semibold rounded hover:bg-emerald-500 transition text-sm shadow-md"
          >
            Approve Policy Override
          </button>
        </div>
      </div>
    </div>
  );
};
