import React, { useState, useRef, useEffect } from 'react';
import type { CorrectionSuggestionData } from '../../types/ocr';
import { SuggestionCard } from './SuggestionCard';

interface ProofreadingEditorProps {
  text: string;
  suggestions: CorrectionSuggestionData[];
  acceptedIds: string[];
  rejectedIds: string[];
  selectedCategory: string;
  selectedSuggestionId: string | null;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  onIgnore: (id: string) => void;
}

export const ProofreadingEditor: React.FC<ProofreadingEditorProps> = ({
  text,
  suggestions,
  acceptedIds,
  rejectedIds,
  selectedCategory,
  selectedSuggestionId,
  onAccept,
  onReject,
  onIgnore,
}) => {
  const [activeSuggestion, setActiveSuggestion] = useState<CorrectionSuggestionData | null>(null);
  const [popoverPos, setPopoverPos] = useState<{ top: number; left: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Active pending suggestions matching current filter
  const pendingSuggestions = suggestions.filter((sug) => {
    const isPending = !acceptedIds.includes(sug.suggestion_id) && !rejectedIds.includes(sug.suggestion_id);
    if (!isPending) return false;
    if (selectedCategory !== 'All' && sug.category !== selectedCategory) return false;
    return true;
  });

  // Focus and pop up suggestion if selected from sidebar
  useEffect(() => {
    if (selectedSuggestionId) {
      const match = pendingSuggestions.find((s) => s.suggestion_id === selectedSuggestionId);
      if (match) {
        setActiveSuggestion(match);
      }
    }
  }, [selectedSuggestionId]);

  const getHighlightStyle = (category: string, isSelected: boolean) => {
    let base = 'cursor-pointer transition-all px-1 py-0.5 rounded-md mx-0.5 font-medium ';
    if (isSelected) {
      return base + 'bg-blue-600 text-white font-extrabold shadow-xs ring-2 ring-blue-400';
    }

    switch (category) {
      case 'Spelling Correction':
        return base + 'border-b-2 border-dashed border-rose-500 bg-rose-50 text-rose-800 hover:bg-rose-100';
      case 'Grammar Correction':
        return base + 'border-b-2 border-dashed border-amber-500 bg-amber-50 text-amber-800 hover:bg-amber-100';
      case 'Missing Word':
        return base + 'border-b-2 border-dashed border-blue-500 bg-blue-50 text-blue-800 hover:bg-blue-100';
      case 'Punctuation Improvement':
        return base + 'border-b-2 border-dashed border-purple-500 bg-purple-50 text-purple-800 hover:bg-purple-100';
      case 'Capitalization':
        return base + 'border-b-2 border-dashed border-teal-500 bg-teal-50 text-teal-800 hover:bg-teal-100';
      case 'OCR Confidence Recovery':
        return base + 'border-b-2 border-dashed border-indigo-500 bg-indigo-50 text-indigo-800 hover:bg-indigo-100';
      default:
        return base + 'border-b-2 border-dashed border-emerald-500 bg-emerald-50 text-emerald-800 hover:bg-emerald-100';
    }
  };

  // Build character offset tokens for rendering highlights inline
  const renderHighlightedContent = () => {
    if (!text) return null;
    if (pendingSuggestions.length === 0) {
      return <span className="whitespace-pre-wrap">{text}</span>;
    }

    // Sort pending suggestions by start_offset
    const sorted = [...pendingSuggestions].sort((a, b) => a.start_offset - b.start_offset);
    const elements: React.ReactNode[] = [];
    let lastIndex = 0;

    sorted.forEach((sug) => {
      const { start_offset, end_offset, category, suggestion_id } = sug;

      // Ensure valid boundaries
      if (start_offset >= lastIndex && end_offset <= text.length && start_offset < end_offset) {
        // Plain text segment before highlight
        if (start_offset > lastIndex) {
          elements.push(
            <span key={`plain_${lastIndex}_${start_offset}`}>
              {text.slice(lastIndex, start_offset)}
            </span>
          );
        }

        const isSelected = activeSuggestion?.suggestion_id === suggestion_id;
        const highlightedText = text.slice(start_offset, end_offset);

        elements.push(
          <span
            key={`sug_${suggestion_id}`}
            onClick={(e) => {
              e.stopPropagation();
              const rect = e.currentTarget.getBoundingClientRect();
              setPopoverPos({ top: rect.bottom + 8, left: Math.max(16, rect.left) });
              setActiveSuggestion(sug);
            }}
            className={getHighlightStyle(category, isSelected)}
            title={`${category}: ${sug.explanation}`}
          >
            {highlightedText}
          </span>
        );

        lastIndex = end_offset;
      }
    });

    // Remaining text after last suggestion
    if (lastIndex < text.length) {
      elements.push(<span key={`plain_end`}>{text.slice(lastIndex)}</span>);
    }

    return <div className="whitespace-pre-wrap leading-relaxed">{elements}</div>;
  };

  return (
    <div ref={containerRef} className="relative w-full flex flex-col space-y-3">
      {/* Professional White Document Paper Editor Surface */}
      <div className="w-full bg-white p-6 sm:p-10 rounded-2xl border border-slate-200/80 font-sans text-slate-800 text-sm sm:text-base leading-relaxed tracking-normal min-h-[480px] shadow-md shadow-slate-200/50 focus-within:border-blue-500/80 transition-all overflow-x-auto select-text">
        {renderHighlightedContent()}
      </div>

      {/* Floating Suggestion Popover Card */}
      {activeSuggestion && (
        <div
          className="fixed z-50 animate-in fade-in zoom-in-95 duration-150"
          style={{
            top: popoverPos ? popoverPos.top : '30%',
            left: popoverPos ? popoverPos.left : '40%',
          }}
        >
          <SuggestionCard
            suggestion={activeSuggestion}
            onAccept={(id) => {
              onAccept(id);
              setActiveSuggestion(null);
            }}
            onReject={(id) => {
              onReject(id);
              setActiveSuggestion(null);
            }}
            onIgnore={(id) => {
              onIgnore(id);
              setActiveSuggestion(null);
            }}
            onClose={() => setActiveSuggestion(null)}
          />
        </div>
      )}
    </div>
  );
};
