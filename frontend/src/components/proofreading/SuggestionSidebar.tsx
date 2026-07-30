import React, { useState } from 'react';
import type { CorrectionSuggestionData } from '../../types/ocr';
import { Check, Search, ChevronRight, ChevronLeft, Sparkles, Filter } from 'lucide-react';

interface SuggestionSidebarProps {
  suggestions: CorrectionSuggestionData[];
  acceptedIds: string[];
  rejectedIds: string[];
  selectedId: string | null;
  onSelectSuggestion: (sug: CorrectionSuggestionData) => void;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const SuggestionSidebar: React.FC<SuggestionSidebarProps> = ({
  suggestions,
  acceptedIds,
  rejectedIds,
  selectedId,
  onSelectSuggestion,
  onAccept,
  onReject,
  isOpen,
  onToggle,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const categories = ['All', 'Spelling Correction', 'Grammar Correction', 'Missing Word', 'Punctuation Improvement', 'OCR Confidence Recovery'];

  const filteredSuggestions = suggestions.filter((sug) => {
    const isPending = !acceptedIds.includes(sug.suggestion_id) && !rejectedIds.includes(sug.suggestion_id);
    if (!isPending) return false;

    const matchesCategory = filterCategory === 'All' || sug.category === filterCategory;
    const matchesSearch =
      sug.original_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sug.proposed_correction.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sug.explanation.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesCategory && matchesSearch;
  });

  return (
    <div
      className={`fixed top-20 right-4 z-40 h-[calc(100vh-6rem)] transition-all duration-300 flex ${
        isOpen ? 'w-80 sm:w-96' : 'w-12'
      }`}
    >
      {/* Toggle Collapse Button */}
      <button
        onClick={onToggle}
        className="h-12 w-12 bg-slate-900 border border-slate-800 rounded-l-2xl flex items-center justify-center text-slate-300 hover:text-white hover:bg-slate-800 shadow-xl self-start mt-4"
        title={isOpen ? 'Collapse Suggestion Sidebar' : 'Expand Suggestion Sidebar'}
      >
        {isOpen ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
      </button>

      {isOpen && (
        <div className="flex-1 bg-slate-900/95 backdrop-blur-xl border border-slate-800 rounded-r-2xl rounded-l-none shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <h4 className="font-bold text-sm text-white">Suggestions Feed</h4>
            </div>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {filteredSuggestions.length} items
            </span>
          </div>

          {/* Search & Category Filter */}
          <div className="p-3 border-b border-slate-800/80 space-y-2 bg-slate-950/40">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search suggestions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
              <Filter className="w-3 h-3 text-slate-500 flex-shrink-0" />
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setFilterCategory(cat)}
                  className={`text-[10px] font-bold px-2.5 py-1 rounded-lg transition-all whitespace-nowrap ${
                    filterCategory === cat
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-slate-800/80 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {cat === 'All' ? 'All' : cat.replace(' Correction', '')}
                </button>
              ))}
            </div>
          </div>

          {/* List Feed */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {filteredSuggestions.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-center p-4">
                <Check className="w-8 h-8 text-emerald-400 mb-2 opacity-80" />
                <p className="text-xs font-semibold text-slate-300">No pending suggestions</p>
                <p className="text-[11px] text-slate-500 mt-1">All issues have been resolved or filtered out.</p>
              </div>
            ) : (
              filteredSuggestions.map((sug) => {
                const isSelected = selectedId === sug.suggestion_id;
                return (
                  <div
                    key={sug.suggestion_id}
                    onClick={() => onSelectSuggestion(sug)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer flex flex-col space-y-2 ${
                      isSelected
                        ? 'bg-slate-800 border-indigo-500 shadow-md ring-1 ring-indigo-500/50'
                        : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                      <span className="font-bold text-indigo-400">Line {sug.line_number}</span>
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300">
                        {sug.category}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 text-xs font-mono">
                      <span className="line-through text-red-400 truncate max-w-[120px]">
                        {sug.original_text}
                      </span>
                      <span className="text-slate-600">→</span>
                      <span className="text-emerald-400 font-bold truncate max-w-[120px]">
                        {sug.proposed_correction}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                      {sug.explanation}
                    </p>

                    <div className="flex items-center justify-end space-x-2 pt-1 border-t border-slate-800/50">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onReject(sug.suggestion_id);
                        }}
                        className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-red-500/20 text-red-400 text-[10px] font-bold transition-all"
                      >
                        Reject
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onAccept(sug.suggestion_id);
                        }}
                        className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-bold shadow-sm transition-all"
                      >
                        Accept
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};
