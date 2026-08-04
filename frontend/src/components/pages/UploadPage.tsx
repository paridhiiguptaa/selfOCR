import React from 'react';
import { UploadZone } from '../UploadZone';
import { PdfPageSelector } from '../PdfPageSelector';
import { Play, Sparkles, SlidersHorizontal, RefreshCw } from 'lucide-react';
import type { PipelineSettings } from '../../types/ocr';

interface UploadPageProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  isProcessing: boolean;
  pdfThumbnails: any[];
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onRunOcr: () => void;
  onReset: () => void;
  backendConnected: boolean;
  settings: PipelineSettings;
  onUpdateSettings: (newSettings: PipelineSettings) => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({
  onFileSelect,
  selectedFile,
  isProcessing,
  pdfThumbnails,
  currentPage,
  totalPages,
  onPageChange,
  onRunOcr,
  onReset,
  backendConnected,
  settings,
  onUpdateSettings,
}) => {
  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-xs font-bold">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <span>Stage 1: Document Upload & Pre-processing</span>
        </div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Upload Educational Documents or Class Notes
        </h2>
        <p className="text-sm text-slate-500 max-w-2xl mx-auto font-medium">
          Supports multi-page PDFs, scanned documents, and rotated handwritten student notes.
        </p>
      </div>

      {/* Main Upload Dropzone Container */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-saas space-y-6">
        <UploadZone
          onFileSelect={onFileSelect}
          selectedFile={selectedFile}
          isProcessing={isProcessing}
        />

        {/* PDF Multi-Page Thumbnail Selector */}
        {pdfThumbnails.length > 0 && (
          <div className="pt-4 border-t border-slate-100">
            <PdfPageSelector
              totalPages={totalPages}
              currentPage={currentPage}
              thumbnails={pdfThumbnails}
              onPageChange={onPageChange}
            />
          </div>
        )}

        {/* Inline Pre-processing Settings Drawer */}
        {selectedFile && (
          <div className="pt-4 border-t border-slate-100 bg-slate-50/50 p-4 rounded-2xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-extrabold text-slate-700 flex items-center space-x-1.5">
                <SlidersHorizontal className="w-4 h-4 text-blue-600" />
                <span>Pre-processing & Pipeline Configuration</span>
              </span>
              <span className="text-[11px] font-semibold text-slate-500">Auto-deskew & Orientation Enabled</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
              <label className="flex items-center space-x-2.5 bg-white p-2.5 rounded-xl border border-slate-200 text-xs cursor-pointer hover:border-blue-300">
                <input
                  type="checkbox"
                  checked={settings.enable_orientation_correction}
                  onChange={(e) =>
                    onUpdateSettings({ ...settings, enable_orientation_correction: e.target.checked })
                  }
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="font-semibold text-slate-700">Auto Rotate (0/90/180/270°)</span>
              </label>

              <label className="flex items-center space-x-2.5 bg-white p-2.5 rounded-xl border border-slate-200 text-xs cursor-pointer hover:border-blue-300">
                <input
                  type="checkbox"
                  checked={settings.enable_deskew}
                  onChange={(e) =>
                    onUpdateSettings({ ...settings, enable_deskew: e.target.checked })
                  }
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="font-semibold text-slate-700">Deskew & Perspective</span>
              </label>

              <label className="flex items-center space-x-2.5 bg-white p-2.5 rounded-xl border border-slate-200 text-xs cursor-pointer hover:border-blue-300">
                <input
                  type="checkbox"
                  checked={settings.enable_quality_enhancement}
                  onChange={(e) =>
                    onUpdateSettings({ ...settings, enable_quality_enhancement: e.target.checked })
                  }
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="font-semibold text-slate-700">CLAHE & Denoise</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {selectedFile && !isProcessing && (
        <div className="flex items-center justify-center space-x-4">
          <button
            onClick={onRunOcr}
            disabled={!backendConnected}
            className="flex items-center space-x-2.5 px-8 py-3.5 rounded-2xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-extrabold text-sm shadow-md shadow-blue-500/25 transition-all transform hover:-translate-y-0.5 cursor-pointer"
          >
            <Play className="w-4.5 h-4.5 fill-current" />
            <span>Start OCR Workflow</span>
          </button>

          <button
            onClick={onReset}
            className="flex items-center space-x-2 px-5 py-3.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-sm border border-slate-200 transition-colors cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Reset Selection</span>
          </button>
        </div>
      )}
    </div>
  );
};
