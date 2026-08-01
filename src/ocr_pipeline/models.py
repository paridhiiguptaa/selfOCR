from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

@dataclass
class TextRegion:
    """Structure representing a bounding box text region in a document."""
    region_id: int
    bbox: Tuple[int, int, int, int]  # [xmin, ymin, xmax, ymax]
    region_type: str = "Text"        # "Title", "Section-header", "Text", "List-item", "Table", "Caption"
    text: str = ""
    confidence: float = 1.0
    quality_score: float = 1.0       # Calibrated multi-factor quality score
    ink_density: float = 0.05
    word_confidences: List[Dict[str, Any]] = field(default_factory=list) # List of {"word": str, "confidence": float}
    quality_indicators: Dict[str, float] = field(default_factory=dict)
    text_type: str = "mixed"         # "printed", "handwritten", "mixed"
    reading_order_idx: int = 0
    line_number: int = 1
    column_number: int = 1
    fallback_triggered: bool = False
    fallback_model: Optional[str] = None
    unpadded_bbox: Optional[Tuple[int, int, int, int]] = None

    @property
    def center(self) -> Tuple[float, float]:
        """Center coordinates of bounding box (x_center, y_center)."""
        xmin, ymin, xmax, ymax = self.bbox
        return (xmin + xmax) / 2.0, (ymin + ymax) / 2.0

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]

@dataclass
class DocumentPage:
    """Structure representing a single processed document page."""
    page_number: int
    total_pages: int
    image: np.ndarray          # RGB numpy array (H, W, 3)
    source_path: str
    width: int
    height: int
    is_pdf: bool = False
    document_classification: str = "mixed_content" # "predominantly_printed", "predominantly_handwritten", "mixed_content"

@dataclass
class PageTelemetry:
    """Detailed timing telemetry for pipeline stages per page."""
    stage_durations: Dict[str, float] = field(default_factory=dict)
    preprocessing_meta: Dict[str, Any] = field(default_factory=dict)
    orientation_meta: Dict[str, Any] = field(default_factory=dict)
    layout_stats: Dict[str, Any] = field(default_factory=dict)
    document_analysis_meta: Dict[str, Any] = field(default_factory=dict)
    quality_calibration_meta: Dict[str, Any] = field(default_factory=dict)
    fallback_count: int = 0
    mean_confidence: float = 0.0
    mean_quality_score: float = 0.0

@dataclass
class OCRResult:
    """Complete document OCR result."""
    document_name: str
    total_pages: int
    transcription_plain: str
    transcription_markdown: str
    pages: List[Dict[str, Any]]
    telemetry: Dict[str, Any]
    export_paths: Dict[str, str] = field(default_factory=dict)

@dataclass
class CorrectionSuggestion:
    """Structure representing a single AI text correction suggestion."""
    suggestion_id: str
    original_text: str
    proposed_correction: str
    category: str  # 'Spelling Correction', 'Grammar Correction', 'Missing Word', 'Punctuation Improvement', 'Capitalization', 'OCR Confidence Recovery', 'Contextual Substitution', 'Character Confusion', 'Sentence Structure', 'Style Suggestion'
    confidence_score: float
    explanation: str
    start_offset: int
    end_offset: int
    line_number: int = 1
    alternative_candidates: List[Dict[str, Any]] = field(default_factory=list) # List of {"candidate": str, "score": float}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suggestion_id": self.suggestion_id,
            "original_text": self.original_text,
            "proposed_correction": self.proposed_correction,
            "category": self.category,
            "confidence_score": round(self.confidence_score, 4),
            "explanation": self.explanation,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "line_number": self.line_number,
            "alternative_candidates": self.alternative_candidates
        }

@dataclass
class CorrectionResult:
    """Structure representing complete text correction analysis output."""
    original_text: str
    corrected_text: str
    suggestions: List[CorrectionSuggestion]
    quality_metrics: Dict[str, int]
    processing_time_sec: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_text": self.original_text,
            "corrected_text": self.corrected_text,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "quality_metrics": self.quality_metrics,
            "processing_time_sec": round(self.processing_time_sec, 3)
        }

