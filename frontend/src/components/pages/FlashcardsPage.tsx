import React from 'react';
import { FlashcardHub } from '../flashcards/FlashcardHub';
import type { CorrectionSuggestionData } from '../../types/ocr';
import { GraduationCap, Sparkles, ArrowRight } from 'lucide-react';

interface FlashcardsPageProps {
  exportedText: string;
  acceptedSuggestions: CorrectionSuggestionData[];
  documentTitle: string;
  isDocumentExported: boolean;
  onNavigateToProofreading: () => void;
}

export const FlashcardsPage: React.FC<FlashcardsPageProps> = ({
  exportedText,
  acceptedSuggestions,
  documentTitle,
  isDocumentExported,
  onNavigateToProofreading,
}) => {
  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-indigo-50 text-indigo-600 font-bold flex items-center justify-center border border-indigo-100 flex-shrink-0">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-extrabold text-slate-900">Stage 5: Educational Flashcards Hub</h2>
              <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                Vocabulary & Study Decks
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Review child-friendly vocabulary cards, context sentences, and study modes generated from your document.
            </p>
          </div>
        </div>

        <button
          onClick={onNavigateToProofreading}
          className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl bg-white hover:bg-slate-50 text-slate-700 font-extrabold text-xs border border-slate-200 shadow-xs transition-all duration-150 transform hover:-translate-y-0.5 cursor-pointer whitespace-nowrap"
        >
          <Sparkles className="w-4 h-4 text-purple-600" />
          <span>Back to Proofreading</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Main Flashcards Workspace */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-saas">
        <FlashcardHub
          exportedText={exportedText}
          acceptedSuggestions={acceptedSuggestions}
          documentTitle={documentTitle}
          isDocumentExported={isDocumentExported}
          onTriggerExport={onNavigateToProofreading}
        />
      </div>
    </div>
  );
};
