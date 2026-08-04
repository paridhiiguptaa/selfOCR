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
    <div className="w-full bg-white border border-slate-200/80 rounded-3xl p-6 shadow-saas space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 text-blue-600 font-extrabold text-xs uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>Educational Study Deck Analytics</span>
          </div>
          <h2 className="text-xl font-black text-slate-900 tracking-tight flex items-center space-x-2">
            <span>{deck.source_document_title || 'Exported Document Deck'}</span>
          </h2>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-xs font-bold text-slate-700">
            <Clock className="w-3.5 h-3.5 text-blue-600" />
            <span>Est. {estTime} min study time</span>
          </div>
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-700">
            <Award className="w-3.5 h-3.5 text-emerald-600" />
            <span>{masteryPct}% Mastered</span>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Metric 1: Total Flashcards */}
        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-xs space-y-2 hover:shadow-saas-md transition-all">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold uppercase tracking-wider">Total Cards</span>
            <div className="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center border border-indigo-100">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900">{totalCards}</p>
          <span className="text-[10px] text-slate-400 font-bold">Vocabulary & study terms</span>
        </div>

        {/* Metric 2: Estimated Study Time */}
        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-xs space-y-2 hover:shadow-saas-md transition-all">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold uppercase tracking-wider">Duration</span>
            <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900">{estTime} <span className="text-xs font-bold text-slate-500">mins</span></p>
          <span className="text-[10px] text-slate-400 font-bold">Active recall pace</span>
        </div>

        {/* Metric 3: Mastery Score */}
        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-xs space-y-2 hover:shadow-saas-md transition-all">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold uppercase tracking-wider">Mastery Rate</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-emerald-600">{masteryPct}%</p>
          <span className="text-[10px] text-slate-400 font-bold">{deck.study_progress?.cards_mastered || 0} / {totalCards} cards mastered</span>
        </div>

        {/* Metric 4: Optimization */}
        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-xs space-y-2 hover:shadow-saas-md transition-all">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold uppercase tracking-wider">Optimization</span>
            <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900">
            {telemetry?.duplicate_cards_removed ?? 0} <span className="text-xs font-semibold text-slate-500">merged</span>
          </p>
          <span className="text-[10px] text-slate-400 font-bold">Duplicates removed</span>
        </div>
      </div>

      {/* Category Breakdown & Difficulty Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        {/* Categories Breakdown */}
        <div className="p-5 bg-slate-50/70 border border-slate-200/80 rounded-2xl space-y-3">
          <div className="flex items-center space-x-2 text-xs font-extrabold text-slate-700 uppercase tracking-wider">
            <PieChart className="w-4 h-4 text-blue-600" />
            <span>Subject & Topic Categories</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(categories).map(([cat, count], idx) => (
              <div
                key={idx}
                className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-xs text-slate-700 font-bold shadow-2xs"
              >
                <span>{cat}</span>
                <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-100 text-[10px] font-extrabold">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Difficulty Distribution */}
        <div className="p-5 bg-slate-50/70 border border-slate-200/80 rounded-2xl space-y-3">
          <div className="flex items-center space-x-2 text-xs font-extrabold text-slate-700 uppercase tracking-wider">
            <BarChart3 className="w-4 h-4 text-emerald-600" />
            <span>Difficulty Breakdown</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-center">
              <span className="text-[10px] font-extrabold text-emerald-700 uppercase block">Easy</span>
              <span className="text-lg font-black text-emerald-900">{difficulty['Easy'] || 0}</span>
            </div>
            <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-center">
              <span className="text-[10px] font-extrabold text-amber-700 uppercase block">Medium</span>
              <span className="text-lg font-black text-amber-900">{difficulty['Medium'] || 0}</span>
            </div>
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-center">
              <span className="text-[10px] font-extrabold text-rose-700 uppercase block">Hard</span>
              <span className="text-lg font-black text-rose-900">{difficulty['Hard'] || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
