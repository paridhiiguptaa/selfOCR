import React, { useState } from 'react';
import type { FlashcardData } from '../../types/ocr';
import {
  RotateCw,
  CheckCircle2,
  Bookmark,
  BookOpen,
  Sparkles,
  Award,
  Lightbulb,
  ChevronRight,
  AlertCircle
} from 'lucide-react';

interface FlashcardViewerProps {
  card: FlashcardData;
  cardIndex: number;
  totalCards: number;
  onToggleMastered: (cardId: string) => void;
  onToggleBookmark: (cardId: string) => void;
  onNext: () => void;
  onPrev: () => void;
}

export const FlashcardViewer: React.FC<FlashcardViewerProps> = ({
  card,
  cardIndex,
  totalCards,
  onToggleMastered,
  onToggleBookmark,
  onNext,
  onPrev,
}) => {
  const [isFlipped, setIsFlipped] = useState<boolean>(false);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const getDifficultyBadge = (diff: string) => {
    switch (diff) {
      case 'Easy':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'Hard':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-amber-50 text-amber-700 border-amber-200';
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col space-y-4">
      {/* Top Card Controls & Telemetry Header */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-extrabold text-slate-700">
            Card {cardIndex + 1} of {totalCards}
          </span>
          <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border ${getDifficultyBadge(card.difficulty)}`}>
            {card.difficulty}
          </span>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-50 text-blue-700 border border-blue-100">
            {card.category}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => onToggleBookmark(card.id)}
            className={`p-2 rounded-xl border transition-all cursor-pointer ${
              card.is_bookmarked
                ? 'bg-amber-50 border-amber-200 text-amber-600'
                : 'bg-white border-slate-200 text-slate-500 hover:text-slate-900 hover:bg-slate-50 shadow-2xs'
            }`}
            title="Bookmark Flashcard"
          >
            <Bookmark className="w-4 h-4 fill-current" />
          </button>
          <button
            onClick={() => onToggleMastered(card.id)}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border text-xs font-extrabold transition-all cursor-pointer ${
              card.is_mastered
                ? 'bg-emerald-50 border-emerald-200 text-emerald-700 shadow-2xs'
                : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 shadow-2xs'
            }`}
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{card.is_mastered ? 'Mastered' : 'Mark Mastered'}</span>
          </button>
        </div>
      </div>

      {/* 3D Flip Card Container */}
      <div
        className="w-full min-h-[420px] cursor-pointer select-none"
        style={{ perspective: '1000px' }}
        onClick={handleFlip}
      >
        <div
          className="relative w-full h-full min-h-[420px] rounded-3xl"
          style={{
            transformStyle: 'preserve-3d',
            transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
            transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
          }}
        >
          {/* FRONT SIDE */}
          <div
            className="absolute inset-0 w-full h-full rounded-3xl bg-white border border-slate-200/80 p-8 flex flex-col justify-between shadow-saas overflow-y-auto"
            style={{
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              transform: 'rotateY(0deg)',
            }}
          >
            {/* Front Header */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center space-x-2 text-blue-600 text-xs font-extrabold uppercase tracking-wider">
                <Sparkles className="w-4 h-4" />
                <span>{card.front.title || 'Learning Challenge'}</span>
              </div>
              <span className="text-xs text-slate-400 font-medium">Tap card to flip answer 🔄</span>
            </div>

            {/* Front Body Challenge */}
            <div className="my-4 space-y-4">
              <p className="text-base font-bold text-slate-800 leading-relaxed">
                {card.front.prompt || card.learning_objective}
              </p>

              {/* Context Sentence Box */}
              {card.original_sentence && (
                <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl space-y-2">
                  <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block">
                    Original Document Context:
                  </span>
                  <p className="text-sm font-medium text-slate-700 italic leading-relaxed">
                    "{card.original_sentence}"
                  </p>
                </div>
              )}

              {/* Front Specific Challenge Helpers */}
              {card.card_style === 'spelling' && (
                <div className="p-3.5 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center justify-between text-xs text-indigo-900 font-semibold">
                  <span>Misspelled Word in Document:</span>
                  <span className="font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2.5 py-1 rounded-lg">
                    {card.accepted_correction.original}
                  </span>
                </div>
              )}

              {card.card_style === 'fill_in_blank' && card.front.sentence_with_blank && (
                <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl text-center">
                  <span className="text-base font-extrabold text-blue-900 font-sans">
                    {card.front.sentence_with_blank}
                  </span>
                </div>
              )}
            </div>

            {/* Front Footer */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100 text-xs text-slate-500 font-medium">
              <div className="flex items-center space-x-1.5">
                <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                <span>Objective: {card.learning_objective}</span>
              </div>
              <div className="flex items-center space-x-1 font-bold text-blue-600">
                <span>Click to Flip</span>
                <RotateCw className="w-3.5 h-3.5" />
              </div>
            </div>
          </div>

          {/* BACK SIDE */}
          <div
            className="absolute inset-0 w-full h-full rounded-3xl bg-white border border-slate-200/80 p-8 flex flex-col justify-between shadow-saas overflow-y-auto"
            style={{
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              transform: 'rotateY(180deg)',
            }}
          >
            {/* Back Header */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center space-x-2 text-emerald-600 text-xs font-extrabold uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4" />
                <span>Correct Form & Word Meaning</span>
              </div>
              <span className="text-xs text-slate-400 font-medium">Tap card to return front 🔄</span>
            </div>

            {/* Back Body */}
            <div className="my-4 space-y-4">
              {/* Correct Answer Highlight */}
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-[11px] font-extrabold text-emerald-700 uppercase tracking-wider block">
                    Correct Form:
                  </span>
                  <span className="text-xl font-extrabold text-slate-900 font-sans">
                    {card.back.correct_answer || card.accepted_correction.proposed}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-500 font-bold block">Original Mistake:</span>
                  <span className="text-xs line-through text-rose-600 font-bold">
                    {card.accepted_correction.original}
                  </span>
                </div>
              </div>

              {/* CHILD-FRIENDLY DICTIONARY MEANING BOX */}
              {(card.back.child_friendly_definition || card.back.word_meaning) && (
                <div className="p-4 bg-purple-50/70 border border-purple-100 rounded-2xl space-y-2">
                  <div className="flex items-center justify-between text-purple-900 font-extrabold text-xs">
                    <div className="flex items-center space-x-2">
                      <BookOpen className="w-4 h-4 text-purple-600" />
                      <span>Child-Friendly Meaning (Ages 8–14):</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {(card.back.detected_pos || card.back.part_of_speech) && (
                        <span className="text-[10px] font-extrabold uppercase tracking-wider text-purple-700 bg-purple-100 border border-purple-200 px-2.5 py-0.5 rounded-md">
                          🔤 {card.back.detected_pos || card.back.part_of_speech}
                        </span>
                      )}
                      {(card.back.phonetic_hint || card.pronunciation) && (
                        <span className="text-[11px] font-mono text-purple-700 bg-purple-100/60 px-2 py-0.5 rounded-md border border-purple-200">
                          {card.back.phonetic_hint || card.pronunciation}
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="text-xs text-purple-900 font-medium leading-relaxed">
                    <strong className="text-slate-900 font-bold">{card.accepted_correction.proposed}</strong>:{' '}
                    {card.back.child_friendly_definition || card.back.word_meaning}
                  </p>
                </div>
              )}

              {/* MANUAL VERIFICATION WARNING BADGE */}
              {(card.requires_manual_verification || card.back.requires_manual_verification) && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-2xl flex items-center space-x-2 text-amber-800 text-xs font-semibold">
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>⚠️ Meaning confidence below 70%. Requires manual verification.</span>
                </div>
              )}

              {/* AUTHORITATIVE OFFICIAL DICTIONARY SOURCE & SENSE */}
              {(card.back.official_dictionary_definition || card.official_dictionary_definition) && (
                <div className="p-3.5 bg-indigo-50/50 border border-indigo-100 rounded-2xl space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-extrabold text-indigo-900 flex items-center space-x-1.5">
                      <span>📚 Official Lexical Definition</span>
                      {card.back.identified_word_sense && (
                        <span className="text-[10px] font-mono text-indigo-700 bg-indigo-100 px-1.5 py-0.5 rounded">
                          [{card.back.identified_word_sense}]
                        </span>
                      )}
                    </span>
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                      ✓ Verified Source: {card.back.dictionary_source || card.dictionary_source || "Learner Dictionary"}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 italic leading-relaxed">
                    "{card.back.official_dictionary_definition || card.official_dictionary_definition}"
                  </p>
                </div>
              )}

              {/* NATURAL EXAMPLE SENTENCE */}
              {(card.back.example_sentence || card.back.usage_example) && (
                <div className="p-4 bg-blue-50/70 border border-blue-100 rounded-2xl space-y-1.5">
                  <div className="flex items-center space-x-2 text-blue-900 font-extrabold text-xs">
                    <Sparkles className="w-4 h-4 text-blue-600" />
                    <span>📝 Natural Context Example Sentence:</span>
                  </div>
                  <p className="text-xs text-blue-900 font-medium italic leading-relaxed">
                    "{card.back.example_sentence || card.back.usage_example}"
                  </p>
                </div>
              )}

              {/* SYNONYMS & ANTONYMS */}
              {((card.back.synonyms && card.back.synonyms.length > 0) || (card.back.antonyms && card.back.antonyms.length > 0)) && (
                <div className="p-3.5 bg-slate-50 border border-slate-200/80 rounded-2xl flex items-center justify-between text-xs gap-4">
                  {card.back.synonyms && card.back.synonyms.length > 0 && (
                    <div className="flex items-center space-x-2">
                      <span className="font-extrabold text-teal-700">🤝 Synonyms:</span>
                      <div className="flex flex-wrap gap-1">
                        {card.back.synonyms.map((syn, idx) => (
                          <span key={idx} className="bg-teal-50 border border-teal-200 text-teal-800 px-2 py-0.5 rounded text-[11px] font-semibold">
                            {syn}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {card.back.antonyms && card.back.antonyms.length > 0 && (
                    <div className="flex items-center space-x-2">
                      <span className="font-extrabold text-rose-700">↔️ Antonyms:</span>
                      <div className="flex flex-wrap gap-1">
                        {card.back.antonyms.map((ant, idx) => (
                          <span key={idx} className="bg-rose-50 border border-rose-200 text-rose-800 px-2 py-0.5 rounded text-[11px] font-semibold">
                            {ant}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Corrected Full Sentence */}
              <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl space-y-1">
                <span className="text-[11px] font-extrabold text-blue-700 uppercase tracking-wider block">
                  Original Document Context (Corrected):
                </span>
                <p className="text-sm font-semibold text-slate-800 leading-relaxed">
                  "{card.corrected_sentence}"
                </p>
              </div>

              {/* Educational Rule & Explanation */}
              <div className="p-4 bg-indigo-50/60 border border-indigo-100 rounded-2xl space-y-2">
                <div className="flex items-center space-x-2 text-indigo-900 font-extrabold text-xs">
                  <Award className="w-4 h-4 text-indigo-600" />
                  <span>💡 Why Corrected & Educational Rule:</span>
                </div>
                <p className="text-xs text-indigo-900 font-medium leading-relaxed">
                  {card.rule}
                </p>
                <p className="text-xs text-slate-600 leading-relaxed pt-1 border-t border-indigo-100">
                  {card.explanation}
                </p>
              </div>

              {/* Extra Learning Tip */}
              {card.back.tip && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-start space-x-2 text-xs text-amber-800">
                  <Lightbulb className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                  <span>{card.back.tip}</span>
                </div>
              )}
            </div>

            {/* Back Footer Tags */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs">
              <div className="flex flex-wrap gap-1.5">
                {card.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded-md bg-slate-100 border border-slate-200 text-[10px] font-bold text-slate-600"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
              <span className="text-[11px] text-slate-500 font-bold">
                Confidence: {Math.round(card.confidence_score * 100)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation & Flip Prompt Buttons */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={onPrev}
          disabled={cardIndex === 0}
          className="px-5 py-2.5 rounded-xl bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-700 text-xs font-bold border border-slate-200 shadow-xs transition-all cursor-pointer"
        >
          ← Previous
        </button>

        <button
          onClick={handleFlip}
          className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-extrabold shadow-md shadow-blue-500/20 transition-all cursor-pointer"
        >
          <RotateCw className="w-4 h-4" />
          <span>{isFlipped ? 'Show Front' : 'Flip to Answer'}</span>
        </button>

        <button
          onClick={onNext}
          disabled={cardIndex === totalCards - 1}
          className="flex items-center space-x-1 px-5 py-2.5 rounded-xl bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-700 text-xs font-bold border border-slate-200 shadow-xs transition-all cursor-pointer"
        >
          <span>Next Card</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
