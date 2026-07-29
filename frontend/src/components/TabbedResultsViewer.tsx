import React, { useState } from 'react';
import type { PageMetadata, OCRResponse } from '../types/ocr';
import { SideBySideSlider } from './SideBySideSlider';
import { BoundingBoxViewer } from './BoundingBoxViewer';
import { RegionTable } from './RegionTable';
import { TextEditor } from './TextEditor';
import { DownloadManager } from './DownloadManager';
import { Image as ImageIcon, Sliders, Box, Table, FileText } from 'lucide-react';

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
  const [activeTab, setActiveTab] = useState<'original' | 'side-by-side' | 'boxes' | 'table' | 'transcription'>('transcription');

  const tabs = [
    { id: 'transcription', label: 'Final Transcription', icon: FileText, primary: true },
    { id: 'boxes', label: 'Detected Regions', icon: Box },
    { id: 'side-by-side', label: 'Preprocessed Comparison', icon: Sliders },
    { id: 'table', label: 'Recognition Results', icon: Table },
    { id: 'original', label: 'Original Document', icon: ImageIcon },
  ];

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
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20'
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
        {/* Tab 1: Original Document */}
        {activeTab === 'original' && (
          <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 flex items-center justify-center min-h-[500px]">
            <img
              src={pageMeta.original_image_base64}
              alt="Original Document"
              className="max-h-[600px] w-auto object-contain rounded-lg shadow-xl"
            />
          </div>
        )}

        {/* Tab 2: Preprocessed Side-by-Side Comparison */}
        {activeTab === 'side-by-side' && (
          <SideBySideSlider
            originalImage={pageMeta.original_image_base64}
            preprocessedImage={pageMeta.preprocessed_image_base64}
            orientationAngle={pageMeta.orientation.rotation_angle}
            skewAngle={pageMeta.orientation.skew_angle}
            perspectiveCorrected={pageMeta.orientation.perspective_corrected}
          />
        )}

        {/* Tab 3: Detected Text Regions (Interactive Bounding Boxes) */}
        {activeTab === 'boxes' && (
          <BoundingBoxViewer
            annotatedImage={pageMeta.annotated_image_base64}
            regions={pageMeta.regions}
          />
        )}

        {/* Tab 4: Recognition Results Table */}
        {activeTab === 'table' && <RegionTable regions={pageMeta.regions} />}

        {/* Tab 5: Final Transcription (Primary Output) */}
        {activeTab === 'transcription' && (
          <div className="flex flex-col space-y-6">
            <TextEditor
              plainText={ocrResult.transcription.plain_text}
              markdownText={ocrResult.transcription.markdown}
              onTextChange={onTextChange}
            />
            <DownloadManager ocrResult={ocrResult} />
          </div>
        )}
      </div>
    </div>
  );
};
