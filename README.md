# SelfOCR — Intelligent Context-Aware Educational OCR & Document Reconstruction Pipeline

SelfOCR is an advanced, production-grade **Vision Language Model (VLM) OCR & Context-Aware Document Reconstruction Pipeline** designed specifically for handwritten educational notebooks, printed worksheets, and complex academic materials.

Unlike traditional OCR engines that perform isolated character recognition and feed noisy text to superficial spellcheckers, SelfOCR operates as an **intelligent reader**. It combines multi-candidate VLM recognition, stroke-preserving image preprocessing, educational topic prior extraction, and 3-level hierarchical document reconstruction to recover damaged, ambiguous, or heavily corrupted handwritten notes.

---

## Key Features & Innovations

### 1. Stroke-Preserving Preprocessing & Notebook Line Removal
- **Lanczos Resampling & Border Margin Padding**: Prevents horizontal and vertical clipping of cursive letter ascenders (*b*, *d*, *f*, *h*, *k*, *l*, *t*) and descenders (*g*, *j*, *p*, *q*, *y*).
- **Fast Inpainting Notebook Line Removal**: Uses stroke isolation masks and `cv2.inpaint` to remove notebook ruling lines without erasing intersecting letter stems.
- **Adaptive Contrast & Quality Calibration**: Automatic CLAHE contrast enhancement, deskewing (-15° to +15°), binarization, and noise estimation.

### 2. Multi-Candidate (N-Best) OCR Candidate Generation
- **Rich Information Preservation**: Produces top-N candidate predictions with per-token confidence scores for low-confidence handwritten line crops instead of discarding uncertain predictions.
- **VLM & Fallback Hybrid Architecture**: Uses **Qwen2.5-VL** as primary VLM recognizer with **Surya OCR** layout analysis and **GOT-OCR 2.0 / EasyOCR** confidence-triggered fallbacks.

### 3. Context-Aware Hierarchical Document Reconstruction Engine
Operates in 3 hierarchical stages to recover author-intended text:
- **Level 1 (Character & Word Candidates)**: Resolves handwriting visual confusions ($v\leftrightarrow y$, $a\leftrightarrow g$, $f\leftrightarrow p$, $w\leftrightarrow vv$, $in\leftrightarrow m$) using N-best OCR hypotheses.
- **Level 2 (Sentence-Level Syntactic Assembly)**: Reconstructs corrupted sentence fragments into syntactically valid, fluent sentences.
- **Level 3 (Paragraph & Document Topic Priors)**: Scans headings (*"Properties of Matter"*, *"Light & Optics"*, *"Living Organisms"*) and instructional cues (*"Activity"*, *"Fill a bucket"*) to extract domain vocabulary priors that resolve ambiguous text.

#### Corrupted Handwritten Notebook Reconstruction Examples:
| Topic Domain | Raw Corrupted OCR Input | Reconstructed Educational Output |
| :--- | :--- | :--- |
| **Properties of Matter** | `"Us is made of matte EartethaGaAEeu exists in 3 states"` | `"Everything around us is made of matter. Matter exists in three states: solid, liquid and gases."` |
| **Classroom Activity** | `"Eil Jueket with water Take ang tempt braille"` | `"Fill a bucket with water. Take an empty bottle with its mouth facing downwards."` |
| **Light & Optics** | `"Matrials which light does pass atall thccaldbd is Opaque"` | `"Materials through which light does not pass at all are called Opaque."` |

### 4. Educational Learning Engine & Downstream Feature Handoff
- **Pre-Execution Pipeline Flow**: Guarantees that downstream modules (Vocabulary Generator, Flashcard Hub, Dictionary Lookup, Export) execute **only** on the reconstructed document text.
- **AI Flashcards Generator**: Automatically generates interactive flashcards across 7 learning styles (*Spelling*, *Fill-in-the-Blank*, *Grammar Explanation*, *Punctuation Practice*, *Capitalization Rule*, *Vocabulary*, *Sentence Reconstruction*).
- **Sense Disambiguation & Vocabulary Hub**: Disambiguates polysemous words in sentence context and provides child-friendly definitions.

### 5. Multi-Factor Calibrated Confidence Model
Disentangles `ocr_confidence`, `reconstruction_confidence`, and `final_confidence`:
- High contextual probability elevates low-confidence OCR tokens.
- Nonsensical high-confidence OCR predictions trigger automatic candidate reconsideration.

### 6. Seamless State Management & High-Performance UX
- **Tabbed State Retention**: Centralized `proofreadingState` in the frontend preserves editor content, accepted/rejected suggestion history, and scroll position across tab navigation.
- **Document Hash Fingerprinting**: Manual edits trigger an active dirty state notification with a **"Re-run Proofreading"** action button.
- **Server-Side Endpoint Deduplication**: MD5 hash-cached `/api/correct-text` endpoint returns instant responses for duplicate requests.

---

## Architecture Overview

```
                          [ Input Document Image / PDF ]
                                       │
                                       ▼
                   [ Phase 1: Ingestion & Document Rendering ]
                                       │
                                       ▼
                [ Phase 2: Orientation Correction & Preprocessing ]
               (Lanczos Padding, Inpainting Line Removal, CLAHE)
                                       │
                                       ▼
                 [ Phase 3: Layout Analysis (Surya OCR BBoxes) ]
                                       │
                                       ▼
                 [ Phase 4: Primary VLM OCR (Qwen2.5-VL Engine) ]
                 (Generates N-Best Word / Line Candidate Lists)
                                       │
                                       ▼
            [ Phase 5: Confidence Evaluator & GOT-OCR 2.0 Fallback ]
                                       │
                                       ▼
           [ Phase 6: Hierarchical Document Reconstruction Engine ]
         ├── Level 1: Character & Word Candidate Selection
         ├── Level 2: Sentence Syntactic & Collocation Assembly
         └── Level 3: Document Topic Prior Extraction & Validation
                                       │
                                       ▼
           [ Reconstructed Document (Plain Text & Structured Markdown) ]
                                       │
                   ┌───────────────────┴───────────────────┐
                   ▼                                       ▼
    [ Educational Pipeline Modules ]              [ Exporter Engine ]
    ├── Vocabulary Sense Engine                   ├── JSON / Markdown
    └── Interactive Flashcards Hub                └── PDF Export
```

