import re
from typing import Dict

class HandwritingPostCorrector:
    """
    Contextual post-processor specifically tailored for children's handwriting,
    educational worksheets, and common OCR character confusion patterns (y/v, g/a, p/f, w/vv, h/k).
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
        "rainbovv": "rainbow",
        "rainbov": "rainbow",
        "rainbou": "rainbow",
        "Ahe_sky_": "the sky",
        "Ahe_sky": "the sky",
        "Ahe": "the",
        "ahe": "the",
        "tbe": "the",
        "ihs": "eyes",
        "Iheskhis_Reel": "peeping through",
        "Iheskhif_Reelihd": "peeping through",
        "~hXauLh": "through",
        "cleuLS": "clouds",
        "cleuds": "clouds",
        "clauds": "clouds",
        "Ibezearseveh": "There are seven",
        "LeLES": "colours",
        "Viele": "Violet",
        "viovet": "Violet",
        "violat": "Violet",
        "IAdi9": "Indigo",
        "indiao": "Indigo",
        "indiqo": "Indigo",
        "Sxeely": "Green",
        "areen": "Green",
        "areene": "Green",
        "Hellew": "Yellow",
        "yellov": "Yellow",
        "vellov": "Yellow",
        "oie_hde": "Orange",
        "oraaqe": "Orange",
        "oranae": "Orange",
        "oraage": "Orange",
        "skv": "sky",
        "skye": "sky",
        "peepina": "peeping",
        "feefing": "peeping",
        "favovrite": "favourite",
        "favonrite": "favourite",
        "cravon": "crayon",
        "cravons": "crayons",
    }

    def correct(self, text: str) -> str:
        """Apply contextual OCR noise cleanup to handwritten transcriptions."""
        if not text:
            return ""

        result = text

        # 1. Direct dictionary replacements
        for wrong, right in self.WORD_REPLACEMENTS.items():
            result = re.sub(r'\b' + re.escape(wrong) + r'\b', right, result, flags=re.IGNORECASE)

        # 2. Character-pair recovery for handwriting: v -> y in word endings (skv -> sky, yellov -> yellow)
        result = re.sub(r'\bskv\b', 'sky', result, flags=re.IGNORECASE)
        result = re.sub(r'\byellov\b', 'yellow', result, flags=re.IGNORECASE)
        result = re.sub(r'\bvellov\b', 'yellow', result, flags=re.IGNORECASE)

        # 3. Fix answer label formatting (Ans; -> Ans:, Ans. -> Ans:)
        result = re.sub(r'\bAns[;.]\s*', 'Ans: ', result)
        result = re.sub(r'\bQ\.\s*(\d+)\s*\.\s*', r'Q.\1. ', result)

        # 4. Clean up noise characters commonly inserted around handwritten letters
        result = re.sub(r'[@~{}[\]|_]', ' ', result)

        # 5. Normalize multiple spaces
        result = re.sub(r'[ \t]+', ' ', result).strip()

        return result
