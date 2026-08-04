import React from 'react';
import { CheckCircle2, Loader2, AlertCircle, Sparkles } from 'lucide-react';

interface PipelineProgressTrackerProps {
  currentStageIndex: number;
  isCompleted: boolean;
  error: string | null;
}

export const PipelineProgressTracker: React.FC<PipelineProgressTrackerProps> = ({
  currentStageIndex,
  isCompleted,
  error,
}) => {
  const stages = [
    'Uploading document',
    'Converting PDF to images',
    'Orientation detection & rotation',
    'Deskewing & perspective correction',
    'Image quality enhancement (CLAHE)',
    'Surya layout & reading order analysis',
    'Primary OCR recognition (Qwen VLM / Crop)',
    'Confidence evaluation & region fallback',
    'Baseline document structure reconstruction',
    'Educational subject detection',
    'Optional multi-model ensemble & VLM verification',
    'Final transcription assembly & export'
  ];

  const progressPercent = isCompleted
    ? 100
    : Math.round(((currentStageIndex + 1) / stages.length) * 100);

  return (
    <div className="w-full space-y-5 select-none">
      {/* Overall Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs font-bold">
          <span className="text-slate-800 flex items-center space-x-1.5">
            <Sparkles className="w-4 h-4 text-blue-600 animate-pulse" />
            <span>
              {isCompleted
                ? 'OCR Pipeline Complete (100%)'
                : error
                ? 'Processing Interrupted'
                : `Executing Step ${currentStageIndex + 1} of ${stages.length}: ${stages[currentStageIndex] || 'Processing...'}`}
            </span>
          </span>
          <span className="text-blue-600 font-extrabold">{progressPercent}%</span>
        </div>

        <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden border border-slate-200/60 p-0.5">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              error
                ? 'bg-rose-500'
                : isCompleted
                ? 'bg-emerald-500'
                : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500'
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Stage Items Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-2">
        {stages.map((stage, idx) => {
          const isDone = isCompleted || idx < currentStageIndex;
          const isCurrent = !isCompleted && !error && idx === currentStageIndex;

          return (
            <div
              key={idx}
              className={`p-3 rounded-2xl border text-xs font-semibold flex items-center space-x-3 transition-all duration-150 ${
                isDone
                  ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                  : isCurrent
                  ? 'bg-blue-50 border-blue-300 text-blue-900 shadow-xs ring-1 ring-blue-400/40'
                  : 'bg-slate-50/50 border-slate-200 text-slate-400'
              }`}
            >
              <div className="flex-shrink-0">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-300 bg-white" />
                )}
              </div>
              <span className="truncate">{stage}</span>
            </div>
          );
        })}
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center space-x-3 text-rose-800 text-xs font-semibold">
          <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
