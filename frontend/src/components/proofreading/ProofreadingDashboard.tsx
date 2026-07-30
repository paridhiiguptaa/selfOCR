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
    <div className="w-full flex flex-col space-y-4 bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl">
      {/* Workflow Stage Progress Indicator */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 shadow-lg shadow-indigo-500/30 text-white">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-wide flex items-center space-x-2">
              <span>AI Proofreading & Correction Studio</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Active Phase 4
              </span>
            </h3>
            <p className="text-xs text-slate-400">Contextual grammar proofreader & missing-word recovery</p>
          </div>
        </div>

        {/* Pipeline Stage Badges */}
        <div className="hidden md:flex items-center space-x-2 text-xs font-semibold">
          <span className="px-3 py-1 rounded-lg bg-slate-800 text-slate-400 border border-slate-700/60">
            1. Document Upload
          </span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-1 rounded-lg bg-slate-800 text-slate-400 border border-slate-700/60">
            2. VLM OCR
          </span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-1 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md border border-blue-400/40">
            3. AI Proofreading
          </span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-1 rounded-lg bg-slate-800 text-slate-400 border border-slate-700/60">
            4. Export
          </span>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Metric 1: Quality Score */}
        <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-slate-400 tracking-wider uppercase flex items-center justify-between">
            Quality Score
            <FileCheck className="w-3.5 h-3.5 text-blue-400" />
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className={`text-2xl font-black ${qualityScore >= 85 ? 'text-emerald-400' : qualityScore >= 70 ? 'text-amber-400' : 'text-red-400'}`}>
              {qualityScore}%
            </span>
            <span className="text-[10px] text-slate-500 font-mono">{processingTimeSec}s</span>
          </div>
        </div>

        {/* Metric 2: Total Suggestions */}
        <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-slate-400 tracking-wider uppercase flex items-center justify-between">
            Suggestions
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-indigo-300">{totalCount}</span>
            <span className="text-[10px] text-indigo-400 font-medium">{pendingCount} pending</span>
          </div>
        </div>

        {/* Metric 3: Spelling Errors */}
        <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-red-400/90 tracking-wider uppercase flex items-center justify-between">
            Spelling
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-red-400">{metrics.spelling_errors}</span>
            <span className="text-[10px] text-red-400/70 font-medium">errors</span>
          </div>
        </div>

        {/* Metric 4: Grammar Errors */}
        <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-amber-400/90 tracking-wider uppercase flex items-center justify-between">
            Grammar
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-amber-400">{metrics.grammar_errors}</span>
            <span className="text-[10px] text-amber-400/70 font-medium">issues</span>
          </div>
        </div>

        {/* Metric 5: Missing Words */}
        <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-blue-400/90 tracking-wider uppercase flex items-center justify-between">
            Missing Words
            <HelpCircle className="w-3.5 h-3.5 text-blue-400" />
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-blue-400">{metrics.missing_words}</span>
            <span className="text-[10px] text-blue-400/70 font-medium">inferred</span>
          </div>
        </div>

        {/* Metric 6: Resolved */}
        <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-emerald-400/90 tracking-wider uppercase flex items-center justify-between">
            Accepted
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-emerald-400">{acceptedIds.length}</span>
            <span className="text-[10px] text-slate-500 font-medium">{rejectedIds.length} rejected</span>
          </div>
        </div>
      </div>
    </div>
  );
};