@dataclass
class Flashcard:
    """Structure representing an educational AI-generated flashcard."""
    id: str
    category: str
    card_style: str  # 'spelling', 'fill_in_blank', 'grammar_explanation', 'punctuation_practice', 'capitalization_rule', 'vocabulary', 'sentence_reconstruction'
    original_sentence: str
    corrected_sentence: str
    front: Dict[str, Any]
    back: Dict[str, Any]
    accepted_correction: Dict[str, str]  # {"original": "...", "proposed": "..."}
    explanation: str
    rule: str
    learning_objective: str
    difficulty: str  # 'Easy', 'Medium', 'Hard'
    confidence_score: float
    source_document_id: str
    source_document_title: str
    created_at: str
    tags: List[str]
    child_friendly_definition: str = ""
    dictionary_meaning: str = ""
    contextual_meaning: str = ""
    example_sentence: str = ""
    part_of_speech: str = ""
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    difficulty_level: str = "Medium"
    pronunciation: str = ""
    detected_pos: str = ""
    identified_word_sense: str = ""
    official_dictionary_definition: str = ""
    simplified_child_definition: str = ""
    generated_example_sentence: str = ""
    dictionary_source: str = ""
    requires_manual_verification: bool = False
    is_mastered: bool = False
    is_bookmarked: bool = False
    needs_review: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "card_style": self.card_style,
            "original_sentence": self.original_sentence,
            "corrected_sentence": self.corrected_sentence,
            "front": self.front,
            "back": self.back,
            "accepted_correction": self.accepted_correction,
            "explanation": self.explanation,
            "rule": self.rule,
            "learning_objective": self.learning_objective,
            "difficulty": self.difficulty,
            "confidence_score": round(self.confidence_score, 4),
            "source_document_id": self.source_document_id,
            "source_document_title": self.source_document_title,
            "created_at": self.created_at,
            "tags": self.tags,
            "child_friendly_definition": self.child_friendly_definition,
            "dictionary_meaning": self.dictionary_meaning,
            "contextual_meaning": self.contextual_meaning,
            "example_sentence": self.example_sentence,
            "part_of_speech": self.part_of_speech,
            "synonyms": self.synonyms,
            "antonyms": self.antonyms,
            "difficulty_level": self.difficulty_level,
            "pronunciation": self.pronunciation,
            "detected_pos": self.detected_pos,
            "identified_word_sense": self.identified_word_sense,
            "official_dictionary_definition": self.official_dictionary_definition,
            "simplified_child_definition": self.simplified_child_definition,
            "generated_example_sentence": self.generated_example_sentence,
            "dictionary_source": self.dictionary_source,
            "requires_manual_verification": self.requires_manual_verification,
            "is_mastered": self.is_mastered,
            "is_bookmarked": self.is_bookmarked,
            "needs_review": self.needs_review
        }

@dataclass
class FlashcardDeck:
    """Structure representing a complete generated flashcard deck inside the learning library."""
    deck_id: str
    source_document_id: str
    source_document_title: str
    exported_document_text: str
    created_at: str
    total_flashcards: int
    categories_distribution: Dict[str, int]
    difficulty_distribution: Dict[str, int]
    estimated_study_time_min: int
    mastery_percentage: float
    study_progress: Dict[str, Any]
    cards: List[Flashcard]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deck_id": self.deck_id,
            "source_document_id": self.source_document_id,
            "source_document_title": self.source_document_title,
            "exported_document_text": self.exported_document_text,
            "created_at": self.created_at,
            "total_flashcards": self.total_flashcards,
            "categories_distribution": self.categories_distribution,
            "difficulty_distribution": self.difficulty_distribution,
            "estimated_study_time_min": self.estimated_study_time_min,
            "mastery_percentage": round(self.mastery_percentage, 1),
            "study_progress": self.study_progress,
            "cards": [c.to_dict() for c in self.cards]
        }


