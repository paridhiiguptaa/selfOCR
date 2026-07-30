import React from 'react';
import { FileText, Sparkles, ArrowLeftRight } from 'lucide-react';

interface DocumentComparisonViewProps {
  originalText: string;
  correctedText: string;
  onClose: () => void;
}

export const DocumentComparisonView: React.FC<DocumentComparisonViewProps> = ({
  originalText,
  correctedText,
  onClose,
}) => {
  return (
    <div className="w-full flex flex-col space-y-4 bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-2xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <ArrowLeftRight className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Document Comparison & Diff Mode</h3>
        </div>
        <button
          onClick={onClose}
          className="text-xs font-bold px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all"
        >
          Exit Comparison Mode
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Column: Original OCR Output */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-400 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
            <span className="flex items-center space-x-1.5 text-amber-400">
              <FileText className="w-3.5 h-3.5" />
              <span>Original Unedited OCR Transcription</span>
            </span>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap min-h-[400px] max-h-[600px] overflow-y-auto leading-relaxed">
            {originalText}
          </div>
        </div>

        {/* Right Column: AI Corrected Text */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-400 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
            <span className="flex items-center space-x-1.5 text-emerald-400">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Proofread & Corrected Text</span>
            </span>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-emerald-200/90 whitespace-pre-wrap min-h-[400px] max-h-[600px] overflow-y-auto leading-relaxed">
            {correctedText}
          </div>
        </div>
      </div>
    </div>
  );
};
