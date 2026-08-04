import React from 'react';
import { BarChart3, TrendingUp, Award, BookOpen, Sparkles } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas flex items-center justify-between">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-600 font-bold flex items-center justify-center border border-emerald-100 flex-shrink-0">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-slate-900">Educational Analytics & Student Progress</h2>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Track handwriting readability scores, vocabulary mastery metrics, and proofreading improvements.
            </p>
          </div>
        </div>
      </div>

      {/* Analytics Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-saas space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">Handwriting Legibility Score</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-3xl font-black text-slate-900">92/100</p>
          <p className="text-xs text-emerald-600 font-semibold">+14% improvement over last 30 days</p>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-saas space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">Vocabulary Mastered</span>
            <BookOpen className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-3xl font-black text-slate-900">184 Words</p>
          <p className="text-xs text-blue-600 font-semibold">88% retention rate in flashcard quizzes</p>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-saas space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">Grammar & OCR Recovery</span>
            <Award className="w-4 h-4 text-purple-600" />
          </div>
          <p className="text-3xl font-black text-slate-900">96.8%</p>
          <p className="text-xs text-purple-600 font-semibold">Average confidence post-AI proofreading</p>
        </div>
      </div>

      {/* Visual Chart Placeholder Card */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-saas space-y-4">
        <h3 className="text-sm font-extrabold text-slate-900 flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <span>Handwriting Readability & Vocabulary Growth (Weekly)</span>
        </h3>

        <div className="h-56 bg-slate-50 rounded-2xl border border-slate-200/60 p-6 flex items-end justify-between space-x-4">
          {[
            { week: 'Week 1', height: '40%', score: '78' },
            { week: 'Week 2', height: '55%', score: '82' },
            { week: 'Week 3', height: '70%', score: '88' },
            { week: 'Week 4', height: '85%', score: '92' },
            { week: 'Current', height: '94%', score: '96' },
          ].map((bar, idx) => (
            <div key={idx} className="flex-1 flex flex-col items-center space-y-2 h-full justify-end">
              <span className="text-[11px] font-bold text-blue-600">{bar.score}</span>
              <div
                style={{ height: bar.height }}
                className="w-full bg-gradient-to-t from-blue-600 to-indigo-500 rounded-t-xl transition-all duration-300 hover:opacity-90"
              />
              <span className="text-[11px] font-semibold text-slate-500">{bar.week}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
