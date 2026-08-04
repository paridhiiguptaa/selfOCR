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
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'Grammar Correction':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'Missing Word':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'Punctuation Improvement':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'Capitalization':
        return 'bg-teal-50 text-teal-700 border-teal-200';
      case 'OCR Confidence Recovery':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      default:
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    }
  };

  return (
    <div className="w-80 bg-white border border-slate-200/90 rounded-2xl p-4 shadow-saas-lg z-50 text-slate-900 flex flex-col space-y-3 animate-fadeIn">
      {/* Card Header: Category & Confidence */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-100">
        <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${getCategoryBadgeClass(suggestion.category)}`}>
          {suggestion.category}
        </span>
        <div className="flex items-center space-x-1.5 text-xs text-slate-500 font-bold">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
          <span>{Math.round(suggestion.confidence_score * 100)}%</span>
          {onClose && (
            <button
              onClick={onClose}
              className="ml-2 text-slate-400 hover:text-slate-600 p-0.5 rounded-md hover:bg-slate-100"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Before / After Preview */}
      <div className="flex items-center justify-between bg-slate-50 p-2.5 rounded-xl border border-slate-200 font-mono text-xs">
        <span className="line-through text-rose-600 font-semibold px-1 max-w-[110px] truncate">
          {suggestion.original_text}
        </span>
        <ArrowRight className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
        <span className="text-emerald-700 font-bold px-1 max-w-[110px] truncate">
          {suggestion.proposed_correction}
        </span>
      </div>

      {/* Rationale Explanation */}
      <div className="flex items-start space-x-2 text-xs text-slate-600 bg-blue-50/50 p-2.5 rounded-xl border border-blue-100">
        <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed font-medium">{suggestion.explanation}</p>
      </div>

      {/* Action Buttons: Accept / Reject / Ignore */}
      <div className="grid grid-cols-3 gap-2 pt-1">
        <button
          onClick={() => onAccept(suggestion.suggestion_id)}
          className="flex items-center justify-center space-x-1 py-1.5 px-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors cursor-pointer"
        >
          <Check className="w-3.5 h-3.5" />
          <span>Accept</span>
        </button>

        <button
          onClick={() => onReject(suggestion.suggestion_id)}
          className="flex items-center justify-center space-x-1 py-1.5 px-2 bg-slate-100 hover:bg-rose-50 hover:text-rose-700 text-slate-700 font-bold text-xs rounded-xl border border-slate-200 transition-colors cursor-pointer"
        >
          <X className="w-3.5 h-3.5 text-rose-500" />
          <span>Reject</span>
        </button>

        <button
          onClick={() => onIgnore(suggestion.suggestion_id)}
          className="flex items-center justify-center space-x-1 py-1.5 px-2 bg-slate-50 hover:bg-slate-100 text-slate-500 font-semibold text-xs rounded-xl border border-slate-200 transition-colors cursor-pointer"
        >
          <EyeOff className="w-3.5 h-3.5" />
          <span>Ignore</span>
        </button>
      </div>
    </div>
  );
};
