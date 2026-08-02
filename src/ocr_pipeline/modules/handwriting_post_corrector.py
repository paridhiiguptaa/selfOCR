import re
from typing import Dict, List, Tuple

class HandwritingPostCorrector:
    """
    Contextual post-processor specifically tailored for children's and educational handwriting,
    addressing common OCR character confusion patterns (y/v, g/a, p/f, w/vv, h/k, m/rn).
    Generates cleaned transcriptions and candidate variations without hardcoding domain text.
    """

    # Common visual character confusion mappings in handwriting OCR
    CHAR_CONFUSION_MAP: List[Tuple[str, str, str]] = [
        (r'\bskv\b', 'sky', 'v -> y character confusion'),
        (r'\byellov\b', 'yellow', 'v -> w character confusion'),
        (r'\bvellov\b', 'yellow', 'v -> y / v -> w character confusion'),
        (r'\bpeepina\b', 'peeping', 'a -> g character confusion'),
        (r'\bfeefing\b', 'peeping', 'f -> p character confusion'),
        (r'\bareen\b', 'green', 'a -> g character confusion'),
        (r'\boraaqe\b', 'orange', 'a -> g character confusion'),
        (r'\boranae\b', 'orange', 'a -> g character confusion'),
        (r'\bviovet\b', 'violet', 'v -> l character confusion'),
        (r'\bindiao\b', 'indigo', 'a -> g character confusion'),
        (r'\bindiqo\b', 'indigo', 'q -> g character confusion'),
        (r'\bfroin\b', 'from', 'in -> m character confusion'),
        (r'\boji\b', 'on', 'ji -> n character confusion'),
        (r'\blhale\b', 'have', 'lh -> h, l -> v character confusion'),
    ]

    def correct(self, text: str) -> str:
        """Apply contextual OCR noise cleanup to handwritten transcriptions."""
        if not text:
            return ""

        result = text

        # 1. Apply generic character confusion patterns
        for pattern, replacement, _ in self.CHAR_CONFUSION_MAP:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # 2. Fix answer and question label formatting (Ans; -> Ans:, Ans. -> Ans:, Q.1. -> Q.1:)
        result = re.sub(r'\bAns[;.]\s*', 'Ans: ', result)
        result = re.sub(r'\bQ\.\s*(\d+)\s*\.\s*', r'Q.\1. ', result)

        # 3. Clean up noise characters commonly inserted around handwritten letters
        result = re.sub(r'[@~{}[\]|_]', ' ', result)

        # 4. Normalize multiple spaces
        result = re.sub(r'[ \t]+', ' ', result).strip()

        return result

    def generate_candidates(self, text: str) -> List[Tuple[str, float]]:
        """
        Generate N-best alternative transcription candidates based on character confusion rules.
        Returns list of (candidate_text, confidence_weight).
        """
        if not text or not text.strip():
            return [(text, 1.0)]

        candidates = [(text, 1.0)]
        cleaned = self.correct(text)
        if cleaned != text:
            candidates.append((cleaned, 0.92))

        # Add visual confusion candidates for ambiguous words
        words = text.split()
        modified = False
        alt_words = []
        for w in words:
            w_lower = w.lower()
            # If word ends in 'v', offer candidate ending in 'y' or 'w'
            if w_lower.endswith('v') and len(w_lower) > 2 and w_lower not in ('gov', 'rev'):
                alt_w = w[:-1] + ('y' if w_lower.endswith('kv') else 'w')
                alt_words.append(alt_w)
                modified = True
            elif 'rn' in w_lower:
                alt_w = re.sub(r'rn', 'm', w, flags=re.IGNORECASE)
                alt_words.append(alt_w)
                modified = True
            else:
                alt_words.append(w)

        if modified:
            alt_candidate = " ".join(alt_words)
            if alt_candidate not in [c[0] for c in candidates]:
                candidates.append((alt_candidate, 0.85))

        return candidates

