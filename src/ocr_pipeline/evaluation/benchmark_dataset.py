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
    ),
    TestCase(
        test_id="tc_07_homophone_sea",
        category="homophone_context",
        raw_ocr_input="I sea the bright rainbow in the sky.",
        ground_truth="I see the bright rainbow in the sky.",
        description="Contextual word substitution of 'sea' to 'see' in sight context."
    ),
    TestCase(
        test_id="tc_08_homophone_there",
        category="homophone_context",
        raw_ocr_input="Their are seven colors in the rainbow.",
        ground_truth="There are seven colors in the rainbow.",
        description="Contextual homophone substitution of 'Their' to 'There' with existential 'are'."
    ),
    TestCase(
        test_id="tc_09_homophone_sun",
        category="homophone_context",
        raw_ocr_input="The son is shining brightly in the sky.",
        ground_truth="The sun is shining brightly in the sky.",
        description="Contextual word substitution of 'son' to 'sun' in sky context."
    ),
    TestCase(
        test_id="tc_10_homophone_cat",
        category="homophone_context",
        raw_ocr_input="I cat the paper with scissors.",
        ground_truth="I cut the paper with scissors.",
        description="Contextual word substitution of 'cat' to 'cut' in cutting context."
    ),
    TestCase(
        test_id="tc_11_multi_word_handwriting",
        category="handwritten",
        raw_ocr_input="The yellov sun is peepina through clouds.",
        ground_truth="The yellow sun is peeping through clouds.",
        description="Multi-word handwritten character confusion recovery ('yellov' -> 'yellow', 'peepina' -> 'peeping')."
    ),
    TestCase(
        test_id="tc_12_notebook_reconstruction_matter",
        category="handwritten",
        raw_ocr_input="Us is made of matte EartethaGaAEeu exists in 3 states",
        ground_truth="Everything around us is made of matter. Matter exists in three states: solid, liquid and gases.",
        description="Educational notebook hierarchical document reconstruction under Properties of Matter topic."
    ),
    TestCase(
        test_id="tc_13_notebook_reconstruction_activity",
        category="handwritten",
        raw_ocr_input="Eil Jueket with water Take ang tempt braille",
        ground_truth="Fill a bucket with water. Take an empty bottle with its mouth facing downwards.",
        description="Classroom activity instructional text reconstruction."
    ),
    TestCase(
        test_id="tc_14_notebook_reconstruction_optics",
        category="handwritten",
        raw_ocr_input="Matrials which light does pass atall thccaldbd is Opaque",
        ground_truth="Materials through which light does not pass at all are called Opaque.",
        description="Light and Optics domain note reconstruction."
    )
]
