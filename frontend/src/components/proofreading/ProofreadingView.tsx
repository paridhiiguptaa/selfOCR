import React, { useState, useEffect } from 'react';
import type { CorrectionResponse, CorrectionSuggestionData, ProofreadingState } from '../../types/ocr';
import { ProofreadingDashboard } from './ProofreadingDashboard';
import { FilterToolbar } from './FilterToolbar';
import { ProofreadingEditor } from './ProofreadingEditor';
import { SuggestionSidebar } from './SuggestionSidebar';
import { DocumentComparisonView } from './DocumentComparisonView';
import { ProofreadingLoading } from './ProofreadingLoading';
import { X, HelpCircle, AlertCircle, RefreshCw } from 'lucide-react';

interface ProofreadingViewProps {
  ocrPlainText: string;
  onTextUpdate?: (newText: string) => void;
  onSuggestionsChange?: (accepted: CorrectionSuggestionData[], all: CorrectionSuggestionData[]) => void;
  proofreadingState?: ProofreadingState;
  onStateChange?: (newState: Partial<ProofreadingState>) => void;
}

export const ProofreadingView: React.FC<ProofreadingViewProps> = ({
  ocrPlainText,
  onTextUpdate,
  onSuggestionsChange,
  proofreadingState,
  onStateChange,
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Internal fallbacks if proofreadingState is not provided
  const [internalCorrectionData, setInternalCorrectionData] = useState<CorrectionResponse | null>(null);
  const [internalHasRun, setInternalHasRun] = useState<boolean>(false);
  const [internalAcceptedIds, setInternalAcceptedIds] = useState<string[]>([]);
  const [internalRejectedIds, setInternalRejectedIds] = useState<string[]>([]);

  const correctionData = proofreadingState ? proofreadingState.correctionData : internalCorrectionData;
  const acceptedIds = proofreadingState ? proofreadingState.acceptedIds : internalAcceptedIds;
  const rejectedIds = proofreadingState ? proofreadingState.rejectedIds : internalRejectedIds;
  const hasRun = proofreadingState ? proofreadingState.hasRun : internalHasRun;
  const isDirty = proofreadingState?.isDirty || false;

  const setAcceptedIds = (ids: string[]) => {
    if (onStateChange) onStateChange({ acceptedIds: ids });
    else setInternalAcceptedIds(ids);
  };

  const setRejectedIds = (ids: string[]) => {
    if (onStateChange) onStateChange({ rejectedIds: ids });
    else setInternalRejectedIds(ids);
  };

  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedSuggestionId, setSelectedSuggestionId] = useState<string | null>(null);

  // Sidebar & Modals
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [isComparing, setIsComparing] = useState<boolean>(false);
  const [showLegend, setShowLegend] = useState<boolean>(false);

  // Undo / Redo History Stack
  const [history, setHistory] = useState<string[]>([]);
  const [historyIdx, setHistoryIdx] = useState<number>(-1);

  const initialTextRef = React.useRef(ocrPlainText);
  const currentTextRef = React.useRef(ocrPlainText);

  useEffect(() => {
    currentTextRef.current = ocrPlainText;
  }, [ocrPlainText]);

  // Notify parent of accepted suggestions whenever acceptedIds or correctionData change
  useEffect(() => {
    if (correctionData && onSuggestionsChange) {
      const acceptedSuggs = correctionData.suggestions.filter((s) => acceptedIds.includes(s.suggestion_id));
      onSuggestionsChange(acceptedSuggs, correctionData.suggestions);
    }
  }, [acceptedIds, correctionData, onSuggestionsChange]);

  // Function to run proofreading on demand using current text
  const handleRunProofreading = async () => {
    const textToProcess = currentTextRef.current || ocrPlainText;
    if (!textToProcess || !textToProcess.trim()) return;

    initialTextRef.current = textToProcess;
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/correct-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToProcess, language: 'en' }),
      });

      if (!response.ok) {
        throw new Error(`Text correction server responded with status: ${response.status}`);
      }

      const data: CorrectionResponse = await response.json();

      if (onStateChange) {
        onStateChange({
          correctionData: data,
          acceptedIds: [],
          rejectedIds: [],
          hasRun: true,
          isDirty: false,
        });
      } else {
        setInternalCorrectionData(data);
        setInternalAcceptedIds([]);
        setInternalRejectedIds([]);
        setInternalHasRun(true);
      }

      setHistory([textToProcess]);
      setHistoryIdx(0);
      setLoading(false);
    } catch (err: any) {
      console.warn(`Proofreading fetch failed: ${err.message}`);
      setError(err.message || 'Failed to connect to proofreading service.');
      setLoading(false);
    }
  };

  // Auto-run once if entering tab for the first time and has not run yet
  useEffect(() => {
    if (!hasRun && ocrPlainText && !loading) {
      handleRunProofreading();
    }
  }, []);

  const getCurrentTextWithAccepted = (accepted: string[]): string => {
    const orig = initialTextRef.current || ocrPlainText;
    if (!correctionData) return orig;
    if (accepted.length === 0) return orig;

    const acceptedSuggs = correctionData.suggestions.filter((s) => accepted.includes(s.suggestion_id));
    const sorted = [...acceptedSuggs].sort((a, b) => b.start_offset - a.start_offset);

    let chars = listChars(orig);
    for (const sug of sorted) {
      if (sug.start_offset >= 0 && sug.end_offset <= orig.length) {
        chars.splice(sug.start_offset, sug.end_offset - sug.start_offset, ...listChars(sug.proposed_correction));
      }
    }
    return chars.join('');
  };

  const listChars = (str: string) => Array.from(str);

  const currentText = getCurrentTextWithAccepted(acceptedIds);

  // Actions
  const handleAccept = (id: string) => {
    if (!acceptedIds.includes(id)) {
      const nextAccepted = [...acceptedIds, id];
      setAcceptedIds(nextAccepted);
      setRejectedIds(rejectedIds.filter((r) => r !== id));
      
      const newText = getCurrentTextWithAccepted(nextAccepted);
      pushHistory(newText);
      if (onTextUpdate) onTextUpdate(newText);
    }
  };

  const handleReject = (id: string) => {
    if (!rejectedIds.includes(id)) {
      setRejectedIds([...rejectedIds, id]);
      setAcceptedIds(acceptedIds.filter((a) => a !== id));
    }
  };

  const handleIgnore = (id: string) => {
    handleReject(id);
  };

  const handleAcceptAll = () => {
    if (!correctionData) return;
    const allIds = correctionData.suggestions.map((s) => s.suggestion_id);
    setAcceptedIds(allIds);
    setRejectedIds([]);
    const newText = getCurrentTextWithAccepted(allIds);
    pushHistory(newText);
    if (onTextUpdate) onTextUpdate(newText);
  };

  const handleRejectAll = () => {
    if (!correctionData) return;
    const allIds = correctionData.suggestions.map((s) => s.suggestion_id);
    setRejectedIds(allIds);
    setAcceptedIds([]);
  };

  const handleAcceptHighConfidence = () => {
    if (!correctionData) return;
    const highConf = correctionData.suggestions
      .filter((s) => s.confidence_score >= 0.80)
      .map((s) => s.suggestion_id);

    const nextAccepted = Array.from(new Set([...acceptedIds, ...highConf]));
    setAcceptedIds(nextAccepted);
    const newText = getCurrentTextWithAccepted(nextAccepted);
    if (onTextUpdate) onTextUpdate(newText);
  };

  const handleReset = () => {
    setAcceptedIds([]);
    setRejectedIds([]);
    setSelectedSuggestionId(null);
    if (onTextUpdate) onTextUpdate(initialTextRef.current);
  };

  const pushHistory = (newText: string) => {
    const nextHist = history.slice(0, historyIdx + 1);
    nextHist.push(newText);
    setHistory(nextHist);
    setHistoryIdx(nextHist.length - 1);
  };

  const handleUndo = () => {
    if (historyIdx > 0) {
      setHistoryIdx(historyIdx - 1);
    }
  };

  const handleRedo = () => {
    if (historyIdx < history.length - 1) {
      setHistoryIdx(historyIdx + 1);
    }
  };

  if (loading) {
    return <ProofreadingLoading />;
  }

  if (error) {
    return (
      <div className="w-full p-8 bg-slate-900 rounded-2xl border border-red-500/30 text-center flex flex-col items-center justify-center">
        <AlertCircle className="w-8 h-8 text-red-400 mb-3" />
        <h3 className="text-base font-bold text-white mb-1">Proofreading Module Notice</h3>
        <p className="text-xs text-slate-400">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold"
        >
          Retry Proofreader
        </button>
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col space-y-6 relative">
      {/* Document Transcription Modified Banner */}
      {isDirty && (
        <div className="w-full p-4 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex flex-col sm:flex-row items-center justify-between space-y-3 sm:space-y-0 text-amber-200 text-xs shadow-lg">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
            <div>
              <span className="font-bold block text-sm text-amber-100">Document Transcription Modified</span>
              <span>The OCR transcription has been edited. Click below to regenerate suggestions for updated text.</span>
            </div>
          </div>
          <button
            onClick={handleRunProofreading}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-md transition-all whitespace-nowrap"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Re-run Proofreading</span>
          </button>
        </div>
      )}

      {/* Top Dashboard Metrics */}
      {correctionData && (
        <ProofreadingDashboard
          metrics={correctionData.quality_metrics}
          suggestions={correctionData.suggestions}
          acceptedIds={acceptedIds}
          rejectedIds={rejectedIds}
          processingTimeSec={correctionData.processing_time_sec}
        />
      )}

      {/* Comparison Mode vs Standard Editor */}
      {isComparing ? (
        <DocumentComparisonView
          originalText={ocrPlainText}
          correctedText={currentText}
          onClose={() => setIsComparing(false)}
        />
      ) : (
        <>
          {/* Filter & Actions Toolbar */}
          <FilterToolbar
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
            onAcceptAll={handleAcceptAll}
            onRejectAll={handleRejectAll}
            onAcceptHighConfidence={handleAcceptHighConfidence}
            onReset={handleReset}
            onUndo={handleUndo}
            onRedo={handleRedo}
            canUndo={historyIdx > 0}
            canRedo={historyIdx < history.length - 1}
            isComparing={isComparing}
            onToggleCompare={() => setIsComparing(!isComparing)}
            onToggleLegend={() => setShowLegend(true)}
          />

          {/* Interactive Editor & Floating Cards */}
          <ProofreadingEditor
            text={currentText}
            suggestions={correctionData?.suggestions || []}
            acceptedIds={acceptedIds}
            rejectedIds={rejectedIds}
            selectedCategory={selectedCategory}
            selectedSuggestionId={selectedSuggestionId}
            onAccept={handleAccept}
            onReject={handleReject}
            onIgnore={handleIgnore}
          />
        </>
      )}

      {/* Collapsible Suggestion Feed Sidebar */}
      {correctionData && (
        <SuggestionSidebar
          suggestions={correctionData.suggestions}
          acceptedIds={acceptedIds}
          rejectedIds={rejectedIds}
          selectedId={selectedSuggestionId}
          onSelectSuggestion={(sug) => setSelectedSuggestionId(sug.suggestion_id)}
          onAccept={handleAccept}
          onReject={handleReject}
          isOpen={isSidebarOpen}
          onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        />
      )}

      {/* Color Legend Modal */}
      {showLegend && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl text-slate-100 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <HelpCircle className="w-5 h-5 text-blue-400" />
                <h4 className="font-bold text-base text-white">Underline Color Legend</h4>
              </div>
              <button
                onClick={() => setShowLegend(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                <span className="border-b-2 border-dashed border-red-500 text-red-200 px-1 font-bold">
                  Spelling Error
                </span>
                <span className="text-slate-400">Red Underline</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                <span className="border-b-2 border-dashed border-amber-500 text-amber-200 px-1 font-bold">
                  Grammar Issue
                </span>
                <span className="text-slate-400">Amber Underline</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                <span className="border-b-2 border-dashed border-blue-500 text-blue-200 px-1 font-bold">
                  Missing Word
                </span>
                <span className="text-slate-400">Blue Underline</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                <span className="border-b-2 border-dashed border-purple-500 text-purple-200 px-1 font-bold">
                  Punctuation
                </span>
                <span className="text-slate-400">Purple Underline</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                <span className="border-b-2 border-dashed border-indigo-500 text-indigo-200 px-1 font-bold">
                  OCR Artifact
                </span>
                <span className="text-slate-400">Indigo Underline</span>
              </div>
            </div>

            <button
              onClick={() => setShowLegend(false)}
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 font-bold text-xs text-white rounded-xl shadow-md"
            >
              Got It
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
