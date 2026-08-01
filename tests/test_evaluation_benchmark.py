import pytest
from src.ocr_pipeline.evaluation.evaluator import PipelineEvaluator, compute_cer, compute_wer
from src.ocr_pipeline.evaluation.benchmark_dataset import BENCHMARK_TEST_CASES

def test_levenshtein_distance_and_metrics():
    assert compute_cer("cat", "cat") == 0.0
    assert compute_cer("cat", "cot") == 1/3
    assert compute_wer("the boy rode", "the boy rode") == 0.0

def test_pipeline_evaluation_benchmark():
    evaluator = PipelineEvaluator()
    report = evaluator.evaluate_benchmark(BENCHMARK_TEST_CASES)

    summary = report["summary"]
    assert summary["total_test_cases"] == len(BENCHMARK_TEST_CASES)
    assert summary["sentence_accuracy"] >= 0.65
    assert summary["mean_character_error_rate"] <= 0.05
    assert summary["proofreading_f1_score"] >= 0.80

    for case in report["cases"]:
        assert "test_id" in case
        assert "final_cer" in case
        assert case["final_cer"] <= case["initial_cer"] or case["is_exact_match"]
