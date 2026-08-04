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
      className={`fixed top-20 right-4 z-40 h-[calc(100vh-6rem)] transition-all duration-300 flex select-none ${
        isOpen ? 'w-80 sm:w-96' : 'w-12'
      }`}
    >
      {/* Toggle Collapse Button */}
      <button
        onClick={onToggle}
        className="h-12 w-12 bg-white border border-slate-200 rounded-l-2xl flex items-center justify-center text-slate-600 hover:text-blue-600 hover:bg-blue-50 shadow-saas self-start mt-4 cursor-pointer"
        title={isOpen ? 'Collapse Suggestion Sidebar' : 'Expand Suggestion Sidebar'}
      >
        {isOpen ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
      </button>

      {isOpen && (
        <div className="flex-1 bg-white border border-slate-200 rounded-r-2xl rounded-l-none shadow-saas-lg flex flex-col overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <h4 className="font-extrabold text-sm text-slate-900">Suggestions Feed</h4>
            </div>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-100">
              {filteredSuggestions.length} items
            </span>
          </div>

          {/* Search & Category Filter */}
          <div className="p-3 border-b border-slate-100 space-y-2 bg-white">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search suggestions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-1.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white"
              />
            </div>

            <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
              <Filter className="w-3 h-3 text-slate-400 flex-shrink-0" />
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setFilterCategory(cat)}
                  className={`text-[10px] font-bold px-2.5 py-1 rounded-lg transition-all whitespace-nowrap cursor-pointer ${
                    filterCategory === cat
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat === 'All' ? 'All' : cat.replace(' Correction', '')}
                </button>
              ))}
            </div>
          </div>

          {/* List Feed */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-slate-50/30">
            {filteredSuggestions.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-center p-4">
                <Check className="w-8 h-8 text-emerald-500 mb-2 opacity-80" />
                <p className="text-xs font-bold text-slate-800">No pending suggestions</p>
                <p className="text-[11px] text-slate-500 mt-1">All issues have been resolved or filtered out.</p>
              </div>
            ) : (
              filteredSuggestions.map((sug) => {
                const isSelected = selectedId === sug.suggestion_id;
                return (
                  <div
                    key={sug.suggestion_id}
                    onClick={() => onSelectSuggestion(sug)}
                    className={`p-3 rounded-2xl border transition-all cursor-pointer flex flex-col space-y-2 ${
                      isSelected
                        ? 'bg-blue-50/70 border-blue-400 shadow-xs'
                        : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-xs'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] text-slate-500 font-bold">
                      <span className="font-extrabold text-blue-600">Line {sug.line_number}</span>
                      <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                        {sug.category}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 text-xs font-mono">
                      <span className="line-through text-rose-600 font-semibold truncate max-w-[120px]">
                        {sug.original_text}
                      </span>
                      <span className="text-slate-400">→</span>
                      <span className="text-emerald-700 font-bold truncate max-w-[120px]">
                        {sug.proposed_correction}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed font-medium">
                      {sug.explanation}
                    </p>

                    <div className="flex items-center justify-end space-x-2 pt-1 border-t border-slate-100">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onReject(sug.suggestion_id);
                        }}
                        className="px-2 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 text-rose-600 text-[10px] font-bold transition-all cursor-pointer"
                      >
                        Reject
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onAccept(sug.suggestion_id);
                        }}
                        className="px-2.5 py-1 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-[10px] font-bold shadow-xs transition-all cursor-pointer"
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
