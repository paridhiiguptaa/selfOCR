import type { OCRResponse, PipelineSettings } from '../types/ocr';

const API_BASE_URL = 'http://localhost:8000';

export async function checkHealth(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);
    const res = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (!res.ok) return false;
    const data = await res.json();
    return data.status === 'ok';
  } catch {
    return false;
  }
}


export async function previewPdf(file: File, dpi: number = 150) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('dpi', dpi.toString());

  const res = await fetch(`${API_BASE_URL}/api/preview-pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'PDF preview failed' }));
    throw new Error(err.detail || 'PDF preview failed');
  }

  return res.json();
}

/** Wall-clock timeout for the OCR API call (5 minutes). */
const OCR_FETCH_TIMEOUT_MS = 300_000;

export async function processOcr(
  file: File,
  settings: PipelineSettings,
  onProgress?: (stageIndex: number, stageName: string) => void
): Promise<OCRResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('pdf_render_dpi', settings.pdf_render_dpi.toString());
  formData.append('enable_orientation_correction', settings.enable_orientation_correction.toString());
  formData.append('enable_deskew', settings.enable_deskew.toString());
  formData.append('enable_perspective_correction', settings.enable_perspective_correction.toString());
  formData.append('enable_quality_enhancement', settings.enable_quality_enhancement.toString());
  if (settings.trocr_model_name) {
    formData.append('trocr_model_name', settings.trocr_model_name);
  }

  // Pipeline stage names matching backend Core and Enhancement pipeline logging
  const stages = [
    'Uploading document',
    'Converting PDF to images',
    'Orientation detection & rotation',
    'Deskewing & perspective correction',
    'Image quality enhancement (CLAHE/Denoise)',
    'Surya layout & reading order analysis',
    'Primary OCR recognition (Qwen VLM / Crop)',
    'Confidence evaluation & region fallback',
    'Baseline document structure reconstruction',
    'Educational subject detection',
    'Optional multi-model ensemble & VLM verification',
    'Final transcription assembly & export'
  ];

  let currentStage = 0;
  const interval = setInterval(() => {
    if (currentStage < stages.length - 1) {
      currentStage++;
      if (onProgress) {
        onProgress(currentStage, stages[currentStage]);
      }
    }
  }, 1800);

  // AbortController for timeout — prevents indefinite hang when Uvicorn stalls/crashes
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, OCR_FETCH_TIMEOUT_MS);

  try {
    if (onProgress) onProgress(0, stages[0]);

    const res = await fetch(`${API_BASE_URL}/api/ocr`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    clearInterval(interval);

    if (!res.ok) {
      // Try to parse rich structured error envelope from api.py
      const err = await res.json().catch(() => ({
        message: 'OCR processing failed',
        stage: 'pipeline_execution',
        exception_type: 'Error',
        module_name: null,
        file_path: null,
        line_number: null
      }));
      const stageName = err.stage ? `[Failed at: ${err.stage}] ` : '';
      const locInfo = err.file_path && err.line_number ? ` in ${err.module_name || 'module'} (${err.file_path}:${err.line_number})` : '';
      const excType = err.exception_type ? `${err.exception_type}: ` : '';
      const msg = `${stageName}${excType}${err.message || err.detail || `OCR processing failed (HTTP ${res.status})`}${locInfo}`;
      throw new Error(msg);
    }

    if (onProgress) onProgress(stages.length - 1, stages[stages.length - 1]);
    return await res.json();

  } catch (error: unknown) {
    clearTimeout(timeoutId);
    clearInterval(interval);

    // Distinguish timeout abort from other network errors
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error(
        `OCR processing timed out after ${OCR_FETCH_TIMEOUT_MS / 60000} minutes. ` +
        'The document may be too large or the server is unresponsive. Please try again.'
      );
    }

    throw error;
  }
}

import type {
  FlashcardGenerateResponse,
  FlashcardDeckData,
  FlashcardDeckMetadata,
  CorrectionSuggestionData
} from '../types/ocr';

export async function generateFlashcards(
  exportedText: string,
  acceptedSuggestions: CorrectionSuggestionData[],
  documentTitle?: string,
  documentId?: string,
  includeRejected?: boolean,
  allSuggestions?: CorrectionSuggestionData[]
): Promise<FlashcardGenerateResponse> {
  const res = await fetch(`${API_BASE_URL}/api/flashcards/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      exported_text: exportedText,
      accepted_suggestions: acceptedSuggestions,
      document_title: documentTitle || 'Untitled Document',
      document_id: documentId,
      include_rejected: includeRejected || false,
      all_suggestions: allSuggestions,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to generate flashcards' }));
    throw new Error(err.detail || 'Failed to generate flashcards');
  }

  return res.json();
}

export async function listFlashcardDecks(): Promise<{ decks: FlashcardDeckMetadata[] }> {
  const res = await fetch(`${API_BASE_URL}/api/flashcards/decks`);
  if (!res.ok) {
    throw new Error('Failed to fetch learning library decks');
  }
  return res.json();
}

export async function getFlashcardDeck(deckId: string): Promise<FlashcardDeckData> {
  const res = await fetch(`${API_BASE_URL}/api/flashcards/decks/${deckId}`);
  if (!res.ok) {
    throw new Error(`Failed to load flashcard deck ${deckId}`);
  }
  return res.json();
}

export async function updateDeckProgress(
  deckId: string,
  cardUpdates: Array<{ id: string; is_mastered?: boolean; is_bookmarked?: boolean; needs_review?: boolean }>
): Promise<FlashcardDeckData> {
  const res = await fetch(`${API_BASE_URL}/api/flashcards/decks/${deckId}/progress`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card_updates: cardUpdates }),
  });

  if (!res.ok) {
    throw new Error('Failed to update deck progress');
  }

  return res.json();
}

export async function deleteFlashcardDeck(deckId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/flashcards/decks/${deckId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete deck');
  }
}

