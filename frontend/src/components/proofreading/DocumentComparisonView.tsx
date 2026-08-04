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
    <div className="w-full flex flex-col space-y-4 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2">
          <ArrowLeftRight className="w-5 h-5 text-blue-600" />
          <h3 className="text-base font-extrabold text-slate-900">Document Side-by-Side Comparison</h3>
        </div>
        <button
          onClick={onClose}
          className="text-xs font-extrabold px-3.5 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-xs transition-all cursor-pointer"
        >
          Exit Comparison Mode
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Column: Original OCR Output */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center justify-between text-xs font-bold bg-amber-50 p-3 rounded-xl border border-amber-200 text-amber-900">
            <span className="flex items-center space-x-1.5">
              <FileText className="w-4 h-4 text-amber-600" />
              <span>Original Unedited OCR Transcription</span>
            </span>
          </div>
          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200/80 font-sans text-xs text-slate-800 whitespace-pre-wrap min-h-[400px] max-h-[600px] overflow-y-auto leading-relaxed shadow-inner">
            {originalText}
          </div>
        </div>

        {/* Right Column: AI Corrected Text */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center justify-between text-xs font-bold bg-emerald-50 p-3 rounded-xl border border-emerald-200 text-emerald-900">
            <span className="flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <span>AI Proofread & Corrected Document</span>
            </span>
          </div>
          <div className="bg-blue-50/40 p-5 rounded-2xl border border-blue-100 font-sans text-xs text-slate-900 whitespace-pre-wrap min-h-[400px] max-h-[600px] overflow-y-auto leading-relaxed shadow-inner font-medium">
            {correctedText}
          </div>
        </div>
      </div>
    </div>
  );
};
