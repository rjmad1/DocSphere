import React, { useState } from 'react';

/**
 * EKOS Main Project Workspace
 * Resizable Three-Panel Layout:
 * 1. Left Panel: Source Documents & Ingestion Queue
 * 2. Center Panel: Document Editor & ASST View
 * 3. Right Panel: Interactive Knowledge Graph & AI Assistant
 */
export const ProjectWorkspace: React.FC = () => {
  const [selectedDoc, setSelectedDoc] = useState<string>("DOC-BRD-001");
  const [activeTab, setActiveTab] = useState<'editor' | 'graph' | 'impact'>('editor');

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-100 font-sans overflow-hidden">
      {/* Left Sidebar - Source Documents */}
      <aside className="w-80 border-r border-slate-800 bg-slate-900 p-4 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-lg text-indigo-400">DocSphere EKOS</h2>
          <span className="text-xs bg-indigo-950 border border-indigo-700 text-indigo-300 px-2 py-0.5 rounded-full">v1.0 MVP</span>
        </div>
        
        <div className="flex flex-col gap-2">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Project Ingestion</h3>
          <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 hover:border-indigo-500/50 cursor-pointer transition">
            <p className="text-sm font-medium text-slate-200">DOC-IN-001.pdf</p>
            <p className="text-xs text-slate-400">Ingested • 24 Entities Extracted</p>
          </div>
        </div>

        <div className="flex flex-col gap-2 flex-1">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Project Initiation Artifacts</h3>
          <ul className="space-y-1">
            {['Business Case', 'Project Charter', 'BRD (DOC-BRD-001)', 'RTM Matrix', 'Solution Design'].map((art, idx) => (
              <li 
                key={idx}
                onClick={() => setSelectedDoc(art)}
                className={`p-2 text-sm rounded cursor-pointer transition ${art.includes('BRD') ? 'bg-indigo-600/20 text-indigo-300 font-medium border border-indigo-500/30' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
              >
                📄 {art}
              </li>
            ))}
          </ul>
        </div>
      </aside>

      {/* Center Panel - Main Document Workspace */}
      <main className="flex-1 flex flex-col border-r border-slate-800 bg-slate-950">
        <header className="h-14 border-b border-slate-800 px-6 flex items-center justify-between bg-slate-900/40">
          <div className="flex items-center gap-3">
            <h1 className="font-semibold text-slate-100">{selectedDoc}</h1>
            <span className="text-xs bg-emerald-950 border border-emerald-700 text-emerald-300 px-2 py-0.5 rounded">APPROVED (v1.0)</span>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setActiveTab('editor')}
              className={`px-3 py-1.5 text-xs font-medium rounded transition ${activeTab === 'editor' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Document Editor
            </button>
            <button 
              onClick={() => setActiveTab('graph')}
              className={`px-3 py-1.5 text-xs font-medium rounded transition ${activeTab === 'graph' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Knowledge Graph
            </button>
            <button 
              onClick={() => setActiveTab('impact')}
              className={`px-3 py-1.5 text-xs font-medium rounded transition ${activeTab === 'impact' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Change Impact Diffs
            </button>
          </div>
        </header>

        <div className="flex-1 p-6 overflow-y-auto">
          {activeTab === 'editor' && (
            <div className="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-xl">
              <h2 className="text-2xl font-bold text-slate-100 mb-4">1. Business Requirements Specification</h2>
              <p className="text-slate-300 mb-6 leading-relaxed">
                The enterprise system shall execute automated multi-currency journal reconciliations at end-of-day.
                <span className="ml-2 inline-flex items-center gap-1 text-xs bg-indigo-950 border border-indigo-700 text-indigo-300 px-2 py-0.5 rounded-full cursor-pointer hover:bg-indigo-900">
                  🏷️ REQ-00847
                </span>
                <span className="ml-1 inline-flex items-center gap-1 text-xs bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded hover:text-slate-200">
                  📌 DOC-IN-001.pdf (p.14)
                </span>
              </p>
            </div>
          )}

          {activeTab === 'graph' && (
            <div className="h-full min-h-[400px] bg-slate-900 border border-slate-800 rounded-xl p-6 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-indigo-600/20 text-indigo-400 flex items-center justify-center mx-auto mb-3 border border-indigo-500/40">
                  🕸️
                </div>
                <h3 className="font-medium text-slate-200">Cytoscape Knowledge Graph Visualizer</h3>
                <p className="text-xs text-slate-400 mt-1">Showing 42 Entity Nodes & 68 Semantic Edges for Project Initiation</p>
              </div>
            </div>
          )}

          {activeTab === 'impact' && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-slate-200 mb-2">Living Documentation Change Impact Analysis</h3>
              <p className="text-sm text-slate-400 mb-4">Upstream change detected in <code className="text-indigo-400 bg-slate-950 px-1.5 py-0.5 rounded">DOC-IN-001.pdf</code></p>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-red-950/30 border border-red-900/50 rounded-lg">
                  <span className="text-xs font-bold text-red-400 uppercase">Current Version (v1.0)</span>
                  <p className="text-sm text-slate-300 mt-2">Reconciliation occurs weekly on Friday EOD.</p>
                </div>
                <div className="p-4 bg-emerald-950/30 border border-emerald-900/50 rounded-lg">
                  <span className="text-xs font-bold text-emerald-400 uppercase">Recommended Update (v1.1)</span>
                  <p className="text-sm text-slate-300 mt-2">Reconciliation occurs daily on automated EOD schedule.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Right Sidebar - AI Assistant & Context */}
      <aside className="w-80 border-l border-slate-800 bg-slate-900 p-4 flex flex-col gap-4">
        <h3 className="font-semibold text-sm text-slate-200">AI Program Director Assistant</h3>
        <div className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 overflow-y-auto space-y-3">
          <div className="p-2 bg-indigo-950/40 border border-indigo-800/40 rounded text-indigo-200">
            🤖 <strong>Chief of Staff Agent:</strong> Analyzed project initiation scope. 100% of requirements map to valid business capabilities in the graph.
          </div>
        </div>
      </aside>
    </div>
  );
};