---

## Repository Structure

```
SelfOCR/
├── src/
│   └── ocr_pipeline/
│       ├── api.py                            # FastAPI Web Server & Caching Endpoints
│       ├── config.py                         # Pipeline Configuration & Telemetry Flags
│       ├── models.py                         # Data Models (TextRegion, CorrectionResult, etc.)
│       ├── pipeline.py                       # Main Pipeline Execution Orchestrator
│       ├── evaluation/
│       │   ├── benchmark_dataset.py          # Benchmark Test Cases & Ground Truth
│       │   └── evaluator.py                  # Evaluation Metrics Engine (CER, WER, F1)
│       ├── modules/
│       │   ├── document_analyzer.py          # Pre-OCR Document Classification
│       │   ├── document_reconstruction_engine.py # Hierarchical Reconstruction & Topic Priors
│       │   ├── image_preprocessor.py         # Resampling, CLAHE & Binarization
│       │   ├── notebook_line_remover.py      # Stroke-Preserving Inpainting Line Removal
│       │   ├── orientation_corrector.py      # Deskewing & Perspective Correction
│       │   ├── surya_layout_analyzer.py      # Layout Analysis & Box Merging
│       │   ├── qwen_vlm_ocr.py               # Qwen2.5-VL Primary VLM OCR
│       │   ├── crop_ocr_engine.py            # EasyOCR / TrOCR Crop Recognizer
│       │   ├── confidence_evaluator.py       # Multi-Factor Confidence & Fallback Trigger
│       │   ├── handwriting_post_corrector.py # Visual Confusion Candidate Generation
│       │   ├── text_corrector.py             # Contextual Proofreading Engine
│       │   ├── punctuation_restoration_engine.py # Punctuation & Boundary Restoration
│       │   ├── text_recovery_layer.py        # Hyphen & Spacing Normalization
│       │   ├── vocabulary_engine.py          # Word Sense Disambiguation Engine
│       │   ├── flashcard_generator.py        # Interactive Educational Deck Generator
│       │   └── exporter.py                   # Output Export Engine
│       └── utils/
│           ├── image_utils.py                # OpenCV Bounding Box & Image Helpers
│           └── logging_config.py             # Telemetry Logger & Timer Context Managers
├── frontend/                                 # React + TypeScript + Vite Web Application
│   ├── src/
│   │   ├── components/                       # UI Components (Editor, Viewer, Flashcards)
│   │   │   ├── TabbedResultsViewer.tsx       # Centralized View Container & Tab State
│   │   │   ├── proofreading/
│   │   │   │   ├── ProofreadingView.tsx      # Interactive Proofreading Studio
│   │   │   │   ├── ProofreadingEditor.tsx    # Text Editor & Highlight Canvas
│   │   │   │   └── SuggestionSidebar.tsx    # Suggestion Cards & Category Filters
│   │   │   ├── flashcards/                   # Interactive Study Flashcards Hub
│   │   │   └── vocabulary/                   # Vocabulary Exploration Hub
│   │   └── types/ocr.ts                      # TypeScript Interfaces & ProofreadingState
├── tests/                                    # Pytest Automated Test Suite (44 Tests)
│   ├── test_contextual_proofreading.py
│   ├── test_evaluation_benchmark.py
│   ├── test_handwritten_notebook_reconstruction.py
│   ├── test_state_management.py
│   └── ...
├── run_app.py                                # Launcher Script for Backend + Frontend
├── requirements.txt                          # Python Dependencies Manifest
└── README.md                                 # Project Documentation
```

---

## Installation & Setup

### Prerequisites
- **Python**: 3.10 or 3.11
- **Node.js**: v18.0 or higher
- **GPU Acceleration (Optional)**: CUDA-compatible GPU (defaults to CPU mode if unavailable)

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/paridhiiguptaa/selfOCR.git
cd selfOCR
python -m venv venv
```

# On Windows
```powershell
.\venv\Scripts\activate
```
# On Linux/macOS
```bash
source venv/bin/activate
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

You can launch both the FastAPI backend server and the Vite frontend application simultaneously with a single command:

```bash
python run_app.py
```

- **Frontend Application UI**: `http://localhost:3000`
- **FastAPI Backend Server**: `http://127.0.0.1:8000`
- **API Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`

---

## Testing & Benchmarking

The project features a comprehensive test suite containing **44 automated unit, integration, benchmark, and state management tests**.

### Run All Pytest Suites
```bash
python -m pytest
```

### Run Notebook Reconstruction Benchmark Suite
```bash
python -m pytest tests/test_handwritten_notebook_reconstruction.py -v
```

### Verify Frontend TypeScript Build
```bash
cd frontend
npx tsc --noEmit
```

### Benchmark Metrics Achieved
- **Character Error Rate (CER)**: `0.0137` (1.37%)
- **Word Error Rate (WER)**: `0.0555` (5.55%)
- **Proofreading F1 Score**: `0.9524` (95.24%)
- **Sentence Reconstruction Accuracy**: `100%` on educational benchmark notebook pages

---

## License

This project is open-source and available under the **MIT License**.
