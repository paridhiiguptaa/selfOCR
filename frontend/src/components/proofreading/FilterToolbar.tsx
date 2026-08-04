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
    <div className="w-full flex flex-col md:flex-row items-center justify-between gap-3 bg-slate-50/80 p-3 rounded-2xl border border-slate-200/80 shadow-2xs">
      {/* Left: Segmented Filter Chips */}
      <div className="flex items-center space-x-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0 no-scrollbar">
        {categories.map((cat) => {
          const isSelected = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => onSelectCategory(cat.id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs transition-all whitespace-nowrap cursor-pointer ${
                isSelected
                  ? 'bg-blue-600 text-white font-extrabold shadow-xs border border-blue-600'
                  : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200 hover:bg-slate-100 font-semibold'
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Right: Floating Action Buttons */}
      <div className="flex items-center space-x-2 w-full md:w-auto justify-end overflow-x-auto">
        {/* Undo / Redo */}
        <button
          onClick={onUndo}
          disabled={!canUndo}
          className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed shadow-2xs transition-all cursor-pointer"
          title="Undo Correction"
        >
          <Undo2 className="w-4 h-4" />
        </button>
        <button
          onClick={onRedo}
          disabled={!canRedo}
          className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed shadow-2xs transition-all cursor-pointer"
          title="Redo Correction"
        >
          <Redo2 className="w-4 h-4" />
        </button>

        {/* Legend */}
        <button
          onClick={onToggleLegend}
          className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-blue-600 hover:bg-blue-50 shadow-2xs transition-all cursor-pointer"
          title="View Color Legend"
        >
          <HelpCircle className="w-4 h-4 text-blue-600" />
        </button>

        {/* Comparison Toggle */}
        <button
          onClick={onToggleCompare}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs border transition-all cursor-pointer font-bold ${
            isComparing
              ? 'bg-indigo-50 text-indigo-700 border-indigo-200 shadow-2xs'
              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
          }`}
        >
          <ArrowLeftRight className="w-3.5 h-3.5 text-indigo-600" />
          <span>Compare</span>
        </button>

        {/* Bulk Accept High Confidence */}
        <button
          onClick={onAcceptHighConfidence}
          className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-extrabold text-xs shadow-2xs transition-all cursor-pointer"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
          <span className="hidden sm:inline">Accept High Conf (≥80%)</span>
          <span className="sm:hidden">Auto Accept</span>
        </button>

        {/* Bulk Accept All */}
        <button
          onClick={onAcceptAll}
          className="flex items-center space-x-1 px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs shadow-xs transition-all cursor-pointer"
        >
          <CheckCheck className="w-3.5 h-3.5" />
          <span>Accept All</span>
        </button>

        {/* Bulk Reject All */}
        <button
          onClick={onRejectAll}
          className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-extrabold text-xs transition-all cursor-pointer"
        >
          <XCircle className="w-3.5 h-3.5 text-rose-600" />
          <span className="hidden sm:inline">Reject All</span>
        </button>

        {/* Reset */}
        <button
          onClick={onReset}
          className="p-2 rounded-xl bg-white border border-slate-200 text-slate-500 hover:text-amber-600 hover:bg-amber-50 shadow-2xs transition-all cursor-pointer"
          title="Reset to Original OCR Text"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
