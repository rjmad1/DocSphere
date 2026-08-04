import React, { useState } from 'react';

interface ImpactDiffViewerProps {
  eventId?: string;
  onApprove?: () => void;
  onReject?: () => void;
}

export const ImpactDiffViewer: React.FC<ImpactDiffViewerProps> = ({
  eventId = "EVT-2026-0804",
  onApprove,
  onReject
}) => {
  const [decision, setDecision] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');

  const handleApprove = () => {
    setDecision('APPROVED');
    if (onApprove) onApprove();
  };

  const handleReject = () => {
    setDecision('REJECTED');
    if (onReject) onReject();
  };

  return (
    <div data-testid="impact-diff-viewer" className="w-full bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col gap-5 text-slate-100 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-lg text-slate-100">Living Documentation Change Impact Analysis</h3>
            <span className="text-xs bg-amber-950 border border-amber-700 text-amber-300 px-2 py-0.5 rounded-full">HIGH RISK</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">Triggered by source update in <code className="text-indigo-400">DOC-IN-001.pdf</code></p>
        </div>

        {decision === 'PENDING' ? (
          <div className="flex items-center gap-2">
            <button 
              onClick={handleReject}
              className="px-4 py-1.5 bg-red-950/60 border border-red-700 text-red-300 text-xs font-semibold rounded hover:bg-red-900/60 transition"
            >
              Reject Change
            </button>
            <button 
              data-testid="publish-diff-button"
              onClick={handleApprove}
              className="px-4 py-1.5 bg-emerald-600 text-white text-xs font-semibold rounded hover:bg-emerald-500 transition shadow-lg"
            >
              Approve & Propagate
            </button>
          </div>
        ) : (
          <span data-testid="diff-status-badge" className={`text-xs font-bold px-3 py-1 rounded border ${decision === 'APPROVED' ? 'bg-emerald-950 border-emerald-700 text-emerald-300' : 'bg-red-950 border-red-700 text-red-300'}`}>
            DECISION: {decision}
          </span>
        )}
      </div>

      {/* Side-by-Side Diff View */}
      <div className="grid grid-cols-2 gap-4">
        {/* Left Column: Current Baseline */}
        <div className="p-4 bg-slate-950 border border-red-900/40 rounded-lg flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-red-400 uppercase tracking-wider">Current Active Baseline (v1.0.0)</span>
            <span className="text-[11px] text-slate-500">DOC-BRD-001</span>
          </div>
          <div data-testid="diff-before" className="p-3 bg-red-950/20 border border-red-900/30 rounded text-xs text-slate-300 font-mono leading-relaxed">
            The system performs multi-currency journal reconciliation on a weekly schedule every Friday EOD.
          </div>
        </div>

        {/* Right Column: AI Recommended Update */}
        <div className="p-4 bg-slate-950 border border-emerald-900/40 rounded-lg flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">AI Recommended Update (v1.1.0)</span>
            <span className="text-[11px] text-slate-500">Citation Confidence: 98%</span>
          </div>
          <div data-testid="diff-after" className="p-3 bg-emerald-950/20 border border-emerald-900/30 rounded text-xs text-slate-300 font-mono leading-relaxed">
            The system shall execute automated multi-currency journal reconciliations at end-of-day.
          </div>
        </div>
      </div>
    </div>
  );
};
