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
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'Hard':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      default:
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col space-y-4">
      {/* Top Card Controls & Telemetry Header */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold text-slate-400">
            Card {cardIndex + 1} of {totalCards}
          </span>
          <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getDifficultyBadge(card.difficulty)}`}>
            {card.difficulty}
          </span>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            {card.category}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => onToggleBookmark(card.id)}
            className={`p-2 rounded-xl border transition-all ${
              card.is_bookmarked
                ? 'bg-amber-500/20 border-amber-500/40 text-amber-400'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
            }`}
            title="Bookmark Flashcard"
          >
            <Bookmark className="w-4 h-4 fill-current" />
          </button>
          <button
            onClick={() => onToggleMastered(card.id)}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition-all ${
              card.is_mastered
                ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
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
            className="absolute inset-0 w-full h-full rounded-3xl bg-slate-900/95 border border-slate-800 p-8 flex flex-col justify-between shadow-2xl overflow-y-auto"
            style={{
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              transform: 'rotateY(0deg)',
            }}
          >
            {/* Front Header */}
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div className="flex items-center space-x-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-4 h-4" />
                <span>{card.front.title || 'Learning Challenge'}</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">Tap card to flip answer 🔄</span>
            </div>

            {/* Front Body Challenge */}
            <div className="my-4 space-y-4">
              <p className="text-base font-semibold text-slate-200">
                {card.front.prompt || card.learning_objective}
              </p>

              {/* Context Sentence Box */}
              {card.original_sentence && (
                <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-2xl space-y-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    Original Document Context:
                  </span>
                  <p className="text-sm font-medium text-slate-300 italic leading-relaxed">
                    "{card.original_sentence}"
                  </p>
                </div>
              )}

              {/* Front Specific Challenge Helpers */}
              {card.card_style === 'spelling' && (
                <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl flex items-center justify-between text-xs text-indigo-300 font-mono">
                  <span>Misspelled Word in Document:</span>
                  <span className="font-bold text-rose-300 bg-rose-950/40 border border-rose-500/30 px-2.5 py-1 rounded-lg">
                    {card.accepted_correction.original}
                  </span>
                </div>
              )}

              {card.card_style === 'fill_in_blank' && card.front.sentence_with_blank && (
                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl text-center">
                  <span className="text-base font-extrabold text-blue-200 font-mono">
                    {card.front.sentence_with_blank}
                  </span>
                </div>
              )}
            </div>

            {/* Front Footer */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs text-slate-400">
              <div className="flex items-center space-x-1.5">
                <BookOpen className="w-3.5 h-3.5 text-slate-500" />
                <span>Objective: {card.learning_objective}</span>
              </div>
              <div className="flex items-center space-x-1 font-semibold text-indigo-400">
                <span>Click to Flip</span>
                <RotateCw className="w-3.5 h-3.5" />
              </div>
            </div>
          </div>

          {/* BACK SIDE */}
          <div
            className="absolute inset-0 w-full h-full rounded-3xl bg-gradient-to-b from-slate-900 via-slate-900 to-indigo-950/70 border border-indigo-500/30 p-8 flex flex-col justify-between shadow-2xl overflow-y-auto"
            style={{
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              transform: 'rotateY(180deg)',
            }}
          >
            {/* Back Header */}
            <div className="flex items-center justify-between border-b border-indigo-500/20 pb-4">
              <div className="flex items-center space-x-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4" />
                <span>Correct Form & Word Meaning</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">Tap card to return front 🔄</span>
            </div>

            {/* Back Body */}
            <div className="my-4 space-y-4">
              {/* Correct Answer Highlight */}
              <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block">
                    Correct Form:
                  </span>
                  <span className="text-lg font-black text-white font-mono">
                    {card.back.correct_answer || card.accepted_correction.proposed}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 block">Original Mistake:</span>
                  <span className="text-xs line-through text-rose-400 font-mono">
                    {card.accepted_correction.original}
                  </span>
                </div>
              </div>

              {/* CHILD-FRIENDLY DICTIONARY MEANING BOX */}
              {(card.back.child_friendly_definition || card.back.word_meaning) && (
                <div className="p-4 bg-purple-950/40 border border-purple-500/30 rounded-2xl space-y-2">
                  <div className="flex items-center justify-between text-purple-300 font-bold text-xs">
                    <div className="flex items-center space-x-2">
                      <BookOpen className="w-4 h-4 text-purple-400" />
                      <span>Child-Friendly Meaning (Ages 8–14):</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {(card.back.detected_pos || card.back.part_of_speech) && (
                        <span className="text-[10px] font-extrabold uppercase tracking-wider text-purple-200 bg-purple-900/70 border border-purple-500/40 px-2.5 py-0.5 rounded-md">
                          🔤 {card.back.detected_pos || card.back.part_of_speech}
                        </span>
                      )}
                      {(card.back.phonetic_hint || card.pronunciation) && (
                        <span className="text-[11px] font-mono text-purple-300 bg-purple-900/40 px-2 py-0.5 rounded-md border border-purple-500/20">
                          {card.back.phonetic_hint || card.pronunciation}
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="text-xs text-purple-100 font-medium leading-relaxed">
                    <strong className="text-white font-mono">{card.accepted_correction.proposed}</strong>:{' '}
                    {card.back.child_friendly_definition || card.back.word_meaning}
                  </p>
                </div>
              )}

              {/* MANUAL VERIFICATION WARNING BADGE */}
              {(card.requires_manual_verification || card.back.requires_manual_verification) && (
                <div className="p-3 bg-amber-950/50 border border-amber-500/40 rounded-2xl flex items-center space-x-2 text-amber-200 text-xs font-semibold">
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>⚠️ Meaning confidence below 70%. Requires manual verification.</span>
                </div>
              )}

              {/* AUTHORITATIVE OFFICIAL DICTIONARY SOURCE & SENSE */}
              {(card.back.official_dictionary_definition || card.official_dictionary_definition) && (
                <div className="p-3.5 bg-indigo-950/30 border border-indigo-500/30 rounded-2xl space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-indigo-300 flex items-center space-x-1.5">
                      <span>📚 Official Lexical Definition</span>
                      {card.back.identified_word_sense && (
                        <span className="text-[10px] font-mono text-indigo-400 bg-indigo-900/40 px-1.5 py-0.5 rounded">
                          [{card.back.identified_word_sense}]
                        </span>
                      )}
                    </span>
                    <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded-full">
                      ✓ Verified Source: {card.back.dictionary_source || card.dictionary_source || "Learner Dictionary"}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 italic leading-relaxed">
                    "{card.back.official_dictionary_definition || card.official_dictionary_definition}"
                  </p>
                </div>
              )}

              {/* NATURAL 8-20 WORD EXAMPLE SENTENCE */}
              {(card.back.example_sentence || card.back.usage_example) && (
                <div className="p-4 bg-blue-950/40 border border-blue-500/30 rounded-2xl space-y-1.5">
                  <div className="flex items-center space-x-2 text-blue-300 font-bold text-xs">
                    <Sparkles className="w-4 h-4 text-blue-400" />
                    <span>📝 Natural Context Example Sentence:</span>
                  </div>
                  <p className="text-xs text-blue-100 font-medium italic leading-relaxed">
                    "{card.back.example_sentence || card.back.usage_example}"
                  </p>
                </div>
              )}

              {/* SYNONYMS & ANTONYMS */}
              {((card.back.synonyms && card.back.synonyms.length > 0) || (card.back.antonyms && card.back.antonyms.length > 0)) && (
                <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-between text-xs gap-4">
                  {card.back.synonyms && card.back.synonyms.length > 0 && (
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-teal-400">🤝 Synonyms:</span>
                      <div className="flex flex-wrap gap-1">
                        {card.back.synonyms.map((syn, idx) => (
                          <span key={idx} className="bg-teal-950/60 border border-teal-500/30 text-teal-200 px-2 py-0.5 rounded text-[11px]">
                            {syn}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {card.back.antonyms && card.back.antonyms.length > 0 && (
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-rose-400">↔️ Antonyms:</span>
                      <div className="flex flex-wrap gap-1">
                        {card.back.antonyms.map((ant, idx) => (
                          <span key={idx} className="bg-rose-950/60 border border-rose-500/30 text-rose-200 px-2 py-0.5 rounded text-[11px]">
                            {ant}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Corrected Full Sentence */}
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-1">
                <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider block">
                  Original Document Context (Corrected):
                </span>
                <p className="text-sm font-semibold text-emerald-200 leading-relaxed">
                  "{card.corrected_sentence}"
                </p>
              </div>

              {/* Educational Rule & Explanation */}
              <div className="p-4 bg-indigo-950/40 border border-indigo-500/20 rounded-2xl space-y-2">
                <div className="flex items-center space-x-2 text-indigo-300 font-bold text-xs">
                  <Award className="w-4 h-4 text-indigo-400" />
                  <span>💡 Why Corrected & Educational Rule:</span>
                </div>
                <p className="text-xs text-indigo-100 font-medium leading-relaxed">
                  {card.rule}
                </p>
                <p className="text-xs text-slate-300 leading-relaxed pt-1 border-t border-indigo-500/10">
                  {card.explanation}
                </p>
              </div>


              {/* Extra Learning Tip */}
              {card.back.tip && (
                <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-start space-x-2 text-xs text-amber-200">
                  <Lightbulb className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                  <span>{card.back.tip}</span>
                </div>
              )}
            </div>


            {/* Back Footer Tags */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-xs">
              <div className="flex flex-wrap gap-1.5">
                {card.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-[10px] font-semibold text-slate-300"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
              <span className="text-[11px] text-slate-400 font-medium">
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
          className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-slate-300 text-xs font-bold border border-slate-800 transition-all"
        >
          ← Previous
        </button>

        <button
          onClick={handleFlip}
          className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-extrabold shadow-lg shadow-indigo-500/20 transition-all"
        >
          <RotateCw className="w-4 h-4" />
          <span>{isFlipped ? 'Show Front' : 'Flip to Answer'}</span>
        </button>

        <button
          onClick={onNext}
          disabled={cardIndex === totalCards - 1}
          className="flex items-center space-x-1 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-bold border border-indigo-500 transition-all"
        >
          <span>Next Card</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
