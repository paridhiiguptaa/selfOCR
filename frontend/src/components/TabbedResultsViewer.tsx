import React, { useState } from 'react';
import type { PageMetadata, OCRResponse, CorrectionSuggestionData } from '../types/ocr';
import { SideBySideSlider } from './SideBySideSlider';
import { BoundingBoxViewer } from './BoundingBoxViewer';
import { RegionTable } from './RegionTable';
import { TextEditor } from './TextEditor';
import { DownloadManager } from './DownloadManager';
import { ProofreadingView } from './proofreading/ProofreadingView';
import { FlashcardHub } from './flashcards/FlashcardHub';
import { Image as ImageIcon, Sliders, Box, Table, FileText, Sparkles, GraduationCap } from 'lucide-react';

interface TabbedResultsViewerProps {
  pageMeta: PageMetadata;
  ocrResult: OCRResponse;
  onTextChange: (newText: string) => void;
}

export const TabbedResultsViewer: React.FC<TabbedResultsViewerProps> = ({
  pageMeta,
  ocrResult,
  onTextChange,
}) => {
  const [activeTab, setActiveTab] = useState<
    'transcription' | 'proofreading' | 'flashcards' | 'side-by-side' | 'boxes' | 'table' | 'original'
  >('transcription');

  const [isDocumentExported, setIsDocumentExported] = useState<boolean>(false);
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<CorrectionSuggestionData[]>([]);
  const [hasRunProofreading, setHasRunProofreading] = useState<boolean>(false);

  const tabs = [
    { id: 'transcription', label: '📄 OCR Transcription & Editor', icon: FileText, primary: true },
    { id: 'proofreading', label: '✨ AI Proofreading Studio', icon: Sparkles, primary: true },
    { id: 'flashcards', label: '🎓 AI Learning Flashcards', icon: GraduationCap, primary: true },
    { id: 'boxes', label: 'Detected Regions', icon: Box },
    { id: 'side-by-side', label: 'Preprocessed Comparison', icon: Sliders },
    { id: 'table', label: 'Recognition Results', icon: Table },
    { id: 'original', label: 'Original Document', icon: ImageIcon },
  ];

  const handleExportTrigger = () => {
    setIsDocumentExported(true);
    setActiveTab('transcription');
  };

  const handleTriggerProofreading = () => {
    setHasRunProofreading(true);
    setActiveTab('proofreading');
  };

  return (
    <div className="w-full flex flex-col space-y-6">
      {/* Tab Navigation Header */}
      <div className="flex space-x-2 bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800 overflow-x-auto shadow-lg">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all whitespace-nowrap ${
                isActive
                  ? tab.primary
                    ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 text-white shadow-md shadow-indigo-500/30 ring-1 ring-indigo-400'
                    : 'bg-slate-800 text-white border border-slate-700 shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content Container */}
      <div className="w-full">
        {/* Tab 1: Final Transcription & Text Editor */}
        {activeTab === 'transcription' && (
          <div className="flex flex-col space-y-6">
            {/* Decoupled Workflow Banner: Show AI Corrections CTA */}
            <div className="flex flex-col sm:flex-row items-center justify-between p-4 bg-gradient-to-r from-indigo-950/80 via-slate-900 to-purple-950/80 rounded-2xl border border-indigo-800/60 shadow-lg">
              <div className="flex items-center space-x-3 mb-3 sm:mb-0">
                <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-md">
                  <Sparkles className="w-5 h-5 animate-pulse" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                    <span>Raw OCR Transcription Ready</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono">
                      {hasRunProofreading ? 'AI Proofread' : 'Raw OCR'}
                    </span>
                  </h4>
                  <p className="text-xs text-slate-300">
                    Review and edit recognized text below, or trigger AI Proofreading to fix spelling, grammar, and punctuation.
                  </p>
                </div>
              </div>
              <button
                onClick={handleTriggerProofreading}
                className="flex items-center space-x-2 px-5 py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/30 border border-indigo-400/40 transition-all transform hover:-translate-y-0.5 active:translate-y-0"
              >
                <Sparkles className="w-4 h-4" />
                <span>Show AI Corrections</span>
              </button>
            </div>

            <TextEditor
              plainText={ocrResult.transcription.plain_text}
              markdownText={ocrResult.transcription.markdown}
              onTextChange={onTextChange}
            />
            <DownloadManager
              ocrResult={ocrResult}
              onExportDocument={() => setIsDocumentExported(true)}
            />
          </div>
        )}

        {/* Tab 2: AI Proofreading & Corrections Studio */}
        {activeTab === 'proofreading' && (
          <ProofreadingView
            ocrPlainText={ocrResult.transcription.plain_text}
            onTextUpdate={onTextChange}
            onSuggestionsChange={(accepted) => {
              setAcceptedSuggestions(accepted);
            }}
          />
        )}

        {/* Tab 3: AI Flashcards Learning Module */}
        {activeTab === 'flashcards' && (
          <FlashcardHub
            exportedText={ocrResult.transcription.plain_text}
            acceptedSuggestions={acceptedSuggestions}
            documentTitle={ocrResult.document_name}
            isDocumentExported={isDocumentExported}
            onTriggerExport={handleExportTrigger}
          />
        )}

        {/* Tab 4: Original Document */}
        {activeTab === 'original' && (
          <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 flex items-center justify-center min-h-[500px]">
            <img
              src={pageMeta.original_image_base64}
              alt="Original Document"
              className="max-h-[600px] w-auto object-contain rounded-lg shadow-xl"
            />
          </div>
        )}

        {/* Tab 5: Preprocessed Side-by-Side Comparison */}
        {activeTab === 'side-by-side' && (
          <SideBySideSlider
            originalImage={pageMeta.original_image_base64}
            preprocessedImage={pageMeta.preprocessed_image_base64}
            orientationAngle={pageMeta.orientation.rotation_angle}
            skewAngle={pageMeta.orientation.skew_angle}
            perspectiveCorrected={pageMeta.orientation.perspective_corrected}
          />
        )}

        {/* Tab 6: Detected Text Regions (Interactive Bounding Boxes) */}
        {activeTab === 'boxes' && (
          <BoundingBoxViewer
            annotatedImage={pageMeta.annotated_image_base64}
            regions={pageMeta.regions}
          />
        )}

        {/* Tab 7: Recognition Results Table */}
        {activeTab === 'table' && <RegionTable regions={pageMeta.regions} />}
      </div>
    </div>
  );
};

