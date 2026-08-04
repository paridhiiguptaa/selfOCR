import React, { useState } from 'react';
import { ProofreadingView } from '../proofreading/ProofreadingView';
import { DownloadManager } from '../DownloadManager';
import type { CorrectionSuggestionData, ProofreadingState, OCRResponse } from '../../types/ocr';
import { Sparkles, GraduationCap, ArrowRight, Download, X } from 'lucide-react';

interface ProofreadingPageProps {
  ocrPlainText: string;
  ocrResult: OCRResponse | null;
  onTextUpdate: (newText: string) => void;
  onSuggestionsChange: (accepted: CorrectionSuggestionData[]) => void;
  proofreadingState: ProofreadingState;
  onStateChange: (newState: Partial<ProofreadingState>) => void;
  onNavigateToFlashcards: () => void;
}

export const ProofreadingPage: React.FC<ProofreadingPageProps> = ({
  ocrPlainText,
  ocrResult,
  onTextUpdate,
  onSuggestionsChange,
  proofreadingState,
  onStateChange,
  onNavigateToFlashcards,
}) => {
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);

  const exportPayload: OCRResponse = ocrResult || {
    status: 'success',
    document_name: 'Proofread_Document.txt',
    total_pages: 1,
    export_paths: { txt: '', markdown: '', json: '' },
    transcription: { plain_text: ocrPlainText, markdown: `# Proofread Document\n\n${ocrPlainText}` },
    pages: []
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-purple-50 text-purple-600 font-bold flex items-center justify-center border border-purple-100 flex-shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-extrabold text-slate-900">Stage 4: AI Proofreading Studio</h2>
              <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                Grammar & Spelling Assistant
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Generate AI corrections to improve transcription accuracy, export files, or create flashcards.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <button
            onClick={() => setIsExportOpen(true)}
            className="flex-1 sm:flex-none flex items-center justify-center space-x-2 px-4 py-2.5 rounded-2xl bg-white hover:bg-slate-50 text-slate-700 font-extrabold text-xs border border-slate-200 shadow-xs transition-all duration-150 cursor-pointer whitespace-nowrap"
          >
            <Download className="w-4 h-4 text-blue-600" />
            <span>Export Document</span>
          </button>

          <button
            onClick={onNavigateToFlashcards}
            className="flex-1 sm:flex-none flex items-center justify-center space-x-2 px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs shadow-md shadow-blue-500/20 transition-all duration-150 transform hover:-translate-y-0.5 cursor-pointer whitespace-nowrap"
          >
            <GraduationCap className="w-4 h-4 text-emerald-300" />
            <span>Generate Flashcards</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Proofreading Studio Workspace */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-saas">
        <ProofreadingView
          ocrPlainText={ocrPlainText}
          onTextUpdate={onTextUpdate}
          onSuggestionsChange={onSuggestionsChange}
          proofreadingState={proofreadingState}
          onStateChange={onStateChange}
        />
      </div>

      {/* Export Options Modal */}
      {isExportOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-3xl w-full p-6 space-y-6 relative animate-fadeIn">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100">
                  <Download className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">Export Proofread Document</h3>
                  <p className="text-xs text-slate-500 font-medium">Select your preferred file format for download</p>
                </div>
              </div>

              <button
                onClick={() => setIsExportOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <DownloadManager
              ocrResult={exportPayload}
              onExportDocument={() => setIsExportOpen(false)}
            />

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setIsExportOpen(false)}
                className="px-5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
