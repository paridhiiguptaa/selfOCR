import React from 'react';
import type { CorrectionSuggestionData } from '../../types/ocr';
import { Check, X, EyeOff, Info, ArrowRight, ShieldCheck } from 'lucide-react';

interface SuggestionCardProps {
  suggestion: CorrectionSuggestionData;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  onIgnore: (id: string) => void;
  onClose?: () => void;
}

export const SuggestionCard: React.FC<SuggestionCardProps> = ({
  suggestion,
  onAccept,
  onReject,
  onIgnore,
  onClose,
}) => {
  const getCategoryBadgeClass = (category: string) => {
    switch (category) {
      case 'Spelling Correction':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'Grammar Correction':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'Missing Word':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'Punctuation Improvement':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'Capitalization':
        return 'bg-teal-500/20 text-teal-300 border-teal-500/30';
      case 'OCR Confidence Recovery':
        return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30';
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
    }
  };

  return (
    <div className="w-80 bg-slate-900 border border-slate-700/80 rounded-2xl p-4 shadow-2xl z-50 text-slate-100 flex flex-col space-y-3 animate-in fade-in zoom-in-95 duration-150">
      {/* Card Header: Category & Confidence */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${getCategoryBadgeClass(suggestion.category)}`}>
          {suggestion.category}
        </span>
        <div className="flex items-center space-x-1.5 text-xs text-slate-400 font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
          <span>{Math.round(suggestion.confidence_score * 100)}%</span>
          {onClose && (
            <button
              onClick={onClose}
              className="ml-2 text-slate-500 hover:text-slate-300 p-0.5 rounded-md hover:bg-slate-800"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Before / After Preview */}
      <div className="flex items-center justify-between bg-slate-950 p-2.5 rounded-xl border border-slate-800 font-mono text-xs">
        <span className="line-through text-red-400/90 font-medium px-1 max-w-[110px] truncate">
          {suggestion.original_text}
        </span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
        <span className="text-emerald-400 font-bold px-1 max-w-[110px] truncate">
          {suggestion.proposed_correction}
        </span>
      </div>

      {/* Rationale Explanation */}
      <div className="flex items-start space-x-2 text-xs text-slate-300 bg-slate-800/40 p-2.5 rounded-xl border border-slate-800">
        <Info className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">{suggestion.explanation}</p>
      </div>

      {/* Action Buttons: Accept / Reject / Ignore */}
      <div className="grid grid-cols-3 gap-2 pt-1">
        <button
          onClick={() => onAccept(suggestion.suggestion_id)}
          className="flex items-center justify-center space-x-1 py-1.5 px-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs rounded-xl shadow-md shadow-emerald-600/20 transition-all"
        >
          <Check className="w-3.5 h-3.5" />
          <span>Accept</span>
        </button>

        <button
          onClick={() => onReject(suggestion.suggestion_id)}
          className="flex items-center justify-center space-x-1 py-1.5 px-2 bg-slate-800 hover:bg-red-500/20 hover:text-red-300 text-slate-300 font-bold text-xs rounded-xl border border-slate-700 hover:border-red-500/40 transition-all"
        >
          <X className="w-3.5 h-3.5 text-red-400" />
          <span>Reject</span>
        </button>

        <button
          onClick={() => onIgnore(suggestion.suggestion_id)}
          className="flex items-center justify-center space-x-1 py-1.5 px-2 bg-slate-800 hover:bg-slate-700 text-slate-400 font-medium text-xs rounded-xl border border-slate-700 transition-all"
        >
          <EyeOff className="w-3.5 h-3.5" />
          <span>Ignore</span>
        </button>
      </div>
    </div>
  );
};
