import pytest
from src.ocr_pipeline.evaluation.nextgen_benchmark import NextGenPlatformBenchmark

def test_nextgen_benchmark_suite():
    bench = NextGenPlatformBenchmark()
    res = bench.run_full_benchmark_suite()

    assert "individual_recognizers_benchmark" in res
    assert "nextgen_pipeline_benchmark" in res
    assert "benchmark_execution_duration_sec" in res
    assert res["nextgen_pipeline_benchmark"]["pipeline_sentence_accuracy"] >= 0.50
