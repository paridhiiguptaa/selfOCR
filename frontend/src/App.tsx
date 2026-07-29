import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { UploadZone } from './components/UploadZone';
import { PdfPageSelector } from './components/PdfPageSelector';
import { PipelineProgressTracker } from './components/PipelineProgressTracker';
import { TabbedResultsViewer } from './components/TabbedResultsViewer';
import { DeveloperModePanel } from './components/DeveloperModePanel';
import { SettingsModal } from './components/SettingsModal';
import { checkHealth, previewPdf, processOcr } from './api/client';
import type { OCRResponse, PipelineSettings } from './types/ocr';
import { Play, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';

export function App() {
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pdfThumbnails, setPdfThumbnails] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  // Processing state
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [stageIndex, setStageIndex] = useState<number>(0);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Results
  const [ocrResult, setOcrResult] = useState<OCRResponse | null>(null);

  // Settings & Dev mode
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [settings, setSettings] = useState<PipelineSettings>({
    pdf_render_dpi: 300,
    enable_orientation_correction: true,
    enable_deskew: true,
    enable_perspective_correction: true,
    enable_quality_enhancement: true,
    min_confidence_threshold: 0.70,
    trocr_model_name: 'microsoft/trocr-small-handwritten',
    developer_mode: false,
  });

  // Check health on mount
  useEffect(() => {
    checkHealth().then(setBackendConnected);
    const interval = setInterval(() => {
      checkHealth().then(setBackendConnected);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Handle File Selection & PDF Thumbnail Extraction
  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setOcrResult(null);
    setIsCompleted(false);
    setErrorMsg(null);
    setCurrentPage(1);

    if (file.name.toLowerCase().endsWith('.pdf')) {
      try {
        const pdfData = await previewPdf(file, 150);
        setPdfThumbnails(pdfData.pages || []);
        setTotalPages(pdfData.total_pages || 1);
      } catch (err: any) {
        console.warn('PDF thumbnail generation failed:', err);
      }
    } else {
      setPdfThumbnails([]);
      setTotalPages(1);
    }
  };

  // Run OCR Pipeline
  const handleRunOcr = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setIsCompleted(false);
    setErrorMsg(null);
    setStageIndex(0);

    try {
      const result = await processOcr(selectedFile, settings, (idx) => {
        setStageIndex(idx);
      });

      setOcrResult(result);
      setIsCompleted(true);
      setIsProcessing(false);
    } catch (err: any) {
      setErrorMsg(err.message || 'An unexpected error occurred during OCR processing.');
      setIsProcessing(false);
    }
  };

  // Reset session
  const handleReset = () => {
    setSelectedFile(null);
    setOcrResult(null);
    setIsCompleted(false);
    setErrorMsg(null);
    setPdfThumbnails([]);
    setCurrentPage(1);
    setTotalPages(1);
  };

  const activePageMeta = ocrResult?.pages[currentPage - 1] || ocrResult?.pages[0];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <Navbar
        backendConnected={backendConnected}
        developerMode={settings.developer_mode}
        onToggleDeveloperMode={() =>
          setSettings((prev) => ({ ...prev, developer_mode: !prev.developer_mode }))
        }
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {/* Hero Banner */}
        <div className="text-center max-w-3xl mx-auto mb-8 space-y-3">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
            <Sparkles className="w-4 h-4" />
            <span>Dual Printed & Handwritten OCR Processing Engine</span>
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Accurate Transcription for Rotated & Complex Documents
          </h2>
          <p className="text-sm text-slate-400">
            Upload images or PDFs to evaluate orientation detection, deskewing, hybrid text region detection, Hugging Face TrOCR recognition, and reading order layout analysis.
          </p>
        </div>

        {/* File Upload Zone */}
        <div className="max-w-3xl mx-auto mb-6">
          <UploadZone
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            isProcessing={isProcessing}
          />
        </div>

        {/* PDF Multi-Page Thumbnail Selector */}
        {pdfThumbnails.length > 0 && (
          <div className="max-w-3xl mx-auto">
            <PdfPageSelector
              totalPages={totalPages}
              currentPage={currentPage}
              thumbnails={pdfThumbnails}
              onPageChange={(page) => setCurrentPage(page)}
            />
          </div>
        )}

        {/* Action Controls (Run OCR Button) */}
        {selectedFile && !isProcessing && !isCompleted && (
          <div className="flex justify-center space-x-4 mb-8">
            <button
              onClick={handleRunOcr}
              disabled={!backendConnected}
              className="flex items-center space-x-2.5 px-8 py-3.5 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white font-bold text-sm shadow-xl shadow-blue-500/25 transition-all transform hover:scale-[1.02]"
            >
              <Play className="w-5 h-5 fill-current" />
              <span>Run OCR Pipeline</span>
            </button>
            <button
              onClick={handleReset}
              className="px-5 py-3.5 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-sm border border-slate-700 transition-colors"
            >
              Reset
            </button>
          </div>
        )}

        {/* Error Banner */}
        {errorMsg && (
          <div className="max-w-3xl mx-auto mb-8 p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center space-x-3 text-rose-300 text-xs">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <div className="flex-1">
              <span className="font-bold block text-sm text-rose-200">Processing Failed</span>
              <span>{errorMsg}</span>
            </div>
            <button
              onClick={() => setErrorMsg(null)}
              className="p-1 rounded text-rose-400 hover:bg-rose-500/20"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Pipeline Progress Tracker */}
        {(isProcessing || isCompleted) && (
          <PipelineProgressTracker
            currentStageIndex={stageIndex}
            isCompleted={isCompleted}
            error={errorMsg}
          />
        )}

        {/* 5-Tab Interactive Results Viewer */}
        {isCompleted && ocrResult && activePageMeta && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">OCR Evaluation Results</h3>
              <button
                onClick={handleReset}
                className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Process Another File</span>
              </button>
            </div>

            <TabbedResultsViewer
              pageMeta={activePageMeta}
              ocrResult={ocrResult}
              onTextChange={(newText) => {
                setOcrResult((prev) =>
                  prev
                    ? {
                        ...prev,
                        transcription: { ...prev.transcription, plain_text: newText },
                      }
                    : null
                );
              }}
            />

            {/* Developer Mode Diagnostics Panel */}
            {settings.developer_mode && (
              <DeveloperModePanel
                pageMeta={activePageMeta}
                telemetry={ocrResult.developer_telemetry}
              />
            )}
          </div>
        )}
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onSaveSettings={(newSettings) => setSettings(newSettings)}
      />
    </div>
  );
}

export default App;
