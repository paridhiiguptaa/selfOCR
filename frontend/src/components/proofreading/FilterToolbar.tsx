import React from 'react';
import { CheckCheck, XCircle, RotateCcw, Undo2, Redo2, ArrowLeftRight, HelpCircle, ShieldCheck } from 'lucide-react';

interface FilterToolbarProps {
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
  onAcceptAll: () => void;
  onRejectAll: () => void;
  onAcceptHighConfidence: () => void;
  onReset: () => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  isComparing: boolean;
  onToggleCompare: () => void;
  onToggleLegend: () => void;
}

export const FilterToolbar: React.FC<FilterToolbarProps> = ({
  selectedCategory,
  onSelectCategory,
  onAcceptAll,
  onRejectAll,
  onAcceptHighConfidence,
  onReset,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  isComparing,
  onToggleCompare,
  onToggleLegend,
}) => {
  const categories = [
    { id: 'All', label: 'All Issues' },
    { id: 'Spelling Correction', label: 'Spelling' },
    { id: 'Grammar Correction', label: 'Grammar' },
    { id: 'Missing Word', label: 'Missing Words' },
    { id: 'Punctuation Improvement', label: 'Punctuation' },
    { id: 'OCR Confidence Recovery', label: 'OCR Noise' },
  ];

  return (
    <div className="w-full flex flex-col md:flex-row items-center justify-between gap-3 bg-slate-900/90 p-3.5 rounded-2xl border border-slate-800 shadow-md">
      {/* Left: Category Pills */}
      <div className="flex items-center space-x-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => onSelectCategory(cat.id)}
            className={`px-3 py-1.5 rounded-xl font-bold text-xs transition-all whitespace-nowrap ${
              selectedCategory === cat.id
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20 border border-blue-400/30'
                : 'bg-slate-950/70 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Right: Actions Toolbar */}
      <div className="flex items-center space-x-2 w-full md:w-auto justify-end overflow-x-auto">
        {/* Undo / Redo */}
        <button
          onClick={onUndo}
          disabled={!canUndo}
          className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          title="Undo Correction"
        >
          <Undo2 className="w-4 h-4" />
        </button>
        <button
          onClick={onRedo}
          disabled={!canRedo}
          className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          title="Redo Correction"
        >
          <Redo2 className="w-4 h-4" />
        </button>

        {/* Legend */}
        <button
          onClick={onToggleLegend}
          className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 hover:text-white transition-all"
          title="View Color Legend"
        >
          <HelpCircle className="w-4 h-4 text-blue-400" />
        </button>

        {/* Comparison Toggle */}
        <button
          onClick={onToggleCompare}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl font-bold text-xs border transition-all ${
            isComparing
              ? 'bg-indigo-600 text-white border-indigo-400'
              : 'bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700'
          }`}
        >
          <ArrowLeftRight className="w-3.5 h-3.5 text-indigo-400" />
          <span>Compare</span>
        </button>

        {/* Bulk Accept High Confidence */}
        <button
          onClick={onAcceptHighConfidence}
          className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 font-bold text-xs transition-all"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden sm:inline">Accept High Conf (≥80%)</span>
          <span className="sm:hidden">Auto Accept</span>
        </button>

        {/* Bulk Accept All */}
        <button
          onClick={onAcceptAll}
          className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition-all"
        >
          <CheckCheck className="w-3.5 h-3.5" />
          <span>Accept All</span>
        </button>

        {/* Bulk Reject All */}
        <button
          onClick={onRejectAll}
          className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-red-500/20 text-slate-300 hover:text-red-300 border border-slate-700 font-bold text-xs transition-all"
        >
          <XCircle className="w-3.5 h-3.5 text-red-400" />
          <span className="hidden sm:inline">Reject All</span>
        </button>

        {/* Reset */}
        <button
          onClick={onReset}
          className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-amber-400 transition-all"
          title="Reset to Original OCR Text"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
