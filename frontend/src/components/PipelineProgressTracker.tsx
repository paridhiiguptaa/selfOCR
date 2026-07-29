import React from 'react';
import { CheckCircle2, Loader2, Circle, AlertTriangle } from 'lucide-react';

interface StageInfo {
  name: string;
}

interface PipelineProgressTrackerProps {
  currentStageIndex: number;
  isCompleted: boolean;
  error?: string | null;
}

export const stagesList: StageInfo[] = [
  { name: 'Uploading document & validating format' },
  { name: 'Converting PDF pages to high-res images (300 DPI)' },
  { name: 'Automatic 0°/90°/180°/270° orientation detection' },
  { name: 'Fine-angle deskewing & 4-corner perspective correction' },
  { name: 'Non-destructive quality enhancement (CLAHE / Denoise)' },
  { name: 'Text region bounding box detection (DBNet)' },
  { name: 'Printed vs Handwritten stroke feature classification' },
  { name: 'Printed text recognition engine (PaddleOCR)' },
  { name: 'Handwritten text recognition engine (Hugging Face TrOCR)' },
  { name: 'Natural reading order & multi-column layout analysis' },
  { name: 'Confidence scoring & low-confidence fallback recovery' },
  { name: 'Reconstructing Plain Text & Markdown transcriptions' },
];

export const PipelineProgressTracker: React.FC<PipelineProgressTrackerProps> = ({
  currentStageIndex,
  isCompleted,
  error,
}) => {
  const percent = isCompleted
    ? 100
    : Math.min(99, Math.round(((currentStageIndex + 1) / stagesList.length) * 100));

  return (
    <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-6 mb-8 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            {!isCompleted && !error && <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />}
            {isCompleted && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
            {error && <AlertTriangle className="w-5 h-5 text-rose-400" />}
            <span>
              {isCompleted
                ? 'OCR Pipeline Processing Completed!'
                : error
                ? 'Processing Interrupted'
                : 'Executing OCR Pipeline...'}
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            {isCompleted
              ? 'All 12 pipeline stages executed successfully'
              : stagesList[currentStageIndex]?.name || 'Initializing...'}
          </p>
        </div>

        <div className="text-right">
          <span className="text-2xl font-black text-blue-400 font-mono">{percent}%</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden mb-6 border border-slate-700/60">
        <div
          className={`h-full transition-all duration-500 rounded-full ${
            error
              ? 'bg-rose-500'
              : isCompleted
              ? 'bg-emerald-500'
              : 'bg-gradient-to-r from-blue-500 to-indigo-500'
          }`}
          style={{ width: `${percent}%` }}
        />
      </div>

      {/* Grid of Stages */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
        {stagesList.map((stage, idx) => {
          let status: 'completed' | 'current' | 'pending' | 'failed' = 'pending';
          if (error && idx === currentStageIndex) {
            status = 'failed';
          } else if (isCompleted || idx < currentStageIndex) {
            status = 'completed';
          } else if (idx === currentStageIndex) {
            status = 'current';
          }

          return (
            <div
              key={idx}
              className={`flex items-center space-x-2.5 p-2.5 rounded-xl border text-xs transition-all ${
                status === 'completed'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : status === 'current'
                  ? 'bg-blue-500/15 border-blue-500/50 text-blue-200 font-semibold glow-blue'
                  : status === 'failed'
                  ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                  : 'bg-slate-900/40 border-slate-800 text-slate-500'
              }`}
            >
              {status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
              {status === 'current' && <Loader2 className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" />}
              {status === 'pending' && <Circle className="w-4 h-4 text-slate-600 flex-shrink-0" />}
              {status === 'failed' && <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />}

              <span className="truncate">{stage.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
