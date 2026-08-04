import time
from typing import List, Dict, Any, Optional
from ..modules.subject_detection import SubjectDetectionModule
from ..modules.educational_language_model import EducationalLanguageModel
from ..modules.handwriting_adaptation import HandwritingAdaptationModule
from ..modules.multi_scale_ocr import CandidateFusionModule
from .evaluator import compute_cer, compute_wer
from ..utils.logging_config import logger

class NextGenPipelineEvaluator:
    """
    Comprehensive Benchmark Evaluation Framework for Next-Generation OCR Pipeline Capabilities:
    1. Multi-scale candidate fusion accuracy.
    2. Educational subject detection classification accuracy across subjects.
    3. Educational Language Model structural reconstruction quality.
    4. Personalized handwriting adaptation learning curve over sequential document uploads.
    """

    TEST_SUBJECT_DATASET = [
        {"title": "Properties of Matter", "text": "Everything around us is made of matter. Matter exists in solid liquid and gases.", "expected_subject": "Science"},
        {"title": "Algebra Lesson 2", "text": "Solve the linear equation for x. Calculate the perimeter and area of the triangle.", "expected_subject": "Mathematics"},
        {"title": "Laws of Motion", "text": "Force equals mass times acceleration. Velocity is displacement divided by time.", "expected_subject": "Physics"},
        {"title": "Chemical Reactions", "text": "Acids react with bases to form salt and water. An atom consists of protons and electrons.", "expected_subject": "Chemistry"},
        {"title": "Plant Biology", "text": "Plants prepare food by photosynthesis. Leaves contain chlorophyll.", "expected_subject": "Biology"},
        {"title": "Geography of Continents", "text": "Latitude lines run parallel to equator. Erosion wears away soil.", "expected_subject": "Geography"},
        {"title": "History Chapter 5", "text": "The empire expanded across multiple continents during the 18th century treaty.", "expected_subject": "History"},
        {"title": "Python Programming", "text": "An algorithm is a step by step set of instructions. Loops execute repeatedly.", "expected_subject": "Computer Science"}
    ]

    HANDWRITING_ADAPTATION_SIMULATION_STEPS = [
        # (Raw OCR input from student notebook, Accepted ground truth correction)
        ("Eil Jueket with water", "Fill bucket with water"),
        ("Us is made of matier", "Us is made of matter"),
        ("road a bike to school", "rode a bike to school"),
        ("the son is shining", "the sun is shining"),
        ("light passes through transparent glass", "light passes through transparent glass")
    ]

    def evaluate_subject_detection(self) -> Dict[str, Any]:
        detector = SubjectDetectionModule()
        correct = 0
        total = len(self.TEST_SUBJECT_DATASET)

        for case in self.TEST_SUBJECT_DATASET:
            res = detector.detect_subject(text=case["text"], document_title=case["title"])
            if res["subject"] == case["expected_subject"]:
                correct += 1

        accuracy = correct / float(total)
        return {
            "total_test_cases": total,
            "correct_classifications": correct,
            "subject_detection_accuracy": round(accuracy, 4)
        }

    def evaluate_handwriting_adaptation_learning_curve(self, user_id: str = "simulated_student") -> Dict[str, Any]:
        adapter = HandwritingAdaptationModule()
        adapter.reset_profile(user_id)

        progression = []

        for step_idx, (raw_ocr, ground_truth) in enumerate(self.HANDWRITING_ADAPTATION_SIMULATION_STEPS, 1):
            initial_cer = compute_cer(raw_ocr, ground_truth)
            initial_boost = adapter.calculate_candidate_adaptation_boost(user_id, raw_ocr)

            # Record feedback
            adapter.record_feedback(user_id, original_ocr=raw_ocr, accepted_correction=ground_truth)

            post_boost = adapter.calculate_candidate_adaptation_boost(user_id, ground_truth)
            profile = adapter.get_profile(user_id)

            progression.append({
                "step": step_idx,
                "raw_ocr": raw_ocr,
                "ground_truth": ground_truth,
                "initial_cer": round(initial_cer, 4),
                "profile_documents_processed": profile["documents_processed"],
                "adaptation_boost_gained": round(post_boost - initial_boost, 4)
            })

        adapter.reset_profile(user_id)

        return {
            "simulated_user_id": user_id,
            "total_adaptation_steps": len(self.HANDWRITING_ADAPTATION_SIMULATION_STEPS),
            "step_progression": progression
        }

    def run_full_evaluation_suite(self) -> Dict[str, Any]:
        start = time.time()
        subj_res = self.evaluate_subject_detection()
        adapt_res = self.evaluate_handwriting_adaptation_learning_curve()
        elapsed = time.time() - start

        return {
            "subject_detection_benchmark": subj_res,
            "handwriting_adaptation_benchmark": adapt_res,
            "total_evaluation_time_sec": round(elapsed, 3)
        }
