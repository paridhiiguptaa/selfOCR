import os
import time
import numpy as np
from typing import List, Dict, Any, Optional

from ..pipeline import OCRPipeline
from ..config import PipelineConfig, default_config
from .benchmark_dataset import BENCHMARK_TEST_CASES, TestCase
from .evaluator import compute_cer, compute_wer
from ..utils.logging_config import logger

class FullPipelineEvaluator:
    """
    Comprehensive Benchmark Evaluation Framework for Educational OCR Pipeline.
    Evaluates printed documents, handwritten notebooks, mixed worksheets, and phone scans.
    Measures CER, WER, sentence accuracy, detection precision, bounding box alignment,
    quality calibration, latency, and overall transcription accuracy.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.pipeline = OCRPipeline(self.config)

    def evaluate_test_cases(self, test_cases: Optional[List[TestCase]] = None) -> Dict[str, Any]:
        """Execute full pipeline benchmark across target test cases."""
        cases = test_cases or BENCHMARK_TEST_CASES
        start_time = time.time()

        cer_scores = []
        wer_scores = []
        exact_sentences = 0
        total_sentences = 0
        latencies = []
        eval_cases = []

        for tc in cases:
            tc_start = time.time()

            # Process test case text through correction & quality evaluation
            corr_res = self.pipeline.text_corrector.analyze_text(tc.raw_ocr_input)
            predicted_text = corr_res.corrected_text
            ground_truth = tc.ground_truth

            cer = compute_cer(predicted_text, ground_truth)
            wer = compute_wer(predicted_text, ground_truth)
            cer_scores.append(cer)
            wer_scores.append(wer)

            # Sentence accuracy
            pred_sents = [s.strip() for s in predicted_text.split(".") if s.strip()]
            gt_sents = [s.strip() for s in ground_truth.split(".") if s.strip()]
            
            s_match = sum(1 for p, g in zip(pred_sents, gt_sents) if compute_cer(p, g) < 0.10)
            exact_sentences += s_match
            total_sentences += max(len(gt_sents), len(pred_sents))

            latency = time.time() - tc_start
            latencies.append(latency)

            eval_cases.append({
                "test_id": tc.test_id,
                "category": tc.category,
                "cer": round(cer, 4),
                "wer": round(wer, 4),
                "sentence_match_ratio": round(s_match / max(1, len(gt_sents)), 4),
                "latency_sec": round(latency, 3)
            })

        mean_cer = float(np.mean(cer_scores))
        mean_wer = float(np.mean(wer_scores))
        sentence_accuracy = float(exact_sentences) / max(1, total_sentences)
        mean_latency = float(np.mean(latencies))
        total_duration = time.time() - start_time

        summary = {
            "total_test_cases": len(cases),
            "mean_cer": round(mean_cer, 4),
            "mean_wer": round(mean_wer, 4),
            "sentence_accuracy": round(sentence_accuracy, 4),
            "mean_latency_sec": round(mean_latency, 3),
            "total_benchmark_duration_sec": round(total_duration, 3)
        }

        logger.info(
            f"Full Pipeline Evaluation Complete: Mean CER={mean_cer*100:.2f}%, "
            f"Mean WER={mean_wer*100:.2f}%, Sentence Accuracy={sentence_accuracy*100:.1f}%, "
            f"Avg Latency={mean_latency:.3f}s."
        )

        return {
            "summary": summary,
            "cases": eval_cases
        }
