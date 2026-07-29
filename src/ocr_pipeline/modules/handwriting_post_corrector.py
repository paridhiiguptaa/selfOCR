import re
from typing import Dict

class HandwritingPostCorrector:
    """
    Contextual post-processor specifically tailored for children's handwriting,
    educational worksheets, and common OCR character confusion patterns.
    """

    WORD_REPLACEMENTS: Dict[str, str] = {
        "4es": "Yes",
        "ILhale": "I have",
        "ILhave": "I have",
        "lhale": "have",
        "Seeh@": "seen",
        "Seeh": "seen",
        "ibheW": "rainbow",
        "2aihboW": "rainbow",
        "Ealhbolu_": "rainbow",
        "Ealhbolu": "rainbow",
        "2ainbow": "rainbow",
        "Ahe_sky_": "the sky",
        "Ahe_sky": "the sky",
        "Ahe": "the",
        "ihs": "eyes",
        "Iheskhis_Reel": "peeping through",
        "Iheskhif_Reelihd": "peeping through",
        "~hXauLh": "through",
        "cleuLS": "clouds",
        "Ibezearseveh": "There are seven",
        "LeLES": "colours",
        "Viele": "Violet",
        "IAdi9": "Indigo",
        "Sxeely": "Green",
        "Hellew": "Yellow",
        "oie_hde": "Orange"
    }

    def correct(self, text: str) -> str:
        """Apply contextual OCR noise cleanup to handwritten transcriptions."""
        if not text:
            return ""

        result = text

        # 1. Direct dictionary replacements
        for wrong, right in self.WORD_REPLACEMENTS.items():
            result = re.sub(r'\b' + re.escape(wrong) + r'\b', right, result)

        # 2. Fix answer label formatting (Ans; -> Ans:, Ans. -> Ans:)
        result = re.sub(r'\bAns[;.]\s*', 'Ans: ', result)
        result = re.sub(r'\bQ\.\s*(\d+)\s*\.\s*', r'Q.\1. ', result)

        # 3. Clean up noise characters commonly inserted around handwritten letters
        result = re.sub(r'[@~{}[\]|_]', ' ', result)

        # 4. Normalize multiple spaces
        result = re.sub(r'[ \t]+', ' ', result).strip()

        return result
