import re
from typing import List, Dict, Any, Tuple, Optional
from ..utils.logging_config import logger

class EducationalLanguageModel:
    """
    Educational Language Understanding Layer.
    Parses document structure (headings, definitions, procedures, activities, Q&A)
    and evaluates candidate transcriptions against educational writing patterns.
    """

    STRUCTURE_PATTERNS = [
        ("Heading", r'^(?:chapter|unit|section|lesson|\d+[\.\)])\s*.*|^(?:properties|states|laws|principles|types)\s+of\s+.*', 0.90),
        ("Definition", r'^(?:definition|defined\s+as|is\s+called|are\s+called|refers\s+to|means)\b|:.*(?:defined|called)', 0.88),
        ("Activity", r'^(?:activity|task|exercise|practical)\s*\d*:?', 0.92),
        ("Experiment", r'^(?:experiment|aim|apparatus|procedure|method)\s*\d*:?', 0.92),
        ("Observation", r'^(?:observation|result|inference|observed)\s*\d*:?', 0.90),
        ("Procedure", r'^(?:fill|take|mix|heat|add|place|measure|connect|press|hold|drop|cut)\s+(?:a|an|the|some|\d+)\b', 0.85),
        ("Conclusion", r'^(?:conclusion|hence|therefore|thus|summary)\s*:?', 0.88),
        ("QA", r'^(?:q\d*|question|ans\d*|answer)\s*[:\.]', 0.90),
        ("Bullet", r'^(?:[\-\*\•\d+\.\)])\s+', 0.85)
    ]

    EDUCATIONAL_HEADING_CORRECTIONS = [
        (r'(?i)\bpropeties\s+of\s+matier\b', 'Properties of Matter'),
        (r'(?i)\bpropertis\s+of\s+matter\b', 'Properties of Matter'),
        (r'(?i)\bactvity\b', 'Activity'),
        (r'(?i)\bexperment\b', 'Experiment'),
        (r'(?i)\bobservaton\b', 'Observation'),
        (r'(?i)\bprocedur\b', 'Procedure'),
        (r'(?i)\bconcluson\b', 'Conclusion'),
        (r'(?i)\bdefination\b', 'Definition'),
        (r'(?i)\bdefinintion\b', 'Definition')
    ]

    def classify_structure(self, text: str) -> str:
        """Categorize structural role of a line of text."""
        clean = text.strip()
        if not clean:
            return "Text"

        for tag, pattern, _ in self.STRUCTURE_PATTERNS:
            if re.search(pattern, clean, flags=re.IGNORECASE):
                return tag

        return "Text"

    def reconstruct_structural_text(
        self,
        text: str,
        subject: str = "General",
        candidates: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[str, str, float]:
        """
        Reconstruct line using educational language understanding and structural role.
        Returns (reconstructed_text, structural_tag, confidence_boost).
        """
        if not text or not text.strip():
            return text, "Text", 0.0

        reconstructed = text
        boost = 0.0

        # Apply structural heading corrections first
        for pat, rep in self.EDUCATIONAL_HEADING_CORRECTIONS:
            if re.search(pat, reconstructed):
                reconstructed = re.sub(pat, rep, reconstructed)
                boost += 0.12

        struct_tag = self.classify_structure(reconstructed)


        # If candidates are provided, pick candidate matching structural tag
        if candidates and len(candidates) > 1:
            best_cand_text = reconstructed
            best_cand_score = 0.0

            for cand in candidates:
                cand_text = cand.get("text", "")
                vis_conf = cand.get("visual_confidence", 0.5)

                # Check if candidate matches structural expectation
                cand_tag = self.classify_structure(cand_text)
                cand_score = vis_conf

                if cand_tag == struct_tag and struct_tag != "Text":
                    cand_score += 0.15

                # Additional check for procedural verbs in procedural context
                if struct_tag in ("Activity", "Experiment", "Procedure"):
                    if re.search(r'\b(fill|take|mix|place|add|measure|observe|check)\b', cand_text, re.I):
                        cand_score += 0.10

                if cand_score > best_cand_score:
                    best_cand_score = cand_score
                    best_cand_text = cand_text

            reconstructed = best_cand_text

        return reconstructed, struct_tag, boost
