import importlib
import sys
import traceback
from typing import List, Dict, Any, Tuple

from .logging_config import logger

# Essential standard library modules required across the pipeline
REQUIRED_STDLIB_MODULES = [
    "os", "sys", "time", "json", "math", "re", "traceback", "base64", "tempfile", "shutil", "hashlib"
]

# Essential third-party packages required across the pipeline
REQUIRED_THIRD_PARTY_MODULES = [
    "cv2", "numpy", "PIL", "torch", "transformers", "fastapi", "pydantic", "surya"
]

# Internal pipeline modules required for full document processing
REQUIRED_INTERNAL_MODULES = [
    "src.ocr_pipeline.config",
    "src.ocr_pipeline.models",
    "src.ocr_pipeline.utils.logging_config",
    "src.ocr_pipeline.utils.image_utils",
    "src.ocr_pipeline.utils.json_utils",
    "src.ocr_pipeline.modules.input_handler",
    "src.ocr_pipeline.modules.orientation_corrector",
    "src.ocr_pipeline.modules.image_preprocessor",
    "src.ocr_pipeline.modules.document_analyzer",
    "src.ocr_pipeline.modules.surya_layout_analyzer",
    "src.ocr_pipeline.modules.qwen_vlm_ocr",
    "src.ocr_pipeline.modules.confidence_evaluator",
    "src.ocr_pipeline.modules.layout_reconstructor",
    "src.ocr_pipeline.modules.exporter",
    "src.ocr_pipeline.modules.text_corrector",
    "src.ocr_pipeline.modules.subject_detection",
    "src.ocr_pipeline.modules.educational_language_model",
    "src.ocr_pipeline.modules.handwriting_adaptation",
    "src.ocr_pipeline.modules.crop_ocr_engine",
    "src.ocr_pipeline.modules.multi_model_ocr_ensemble",
    "src.ocr_pipeline.modules.vlm_verifier",
    "src.ocr_pipeline.modules.flashcard_generator",
    "src.ocr_pipeline.modules.vocabulary_engine",
    "src.ocr_pipeline.pipeline",
]


def validate_pipeline_imports(fail_fast: bool = True) -> Dict[str, Any]:
    """
    Lightweight startup validation routine.
    Verifies that all required standard libraries, third-party dependencies,
    and internal pipeline modules can be cleanly imported without NameError,
    ImportError, or missing module attributes.

    Returns a summary dictionary of validation status.
    Raises RuntimeError on failure if `fail_fast=True`.
    """
    logger.info("[STARTUP VALIDATOR] Executing pre-flight module import validation...")
    results: Dict[str, Any] = {
        "status": "passed",
        "total_checked": 0,
        "failed_imports": [],
        "passed_modules": []
    }

    all_modules = (
        [("stdlib", m) for m in REQUIRED_STDLIB_MODULES] +
        [("third_party", m) for m in REQUIRED_THIRD_PARTY_MODULES] +
        [("internal", m) for m in REQUIRED_INTERNAL_MODULES]
    )

    for category, mod_name in all_modules:
        results["total_checked"] += 1
        try:
            mod = importlib.import_module(mod_name)
            results["passed_modules"].append(mod_name)
        except Exception as e:
            tb_str = traceback.format_exc()
            error_entry = {
                "category": category,
                "module_name": mod_name,
                "exception_type": type(e).__name__,
                "message": str(e),
                "traceback": tb_str
            }
            results["failed_imports"].append(error_entry)
            results["status"] = "failed"
            logger.error(
                f"[STARTUP VALIDATOR FAIL] Required module '{mod_name}' ({category}) "
                f"failed to import: {type(e).__name__}: {e}"
            )

    # Validate essential runtime symbols (e.g. time.time, json.dumps, os.path)
    symbol_checks = [
        ("time", "time"),
        ("time", "perf_counter"),
        ("json", "dumps"),
        ("json", "loads"),
        ("os", "path"),
        ("traceback", "format_exc"),
    ]
    for mod_name, attr in symbol_checks:
        try:
            m = importlib.import_module(mod_name)
            if not hasattr(m, attr):
                raise AttributeError(f"Module '{mod_name}' has no attribute '{attr}'")
        except Exception as e:
            results["failed_imports"].append({
                "category": "symbol",
                "module_name": f"{mod_name}.{attr}",
                "exception_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            })
            results["status"] = "failed"

    if results["status"] == "failed":
        summary_msg = (
            f"Startup validation failed! {len(results['failed_imports'])} module(s) could not be imported: " +
            ", ".join(fi['module_name'] for fi in results['failed_imports'])
        )
        logger.critical(f"[STARTUP VALIDATOR] {summary_msg}")
        if fail_fast:
            raise RuntimeError(summary_msg)
    else:
        logger.info(
            f"[STARTUP VALIDATOR] All {results['total_checked']} pipeline dependencies "
            f"and modules validated successfully."
        )

    return results
