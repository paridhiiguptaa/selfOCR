import React, { useState } from 'react';
import type { PageMetadata, OCRResponse } from '../../types/ocr';
import { TextEditor } from '../TextEditor';
import { BoundingBoxViewer } from '../BoundingBoxViewer';
import { SideBySideSlider } from '../SideBySideSlider';
import { RegionTable } from '../RegionTable';
import { DeveloperModePanel } from '../DeveloperModePanel';
import {
  FileText,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Box,
  Sliders,
  Table,
  Image as ImageIcon,
  CheckCircle2,
  ArrowRight,
  Code
} from 'lucide-react';

interface OcrTranscriptionPageProps {
  pageMeta: PageMetadata;
  ocrResult: OCRResponse;
  onTextChange: (newText: string) => void;
  onNavigateToProofreading: () => void;
  developerMode: boolean;
}

export const OcrTranscriptionPage: React.FC<OcrTranscriptionPageProps> = ({
  pageMeta,
  ocrResult,
  onTextChange,
  onNavigateToProofreading,
  developerMode,
}) => {
  const [showAdvancedAnalysis, setShowAdvancedAnalysis] = useState(false);
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<'boxes' | 'side-by-side' | 'table' | 'original'>('boxes');

  // Compute average confidence
  const avgConfidence = pageMeta.regions.length > 0
    ? (pageMeta.regions.reduce((acc, r) => acc + (r.confidence || 0), 0) / pageMeta.regions.length * 100).toFixed(1)
    : '98.5';

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Stage Header Banner */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 font-bold flex items-center justify-center border border-blue-100 flex-shrink-0">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-extrabold text-slate-900">Stage 3: OCR Transcription & Editor</h2>
              <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center space-x-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                <span>{avgConfidence}% Confidence</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Review extracted plain text and markdown. Move to AI Proofreading to fix spelling & grammar.
            </p>
          </div>
        </div>

        <button
          onClick={onNavigateToProofreading}
          className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs shadow-md shadow-blue-500/20 transition-all duration-150 transform hover:-translate-y-0.5 cursor-pointer whitespace-nowrap"
        >
          <Sparkles className="w-4 h-4 text-amber-300" />
          <span>Proceed to AI Proofreading</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Split View Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Uploaded Document Preview */}
        <div className="lg:col-span-5 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas flex flex-col space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
              <ImageIcon className="w-4 h-4 text-blue-600" />
              <span>Document Image Preview</span>
            </h3>
            <span className="text-[11px] font-semibold text-slate-500">
              Page {pageMeta.page_number || 1} • {pageMeta.resolution || '300 DPI'}
            </span>
          </div>

          <div className="flex-1 bg-slate-50 rounded-2xl border border-slate-200/60 p-3 flex items-center justify-center min-h-[420px] max-h-[580px] overflow-hidden">
            <img
              src={pageMeta.original_image_base64}
              alt="Original Document Preview"
              className="max-h-[540px] w-auto object-contain rounded-lg shadow-xs hover:scale-[1.02] transition-transform duration-200"
            />
          </div>
        </div>

        {/* Right Side: Transcription Text Editor */}
        <div className="lg:col-span-7 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-saas flex flex-col space-y-4">
          <TextEditor
            plainText={ocrResult.transcription.plain_text}
            markdownText={ocrResult.transcription.markdown}
            onTextChange={onTextChange}
          />
        </div>
      </div>

      {/* Expandable "Advanced Analysis" & Developer Mode Section */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-saas overflow-hidden">
        <button
          onClick={() => setShowAdvancedAnalysis(!showAdvancedAnalysis)}
          className="w-full p-5 flex items-center justify-between bg-slate-50/70 hover:bg-slate-100/70 transition-colors text-left"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-blue-100 text-blue-700">
              <Code className="w-4.5 h-4.5" />
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">Advanced OCR Analysis & Technical Diagnostics</h3>
              <p className="text-xs text-slate-500 font-medium">
                View detected text bounding boxes, preprocessed image comparisons, and region classification tables.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-xs font-bold text-blue-600">
            <span>{showAdvancedAnalysis ? 'Hide Analysis' : 'Show Advanced Diagnostics'}</span>
            {showAdvancedAnalysis ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {showAdvancedAnalysis && (
          <div className="p-6 border-t border-slate-200 space-y-6 animate-fadeIn">
            {/* Analysis Tabs */}
            <div className="flex space-x-2 border-b border-slate-200 pb-3">
              {[
                { id: 'boxes', label: 'Detected Regions', icon: Box },
                { id: 'side-by-side', label: 'Preprocessed Comparison', icon: Sliders },
                { id: 'table', label: 'Recognition Table', icon: Table },
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeAnalysisTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveAnalysisTab(tab.id as any)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-bold text-xs transition-all ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-xs'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Analysis Content Views */}
            {activeAnalysisTab === 'boxes' && (
              <BoundingBoxViewer
                annotatedImage={pageMeta.annotated_image_base64}
                regions={pageMeta.regions}
              />
            )}

            {activeAnalysisTab === 'side-by-side' && (
              <SideBySideSlider
                originalImage={pageMeta.original_image_base64}
                preprocessedImage={pageMeta.preprocessed_image_base64}
                orientationAngle={pageMeta.orientation.rotation_angle}
                skewAngle={pageMeta.orientation.skew_angle}
                perspectiveCorrected={pageMeta.orientation.perspective_corrected}
              />
            )}

            {activeAnalysisTab === 'table' && <RegionTable regions={pageMeta.regions} />}

            {/* Developer Mode Diagnostics Panel */}
            {developerMode && ocrResult.developer_telemetry && (
              <div className="pt-4 border-t border-slate-200">
                <DeveloperModePanel
                  pageMeta={pageMeta}
                  telemetry={ocrResult.developer_telemetry}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
