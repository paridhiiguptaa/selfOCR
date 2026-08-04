import React, { useState } from 'react';
import { Clock, Search, FileText, GraduationCap } from 'lucide-react';
import type { NavModule } from '../Sidebar';

interface HistoryPageProps {
  onNavigate: (module: NavModule) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ onNavigate }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'documents' | 'flashcards'>('all');

  const historyItems = [
    {
      id: 'h-1',
      title: 'Sample Science Class Notes - Photosynthesis.pdf',
      category: 'Science',
      type: 'PDF Document',
      date: 'Today, 10:14 AM',
      pages: 3,
      words: 420,
      hasDeck: true,
      deckSize: 12,
    },
    {
      id: 'h-2',
      title: 'History Homework - Early Civilizations.png',
      category: 'History',
      type: 'Handwritten Image',
      date: 'Yesterday, 4:30 PM',
      pages: 1,
      words: 215,
      hasDeck: true,
      deckSize: 8,
    },
    {
      id: 'h-3',
      title: 'English Essay Draft - Rotated Notes.jpg',
      category: 'English',
      type: 'Rotated Note',
      date: 'Aug 2, 2026',
      pages: 2,
      words: 340,
      hasDeck: true,
      deckSize: 15,
    },
    {
      id: 'h-4',
      title: 'Math Workbook Exercises Page 12.png',
      category: 'Mathematics',
      type: 'Worksheet',
      date: 'Jul 30, 2026',
      pages: 1,
      words: 180,
      hasDeck: false,
      deckSize: 0,
    },
  ];

  const filtered = historyItems.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.category.toLowerCase().includes(searchTerm.toLowerCase());
    if (filterType === 'documents') return matchesSearch && !item.hasDeck;
    if (filterType === 'flashcards') return matchesSearch && item.hasDeck;
    return matchesSearch;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 font-bold flex items-center justify-center border border-blue-100 flex-shrink-0">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-slate-900">Document & Study History</h2>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Access your previous class notes, transcriptions, and generated flashcard decks.
            </p>
          </div>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search documents or decks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div className="flex bg-slate-100 p-1 rounded-xl">
            {(['all', 'documents', 'flashcards'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition-all ${
                  filterType === type ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* History Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filtered.map((item) => (
          <div
            key={item.id}
            onClick={() => onNavigate('transcription')}
            className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-saas hover:shadow-saas-md transition-all duration-200 cursor-pointer space-y-4 group"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-3 rounded-2xl bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 uppercase tracking-wider">
                    {item.category}
                  </span>
                  <h3 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-1 mt-1">
                    {item.title}
                  </h3>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100">
              <span>{item.type} • {item.pages} page{item.pages > 1 ? 's' : ''}</span>
              <span className="font-semibold">{item.date}</span>
            </div>

            {item.hasDeck && (
              <div className="flex items-center justify-between bg-purple-50/70 p-2.5 rounded-xl text-xs font-bold text-purple-700">
                <div className="flex items-center space-x-2">
                  <GraduationCap className="w-4 h-4 text-purple-600" />
                  <span>Flashcard Deck Available</span>
                </div>
                <span>{item.deckSize} Cards</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
