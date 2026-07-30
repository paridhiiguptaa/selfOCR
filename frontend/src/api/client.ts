import type { OCRResponse, PipelineSettings } from '../types/ocr';

const API_BASE_URL = 'http://localhost:8000';

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
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

  // Simulate real-time progress stage steps while fetch is in progress
  const stages = [
    'Uploading document',
    'Converting PDF to images',
    'Orientation detection & rotation',
    'Deskewing & perspective correction',
    'Image quality enhancement (CLAHE/Denoise)',
    'Text region detection',
    'Printed vs handwritten classification',
    'Printed text recognition',
    'Handwritten text recognition (TrOCR)',
    'Layout reading order reconstruction',
    'Confidence evaluation & fallback recovery',
    'Generating final transcription payload'
  ];

  let currentStage = 0;
  const interval = setInterval(() => {
    if (currentStage < stages.length - 1) {
      currentStage++;
      if (onProgress) {
        onProgress(currentStage, stages[currentStage]);
      }
    }
  }, 1200);

  try {
    if (onProgress) onProgress(0, stages[0]);
    const res = await fetch(`${API_BASE_URL}/api/ocr`, {
      method: 'POST',
      body: formData,
    });

    clearInterval(interval);

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'OCR Processing failed' }));
      throw new Error(err.detail || 'OCR Processing failed');
    }

    if (onProgress) onProgress(stages.length - 1, stages[stages.length - 1]);
    return await res.json();
  } catch (error) {
    clearInterval(interval);
    throw error;
  }
}
