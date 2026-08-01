from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class TestCase:
    """Structure representing a single benchmark evaluation test case."""
    test_id: str
    category: str # "handwritten", "printed", "mixed_worksheet", "homophone_context"
    raw_ocr_input: str
    ground_truth: str
    description: str

BENCHMARK_TEST_CASES: List[TestCase] = [
    TestCase(
        test_id="tc_01_homophone_road",
        category="homophone_context",
        raw_ocr_input="The boy road the bicycle to school.",
        ground_truth="The boy rode the bicycle to school.",
        description="Contextual word substitution of 'road' to 'rode' in bicycle sentence context."
    ),
    TestCase(
        test_id="tc_02_homophone_red",
        category="homophone_context",
        raw_ocr_input="She red the book yesterday afternoon.",
        ground_truth="She read the book yesterday afternoon.",
        description="Contextual word substitution of 'red' to 'read' in book reading sentence context."
    ),
    TestCase(
        test_id="tc_03_handwriting_confusion_sky",
        category="handwritten",
        raw_ocr_input="The skv is blue and bright.",
        ground_truth="The sky is blue and bright.",
        description="Character confusion correction of 'skv' (v -> y) to 'sky'."
    ),
    TestCase(
        test_id="tc_04_handwriting_confusion_peeping",
        category="handwritten",
        raw_ocr_input="The sun is peepina through clouds.",
        ground_truth="The sun is peeping through clouds.",
        description="Character confusion correction of 'peepina' (a -> g) to 'peeping'."
    ),
    TestCase(
        test_id="tc_05_printed_worksheet",
        category="printed",
        raw_ocr_input="Answer the following question. Fix implomentation of froin platform.",
        ground_truth="Answer the following questions. Fix implementation of from the platform.",
        description="Spelling correction ('implomentation'), OCR misread ('froin'), and article insertion."
    ),
    TestCase(
        test_id="tc_06_capitalization_and_punct",
        category="printed",
        raw_ocr_input="ans: yes i have seen the rainbow ?",
        ground_truth="Ans: Yes, I have seen the rainbow?",
        description="Answer tag capitalization, pronoun 'i' capitalization, and space before question mark."
    )
]
