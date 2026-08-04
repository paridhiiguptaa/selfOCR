import React from 'react';
import { DownloadManager } from '../DownloadManager';
import type { OCRResponse } from '../../types/ocr';
import { Download } from 'lucide-react';

interface ExportPageProps {
  ocrResult: OCRResponse | null;
  onExportDocument: () => void;
}

export const ExportPage: React.FC<ExportPageProps> = ({
  ocrResult,
  onExportDocument,
}) => {
  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas flex items-center justify-between">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 font-bold flex items-center justify-center border border-blue-100 flex-shrink-0">
            <Download className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-slate-900">Stage 6: Export Document & Study Decks</h2>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Select your preferred format to save your transcribed text, proofread corrections, or flashcards.
            </p>
          </div>
        </div>
      </div>

      {ocrResult ? (
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-saas space-y-6">
          <DownloadManager
            ocrResult={ocrResult}
            onExportDocument={onExportDocument}
          />
        </div>
      ) : (
        <div className="bg-white p-12 rounded-3xl border border-slate-200/80 shadow-saas text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
            <Download className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-800">No Document Ready for Export</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Please upload a document and run the OCR processing pipeline to generate exportable files.
          </p>
        </div>
      )}
    </div>
  );
};
