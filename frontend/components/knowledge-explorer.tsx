import React, { useState } from 'react';

interface KnowledgeExplorerProps {
  rootEntityId?: str;
}

export const KnowledgeExplorer: React.FC<KnowledgeExplorerProps> = ({
  rootEntityId = "REQ-00847"
}) => {
  const [selectedNode, setSelectedNode] = useState<string>(rootEntityId);
  const [depth, setDepth] = useState<number>(2);

  return (
    <div className="w-full h-full bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col gap-4 text-slate-100">
      {/* Visualizer Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <span className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">🕸️</span>
          <div>
            <h3 className="font-bold text-slate-100 text-base">Cytoscape Knowledge Graph Visualizer</h3>
            <p className="text-xs text-slate-400">Root Node: <code className="text-indigo-400 font-mono">{rootEntityId}</code></p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <label className="text-xs text-slate-400 font-medium">Traversal Depth:</label>
          <select 
            value={depth} 
            onChange={(e) => setDepth(Number(e.target.value))}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded px-2 py-1 focus:outline-none"
          >
            <option value={1}>1 Level</option>
            <option value={2}>2 Levels</option>
            <option value={3}>3 Levels</option>
          </select>
        </div>
      </div>

      {/* Force-Directed Graph Layout Simulation */}
      <div className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-6 flex items-center justify-center relative overflow-hidden">
        <div className="flex flex-col items-center gap-8 z-10">
          <div 
            onClick={() => setSelectedNode("CAP-0012")}
            className="p-4 bg-emerald-950/60 border border-emerald-600/60 rounded-xl text-center cursor-pointer hover:scale-105 transition shadow-lg"
          >
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wide">BusinessCapability</span>
            <p className="font-mono text-sm font-semibold text-slate-100 mt-1">CAP-0012</p>
            <p className="text-xs text-slate-300">Multi-Currency Reconciliation</p>
          </div>

          <div className="h-8 w-0.5 bg-indigo-500/50 relative">
            <span className="absolute -left-12 top-1 text-[10px] bg-slate-900 px-1 border border-slate-800 text-slate-400">IMPLEMENTS</span>
          </div>

          <div 
            onClick={() => setSelectedNode("REQ-00847")}
            className="p-4 bg-indigo-950/60 border border-indigo-600/60 rounded-xl text-center cursor-pointer hover:scale-105 transition shadow-lg"
          >
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wide">BusinessRequirement</span>
            <p className="font-mono text-sm font-semibold text-slate-100 mt-1">REQ-00847</p>
            <p className="text-xs text-slate-300">Automated EOD Journal Sync</p>
          </div>
        </div>
      </div>

      {/* Selected Node Details Bar */}
      <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between text-xs text-slate-300">
        <div>Selected Node: <strong className="text-indigo-400 font-mono">{selectedNode}</strong></div>
        <div>State: <span className="bg-emerald-950 border border-emerald-700 text-emerald-300 px-2 py-0.5 rounded">APPROVED</span></div>
      </div>
    </div>
  );
};
