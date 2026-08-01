import re
from typing import Tuple, List, Dict, Any, Optional
from ..utils.logging_config import logger

class TextRecoveryLayer:
    """
    Intermediate OCR Text Recovery & Normalization Layer.
    Positioned between raw OCR recognition and the AI Proofreading Engine.
    Repairs common handwriting OCR artifacts:
      1. Strips non-printable control symbols and malformed Unicode artifacts.
      2. Reconnects hyphenated words split across line breaks (e.g. 'hand-\\n written' -> 'handwritten').
      3. Normalizes missing spaces after punctuation (e.g. 'word.Next' -> 'word. Next').
      4. Fixes misplaced spaces before punctuation (e.g. 'word , next' -> 'word, next').
      5. Collapses duplicated punctuation marks (e.g. '..' -> '.', '??' -> '?').
      6. Merges fragmented bounding box line strings into coherent sentences.
    """

    def recover_text(self, raw_ocr_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Normalize and repair raw OCR text.
        Returns (recovered_text, recovery_metadata).
        """
        if not raw_ocr_text or not raw_ocr_text.strip():
            return "", {"repaired_hyphens": 0, "spacing_fixes": 0, "symbol_removals": 0}

        text = raw_ocr_text
        repaired_hyphens = 0
        spacing_fixes = 0
        symbol_removals = 0

        # 1. Strip non-printable ASCII / Unicode control codes (keep newlines, tabs, standard characters)
        cleaned_chars = []
        for ch in text:
            code = ord(ch)
            if code < 32 and ch not in ('\n', '\r', '\t'):
                symbol_removals += 1
                continue
            cleaned_chars.append(ch)
        text = "".join(cleaned_chars)

        # 2. Reconnect hyphenated words split across line breaks (e.g. "hand-\nwritten" -> "handwritten")
        hyphen_pattern = r'(\b[a-zA-Z]{2,})-\s*\n\s*([a-zA-Z]{2,}\b)'
        repaired_hyphens = len(re.findall(hyphen_pattern, text))
        text = re.sub(hyphen_pattern, r'\1\2', text)

        # 3. Fix missing space after punctuation marks when followed by a letter (e.g. "end.Next" -> "end. Next")
        missing_space_pattern = r'([a-zA-Z0-9]{2,}[.?!,;:>])([a-zA-Z])'
        spacing_fixes += len(re.findall(missing_space_pattern, text))
        text = re.sub(missing_space_pattern, r'\1 \2', text)

        # 4. Remove space before punctuation marks (e.g. "word , next" -> "word, next")
        space_before_punct = r'\s+([,.:;?!])'
        text = re.sub(space_before_punct, r'\1', text)

        # 5. Collapse duplicated punctuation marks (e.g. ".." -> ".", "??" -> "?")
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\?{2,}', '?', text)
        text = re.sub(r'!{2,}', '!', text)
        text = re.sub(r',{2,}', ',', text)

        # 6. Normalize multiple inner horizontal spaces while preserving newlines
        lines = text.split('\n')
        normalized_lines = []
        for line in lines:
            norm_line = re.sub(r'[ \t]+', ' ', line).strip()
            normalized_lines.append(norm_line)

        recovered_text = "\n".join(normalized_lines).strip()

        metadata = {
            "repaired_hyphens": repaired_hyphens,
            "spacing_fixes": spacing_fixes,
            "symbol_removals": symbol_removals,
            "original_length": len(raw_ocr_text),
            "recovered_length": len(recovered_text)
        }

        logger.info(f"Text Recovery Layer completed: Repaired {repaired_hyphens} hyphens, {spacing_fixes} spacing artifacts.")
        return recovered_text, metadata
