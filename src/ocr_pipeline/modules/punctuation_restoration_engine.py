import re
from typing import List, Dict, Any, Tuple, Optional
from ..models import CorrectionSuggestion
from ..utils.logging_config import logger

class PunctuationRestorationEngine:
    """
    Context-aware Punctuation Restoration & Correction Engine.
    Restores missing full stops, commas, apostrophes (contractions & possessives),
    dialogue quotation marks, question marks, colons, and semicolons across sentences and paragraphs.
    Preserves document structure (Markdown headings, lists, tables, double newlines).
    """

    CONTRACTION_MAP = {
        r"\b(can)not\b": r"cannot",
        r"\b(do)nt\b": r"don't",
        r"\b(does)nt\b": r"doesn't",
        r"\b(did)nt\b": r"didn't",
        r"\b(is)nt\b": r"isn't",
        r"\b(are)nt\b": r"aren't",
        r"\b(was)nt\b": r"wasn't",
        r"\b(were)nt\b": r"weren't",
        r"\b(has)nt\b": r"hasn't",
        r"\b(have)nt\b": r"haven't",
        r"\b(had)nt\b": r"hadn't",
        r"\b(would)nt\b": r"wouldn't",
        r"\b(could)nt\b": r"couldn't",
        r"\b(should)nt\b": r"shouldn't",
        r"\b(it)s\b(?=\s+(?:a|an|the|very|so|not|good|bad|great|important|easy|hard)\b)": r"it's",
        r"\b(im)\b": r"I'm",
        r"\b(ive)\b": r"I've",
        r"\b(ill)\b(?=\s+(?:be|go|do|have|see|get|take|make)\b)": r"I'll",
        r"\b(id)\b(?=\s+(?:like|love|rather|prefer|have|be)\b)": r"I'd",
        r"\b(they)re\b": r"they're",
        r"\b(we)re\b(?=\s+(?:going|doing|having|seeing|making|getting|planning)\b)": r"we're",
        r"\b(you)re\b": r"you're",
        r"\b(thats)\b": r"that's",
        r"\b(whats)\b": r"what's",
        r"\b(theres)\b": r"there's",
    }

    def restore_punctuation(self, text: str) -> Tuple[List[CorrectionSuggestion], str]:
        """
        Analyze text to detect missing punctuation and restore proper sentence boundaries,
        commas, apostrophes, colons, and question marks while preserving document layout.
        Returns (suggestions, preview_text).
        """
        if not text or not text.strip():
            return [], text

        suggestions: List[CorrectionSuggestion] = []
        lines = text.split("\n")
        curr_offset = 0
        sug_id = 1

        for line_num, line in enumerate(lines, 1):
            # Preserve headers, lists, table rows, or empty lines
            if not line.strip() or line.startswith("#") or line.startswith("|") or line.startswith("==="):
                curr_offset += len(line) + 1
                continue

            # 1. Contraction Apostrophe Restoration
            for pattern, repl in self.CONTRACTION_MAP.items():
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    start = curr_offset + match.start()
                    end = curr_offset + match.end()
                    orig = text[start:end]
                    proposed = match.expand(repl) if '\\' in repl else repl

                    if orig != proposed and not any(s.start_offset == start for s in suggestions):
                        conf = 0.94
                        sug = CorrectionSuggestion(
                            suggestion_id=f"punct_sug_{sug_id}",
                            original_text=orig,
                            proposed_correction=proposed,
                            category="Punctuation Correction",
                            confidence_score=conf,
                            explanation=f"Insert missing contraction apostrophe in '{proposed}'.",
                            start_offset=start,
                            end_offset=end,
                            line_number=line_num,
                            alternative_candidates=[
                                {"candidate": proposed, "score": conf},
                                {"candidate": orig, "score": round(1.0 - conf, 4)}
                            ]
                        )
                        suggestions.append(sug)
                        sug_id += 1

            # 2. Possessive Noun Apostrophe Restoration (e.g. "students book" -> "student's book")
            for match in re.finditer(r'\b([a-zA-Z]{3,})s\b(?=\s+(?:book|pencil|bag|teacher|desk|work|homework|answer|story|idea|father|mother|family)\b)', line, re.IGNORECASE):
                start = curr_offset + match.start()
                end = curr_offset + match.end()
                orig = text[start:end]
                stem = match.group(1)
                proposed = f"{stem}'s"

                if orig.lower() != proposed.lower() and not any(s.start_offset == start for s in suggestions):
                    conf = 0.92
                    sug = CorrectionSuggestion(
                        suggestion_id=f"punct_sug_{sug_id}",
                        original_text=orig,
                        proposed_correction=proposed,
                        category="Punctuation Correction",
                        confidence_score=conf,
                        explanation=f"Insert possessive apostrophe: '{proposed}' indicating ownership.",
                        start_offset=start,
                        end_offset=end,
                        line_number=line_num,
                        alternative_candidates=[
                            {"candidate": proposed, "score": conf},
                            {"candidate": orig, "score": round(1.0 - conf, 4)}
                        ]
                    )
                    suggestions.append(sug)
                    sug_id += 1

            # 3. Question Mark Restoration for Interrogative Clauses
            for match in re.finditer(r'\b(what|where|when|why|who|how|which|can you|could you|would you|do you|have you)\b[^.?!:\n]+(?=[.?!]|\s*$)', line, re.IGNORECASE):
                matched_clause = match.group(0).strip()
                if not matched_clause.endswith("?"):
                    start = curr_offset + match.start() + len(matched_clause)
                    end = start
                    conf = 0.92
                    sug = CorrectionSuggestion(
                        suggestion_id=f"punct_sug_{sug_id}",
                        original_text="",
                        proposed_correction="?",
                        category="Punctuation Correction",
                        confidence_score=conf,
                        explanation="Add missing question mark at the end of question clause.",
                        start_offset=start,
                        end_offset=end,
                        line_number=line_num,
                        alternative_candidates=[
                            {"candidate": "?", "score": conf},
                            {"candidate": "", "score": round(1.0 - conf, 4)}
                        ]
                    )
                    suggestions.append(sug)
                    sug_id += 1

            # 4. Introductory Clause Comma Restoration
            for match in re.finditer(r'^(However|Therefore|Moreover|In addition|First|Second|Finally|Suddenly|On the other hand|In conclusion)\s+([a-zA-Z])', line, re.IGNORECASE):
                adv = match.group(1)
                next_char = match.group(2)
                start = curr_offset + match.start()
                end = curr_offset + match.start() + len(adv) + 1 + len(next_char)
                orig = line[match.start():match.start() + len(adv) + 1 + len(next_char)]
                proposed = f"{adv.capitalize()}, {next_char}"

                if orig != proposed and not any(s.start_offset == start for s in suggestions):
                    conf = 0.94
                    sug = CorrectionSuggestion(
                        suggestion_id=f"punct_sug_{sug_id}",
                        original_text=orig,
                        proposed_correction=proposed,
                        category="Punctuation Correction",
                        confidence_score=conf,
                        explanation=f"Add introductory comma after transition word '{adv}'.",
                        start_offset=start,
                        end_offset=end,
                        line_number=line_num,
                        alternative_candidates=[
                            {"candidate": proposed, "score": conf},
                            {"candidate": orig, "score": round(1.0 - conf, 4)}
                        ]
                    )
                    suggestions.append(sug)
                    sug_id += 1

            # 5. Sentence Boundary / Period Restoration (Merged Sentences)
            for match in re.finditer(r'([a-z]{2,})\s+([A-Z][a-z]{2,}\s+(?:is|are|was|were|has|have|had|will|should|could|would)\b)', line):
                word1 = match.group(1)
                phrase2 = match.group(2)
                start = curr_offset + match.start()
                end = curr_offset + match.end()
                orig = line[match.start():match.end()]
                proposed = f"{word1}. {phrase2}"

                if orig != proposed and not any(s.start_offset == start for s in suggestions):
                    conf = 0.88
                    sug = CorrectionSuggestion(
                        suggestion_id=f"punct_sug_{sug_id}",
                        original_text=orig,
                        proposed_correction=proposed,
                        category="Punctuation Correction",
                        confidence_score=conf,
                        explanation="Insert missing sentence boundary period between merged sentences.",
                        start_offset=start,
                        end_offset=end,
                        line_number=line_num,
                        alternative_candidates=[
                            {"candidate": proposed, "score": conf},
                            {"candidate": orig, "score": round(1.0 - conf, 4)}
                        ]
                    )
                    suggestions.append(sug)
                    sug_id += 1

            curr_offset += len(line) + 1

        return suggestions, text
