import React, { useState, useEffect } from 'react';
import type { FlashcardDeckMetadata } from '../../types/ocr';
import { listFlashcardDecks, deleteFlashcardDeck } from '../../api/client';
import {
  BookOpen,
  Calendar,
  Clock,
  Trash2,
  Play,
  Layers,
  AlertCircle,
  Search,
  Sparkles
} from 'lucide-react';

interface DeckLibraryProps {
  onSelectDeck: (deckId: string) => void;
  activeDeckId?: string;
}

export const DeckLibrary: React.FC<DeckLibraryProps> = ({ onSelectDeck, activeDeckId }) => {
  const [decks, setDecks] = useState<FlashcardDeckMetadata[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadDecks = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listFlashcardDecks();
      setDecks(res.decks || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load personal learning library decks.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDecks();
  }, []);

  const handleDelete = async (e: React.MouseEvent, deckId: string) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this flashcard deck from your library?')) {
      return;
    }
    try {
      await deleteFlashcardDeck(deckId);
      setDecks((prev) => prev.filter((d) => d.deck_id !== deckId));
    } catch (err: any) {
      alert(err.message || 'Failed to delete deck');
    }
  };

  const filteredDecks = decks.filter((d) =>
    (d.source_document_title || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="w-full space-y-6">
      {/* Library Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/80 p-5 rounded-2xl border border-slate-800 shadow-lg">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 text-indigo-400 font-bold text-xs uppercase tracking-wider">
            <BookOpen className="w-4 h-4" />
            <span>Personal Learning Library</span>
          </div>
          <h3 className="text-lg font-black text-white">Your Saved Flashcard Decks</h3>
        </div>

        {/* Search Deck Bar */}
        <div className="relative max-w-xs w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search saved decks..."
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {loading && (
        <div className="p-12 text-center text-slate-400 text-xs font-semibold space-y-2">
          <Sparkles className="w-6 h-6 text-indigo-400 animate-spin mx-auto" />
          <p>Loading your personal learning library...</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center space-x-3 text-rose-300 text-xs">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {!loading && !error && filteredDecks.length === 0 && (
        <div className="p-12 bg-slate-900/60 border border-slate-800 rounded-3xl text-center space-y-3">
          <Layers className="w-10 h-10 text-slate-600 mx-auto" />
          <h4 className="text-sm font-bold text-slate-300">No Flashcard Decks Found</h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            {searchQuery
              ? `No decks match '${searchQuery}'. Try clearing your search filter.`
              : 'Export a corrected document from the AI Proofreading Studio to generate your first personalized deck!'}
          </p>
        </div>
      )}

      {/* Grid of Saved Decks */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDecks.map((d) => {
          const isCurrentActive = d.deck_id === activeDeckId;
          const createdDate = d.created_at
            ? new Date(d.created_at).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })
            : 'Recent';

          return (
            <div
              key={d.deck_id}
              onClick={() => onSelectDeck(d.deck_id)}
              className={`group cursor-pointer bg-slate-900 hover:bg-slate-800/90 border rounded-3xl p-6 transition-all shadow-xl flex flex-col justify-between space-y-4 ${
                isCurrentActive
                  ? 'border-indigo-500 ring-1 ring-indigo-500/50 bg-indigo-950/20'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              {/* Deck Top Meta */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 flex items-center space-x-1.5">
                    <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                    <span>{createdDate}</span>
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-950 text-indigo-300 border border-slate-800">
                      {d.total_flashcards} Cards
                    </span>
                    <button
                      onClick={(e) => handleDelete(e, d.deck_id)}
                      className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                      title="Delete Deck"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <h4 className="text-base font-black text-white tracking-tight group-hover:text-indigo-300 transition-colors line-clamp-1">
                  {d.source_document_title || 'Untitled Document'}
                </h4>

                {/* Categories Badge list */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {Object.keys(d.categories_distribution || {}).slice(0, 3).map((cat, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800 text-[10px] font-semibold text-slate-300"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              </div>

              {/* Progress & Study Button */}
              <div className="pt-4 border-t border-slate-800/80 space-y-3">
                {/* Mastery Progress Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>Mastery Progress</span>
                    <span className="font-bold text-emerald-400">{d.mastery_percentage}%</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full transition-all"
                      style={{ width: `${Math.max(4, d.mastery_percentage)}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-slate-500" />
                    <span>~{d.estimated_study_time_min} mins</span>
                  </span>

                  <span className="flex items-center space-x-1 text-xs font-bold text-indigo-400 group-hover:translate-x-0.5 transition-transform">
                    <span>{isCurrentActive ? 'Continue Study' : 'Open Deck'}</span>
                    <Play className="w-3.5 h-3.5 fill-current" />
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
