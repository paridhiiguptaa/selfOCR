export interface TextRegionData {
  region_id: number;
  reading_order_idx: number;
  line_number?: number;
  column_number?: number;
  region_type: string;
  bbox: [number, number, number, number]; // [xmin, ymin, xmax, ymax]
  text: string;
  confidence: number;
  text_type?: 'printed' | 'handwritten' | 'mixed';
  fallback_triggered: boolean;
  fallback_model?: string;
}

export interface OrientationMeta {
  rotation_angle: number;
  skew_angle: number;
  perspective_corrected: boolean;
}

export interface QualityMetrics {
  contrast: number;
  brightness_mean: number;
  brightness_std: number;
  noise_std: number;
}

export interface PreprocessingMeta {
  skipped: boolean;
  denoised: boolean;
  clahe_applied: boolean;
  shadow_removed: boolean;
  border_removed: boolean;
  quality_metrics: QualityMetrics;
}

export interface LayoutMeta {
  engine: string;
  region_count: number;
  detected_types: Record<string, number>;
}

export interface TranscriptionPayload {
  plain_text: string;
  markdown: string;
}

export interface PageMetadata {
  page_number: number;
  resolution: string;
  orientation: OrientationMeta;
  preprocessing: PreprocessingMeta;
  layout_analysis?: LayoutMeta;
  detected_regions_count?: number;
  original_image_base64: string;
  preprocessed_image_base64: string;
  annotated_image_base64: string;
  regions: TextRegionData[];
  transcription: TranscriptionPayload;
}

export interface StageTelemetry {
  stage: string;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped' | 'failed';
  duration_sec?: number;
}

export interface DeveloperTelemetry {
  total_processing_time_sec: number;
  device: string;
  qwen_vlm_model?: string;
  got_fallback_model?: string;
  confidence_threshold: number;
  stages_executed: StageTelemetry[];
}

export interface OCRResponse {
  status: string;
  document_name: string;
  total_pages: number;
  export_paths: {
    txt?: string;
    markdown?: string;
    json?: string;
  };
  transcription: TranscriptionPayload;
  pages: PageMetadata[];
  developer_telemetry?: DeveloperTelemetry;
}

export interface PipelineSettings {
  pdf_render_dpi: number;
  enable_orientation_correction: boolean;
  enable_deskew: boolean;
  enable_perspective_correction: boolean;
  enable_quality_enhancement: boolean;
  min_confidence_threshold: number;
  developer_mode: boolean;
}
