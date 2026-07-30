import React from 'react';
import type { FlashcardDeckData, FlashcardTelemetry } from '../../types/ocr';
import {
  Layers,
  Clock,
  Award,
  Sparkles,
  Zap,
  BarChart3,
  CheckCircle2,
  PieChart
} from 'lucide-react';

interface LearningDashboardProps {
  deck: FlashcardDeckData;
  telemetry?: FlashcardTelemetry;
}

export const LearningDashboard: React.FC<LearningDashboardProps> = ({ deck, telemetry }) => {
  const totalCards = deck.total_flashcards;
  const categories = deck.categories_distribution || {};
  const difficulty = deck.difficulty_distribution || {};
  const estTime = deck.estimated_study_time_min;
  const masteryPct = deck.mastery_percentage || 0;

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 text-indigo-400 font-bold text-xs uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>AI Learning Flashcards Dashboard</span>
          </div>
          <h2 className="text-xl font-black text-white tracking-tight flex items-center space-x-2">
            <span>{deck.source_document_title || 'Exported Document Deck'}</span>
          </h2>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>Est. {estTime} min study time</span>
          </div>
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-xs font-bold text-indigo-300">
            <Award className="w-3.5 h-3.5 text-indigo-400" />
            <span>{masteryPct}% Mastered</span>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Metric 1: Total Flashcards */}
        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Total Cards</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-black text-white">{totalCards}</p>
          <span className="text-[10px] text-slate-500 font-mono">Personalized from corrections</span>
        </div>

        {/* Metric 2: Estimated Study Time */}
        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Study Duration</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-black text-white">{estTime} <span className="text-sm font-semibold text-slate-400">mins</span></p>
          <span className="text-[10px] text-slate-500 font-mono">Active recall pace</span>
        </div>

        {/* Metric 3: Mastery Score */}
        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Mastery Rate</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black text-emerald-400">{masteryPct}%</p>
          <span className="text-[10px] text-slate-500 font-mono">{deck.study_progress?.cards_mastered || 0} / {totalCards} cards mastered</span>
        </div>

        {/* Metric 4: Duplicates & Optimization */}
        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Optimization</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-black text-white">
            {telemetry?.duplicate_cards_removed ?? 0} <span className="text-xs font-normal text-slate-400">merged</span>
          </p>
          <span className="text-[10px] text-slate-500 font-mono">Duplicates removed</span>
        </div>
      </div>

      {/* Category Breakdown & Difficulty Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        {/* Categories Breakdown */}
        <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-3">
          <div className="flex items-center space-x-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
            <PieChart className="w-4 h-4 text-indigo-400" />
            <span>Mistake Categories</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(categories).map(([cat, count], idx) => (
              <div
                key={idx}
                className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300"
              >
                <span className="font-semibold">{cat}</span>
                <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] font-black">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Difficulty Distribution */}
        <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-3">
          <div className="flex items-center space-x-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            <span>Difficulty Breakdown</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-center">
              <span className="text-[10px] font-bold text-emerald-400 uppercase block">Easy</span>
              <span className="text-lg font-black text-emerald-200">{difficulty['Easy'] || 0}</span>
            </div>
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-center">
              <span className="text-[10px] font-bold text-amber-400 uppercase block">Medium</span>
              <span className="text-lg font-black text-amber-200">{difficulty['Medium'] || 0}</span>
            </div>
            <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-center">
              <span className="text-[10px] font-bold text-rose-400 uppercase block">Hard</span>
              <span className="text-lg font-black text-rose-200">{difficulty['Hard'] || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
