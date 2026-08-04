import React from 'react';
import { PipelineProgressTracker } from '../PipelineProgressTracker';
import { Cpu, ArrowRight, CheckCircle2, RefreshCw } from 'lucide-react';

interface OcrProcessingPageProps {
  stageIndex: number;
  isCompleted: boolean;
  error: string | null;
  onNavigateToTranscription: () => void;
  onRetry: () => void;
}

export const OcrProcessingPage: React.FC<OcrProcessingPageProps> = ({
  stageIndex,
  isCompleted,
  error,
  onNavigateToTranscription,
  onRetry,
}) => {
  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-xs font-bold">
          <Cpu className="w-4 h-4 text-blue-600 animate-spin" />
          <span>Stage 2: Hybrid OCR Pipeline Processing</span>
        </div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          {isCompleted ? 'Processing Complete!' : 'Extracting Text & Analyzing Layout'}
        </h2>
        <p className="text-sm text-slate-500 font-medium max-w-xl mx-auto">
          Executing orientation detection, deskewing, hybrid text region classification, and Hugging Face TrOCR recognition.
        </p>
      </div>

      {/* Progress Tracker Card */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-saas">
        <PipelineProgressTracker
          currentStageIndex={stageIndex}
          isCompleted={isCompleted}
          error={error}
        />
      </div>

      {/* Completion CTA Card */}
      {isCompleted && (
        <div className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-6 rounded-3xl shadow-saas-lg flex flex-col sm:flex-row items-center justify-between gap-4 animate-scaleUp">
          <div className="flex items-center space-x-3.5">
            <div className="p-3 bg-white/20 rounded-2xl backdrop-blur-xs">
              <CheckCircle2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h4 className="text-base font-extrabold text-white">Transcription Ready</h4>
              <p className="text-xs text-emerald-100 font-medium">
                Text and document layout successfully extracted. Proceed to editor.
              </p>
            </div>
          </div>

          <button
            onClick={onNavigateToTranscription}
            className="flex items-center space-x-2 px-6 py-3 rounded-2xl bg-white hover:bg-emerald-50 text-emerald-800 font-extrabold text-sm shadow-md transition-all duration-150 transform hover:-translate-y-0.5 cursor-pointer whitespace-nowrap"
          >
            <span>Open Transcription Editor</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Error Retry Option */}
      {error && (
        <div className="flex justify-center">
          <button
            onClick={onRetry}
            className="flex items-center space-x-2 px-6 py-3 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-sm shadow-md transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Retry OCR Pipeline</span>
          </button>
        </div>
      )}
    </div>
  );
};
