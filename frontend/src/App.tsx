import { useState, useEffect } from 'react';
import { Sidebar, type NavModule } from './components/Sidebar';
import { LoginPage } from './components/auth/LoginPage';
import { DashboardPage } from './components/pages/DashboardPage';
import { UploadPage } from './components/pages/UploadPage';
import { OcrProcessingPage } from './components/pages/OcrProcessingPage';
import { OcrTranscriptionPage } from './components/pages/OcrTranscriptionPage';
import { ProofreadingPage } from './components/pages/ProofreadingPage';
import { FlashcardsPage } from './components/pages/FlashcardsPage';
import { HistoryPage } from './components/pages/HistoryPage';
import { AnalyticsPage } from './components/pages/AnalyticsPage';
import { SettingsModal } from './components/SettingsModal';
import { checkHealth, previewPdf, processOcr } from './api/client';
import type { OCRResponse, PipelineSettings, CorrectionSuggestionData, ProofreadingState } from './types/ocr';
import { Menu, Settings as SettingsIcon, CheckCircle2, XCircle } from 'lucide-react';

export function App() {
  // Authentication state
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(true);

  // Active module / page navigation
  const [currentModule, setCurrentModule] = useState<NavModule>('dashboard');

  // Backend connection state
  const [backendConnected, setBackendConnected] = useState<boolean>(false);

  // Mobile sidebar state
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);

  // File selection & PDF metadata
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pdfThumbnails, setPdfThumbnails] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  // Processing state
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [stageIndex, setStageIndex] = useState<number>(0);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // OCR Results & Proofreading / Flashcard state
  const [ocrResult, setOcrResult] = useState<OCRResponse | null>(null);
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<CorrectionSuggestionData[]>([]);

  const [proofreadingState, setProofreadingState] = useState<ProofreadingState>({
    correctionData: null,
    acceptedIds: [],
    rejectedIds: [],
    hasRun: false,
    documentHash: '',
    isDirty: false,
  });

  // Settings & Developer mode
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

  // Health check on mount & periodic polling
  useEffect(() => {
    checkHealth().then(setBackendConnected);
    const interval = setInterval(() => {
      checkHealth().then((connected) => {
        if (connected || !isProcessing) {
          setBackendConnected(connected);
        }
      });
    }, 10000);
    return () => clearInterval(interval);
  }, [isProcessing]);

  // Handle File Selection
  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setOcrResult(null);
    setIsCompleted(false);
    setErrorMsg(null);
    setCurrentPage(1);
    setProofreadingState({
      correctionData: null,
      acceptedIds: [],
      rejectedIds: [],
      hasRun: false,
      documentHash: '',
      isDirty: false,
    });

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

  // Run OCR Pipeline & transition module automatically
  const handleRunOcr = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setIsCompleted(false);
    setErrorMsg(null);
    setStageIndex(0);
    setCurrentModule('processing');

    try {
      const result = await processOcr(selectedFile, settings, (idx) => {
        setStageIndex(idx);
      });

      setOcrResult(result);
      setIsCompleted(true);
      setIsProcessing(false);
      setProofreadingState((prev) => ({
        ...prev,
        documentHash: result.transcription.plain_text,
      }));
    } catch (err: any) {
      // Keep the user on the processing page so the error banner and Retry button are visible.
      // Do NOT navigate away — the OcrProcessingPage renders the error state with a retry option.
      setErrorMsg(err.message || 'An unexpected error occurred during OCR processing.');
      setIsProcessing(false);
      // currentModule intentionally stays as 'processing'
    }
  };

  // Reset document session
  const handleReset = () => {
    setSelectedFile(null);
    setOcrResult(null);
    setIsCompleted(false);
    setErrorMsg(null);
    setPdfThumbnails([]);
    setCurrentPage(1);
    setTotalPages(1);
    setCurrentModule('upload');
  };

  // If user is not logged in, render the Login Page
  if (!isLoggedIn) {
    return <LoginPage onLogin={() => setIsLoggedIn(true)} />;
  }

  const activePageMeta = ocrResult?.pages[currentPage - 1] || ocrResult?.pages[0];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans">
      {/* Persistent Left Sidebar Navigation */}
      <Sidebar
        currentModule={currentModule}
        onSelectModule={(mod) => {
          // Block navigation away from the processing page while OCR is running.
          // The user must wait for completion or see the error — no silent page resets.
          if (isProcessing && currentModule === 'processing') {
            return;
          }
          if (mod === 'settings') {
            setIsSettingsOpen(true);
          } else {
            setCurrentModule(mod);
          }
        }}
        backendConnected={backendConnected}
        developerMode={settings.developer_mode}
        onToggleDeveloperMode={() =>
          setSettings((prev) => ({ ...prev, developer_mode: !prev.developer_mode }))
        }
        onLogout={() => setIsLoggedIn(false)}
        isMobileOpen={isMobileSidebarOpen}
        onToggleMobile={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
      />

      {/* Main Workspace Container */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        {/* Top Header Bar */}
        <header className="sticky top-0 z-20 bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-6 py-4 flex items-center justify-between shadow-2xs">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsMobileSidebarOpen(true)}
              className="lg:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div>
              <h2 className="text-base sm:text-lg font-black text-slate-900 capitalize tracking-tight">
                {currentModule === 'dashboard'
                  ? 'Dashboard Overview'
                  : currentModule === 'upload'
                  ? 'Upload Document'
                  : currentModule === 'processing'
                  ? 'OCR Processing'
                  : currentModule === 'transcription'
                  ? 'OCR Transcription Editor'
                  : currentModule === 'proofreading'
                  ? 'AI Proofreading Studio'
                  : currentModule === 'flashcards'
                  ? 'Educational Flashcards'
                  : currentModule === 'history'
                  ? 'Document History'
                  : currentModule === 'analytics'
                  ? 'Learning Analytics'
                  : 'Settings'}
              </h2>
              <p className="text-[11px] text-slate-500 font-semibold hidden sm:block">
                EduAI SaaS Educational Platform • Dual TrOCR Engine
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Connection Status Pill */}
            <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-700">
              {backendConnected ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>API Online</span>
                </>
              ) : (
                <>
                  <XCircle className="w-3.5 h-3.5 text-rose-500" />
                  <span>API Offline</span>
                </>
              )}
            </div>

            {/* Quick Settings Icon */}
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="p-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-xl border border-slate-200 transition-colors"
              title="Pipeline Settings"
            >
              <SettingsIcon className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Dynamic Module Page Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {currentModule === 'dashboard' && (
            <DashboardPage
              onNavigate={(mod) => setCurrentModule(mod)}
              hasActiveDocument={!!ocrResult}
              activeDocName={ocrResult?.document_name}
              activeDocPageCount={ocrResult?.total_pages}
            />
          )}

          {currentModule === 'upload' && (
            <UploadPage
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              isProcessing={isProcessing}
              pdfThumbnails={pdfThumbnails}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={(p) => setCurrentPage(p)}
              onRunOcr={handleRunOcr}
              onReset={handleReset}
              backendConnected={backendConnected}
              settings={settings}
              onUpdateSettings={(newSet) => setSettings(newSet)}
            />
          )}

          {currentModule === 'processing' && (
            <OcrProcessingPage
              stageIndex={stageIndex}
              isCompleted={isCompleted}
              error={errorMsg}
              onNavigateToTranscription={() => setCurrentModule('transcription')}
              onRetry={handleRunOcr}
            />
          )}

          {currentModule === 'transcription' && (
            ocrResult && activePageMeta ? (
              <OcrTranscriptionPage
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
                onNavigateToProofreading={() => setCurrentModule('proofreading')}
                developerMode={settings.developer_mode}
              />
            ) : (
              <UploadPage
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
                isProcessing={isProcessing}
                pdfThumbnails={pdfThumbnails}
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={(p) => setCurrentPage(p)}
                onRunOcr={handleRunOcr}
                onReset={handleReset}
                backendConnected={backendConnected}
                settings={settings}
                onUpdateSettings={(newSet) => setSettings(newSet)}
              />
            )
          )}

          {currentModule === 'proofreading' && (
            <ProofreadingPage
              ocrPlainText={ocrResult?.transcription.plain_text || 'Sample handwritten class notes ready for AI proofreading.'}
              ocrResult={ocrResult}
              onTextUpdate={(newText) => {
                if (ocrResult) {
                  setOcrResult({
                    ...ocrResult,
                    transcription: { ...ocrResult.transcription, plain_text: newText },
                  });
                }
              }}
              onSuggestionsChange={(accepted) => setAcceptedSuggestions(accepted)}
              proofreadingState={proofreadingState}
              onStateChange={(newState) => setProofreadingState((prev) => ({ ...prev, ...newState }))}
              onNavigateToFlashcards={() => setCurrentModule('flashcards')}
            />
          )}

          {currentModule === 'flashcards' && (
            <FlashcardsPage
              exportedText={ocrResult?.transcription.plain_text || 'Sample handwritten class notes ready for flashcards.'}
              acceptedSuggestions={acceptedSuggestions}
              documentTitle={ocrResult?.document_name || 'Class Notes'}
              isDocumentExported={true}
              onNavigateToProofreading={() => setCurrentModule('proofreading')}
            />
          )}

          {currentModule === 'history' && (
            <HistoryPage onNavigate={(mod) => setCurrentModule(mod)} />
          )}

          {currentModule === 'analytics' && <AnalyticsPage />}
        </main>
      </div>

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
