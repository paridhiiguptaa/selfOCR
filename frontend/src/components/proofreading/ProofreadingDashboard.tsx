import React from 'react';
import type { CorrectionQualityMetrics, CorrectionSuggestionData } from '../../types/ocr';
import { Sparkles, CheckCircle2, AlertTriangle, HelpCircle, FileCheck, Layers } from 'lucide-react';

interface ProofreadingDashboardProps {
  metrics: CorrectionQualityMetrics;
  suggestions: CorrectionSuggestionData[];
  acceptedIds: string[];
  rejectedIds: string[];
  processingTimeSec: number;
}

export const ProofreadingDashboard: React.FC<ProofreadingDashboardProps> = ({
  metrics,
  suggestions,
  acceptedIds,
  rejectedIds,
  processingTimeSec,
}) => {
  const pendingCount = suggestions.length - acceptedIds.length - rejectedIds.length;
  const totalCount = suggestions.length;

  // Calculate dynamic document quality score (0 to 100%)
  const qualityScore = totalCount === 0 
    ? 100 
    : Math.max(50, Math.round(100 - (pendingCount * 3.5)));

  return (
    <div className="w-full flex flex-col space-y-4 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas">
      {/* Workflow Stage Progress Indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 font-bold flex items-center justify-center border border-purple-100 flex-shrink-0">
            <Sparkles className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900 flex items-center space-x-2">
              <span>AI Proofreading & Correction Studio</span>
              <span className="text-[11px] font-extrabold px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                Phase 4 Active
              </span>
            </h3>
            <p className="text-xs text-slate-500 font-medium">Contextual grammar proofreader & missing-word recovery</p>
          </div>
        </div>

        {/* Modern Horizontal Stepper */}
        <div className="hidden lg:flex items-center space-x-2 text-xs font-semibold">
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 font-extrabold">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>1. Upload</span>
          </div>
          <span className="text-slate-300 font-bold">→</span>
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 font-extrabold">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>2. VLM OCR</span>
          </div>
          <span className="text-slate-300 font-bold">→</span>
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-blue-600 text-white font-extrabold shadow-xs">
            <Sparkles className="w-3.5 h-3.5 text-purple-200" />
            <span>3. Proofreading</span>
          </div>
          <span className="text-slate-300 font-bold">→</span>
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-slate-100 text-slate-500 border border-slate-200 font-semibold">
            <span>4. Study Decks</span>
          </div>
        </div>
      </div>

      {/* Reusable White Metrics Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Metric 1: Quality Score */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-saas-md transition-all flex flex-col justify-between space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold tracking-wider uppercase">Quality Score</span>
            <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100">
              <FileCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className={`text-2xl font-black ${qualityScore >= 85 ? 'text-emerald-600' : qualityScore >= 70 ? 'text-amber-600' : 'text-rose-600'}`}>
              {qualityScore}%
            </span>
            <span className="text-[10px] text-slate-400 font-bold">{processingTimeSec}s</span>
          </div>
        </div>

        {/* Metric 2: Total Suggestions */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-saas-md transition-all flex flex-col justify-between space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold tracking-wider uppercase">Suggestions</span>
            <div className="w-7 h-7 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center border border-purple-100">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-slate-900">{totalCount}</span>
            <span className="text-[10px] text-purple-600 font-bold">{pendingCount} pending</span>
          </div>
        </div>

        {/* Metric 3: Spelling Errors */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-saas-md transition-all flex flex-col justify-between space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold text-rose-600 tracking-wider uppercase">Spelling</span>
            <div className="w-7 h-7 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center border border-rose-100">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-rose-600">{metrics.spelling_errors}</span>
            <span className="text-[10px] text-slate-400 font-bold">errors</span>
          </div>
        </div>

        {/* Metric 4: Grammar Errors */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-saas-md transition-all flex flex-col justify-between space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold text-amber-600 tracking-wider uppercase">Grammar</span>
            <div className="w-7 h-7 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-amber-600">{metrics.grammar_errors}</span>
            <span className="text-[10px] text-slate-400 font-bold">issues</span>
          </div>
        </div>

        {/* Metric 5: Missing Words */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-saas-md transition-all flex flex-col justify-between space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold text-indigo-600 tracking-wider uppercase">Missing Words</span>
            <div className="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center border border-indigo-100">
              <HelpCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-indigo-600">{metrics.missing_words}</span>
            <span className="text-[10px] text-slate-400 font-bold">inferred</span>
          </div>
        </div>

        {/* Metric 6: Resolved / Accepted */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-saas-md transition-all flex flex-col justify-between space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-extrabold text-emerald-600 tracking-wider uppercase">Accepted</span>
            <div className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-emerald-600">{acceptedIds.length}</span>
            <span className="text-[10px] text-slate-400 font-bold">{rejectedIds.length} rejected</span>
          </div>
        </div>
      </div>
    </div>
  );
};
