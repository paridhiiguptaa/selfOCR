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
    <div className="bg-white border border-slate-200/80 rounded-3xl p-8 space-y-6 max-w-2xl mx-auto shadow-saas">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center space-x-2 text-blue-600 font-extrabold text-xs uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Fill-in-the-Blank Exercise</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-100 text-slate-700">
          {card.category}
        </span>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-bold text-slate-800">
          Complete the sentence by typing the correct missing word:
        </p>

        <div className="p-6 bg-slate-50 border border-slate-200/80 rounded-2xl text-center">
          <span className="text-base font-bold text-slate-900 leading-relaxed font-sans">
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
                className="flex-1 px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-900 font-sans text-sm focus:outline-none focus:border-blue-500 shadow-2xs"
                autoFocus
              />
              <button
                type="submit"
                disabled={!userInputValue.trim()}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-extrabold text-xs rounded-xl shadow-xs transition-all cursor-pointer"
              >
                Submit Answer
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            {/* Result Notification */}
            <div
              className={`p-4 rounded-2xl border flex items-center space-x-3 ${
                isCorrect
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                  : 'bg-rose-50 border-rose-200 text-rose-800'
              }`}
            >
              {isCorrect ? <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0" /> : <XCircle className="w-6 h-6 text-rose-600 flex-shrink-0" />}
              <div className="flex flex-col">
                <span className="font-extrabold text-sm">
                  {isCorrect ? 'Correct! Excellent Recall!' : 'Incorrect Answer'}
                </span>
                <span className="text-xs font-semibold">
                  Correct Answer: <strong className="font-bold text-slate-900">{correctAnswer}</strong>
                </span>
              </div>
            </div>

            {/* Child-Friendly Meaning Box */}
            {(card.back.child_friendly_definition || card.back.word_meaning) && (
              <div className="p-4 bg-purple-50/70 border border-purple-100 rounded-2xl space-y-1.5">
                <div className="flex items-center justify-between text-purple-900 font-extrabold text-xs">
                  <div className="flex items-center space-x-2">
                    <BookOpen className="w-4 h-4 text-purple-600" />
                    <span>📖 Child-Friendly Meaning:</span>
                  </div>
                  {card.back.part_of_speech && (
                    <span className="text-[10px] font-extrabold uppercase tracking-wider text-purple-700 bg-purple-100 border border-purple-200 px-2 py-0.5 rounded-md">
                      🔤 {card.back.part_of_speech}
                    </span>
                  )}
                </div>
                <p className="text-xs text-purple-900 font-medium leading-relaxed">
                  <strong className="text-slate-900 font-bold">{card.accepted_correction.proposed}</strong>:{' '}
                  {card.back.child_friendly_definition || card.back.word_meaning}
                </p>
              </div>
            )}

            {/* Natural Example Sentence */}
            {(card.back.example_sentence || card.back.usage_example) && (
              <div className="p-4 bg-blue-50/70 border border-blue-100 rounded-2xl space-y-1">
                <div className="flex items-center space-x-2 text-blue-900 font-extrabold text-xs">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  <span>📝 Natural Example Sentence:</span>
                </div>
                <p className="text-xs text-blue-900 font-medium italic leading-relaxed">
                  "{card.back.example_sentence || card.back.usage_example}"
                </p>
              </div>
            )}

            {/* Explanation Box */}
            <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl space-y-2">
              <span className="text-xs font-extrabold text-indigo-700 uppercase tracking-wider block">
                Educational Rule & Context:
              </span>
              <p className="text-xs text-slate-700 leading-relaxed font-medium">{card.rule}</p>
              <p className="text-xs font-bold text-emerald-700 pt-1">
                "{card.corrected_sentence}"
              </p>
            </div>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-bold rounded-xl cursor-pointer"
              >
                Try Again
              </button>
              <button
                onClick={onNext}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-extrabold rounded-xl flex items-center space-x-1 shadow-xs cursor-pointer"
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
    <div className="bg-white border border-slate-200/80 rounded-3xl p-8 space-y-6 max-w-2xl mx-auto shadow-saas">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center space-x-2 text-purple-600 font-extrabold text-xs uppercase tracking-wider">
          <HelpCircle className="w-4 h-4" />
          <span>Multiple Choice Quiz</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-100 text-slate-700">
          {card.category}
        </span>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-bold text-slate-800">
          {card.front.prompt || 'Select the correct correction for this sentence:'}
        </p>

        <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl italic text-sm text-slate-700 font-medium">
          "{card.original_sentence}"
        </div>

        {/* 4 Option Buttons */}
        <div className="grid grid-cols-1 gap-3">
          {options.map((opt, idx) => {
            const isThisCorrect = opt.trim().toLowerCase() === correctAnswer.trim().toLowerCase();
            const isSelected = selectedOption === opt;

            let btnStyle = 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-800 font-semibold';
            if (submitted) {
              if (isThisCorrect) {
                btnStyle = 'bg-emerald-50 border-emerald-300 text-emerald-800 font-extrabold';
              } else if (isSelected) {
                btnStyle = 'bg-rose-50 border-rose-300 text-rose-800 font-extrabold';
              } else {
                btnStyle = 'bg-slate-50 border-slate-200 text-slate-400';
              }
            }

            return (
              <button
                key={idx}
                onClick={() => handleSelect(opt)}
                disabled={submitted}
                className={`w-full p-4 rounded-2xl border text-left text-xs font-sans transition-all flex items-center justify-between shadow-2xs cursor-pointer ${btnStyle}`}
              >
                <span>{opt}</span>
                {submitted && isThisCorrect && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                {submitted && isSelected && !isThisCorrect && <XCircle className="w-4 h-4 text-rose-600" />}
              </button>
            );
          })}
        </div>

        {/* Post-submission details */}
        {submitted && (
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <div className="p-4 bg-indigo-50/60 border border-indigo-100 rounded-2xl space-y-1">
              <span className="text-xs font-extrabold text-indigo-900 uppercase tracking-wider block">
                Educational Rule:
              </span>
              <p className="text-xs text-slate-700 leading-relaxed font-medium">{card.rule}</p>
              <p className="text-xs text-slate-500 pt-1">{card.explanation}</p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={onNext}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-extrabold rounded-xl flex items-center space-x-1 shadow-xs cursor-pointer"
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
    <div className="bg-white border border-slate-200/80 rounded-3xl p-8 space-y-6 max-w-2xl mx-auto shadow-saas">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center space-x-2 text-emerald-600 font-extrabold text-xs uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Type the Correct Form</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-100 text-slate-700">
          Active Recall Practice
        </span>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-bold text-slate-800">
          Type the precise correction for the highlighted mistake in this sentence:
        </p>

        <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl space-y-2">
          <p className="text-sm font-medium text-slate-700 italic">
            "{card.original_sentence}"
          </p>
          <div className="flex items-center space-x-2 text-xs font-semibold text-rose-700">
            <span>Mistake identified:</span>
            <span className="px-2 py-0.5 bg-rose-50 border border-rose-200 rounded font-extrabold">
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
                className="flex-1 px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-900 font-sans text-sm focus:outline-none focus:border-emerald-500 shadow-2xs"
                autoFocus
              />
              <button
                type="submit"
                disabled={!typedText.trim()}
                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-extrabold text-xs rounded-xl shadow-xs cursor-pointer"
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
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                  : 'bg-rose-50 border-rose-200 text-rose-800'
              }`}
            >
              {isCorrect ? <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" /> : <XCircle className="w-6 h-6 text-rose-600 shrink-0" />}
              <div>
                <span className="font-extrabold text-sm block">
                  {isCorrect ? 'Correct! Excellent Recall!' : 'Not Quite Right'}
                </span>
                <span className="text-xs font-semibold">
                  Your entry: "{typedText}" | Expected: "{targetCorrection}"
                </span>
              </div>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl space-y-1">
              <span className="text-xs font-extrabold text-indigo-700 uppercase tracking-wider block">
                Rule & Explanation:
              </span>
              <p className="text-xs text-slate-700 font-medium">{card.rule}</p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={onNext}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-extrabold rounded-xl flex items-center space-x-1 shadow-xs cursor-pointer"
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
    <div className="bg-white border border-slate-200/80 rounded-3xl p-8 space-y-6 max-w-2xl mx-auto shadow-saas">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center space-x-2 text-amber-600 font-extrabold text-xs uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Sentence Reconstruction Exercise</span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-100 text-slate-700">
          Sentence Structure
        </span>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-bold text-slate-800">
          Reconstruct the original sentence into its finalized, grammatically corrected structure:
        </p>

        <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl space-y-1">
          <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block">
            Original Flawed Sentence:
          </span>
          <p className="text-sm font-medium text-rose-700 italic">
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
              className="w-full p-4 bg-white border border-slate-200 rounded-2xl text-slate-800 font-sans text-sm focus:outline-none focus:border-amber-500 leading-relaxed resize-none shadow-2xs"
            />
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={!typedSentence.trim()}
                className="px-6 py-3 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white font-extrabold text-xs rounded-xl shadow-xs cursor-pointer"
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
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                  : 'bg-amber-50 border-amber-200 text-amber-800'
              }`}
            >
              {isCorrect ? <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" /> : <Lightbulb className="w-6 h-6 text-amber-600 shrink-0" />}
              <div>
                <span className="font-extrabold text-sm block">
                  {isCorrect ? 'Perfect Sentence Reconstruction!' : 'Target Corrected Sentence Comparison:'}
                </span>
                <span className="text-xs font-semibold text-slate-900 block pt-0.5">
                  "{card.corrected_sentence}"
                </span>
              </div>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl space-y-1">
              <span className="text-xs font-extrabold text-indigo-700 uppercase tracking-wider block">
                Educational Rule:
              </span>
              <p className="text-xs text-slate-700 font-medium">{card.rule}</p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={onNext}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-extrabold rounded-xl flex items-center space-x-1 shadow-xs cursor-pointer"
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
