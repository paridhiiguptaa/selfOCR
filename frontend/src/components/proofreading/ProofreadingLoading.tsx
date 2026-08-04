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
    <div className="w-full flex flex-col items-center justify-center p-12 bg-white rounded-3xl border border-slate-200/80 shadow-saas min-h-[400px]">
      <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center shadow-2xs mb-6">
        <Sparkles className="w-7 h-7 text-blue-600 animate-spin" />
      </div>

      <h3 className="text-lg font-extrabold text-slate-900 mb-1 tracking-tight">
        AI Contextual Proofreading Engine Active
      </h3>
      <p className="text-xs text-slate-500 font-medium mb-6">Analyzing document structure and transcription confidence</p>

      <div className="w-full max-w-md bg-slate-50/80 p-5 rounded-2xl border border-slate-200/80 space-y-3 font-sans text-xs">
        {steps.map((msg, idx) => {
          const isDone = idx < step;
          const isCurrent = idx === step;

          return (
            <div
              key={msg}
              className={`flex items-center space-x-3 transition-all ${
                isDone
                  ? 'text-emerald-700 font-bold'
                  : isCurrent
                  ? 'text-blue-700 font-extrabold'
                  : 'text-slate-400 font-medium'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 text-blue-600 animate-spin flex-shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-300 flex-shrink-0" />
              )}
              <span>{msg}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
