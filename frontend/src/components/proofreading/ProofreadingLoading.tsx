import React, { useState, useEffect } from 'react';
import { Sparkles, CheckCircle2, Loader2 } from 'lucide-react';

interface ProofreadingLoadingProps {
  onComplete?: () => void;
}

export const ProofreadingLoading: React.FC<ProofreadingLoadingProps> = () => {
  const [step, setStep] = useState<number>(0);

  const steps = [
    'Analyzing grammar & sentence syntax...',
    'Checking contextual spelling & vocabulary...',
    'Detecting missing connecting words & articles...',
    'Recovering OCR transcription artifacts...',
    'Generating structured correction suggestions...',
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 450);
    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <div className="w-full flex flex-col items-center justify-center p-12 bg-slate-900/90 rounded-2xl border border-slate-800 shadow-2xl min-h-[400px]">
      <div className="relative mb-6">
        <div className="absolute -inset-4 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 blur-lg opacity-40 animate-pulse" />
        <div className="relative p-4 bg-slate-950 rounded-2xl border border-slate-800 text-indigo-400">
          <Sparkles className="w-8 h-8 animate-spin" />
        </div>
      </div>

      <h3 className="text-lg font-bold text-white mb-2 tracking-wide">
        AI Contextual Proofreading Engine Active
      </h3>
      <p className="text-xs text-slate-400 mb-6">Analyzing document structure and transcription confidence</p>

      <div className="w-full max-w-md bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3 font-mono text-xs">
        {steps.map((msg, idx) => {
          const isDone = idx < step;
          const isCurrent = idx === step;

          return (
            <div
              key={msg}
              className={`flex items-center space-x-3 transition-all ${
                isDone
                  ? 'text-emerald-400 font-semibold'
                  : isCurrent
                  ? 'text-indigo-300 font-bold animate-pulse'
                  : 'text-slate-600'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 text-indigo-400 animate-spin flex-shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-800 flex-shrink-0" />
              )}
              <span>{msg}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
