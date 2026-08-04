import React, { useState } from 'react';

interface DocumentEditorProps {
  documentId: string;
  title: string;
  initialContent?: string;
  onContentChange?: (content: string) => void;
}

export const DocumentEditor: React.FC<DocumentEditorProps> = ({
  documentId,
  title,
  initialContent = "The system shall execute automated multi-currency journal reconciliations at end-of-day.",
  onContentChange
}) => {
  const [content, setContent] = useState(initialContent);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    if (onContentChange) {
      onContentChange(e.target.value);
    }
  };

  return (
    <div className="w-full bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl flex flex-col gap-4 text-slate-100">
      {/* Document Toolbar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100">{title}</h2>
          <p className="text-xs text-slate-400">ID: <code className="text-indigo-400">{documentId}</code> • TipTap ASST Synchronized</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1 bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 text-xs font-semibold rounded hover:bg-indigo-600/30">
            ➕ Add Entity Chip
          </button>
          <button className="px-3 py-1 bg-slate-800 text-slate-300 text-xs font-semibold rounded hover:bg-slate-700">
            📌 Insert Citation
          </button>
        </div>
      </div>

      {/* Editor Body */}
      <div className="flex flex-col gap-3">
        <textarea
          data-testid="tiptap-editor-pane"
          value={content}
          onChange={handleTextChange}
          rows={8}
          className="w-full bg-slate-950 border border-slate-800 rounded-lg p-4 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 font-mono leading-relaxed resize-none"
        />

        {/* Live Entity Chips Footer */}
        <div className="flex items-center gap-2 pt-2 border-t border-slate-800/60">
          <span className="text-xs text-slate-400 font-medium">Bound Entities:</span>
          <span data-testid="entity-node-tag" className="text-xs bg-indigo-950 border border-indigo-700 text-indigo-300 px-2.5 py-0.5 rounded-full flex items-center gap-1 cursor-pointer">
            🏷️ REQ-00847
          </span>
          <span className="text-xs bg-indigo-950 border border-indigo-700 text-indigo-300 px-2.5 py-0.5 rounded-full flex items-center gap-1 cursor-pointer">
            🏷️ CAP-0012
          </span>
        </div>
      </div>
    </div>
  );
};
