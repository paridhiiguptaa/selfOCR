"""
test_startup_validator.py

Unit tests verifying pre-flight startup module validation:
  1. All required standard libraries and third-party dependencies are importable.
  2. All internal OCR pipeline modules import cleanly.
  3. validate_pipeline_imports() returns status 'passed'.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ocr_pipeline.utils.startup_validator import validate_pipeline_imports


def test_startup_pipeline_imports_validation():
    """Verify that all pipeline modules and standard libraries pass pre-flight validation."""
    results = validate_pipeline_imports(fail_fast=False)

    assert results["status"] == "passed"
    assert results["total_checked"] > 20
    assert len(results["failed_imports"]) == 0
    assert len(results["passed_modules"]) == results["total_checked"]
