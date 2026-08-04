import os
import json
import re
from typing import List, Dict, Any, Tuple, Optional
from ..config import PipelineConfig, default_config
from ..utils.logging_config import logger

class HandwritingAdaptationModule:
    """
    Personalized Handwriting Adaptation Module.
    Maintains persistent user handwriting profiles to learn student-specific character confusions,
    writing style traits, and systematic OCR errors without altering base model weights.
    """

    DEFAULT_CONFUSIONS = {
        "v": {"y": 0.35, "u": 0.20},
        "y": {"v": 0.35, "g": 0.25},
        "g": {"a": 0.30, "q": 0.20},
        "a": {"g": 0.30, "o": 0.20},
        "cl": {"d": 0.40},
        "rn": {"m": 0.40},
        "1": {"l": 0.35, "I": 0.30},
        "l": {"1": 0.35, "I": 0.25},
        "5": {"S": 0.35, "s": 0.25},
        "0": {"O": 0.35, "o": 0.30}
    }

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.storage_dir = os.path.abspath(self.config.user_profile_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_profile_path(self, user_id: str) -> str:
        safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', user_id)
        return os.path.join(self.storage_dir, f"{safe_id}_profile.json")

    def get_profile(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Load persistent handwriting profile for user_id."""
        uid = user_id or self.config.default_user_id
        if uid in self._cache:
            return self._cache[uid]

        file_path = self._get_profile_path(uid)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    self._cache[uid] = profile
                    return profile
            except Exception as e:
                logger.warning(f"Failed to load profile for user '{uid}': {e}")

        # Initialize default fresh profile
        default_profile = {
            "user_id": uid,
            "documents_processed": 0,
            "corrections_accepted": 0,
            "character_confusions": dict(self.DEFAULT_CONFUSIONS),
            "custom_vocabulary": {},
            "writing_style": {
                "avg_stroke_width": 2.5,
                "avg_letter_spacing": 1.2,
                "slant": "vertical",
                "uppercase_frequency": 0.15
            },
            "systematic_errors": {},
            "version": "1.0.0"
        }
        self._save_profile(uid, default_profile)
        return default_profile

    def _save_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        file_path = self._get_profile_path(user_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2)
            self._cache[user_id] = profile
        except Exception as e:
            logger.error(f"Failed to save profile for user '{user_id}': {e}")

    def record_feedback(
        self,
        user_id: Optional[str],
        original_ocr: str,
        accepted_correction: str
    ) -> Dict[str, Any]:
        """
        Incrementally update handwriting profile when user accepts or edits an OCR correction.
        Learns systematic word confusions and character substitutions.
        """
        uid = user_id or self.config.default_user_id
        profile = self.get_profile(uid)

        orig_clean = original_ocr.strip().lower()
        corr_clean = accepted_correction.strip().lower()

        if orig_clean != corr_clean and orig_clean and corr_clean:
            # Record systematic word mapping
            sys_errs = profile.get("systematic_errors", {})
            sys_errs[orig_clean] = sys_errs.get(orig_clean, 0) + 1
            profile["systematic_errors"] = sys_errs

            # Record custom vocabulary preference
            vocab = profile.get("custom_vocabulary", {})
            vocab[corr_clean] = vocab.get(corr_clean, 0) + 1
            profile["custom_vocabulary"] = vocab

            # Infer character pair confusions if string lengths match
            if len(orig_clean) == len(corr_clean):
                confusions = profile.get("character_confusions", {})
                for o_char, c_char in zip(orig_clean, corr_clean):
                    if o_char != c_char:
                        char_map = confusions.get(o_char, {})
                        char_map[c_char] = round(char_map.get(c_char, 0.20) + 0.05, 3)
                        confusions[o_char] = char_map
                profile["character_confusions"] = confusions

            profile["corrections_accepted"] = profile.get("corrections_accepted", 0) + 1

        profile["documents_processed"] = profile.get("documents_processed", 0) + 1
        self._save_profile(uid, profile)
        return profile

    def calculate_candidate_adaptation_boost(
        self,
        user_id: Optional[str],
        candidate_text: str
    ) -> float:
        """
        Calculate Bayesian rescoring boost for candidate text based on user profile priors.
        """
        uid = user_id or self.config.default_user_id
        profile = self.get_profile(uid)

        if not candidate_text:
            return 0.0

        cand_lower = candidate_text.strip().lower()
        boost = 0.0

        # Check systematic error mappings
        sys_errs = profile.get("systematic_errors", {})
        if cand_lower in sys_errs:
            boost += min(0.20, sys_errs[cand_lower] * 0.05)

        # Check custom vocabulary frequency
        custom_vocab = profile.get("custom_vocabulary", {})
        words = cand_lower.split()
        for w in words:
            clean_w = re.sub(r'[^a-z0-9]', '', w)
            if clean_w in custom_vocab:
                boost += min(0.12, custom_vocab[clean_w] * 0.03)

        return min(0.25, boost)

    def reset_profile(self, user_id: Optional[str] = None) -> bool:
        """Reset user handwriting adaptation profile."""
        uid = user_id or self.config.default_user_id
        file_path = self._get_profile_path(uid)
        if uid in self._cache:
            del self._cache[uid]
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Handwriting adaptation profile for '{uid}' reset successfully.")
                return True
            except Exception as e:
                logger.error(f"Failed to delete profile file for '{uid}': {e}")
                return False
        return True
