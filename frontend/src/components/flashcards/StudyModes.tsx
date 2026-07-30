import React, { useState } from 'react';
import type { FlashcardData } from '../../types/ocr';
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
  ArrowRight,
  Lightbulb,
  BookOpen
} from 'lucide-react';

interface StudyModeProps {
  card: FlashcardData;
  onAnswerComplete: (isCorrect: boolean) => void;
  onNext: () => void;
}

/* 1. Fill-in-the-Blanks Mode */
export const FillInBlankMode: React.FC<StudyModeProps> = ({ card, onAnswerComplete, onNext }) => {
  const [userInputValue, setUserInputValue] = useState<string>('');
  const [submitted, setSubmitted] = useState<boolean>(false);

  const correctAnswer = card.back.correct_answer || card.accepted_correction.proposed;
  const isCorrect = userInputValue.trim().toLowerCase() === correctAnswer.trim().toLowerCase();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInputValue.trim()) return;
    setSubmitted(true);
    onAnswerComplete(isCorrect);
  };

  const handleReset = () => {
    setUserInputValue('');
    setSubmitted(false);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 max-w-2xl mx-auto shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2 text-blue-400 font-bold text-xs uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Fill-in-the-Blank Exercise</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300">
          {card.category}
        </span>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-semibold text-slate-300">
          Complete the sentence by typing the correct missing word:
        </p>

        <div className="p-6 bg-slate-950 border border-slate-800 rounded-2xl text-center">
          <span className="text-base font-semibold text-slate-200 leading-relaxed">
            {card.front.sentence_with_blank || card.original_sentence.replace(card.accepted_correction.original, '[ _____ ]')}
          </span>
        </div>

        {!submitted ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex space-x-3">
              <input
                type="text"
                value={userInputValue}
                onChange={(e) => setUserInputValue(e.target.value)}
                placeholder="Type the missing word..."
                className="flex-1 px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-white font-mono text-sm focus:outline-none focus:border-blue-500"
                autoFocus
              />
              <button
                type="submit"
                disabled={!userInputValue.trim()}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-lg transition-all"
              >
                Submit Answer
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4 pt-2">
            {/* Feedback Banner */}
            <div
              className={`p-4 rounded-2xl border flex items-center space-x-3 ${
                isCorrect
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              }`}
            >
              {isCorrect ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0" />
              ) : (
                <XCircle className="w-6 h-6 text-rose-400 flex-shrink-0" />
              )}
              <div className="flex-1">
                <span className="font-bold text-sm block">
                  {isCorrect ? 'Excellent! Perfect Match!' : 'Incorrect Answer'}
                </span>
                <span className="text-xs">
                  Correct Answer: <strong className="font-mono text-white">{correctAnswer}</strong>
                </span>
              </div>
            </div>

            {/* Child-Friendly Meaning Box */}
            {(card.back.child_friendly_definition || card.back.word_meaning) && (
              <div className="p-4 bg-purple-950/40 border border-purple-500/30 rounded-2xl space-y-1.5">
                <div className="flex items-center justify-between text-purple-300 font-bold text-xs">
                  <div className="flex items-center space-x-2">
                    <BookOpen className="w-4 h-4 text-purple-400" />
                    <span>📖 Child-Friendly Meaning:</span>
                  </div>
                  {card.back.part_of_speech && (
                    <span className="text-[10px] font-extrabold uppercase tracking-wider text-purple-200 bg-purple-900/70 border border-purple-500/40 px-2 py-0.5 rounded-md">
                      🔤 {card.back.part_of_speech}
                    </span>
                  )}
                </div>
                <p className="text-xs text-purple-100 font-medium leading-relaxed">
                  <strong className="text-white font-mono">{card.accepted_correction.proposed}</strong>:{' '}
                  {card.back.child_friendly_definition || card.back.word_meaning}
                </p>
              </div>
            )}

            {/* Natural Example Sentence */}
            {(card.back.example_sentence || card.back.usage_example) && (
              <div className="p-4 bg-blue-950/40 border border-blue-500/30 rounded-2xl space-y-1">
                <div className="flex items-center space-x-2 text-blue-300 font-bold text-xs">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  <span>📝 Natural Example Sentence:</span>
                </div>
                <p className="text-xs text-blue-100 font-medium italic leading-relaxed">
                  "{card.back.example_sentence || card.back.usage_example}"
                </p>
              </div>
            )}



            {/* Explanation Box */}
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-2">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block">
                Educational Rule & Context:
              </span>
              <p className="text-xs text-slate-300 leading-relaxed">{card.rule}</p>
              <p className="text-xs font-medium text-emerald-300 pt-1">
                "{card.corrected_sentence}"
              </p>
            </div>


            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl"
              >
                Try Again
              </button>
              <button
                onClick={onNext}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl flex items-center space-x-1"
              >
                <span>Next Card</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/* 2. Multiple Choice Quiz Mode */
export const MultipleChoiceMode: React.FC<StudyModeProps> = ({ card, onAnswerComplete, onNext }) => {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<boolean>(false);

  const correctAnswer = card.back.correct_answer || card.accepted_correction.proposed;
  const rawOptions = card.front.options && card.front.options.length > 1
    ? card.front.options
    : [correctAnswer, card.accepted_correction.original, "however", "which"];

  // Unique options
  const options = Array.from(new Set(rawOptions));

  const handleSelect = (opt: string) => {
    if (submitted) return;
    setSelectedOption(opt);
    setSubmitted(true);
    const isCorrect = opt.trim().toLowerCase() === correctAnswer.trim().toLowerCase();
    onAnswerComplete(isCorrect);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 max-w-2xl mx-auto shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2 text-purple-400 font-bold text-xs uppercase tracking-wider">
          <HelpCircle className="w-4 h-4" />
          <span>Multiple Choice Quiz</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300">
          {card.category}
        </span>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-semibold text-slate-200">
          {card.front.prompt || 'Select the correct correction for this sentence:'}
        </p>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl italic text-sm text-slate-300">
          "{card.original_sentence}"
        </div>

        {/* 4 Option Buttons */}
        <div className="grid grid-cols-1 gap-3">
          {options.map((opt, idx) => {
            const isThisCorrect = opt.trim().toLowerCase() === correctAnswer.trim().toLowerCase();
            const isSelected = selectedOption === opt;

            let btnStyle = 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-200';
            if (submitted) {
              if (isThisCorrect) {
                btnStyle = 'bg-emerald-500/20 border-emerald-500/50 text-emerald-200 font-bold';
              } else if (isSelected) {
                btnStyle = 'bg-rose-500/20 border-rose-500/50 text-rose-200 font-bold';
              } else {
                btnStyle = 'bg-slate-950/50 border-slate-900 text-slate-500';
              }
            }

            return (
              <button
                key={idx}
                onClick={() => handleSelect(opt)}
                disabled={submitted}
                className={`w-full p-4 rounded-2xl border text-left text-xs font-mono transition-all flex items-center justify-between ${btnStyle}`}
              >
                <span>{opt}</span>
                {submitted && isThisCorrect && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                {submitted && isSelected && !isThisCorrect && <XCircle className="w-4 h-4 text-rose-400" />}
              </button>
            );
          })}
        </div>

        {/* Post-submission details */}
        {submitted && (
          <div className="space-y-4 pt-4 border-t border-slate-800">
            <div className="p-4 bg-indigo-950/40 border border-indigo-500/20 rounded-2xl space-y-1">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block">
                Educational Rule:
              </span>
              <p className="text-xs text-slate-300 leading-relaxed">{card.rule}</p>
              <p className="text-xs text-slate-400 pt-1">{card.explanation}</p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={onNext}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl flex items-center space-x-1"
              >
                <span>Next Challenge</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/* 3. Type the Answer Mode */
export const TypeAnswerMode: React.FC<StudyModeProps> = ({ card, onAnswerComplete, onNext }) => {
  const [typedText, setTypedText] = useState<string>('');
  const [submitted, setSubmitted] = useState<boolean>(false);

  const targetCorrection = card.accepted_correction.proposed;
  const isCorrect = typedText.trim().toLowerCase() === targetCorrection.trim().toLowerCase();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!typedText.trim()) return;
    setSubmitted(true);
    onAnswerComplete(isCorrect);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 max-w-2xl mx-auto shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Type the Correct Form</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300">
          Active Recall Practice
        </span>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-semibold text-slate-200">
          Type the precise correction for the highlighted mistake in this sentence:
        </p>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-2">
          <p className="text-sm font-medium text-slate-300 italic">
            "{card.original_sentence}"
          </p>
          <div className="flex items-center space-x-2 text-xs font-mono text-rose-300">
            <span>Mistake identified:</span>
            <span className="px-2 py-0.5 bg-rose-500/20 border border-rose-500/30 rounded font-bold">
              {card.accepted_correction.original}
            </span>
          </div>
        </div>

        {!submitted ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex space-x-3">
              <input
                type="text"
                value={typedText}
                onChange={(e) => setTypedText(e.target.value)}
                placeholder={`Type the correct replacement for '${card.accepted_correction.original}'...`}
                className="flex-1 px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-white font-mono text-sm focus:outline-none focus:border-emerald-500"
                autoFocus
              />
              <button
                type="submit"
                disabled={!typedText.trim()}
                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-lg"
              >
                Check Answer
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div
              className={`p-4 rounded-2xl border flex items-center space-x-3 ${
                isCorrect
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              }`}
            >
              {isCorrect ? <CheckCircle2 className="w-6 h-6 text-emerald-400" /> : <XCircle className="w-6 h-6 text-rose-400" />}
              <div>
                <span className="font-bold text-sm block">
                  {isCorrect ? 'Correct! Excellent Recall!' : 'Not Quite Right'}
                </span>
                <span className="text-xs font-mono">
                  Your entry: "{typedText}" | Expected: "{targetCorrection}"
                </span>
              </div>
            </div>

            <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-1">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block">
                Rule & Explanation:
              </span>
              <p className="text-xs text-slate-300">{card.rule}</p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={onNext}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl flex items-center space-x-1"
              >
                <span>Next Card</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/* 4. Sentence Reconstruction Mode */
export const SentenceReconstructionMode: React.FC<StudyModeProps> = ({ card, onAnswerComplete, onNext }) => {
  const [typedSentence, setTypedSentence] = useState<string>('');
  const [submitted, setSubmitted] = useState<boolean>(false);

  const targetSentence = card.corrected_sentence.trim();
  const isCorrect = typedSentence.trim().toLowerCase() === targetSentence.toLowerCase();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!typedSentence.trim()) return;
    setSubmitted(true);
    onAnswerComplete(isCorrect);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 max-w-2xl mx-auto shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Sentence Reconstruction Exercise</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300">
          Sentence Structure
        </span>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-semibold text-slate-200">
          Reconstruct the original sentence into its finalized, grammatically corrected structure:
        </p>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-1">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
            Original Flawed Sentence:
          </span>
          <p className="text-sm font-medium text-rose-300 italic">
            "{card.original_sentence}"
          </p>
        </div>

        {!submitted ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              rows={3}
              value={typedSentence}
              onChange={(e) => setTypedSentence(e.target.value)}
              placeholder="Type the full reconstructed sentence here..."
              className="w-full p-4 bg-slate-950 border border-slate-700 rounded-2xl text-white font-sans text-sm focus:outline-none focus:border-amber-500 leading-relaxed resize-none"
            />
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={!typedSentence.trim()}
                className="px-6 py-3 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-lg"
              >
                Validate Reconstruction
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div
              className={`p-4 rounded-2xl border flex items-center space-x-3 ${
                isCorrect
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
              }`}
            >
              {isCorrect ? <CheckCircle2 className="w-6 h-6 text-emerald-400" /> : <Lightbulb className="w-6 h-6 text-amber-400" />}
              <div>
                <span className="font-bold text-sm block">
                  {isCorrect ? 'Perfect Sentence Reconstruction!' : 'Target Corrected Sentence Comparison:'}
                </span>
                <span className="text-xs font-semibold text-white block pt-0.5">
                  "{card.corrected_sentence}"
                </span>
              </div>
            </div>

            <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-1">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block">
                Educational Rule:
              </span>
              <p className="text-xs text-slate-300">{card.rule}</p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={onNext}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl flex items-center space-x-1"
              >
                <span>Next Challenge</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
