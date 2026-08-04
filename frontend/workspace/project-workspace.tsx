import React, { useState } from 'react';
import { DocumentEditor } from '../components/document-editor';
import { KnowledgeExplorer } from '../components/knowledge-explorer';
import { ImpactDiffViewer } from '../components/impact-diff-viewer';

/**
 * EKOS Main Project Workspace
 * Resizable Three-Panel Layout:
 * 1. Left Panel: Source Documents & Ingestion Queue
 * 2. Center Panel: Document Editor & ASST View
 * 3. Right Panel: Interactive Knowledge Graph & AI Assistant
 */
export const ProjectWorkspace: React.FC = () => {
  const [selectedDoc, setSelectedDoc] = useState<string>("DOC-BRD-001");

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

      {/* Main Multi-Panel Row Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Panel 1: Document Editor */}
        <div className="flex-1 border-r border-slate-800 p-4 overflow-y-auto bg-slate-950">
          <DocumentEditor documentId="DOC-BRD-001" title={selectedDoc} />
        </div>

        {/* Panel 2: Knowledge Graph */}
        <div className="flex-1 border-r border-slate-800 p-4 overflow-y-auto bg-slate-950">
          <KnowledgeExplorer rootEntityId="REQ-00847" />
        </div>

        {/* Panel 3: Change Impact Diff Viewer */}
        <div className="flex-1 p-4 overflow-y-auto bg-slate-950">
          <ImpactDiffViewer />
        </div>
      </div>
    </div>
  );
};
