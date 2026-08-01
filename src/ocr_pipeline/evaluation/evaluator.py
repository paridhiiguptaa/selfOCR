import time
from typing import List, Dict, Any, Tuple, Optional
from .benchmark_dataset import BENCHMARK_TEST_CASES, TestCase
from ..modules.text_corrector import TextCorrectionEngine
from ..utils.logging_config import logger

def compute_levenshtein_distance(seq1: List[Any], seq2: List[Any]) -> int:
    """Compute Levenshtein distance between two sequences (chars or word tokens)."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[m][n]

def compute_cer(hypothesis: str, reference: str) -> float:
    """Calculate Character Error Rate (CER)."""
    ref_chars = list(reference)
    hyp_chars = list(hypothesis)
    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0
    dist = compute_levenshtein_distance(hyp_chars, ref_chars)
    return float(dist) / float(len(ref_chars))

def compute_wer(hypothesis: str, reference: str) -> float:
    """Calculate Word Error Rate (WER)."""
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    dist = compute_levenshtein_distance(hyp_words, ref_words)
    return float(dist) / float(len(ref_words))

class PipelineEvaluator:
    """
    Comprehensive evaluation framework for OCR and AI Proofreading pipeline.
    Calculates Character Error Rate (CER), Word Error Rate (WER), Sentence Accuracy,
    Correction Precision, Recall, and F1 Score on benchmark datasets.
    """

    def __init__(self):
        self.correction_engine = TextCorrectionEngine()

    def evaluate_benchmark(self, test_cases: Optional[List[TestCase]] = None) -> Dict[str, Any]:
        """Run full evaluation suite across benchmark test cases."""
        cases = test_cases or BENCHMARK_TEST_CASES
        start_time = time.time()

        case_results = []
        total_cer = 0.0
        total_wer = 0.0
        exact_matches = 0

        tp = 0  # True Positives: correctly modified erroneous tokens
        fp = 0  # False Positives: modified correctly spelled tokens
        fn = 0  # False Negatives: failed to correct erroneous tokens

        for tc in cases:
            corr_result = self.correction_engine.analyze_text(tc.raw_ocr_input)
            predicted_output = corr_result.corrected_text

            initial_cer = compute_cer(tc.raw_ocr_input, tc.ground_truth)
            initial_wer = compute_wer(tc.raw_ocr_input, tc.ground_truth)

            final_cer = compute_cer(predicted_output, tc.ground_truth)
            final_wer = compute_wer(predicted_output, tc.ground_truth)

            is_exact = (predicted_output.strip() == tc.ground_truth.strip())
            if is_exact:
                exact_matches += 1

            total_cer += final_cer
            total_wer += final_wer

            # Precision/Recall estimation
            if final_cer < initial_cer or is_exact:
                tp += 1
            elif len(corr_result.suggestions) > 0 and final_cer >= initial_cer:
                fp += 1
            elif initial_cer > 0 and final_cer == initial_cer:
                fn += 1

            case_results.append({
                "test_id": tc.test_id,
                "category": tc.category,
                "description": tc.description,
                "raw_input": tc.raw_ocr_input,
                "predicted_output": predicted_output,
                "ground_truth": tc.ground_truth,
                "initial_cer": round(initial_cer, 4),
                "final_cer": round(final_cer, 4),
                "initial_wer": round(initial_wer, 4),
                "final_wer": round(final_wer, 4),
                "is_exact_match": is_exact,
                "suggestions_generated": len(corr_result.suggestions)
            })

        num_cases = max(1, len(cases))
        mean_cer = total_cer / num_cases
        mean_wer = total_wer / num_cases
        sentence_accuracy = exact_matches / num_cases

        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1_score = (2 * precision * recall) / max(1e-6, precision + recall)

        elapsed = time.time() - start_time

        report = {
            "summary": {
                "total_test_cases": num_cases,
                "exact_sentence_matches": exact_matches,
                "sentence_accuracy": round(sentence_accuracy, 4),
                "mean_character_error_rate": round(mean_cer, 4),
                "mean_word_error_rate": round(mean_wer, 4),
                "proofreading_precision": round(precision, 4),
                "proofreading_recall": round(recall, 4),
                "proofreading_f1_score": round(f1_score, 4),
                "evaluation_duration_sec": round(elapsed, 3)
            },
            "cases": case_results
        }

        logger.info(
            f"Benchmark Evaluation Complete: CER={mean_cer:.4f}, WER={mean_wer:.4f}, "
            f"Accuracy={sentence_accuracy*100:.1f}%, F1={f1_score:.4f}"
        )
        return report
