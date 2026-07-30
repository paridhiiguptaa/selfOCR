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
  trocr_model?: string;
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
  trocr_model_name?: string;
}

export interface CorrectionSuggestionData {
  suggestion_id: string;
  original_text: string;
  proposed_correction: string;
  category: 'Spelling Correction' | 'Grammar Correction' | 'Missing Word' | 'Punctuation Improvement' | 'Capitalization' | 'OCR Confidence Recovery' | 'Sentence Structure' | 'Style Suggestion' | string;
  confidence_score: number;
  explanation: string;
  start_offset: number;
  end_offset: number;
  line_number: number;
}

export interface CorrectionQualityMetrics {
  spelling_errors: number;
  grammar_errors: number;
  missing_words: number;
  punctuation_corrections: number;
  total_suggestions: number;
}

export interface CorrectionResponse {
  original_text: string;
  corrected_text: string;
  suggestions: CorrectionSuggestionData[];
  quality_metrics: CorrectionQualityMetrics;
  processing_time_sec: number;
}

export type CardStyle =
  | 'spelling'
  | 'fill_in_blank'
  | 'grammar_explanation'
  | 'punctuation_practice'
  | 'capitalization_rule'
  | 'vocabulary'
  | 'sentence_reconstruction';

export type CardDifficulty = 'Easy' | 'Medium' | 'Hard';

export interface FlashcardData {
  id: string;
  category: string;
  card_style: CardStyle;
  original_sentence: string;
  corrected_sentence: string;
  front: {
    title?: string;
    prompt?: string;
    context_sentence?: string;
    target_word?: string;
    sentence_with_blank?: string;
    hint?: string;
    options?: string[];
    highlighted_error?: string;
    scrambled_tokens?: string[];
    study_type?: string;
    [key: string]: any;
  };
  back: {
    correct_answer: string;
    explanation: string;
    rule: string;
    child_friendly_definition?: string;
    dictionary_meaning?: string;
    contextual_meaning?: string;
    example_sentence?: string;
    usage_example?: string;
    part_of_speech?: string;
    word_meaning?: string;
    phonetic_hint?: string;
    original_sentence?: string;
    corrected_sentence?: string;
    extra_examples?: string[];
    tip?: string;
    synonyms?: string[];
    antonyms?: string[];
    error_found?: string;
    corrected_form?: string;
    [key: string]: any;
  };
  accepted_correction: {
    original: string;
    proposed: string;
  };
  explanation: string;
  rule: string;
  learning_objective: string;
  difficulty: CardDifficulty;
  confidence_score: number;
  source_document_id: string;
  source_document_title: string;
  created_at: string;
  tags: string[];
  child_friendly_definition?: string;
  dictionary_meaning?: string;
  contextual_meaning?: string;
  example_sentence?: string;
  part_of_speech?: string;
  synonyms?: string[];
  antonyms?: string[];
  difficulty_level?: string;
  pronunciation?: string;
  detected_pos?: string;
  identified_word_sense?: string;
  official_dictionary_definition?: string;
  simplified_child_definition?: string;
  generated_example_sentence?: string;
  dictionary_source?: string;
  requires_manual_verification?: boolean;
  is_mastered?: boolean;
  is_bookmarked?: boolean;
  needs_review?: boolean;
}

export interface DeckStudyProgress {
  cards_completed: number;
  cards_mastered: number;
  cards_bookmarked: number;
  last_studied_at: string | null;
}

export interface FlashcardDeckData {
  deck_id: string;
  source_document_id: string;
  source_document_title: string;
  exported_document_text: string;
  created_at: string;
  total_flashcards: number;
  categories_distribution: Record<string, number>;
  difficulty_distribution: Record<string, number>;
  estimated_study_time_min: number;
  mastery_percentage: number;
  study_progress: DeckStudyProgress;
  cards: FlashcardData[];
}

export interface FlashcardDeckMetadata {
  deck_id: string;
  source_document_id: string;
  source_document_title: string;
  created_at: string;
  total_flashcards: number;
  categories_distribution: Record<string, number>;
  difficulty_distribution: Record<string, number>;
  estimated_study_time_min: number;
  mastery_percentage: number;
  study_progress: DeckStudyProgress;
}

export interface FlashcardTelemetry {
  processing_time_sec: number;
  accepted_corrections_processed: number;
  duplicate_cards_removed: number;
  flashcards_generated: number;
  category_distribution: Record<string, number>;
  difficulty_distribution: Record<string, number>;
  unconvertible_corrections: number;
  confidence_statistics: {
    mean_confidence: number;
  };
}

export interface FlashcardGenerateResponse {
  deck: FlashcardDeckData;
  telemetry: FlashcardTelemetry;
}


