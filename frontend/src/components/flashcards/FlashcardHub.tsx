import React, { useState, useEffect } from 'react';
import type {
  FlashcardDeckData,
  CorrectionSuggestionData,
  FlashcardTelemetry
} from '../../types/ocr';
import { generateFlashcards, getFlashcardDeck, updateDeckProgress } from '../../api/client';
import { LearningDashboard } from './LearningDashboard';
import { DeckLibrary } from './DeckLibrary';
import { FlashcardViewer } from './FlashcardViewer';
import {
  FillInBlankMode,
  MultipleChoiceMode,
  TypeAnswerMode,
  SentenceReconstructionMode
} from './StudyModes';
import {
  Sparkles,
  Lock,
  Download,
  GraduationCap,
  BookOpen,
  Layers,
  RotateCw,
  Shuffle,
  AlertCircle,
  Search
} from 'lucide-react';

interface FlashcardHubProps {
  exportedText: string;
  acceptedSuggestions: CorrectionSuggestionData[];
  documentTitle?: string;
  isDocumentExported: boolean;
  onTriggerExport: () => void;
}

export const FlashcardHub: React.FC<FlashcardHubProps> = ({
  exportedText,
  acceptedSuggestions,
  documentTitle,
  isDocumentExported,
  onTriggerExport,
}) => {
  const [deck, setDeck] = useState<FlashcardDeckData | null>(null);
  const [telemetry, setTelemetry] = useState<FlashcardTelemetry | undefined>(undefined);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Navigation & Modes
  const [activeTab, setActiveTab] = useState<'study' | 'library' | 'dashboard'>('study');
  const [studyMode, setStudyMode] = useState<
    'standard' | 'fill_in_blank' | 'multiple_choice' | 'type_answer' | 'reconstruction' | 'review'
  >('standard');

  // Filters & State
  const [cardIndex, setCardIndex] = useState<number>(0);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [includeRejected, setIncludeRejected] = useState<boolean>(false);

  // Handle Flashcard Deck Generation
  const handleGenerateDeck = async () => {
    if (!exportedText || !exportedText.trim()) {
      setErrorMsg('No document text available to generate study flashcards.');
      return;
    }

    setIsGenerating(true);
    setErrorMsg(null);
    try {
      const res = await generateFlashcards(
        exportedText,
        acceptedSuggestions || [],
        documentTitle || 'Exported Document.pdf',
        undefined,
        includeRejected
      );
      setDeck(res.deck);
      setTelemetry(res.telemetry);
      setCardIndex(0);
      setActiveTab('study');
    } catch (err: any) {
      setErrorMsg(err.message || 'Flashcard deck generation failed.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Auto-generate deck when entering tab if document text is present and deck is null
  useEffect(() => {
    if (exportedText && exportedText.trim() && !deck && !isGenerating) {
      handleGenerateDeck();
    }
  }, [exportedText]);

  // Load a deck from Library
  const handleSelectDeckFromLibrary = async (deckId: string) => {
    try {
      const loadedDeck = await getFlashcardDeck(deckId);
      setDeck(loadedDeck);
      setCardIndex(0);
      setActiveTab('study');
    } catch (err: any) {
      alert(err.message || 'Failed to load deck');
    }
  };

  // Card Progress Updates (Mastered / Bookmarked)
  const handleToggleMastered = async (cardId: string) => {
    if (!deck) return;
    const cards = [...deck.cards];
    const target = cards.find((c) => c.id === cardId);
    if (!target) return;

    target.is_mastered = !target.is_mastered;
    const masteredCount = cards.filter((c) => c.is_mastered).length;
    const masteryPct = Math.round((masteredCount / cards.length) * 100);

    const updatedDeck = {
      ...deck,
      cards,
      mastery_percentage: masteryPct,
      study_progress: {
        ...deck.study_progress,
        cards_mastered: masteredCount,
      },
    };
    setDeck(updatedDeck);

    // Save on backend asynchronously
    updateDeckProgress(deck.deck_id, [
      { id: cardId, is_mastered: target.is_mastered },
    ]).catch((err) => console.warn('Failed to sync progress:', err));
  };

  const handleToggleBookmark = async (cardId: string) => {
    if (!deck) return;
    const cards = [...deck.cards];
    const target = cards.find((c) => c.id === cardId);
    if (!target) return;

    target.is_bookmarked = !target.is_bookmarked;
    setDeck({ ...deck, cards });

    updateDeckProgress(deck.deck_id, [
      { id: cardId, is_bookmarked: target.is_bookmarked },
    ]).catch((err) => console.warn('Failed to sync bookmark:', err));
  };

  // Shuffle Cards
  const handleShuffle = () => {
    if (!deck) return;
    const shuffled = [...deck.cards].sort(() => Math.random() - 0.5);
    setDeck({ ...deck, cards: shuffled });
    setCardIndex(0);
  };

  // Filtered Cards List
  const filteredCards = (deck?.cards || []).filter((c) => {
    if (selectedCategory !== 'All' && c.category !== selectedCategory) return false;
    if (selectedDifficulty !== 'All' && c.difficulty !== selectedDifficulty) return false;
    if (studyMode === 'review' && !c.is_bookmarked && c.is_mastered) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const textMatch =
        c.original_sentence.toLowerCase().includes(q) ||
        c.corrected_sentence.toLowerCase().includes(q) ||
        c.explanation.toLowerCase().includes(q) ||
        c.tags.some((t) => t.toLowerCase().includes(q));
      if (!textMatch) return false;
    }
    return true;
  });

  const activeCard = filteredCards[cardIndex] || filteredCards[0];

  // 1. LOCKED STATE (If Document has NOT been exported yet)
  if (!isDocumentExported) {
    return (
      <div className="w-full p-8 sm:p-12 bg-white border border-slate-200/80 rounded-3xl text-center flex flex-col items-center justify-center space-y-8 shadow-saas">
        <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center shadow-2xs">
          <Lock className="w-7 h-7" />
        </div>

        <div className="max-w-lg space-y-2">
          <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">
            Educational Flashcards Workflow
          </h3>
          <p className="text-xs text-slate-500 font-medium leading-relaxed">
            Flashcards are created from your finalized proofreading corrections and document text. Follow the 3-step workflow below to generate your personalized active recall study decks.
          </p>
        </div>

        {/* 3-Step Horizontal Onboarding Workflow */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-3xl pt-2">
          {/* Step 1 */}
          <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/80 flex flex-col items-center text-center space-y-2">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center font-bold">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="text-xs font-extrabold text-slate-900">1. Review & Approve</span>
            <p className="text-[11px] text-slate-500 font-medium">Approve grammar edits in Proofreading Studio</p>
          </div>

          {/* Step 2 */}
          <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/80 flex flex-col items-center text-center space-y-2">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 border border-purple-100 flex items-center justify-center font-bold">
              <Download className="w-5 h-5" />
            </div>
            <span className="text-xs font-extrabold text-slate-900">2. Export Document</span>
            <p className="text-[11px] text-slate-500 font-medium">Download finalized text, markdown or JSON</p>
          </div>

          {/* Step 3 */}
          <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/80 flex flex-col items-center text-center space-y-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-100 flex items-center justify-center font-bold">
              <GraduationCap className="w-5 h-5" />
            </div>
            <span className="text-xs font-extrabold text-slate-900">3. Unlock Flashcards</span>
            <p className="text-[11px] text-slate-500 font-medium">Study active recall vocabulary cards</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
          <button
            onClick={onTriggerExport}
            className="flex items-center space-x-2 px-6 py-3 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs shadow-md shadow-blue-500/20 transition-all transform hover:-translate-y-0.5 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export Document & Unlock Flashcards</span>
          </button>
        </div>
      </div>
    );
  }

  // 2. GENERATING STATE
  if (isGenerating) {
    return (
      <div className="w-full p-16 bg-white border border-slate-200/80 rounded-3xl text-center flex flex-col items-center justify-center space-y-4 shadow-saas">
        <Sparkles className="w-10 h-10 text-blue-600 animate-spin" />
        <h3 className="text-lg font-extrabold text-slate-900">Generating Personalized Educational Flashcards...</h3>
        <p className="text-xs text-slate-500 max-w-sm font-medium">
          Extracting vocabulary definitions, context sentences, categorizing mistake patterns, and building study challenges.
        </p>
      </div>
    );
  }

  // 3. MAIN STUDY & LIBRARY STUDIO
  return (
    <div className="w-full space-y-6">
      {/* Navigation Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-50/80 p-3 rounded-2xl border border-slate-200/80 shadow-2xs">
        {/* Left View Switcher */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('study')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'study'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Study Player</span>
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'dashboard'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Dashboard Stats</span>
          </button>
          <button
            onClick={() => setActiveTab('library')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'library'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Learning Library</span>
          </button>
        </div>

        {/* Right Re-Generate & Options */}
        <div className="flex items-center space-x-3">
          <label className="flex items-center space-x-2 text-xs font-semibold text-slate-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={includeRejected}
              onChange={(e) => setIncludeRejected(e.target.checked)}
              className="rounded bg-white border-slate-300 text-blue-600 focus:ring-blue-500"
            />
            <span>Include unaccepted suggestions</span>
          </label>

          <button
            onClick={handleGenerateDeck}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-bold shadow-2xs transition-colors cursor-pointer"
          >
            <RotateCw className="w-3.5 h-3.5 text-blue-600" />
            <span>Re-Generate Deck</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center space-x-3 text-rose-800 text-xs font-medium">
          <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* VIEW 1: DASHBOARD STATS */}
      {activeTab === 'dashboard' && deck && (
        <LearningDashboard deck={deck} telemetry={telemetry} />
      )}

      {/* VIEW 2: LEARNING LIBRARY */}
      {activeTab === 'library' && (
        <DeckLibrary
          onSelectDeck={handleSelectDeckFromLibrary}
          activeDeckId={deck?.deck_id}
        />
      )}

      {/* VIEW 3: STUDY PLAYER */}
      {activeTab === 'study' && deck && (
        <div className="space-y-6">
          {/* Study Toolbar & Filters */}
          <div className="bg-slate-50/80 border border-slate-200/80 rounded-2xl p-3 flex flex-wrap items-center justify-between gap-4 shadow-2xs">
            {/* Study Mode Selector Pills */}
            <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 sm:pb-0 no-scrollbar">
              <button
                onClick={() => setStudyMode('standard')}
                className={`px-3 py-1.5 rounded-xl text-xs transition-all cursor-pointer ${
                  studyMode === 'standard'
                    ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                    : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200 font-semibold'
                }`}
              >
                Standard Flip
              </button>
              <button
                onClick={() => setStudyMode('fill_in_blank')}
                className={`px-3 py-1.5 rounded-xl text-xs transition-all cursor-pointer ${
                  studyMode === 'fill_in_blank'
                    ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                    : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200 font-semibold'
                }`}
              >
                Fill-in-Blank
              </button>
              <button
                onClick={() => setStudyMode('multiple_choice')}
                className={`px-3 py-1.5 rounded-xl text-xs transition-all cursor-pointer ${
                  studyMode === 'multiple_choice'
                    ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                    : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200 font-semibold'
                }`}
              >
                Multiple Choice
              </button>
              <button
                onClick={() => setStudyMode('type_answer')}
                className={`px-3 py-1.5 rounded-xl text-xs transition-all cursor-pointer ${
                  studyMode === 'type_answer'
                    ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                    : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200 font-semibold'
                }`}
              >
                Type Answer
              </button>
              <button
                onClick={() => setStudyMode('reconstruction')}
                className={`px-3 py-1.5 rounded-xl text-xs transition-all cursor-pointer ${
                  studyMode === 'reconstruction'
                    ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                    : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200 font-semibold'
                }`}
              >
                Sentence Reconstruct
              </button>
              <button
                onClick={() => setStudyMode('review')}
                className={`px-3 py-1.5 rounded-xl text-xs transition-all cursor-pointer ${
                  studyMode === 'review'
                    ? 'bg-blue-600 text-white font-extrabold shadow-xs'
                    : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200 font-semibold'
                }`}
              >
                Review Mode
              </button>
            </div>

            {/* Controls: Shuffle, Category, Search */}
            <div className="flex items-center space-x-2">
              {/* Search Card Text Input */}
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCardIndex(0);
                  }}
                  placeholder="Search cards..."
                  className="pl-8 pr-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 w-32 sm:w-40 font-medium"
                />
              </div>

              <button
                onClick={handleShuffle}
                className="p-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold flex items-center space-x-1 shadow-2xs transition-all cursor-pointer"
                title="Shuffle Cards"
              >
                <Shuffle className="w-3.5 h-3.5 text-blue-600" />
                <span>Shuffle</span>
              </button>

              {/* Category Filter Dropdown */}
              <select
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setCardIndex(0);
                }}
                className="px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-700 focus:outline-none focus:border-blue-500 shadow-2xs"
              >
                <option value="All">All Categories</option>
                {Object.keys(deck.categories_distribution || {}).map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>

              {/* Difficulty Filter Dropdown */}
              <select
                value={selectedDifficulty}
                onChange={(e) => {
                  setSelectedDifficulty(e.target.value);
                  setCardIndex(0);
                }}
                className="px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-700 focus:outline-none focus:border-blue-500 shadow-2xs"
              >
                <option value="All">All Difficulties</option>
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
          </div>

          {/* Active Card Viewer / Interactive Study Mode */}
          {filteredCards.length > 0 && activeCard ? (
            <div className="w-full">
              {studyMode === 'standard' && (
                <FlashcardViewer
                  card={activeCard}
                  cardIndex={cardIndex}
                  totalCards={filteredCards.length}
                  onToggleMastered={handleToggleMastered}
                  onToggleBookmark={handleToggleBookmark}
                  onNext={() => setCardIndex(Math.min(filteredCards.length - 1, cardIndex + 1))}
                  onPrev={() => setCardIndex(Math.max(0, cardIndex - 1))}
                />
              )}

              {studyMode === 'fill_in_blank' && (
                <FillInBlankMode
                  card={activeCard}
                  onAnswerComplete={(correct) => {
                    if (correct) handleToggleMastered(activeCard.id);
                  }}
                  onNext={() => setCardIndex(Math.min(filteredCards.length - 1, cardIndex + 1))}
                />
              )}

              {studyMode === 'multiple_choice' && (
                <MultipleChoiceMode
                  card={activeCard}
                  onAnswerComplete={(correct) => {
                    if (correct) handleToggleMastered(activeCard.id);
                  }}
                  onNext={() => setCardIndex(Math.min(filteredCards.length - 1, cardIndex + 1))}
                />
              )}

              {studyMode === 'type_answer' && (
                <TypeAnswerMode
                  card={activeCard}
                  onAnswerComplete={(correct) => {
                    if (correct) handleToggleMastered(activeCard.id);
                  }}
                  onNext={() => setCardIndex(Math.min(filteredCards.length - 1, cardIndex + 1))}
                />
              )}

              {studyMode === 'reconstruction' && (
                <SentenceReconstructionMode
                  card={activeCard}
                  onAnswerComplete={(correct) => {
                    if (correct) handleToggleMastered(activeCard.id);
                  }}
                  onNext={() => setCardIndex(Math.min(filteredCards.length - 1, cardIndex + 1))}
                />
              )}

              {studyMode === 'review' && (
                <FlashcardViewer
                  card={activeCard}
                  cardIndex={cardIndex}
                  totalCards={filteredCards.length}
                  onToggleMastered={handleToggleMastered}
                  onToggleBookmark={handleToggleBookmark}
                  onNext={() => setCardIndex(Math.min(filteredCards.length - 1, cardIndex + 1))}
                  onPrev={() => setCardIndex(Math.max(0, cardIndex - 1))}
                />
              )}
            </div>
          ) : (
            <div className="p-12 bg-slate-900 border border-slate-800 rounded-3xl text-center space-y-3">
              <Layers className="w-10 h-10 text-slate-600 mx-auto" />
              <h4 className="text-sm font-bold text-slate-300">No Cards Match Current Filter</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Try switching categories or difficulty filters to view remaining flashcards.
              </p>
              <button
                onClick={() => {
                  setSelectedCategory('All');
                  setSelectedDifficulty('All');
                  setStudyMode('standard');
                }}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-bold text-white rounded-xl"
              >
                Reset Filters
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
