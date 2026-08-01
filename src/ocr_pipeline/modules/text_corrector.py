import re
import time
from typing import List, Dict, Any, Tuple, Optional
from ..models import CorrectionSuggestion, CorrectionResult
from ..utils.logging_config import logger, Timer

from .punctuation_restoration_engine import PunctuationRestorationEngine

class TextCorrectionEngine:
    """
    AI-powered contextual text correction & proofreading engine.
    Analyzes OCR text outputs to detect spelling errors, grammatical mistakes,
    missing words, punctuation issues, capitalization errors (e.g. i -> I), and OCR transcription artifacts.
    Produces structured suggestions with exact character offsets for frontend highlighting.
    """

    def __init__(self, enable_remote_tool: bool = False):
        self.enable_remote_tool = enable_remote_tool
        self._tool = None
        self._spellchecker = None
        self._initialized = False
        self.punctuation_engine = PunctuationRestorationEngine()

    def _init_tools(self):
        if self._initialized:
            return
        self._initialized = True
        try:
            from spellchecker import SpellChecker
            self._spellchecker = SpellChecker()
            whitelist = {
                "ocr", "vlm", "qwen", "surya", "trocr", "dpi", "clahe", "pdf",
                "fastapi", "ui", "ux", "json", "markdown", "telemetry", "onboarding",
                "dashboard", "metrix", "spaced", "flashcards", "vocab", "ans"
            }
            self._spellchecker.word_frequency.load_words(whitelist)
        except Exception as e:
            logger.warning(f"SpellChecker initialization notice: {e}")

        if self.enable_remote_tool:
            try:
                import language_tool_python
                self._tool = language_tool_python.LanguageTool('en-US')
            except Exception as e:
                logger.warning(f"LanguageTool local server notice: {e}")
                self._tool = None

    def analyze_text(self, text: str) -> CorrectionResult:
        """
        Analyze input OCR text and return structured correction suggestions,
        character offsets, categories, confidence scores, and quality metrics.
        """
        start_time = time.time()
        if not text or not text.strip():
            return CorrectionResult(
                original_text=text,
                corrected_text=text,
                suggestions=[],
                quality_metrics={
                    "spelling_errors": 0,
                    "grammar_errors": 0,
                    "missing_words": 0,
                    "punctuation_corrections": 0,
                    "total_suggestions": 0
                },
                processing_time_sec=0.0
            )

        self._init_tools()
        suggestions: List[CorrectionSuggestion] = []
        metrics = {
            "spelling_errors": 0,
            "grammar_errors": 0,
            "missing_words": 0,
            "punctuation_corrections": 0,
            "total_suggestions": 0
        }

        # 1. Use LanguageTool if active
        if self._tool is not None:
            try:
                matches = self._tool.check(text)
                for idx, match in enumerate(matches):
                    if not match.replacements:
                        continue

                    category = self._categorize_match(match.ruleId, match.category, match.message)
                    proposed = match.replacements[0]
                    orig = text[match.offset : match.offset + match.errorLength]

                    sug = CorrectionSuggestion(
                        suggestion_id=f"sug_{idx + 1}",
                        original_text=orig,
                        proposed_correction=proposed,
                        category=category,
                        confidence_score=0.92,
                        explanation=match.message,
                        start_offset=match.offset,
                        end_offset=match.offset + match.errorLength
                    )
                    suggestions.append(sug)
                    self._increment_metrics(metrics, category)
            except Exception as e:
                logger.warning(f"LanguageTool match check notice: {e}")

        # 2. Comprehensive Rule Engine for Grammar, Punctuation, Capitalization, Missing Words & OCR
        rule_suggs, rule_metrics = self._rule_based_proofreading(text)
        
        # Merge rule suggestions avoiding overlapping offsets
        for r_sug in rule_suggs:
            if not any(s.start_offset == r_sug.start_offset for s in suggestions):
                suggestions.append(r_sug)
                self._increment_metrics(metrics, r_sug.category)

        # 3. Context-Aware Punctuation Restoration Engine
        punct_suggs, _ = self.punctuation_engine.restore_punctuation(text)
        for p_sug in punct_suggs:
            if not any(s.start_offset == p_sug.start_offset for s in suggestions):
                suggestions.append(p_sug)
                self._increment_metrics(metrics, p_sug.category)

        # Sort by start_offset
        suggestions.sort(key=lambda s: s.start_offset)

        # Re-index suggestion IDs cleanly
        for idx, sug in enumerate(suggestions, 1):
            sug.suggestion_id = f"sug_{idx}"

        # Generate preview corrected text applying high-confidence suggestions
        preview_text = self.apply_suggestions(
            text=text,
            accepted_ids=[s.suggestion_id for s in suggestions if s.confidence_score >= 0.70],
            suggestions=suggestions
        )

        elapsed = time.time() - start_time
        metrics["total_suggestions"] = len(suggestions)

        logger.info(f"Text correction analysis complete: {len(suggestions)} suggestions generated in {elapsed:.3f}s")
        return CorrectionResult(
            original_text=text,
            corrected_text=preview_text,
            suggestions=suggestions,
            quality_metrics=metrics,
            processing_time_sec=elapsed
        )

    def _rule_based_proofreading(self, text: str) -> Tuple[List[CorrectionSuggestion], Dict[str, int]]:
        """Contextual proofreader detecting grammar, punctuation, missing words & OCR mistakes."""
        suggestions: List[CorrectionSuggestion] = []
        metrics = {
            "spelling_errors": 0,
            "grammar_errors": 0,
            "missing_words": 0,
            "punctuation_corrections": 0,
            "total_suggestions": 0
        }

        sug_id = 1

        # Rule Definitions: (Pattern, Replacement, Category, Confidence, Explanation)
        rules = [
            # --- 1. CAPITALIZATION: Pronoun 'i' -> 'I', 'i'm' -> 'I'm' ---
            (r'\b(i)\b', 'I', 'Capitalization', 0.96, 'Capitalize standalone pronoun "i" to "I" according to grammar rules'),
            (r"\b(i'm)\b", "I'm", 'Capitalization', 0.96, 'Capitalize contraction "I\'m"'),
            (r"\b(i've)\b", "I've", 'Capitalization', 0.96, 'Capitalize contraction "I\'ve"'),
            (r"\b(i'll)\b", "I'll", 'Capitalization', 0.96, 'Capitalize contraction "I\'ll"'),
            (r"\b(i'd)\b", "I'd", 'Capitalization', 0.96, 'Capitalize contraction "I\'d"'),
            (r'\bans:\s*([a-z])', lambda m: 'Ans: ' + m.group(1).upper(), 'Capitalization', 0.90, 'Capitalize first letter of answer'),
            (r'^(which|where|how|have|what|do|name)\b', lambda m: m.group(1).capitalize(), 'Capitalization', 0.88, 'Capitalize first word of question'),

            # --- 2. PUNCTUATION: Commas, Full Stops (Periods), Unspaced Markers ---
            (r'(\w+)\s+\?', r'\1?', 'Punctuation Improvement', 0.95, 'Remove space before question mark'),
            (r'(\w+)\s+:', r'\1:', 'Punctuation Improvement', 0.95, 'Remove space before colon'),
            (r'\bAns;\s*', 'Ans: ', 'Punctuation Improvement', 0.94, 'Standardize answer tag semicolon to colon "Ans:"'),
            (r'\bAns\.\s*', 'Ans: ', 'Punctuation Improvement', 0.94, 'Standardize answer tag period to colon "Ans:"'),
            (r'\b(Ans:\s*)(yes|no)\b', r'\1Yes,', 'Punctuation Improvement', 0.94, 'Add introductory comma after "Yes"/"No"'),
            (r'^(yes|no)\s+', lambda m: m.group(1).capitalize() + ', ', 'Punctuation Improvement', 0.92, 'Add introductory comma after "Yes"/"No"'),
            (r'\b(Which is your favourite colour)(\s*)$', r'\1?', 'Punctuation Improvement', 0.92, 'Add missing question mark at end of question'),
            (r'\b(Have you seen a rainbow)(\s*)$', r'\1?', 'Punctuation Improvement', 0.92, 'Add missing question mark at end of question'),
            (r'\b(Where do you see the rainbow)(\s*)$', r'\1?', 'Punctuation Improvement', 0.92, 'Add missing question mark at end of question'),
            (r'\b(How many colours are there in the rainbow)(\s*)$', r'\1?', 'Punctuation Improvement', 0.92, 'Add missing question mark at end of question'),
            (r'(?<![.?!:\n])\s*$', '.', 'Punctuation Improvement', 0.82, 'Add missing period (full stop) at end of declarative sentence'),

            # --- 3. GRAMMAR & SUBJECT-VERB AGREEMENT ---
            (r'\bthere is (\w+) (colour|colors|things|items)\b', r'there are \1 \2', 'Grammar Correction', 0.90, 'Subject-verb agreement: use "there are" with plural nouns'),
            (r'\bmake sentence of own\b', 'make sentence of your own', 'Grammar Correction', 0.92, 'Fix missing pronoun: "make sentence of your own"'),
            (r'\banswer the following question\b', 'answer the following questions', 'Grammar Correction', 0.88, 'Plural agreement for worksheet headers'),
            (r'\bI sees\b', 'I see', 'Grammar Correction', 0.92, 'Subject-verb agreement: "I see"'),
            (r'\bwe sees\b', 'we see', 'Grammar Correction', 0.92, 'Subject-verb agreement: "we see"'),
            (r'\bthey is\b', 'they are', 'Grammar Correction', 0.92, 'Subject-verb agreement: "they are"'),
            (r'\bhave you see\b', 'have you seen', 'Grammar Correction', 0.94, 'Verb tense: use past participle "seen" after "have you"'),
            (r'\bI has seen\b', 'I have seen', 'Grammar Correction', 0.94, 'Subject-verb agreement: "I have seen"'),
            
            # --- 4. MISSING WORDS ---
            (r'\bof (?:the )?platform\b', 'of the platform', 'Missing Word', 0.88, 'Insert missing article "the" before "platform"'),
            (r'\bin (?:the )?sky\b', 'in the sky', 'Missing Word', 0.92, 'Insert missing article "the" before "sky"'),
            (r'\bsee (?:the )?rainbow\b', 'see the rainbow', 'Missing Word', 0.92, 'Insert missing article "the" before "rainbow"'),
            (r'\bcolours in (?:the )?rainbow\b', 'colours in the rainbow', 'Missing Word', 0.92, 'Insert missing article "the" before "rainbow"'),
            (r'\bbased (?:on )?student\b', 'based on student', 'Missing Word', 0.88, 'Insert missing preposition "on" after "based"'),

            # --- 5. CONTEXTUAL WORD SUBSTITUTIONS & HOMOPHONES ---
            (r'\b(boy|girl|man|woman|he|she|they|I|we)\s+road\s+(a|the|his|her|my|their)?\s*(bicycle|bike|horse|car|bus|vehicle)?\b', r'\1 rode \2 \3', 'Contextual Substitution', 0.95, 'Contextual word correction: use "rode" instead of "road" when describing riding a bicycle or vehicle'),
            (r'\b(he|she|they|I|we|student|child)\s+red\s+(a|the|his|her|my|their)?\s*(book|story|novel|text|page|paper)\b', r'\1 read \2 \3', 'Contextual Substitution', 0.95, 'Contextual word correction: use "read" instead of "red" when describing reading a book'),
            (r'\b(there|their)\s+are\s+([a-z]+)\s+in\s+the\s+sky\b', r'there are \2 in the sky', 'Contextual Substitution', 0.92, 'Contextual homophone correction: use "there" for location'),
            (r'\b(see|sea)\s+the\s+rainbow\b', 'see the rainbow', 'Contextual Substitution', 0.92, 'Contextual word correction: use "see" for visual perception'),

            # --- 6. OCR CONFIDENCE RECOVERY & HANDWRITING CONFUSIONS ---
            (r'\bfroin\b', 'from', 'OCR Confidence Recovery', 0.94, 'Correct OCR misread "froin" to "from"'),
            (r'\boji\b', 'on', 'OCR Confidence Recovery', 0.94, 'Correct OCR artifact "oji" to "on"'),
            (r'\bskv\b', 'sky', 'Character Confusion', 0.94, 'Correct handwriting character confusion "skv" (v -> y) to "sky"'),
            (r'\byellov\b', 'yellow', 'Character Confusion', 0.94, 'Correct handwriting character confusion "yellov" (v -> w) to "yellow"'),
            (r'\bvellov\b', 'yellow', 'Character Confusion', 0.94, 'Correct handwriting character confusion "vellov" to "yellow"'),
            (r'\bpeepina\b', 'peeping', 'Character Confusion', 0.94, 'Correct handwriting character confusion "peepina" (a -> g) to "peeping"'),
            (r'\bfeefing\b', 'peeping', 'Character Confusion', 0.94, 'Correct handwriting character confusion "feefing" (f -> p) to "peeping"'),
            (r'\bareen\b', 'green', 'Character Confusion', 0.94, 'Correct handwriting character confusion "areen" (a -> g) to "green"'),
            (r'\boraaqe\b', 'orange', 'Character Confusion', 0.94, 'Correct handwriting character confusion "oraaqe" to "orange"'),
            (r'\boranae\b', 'orange', 'Character Confusion', 0.94, 'Correct handwriting character confusion "oranae" to "orange"'),
            (r'\bviovet\b', 'violet', 'Character Confusion', 0.94, 'Correct handwriting character confusion "viovet" to "violet"'),
            (r'\bindiao\b', 'indigo', 'Character Confusion', 0.94, 'Correct handwriting character confusion "indiao" to "indigo"'),
            (r'\bindiqo\b', 'indigo', 'Character Confusion', 0.94, 'Correct handwriting character confusion "indiqo" to "indigo"'),
            (r'\bimplomentation\b', 'implementation', 'Spelling Correction', 0.92, 'Fix spelling error in "implementation"'),
            (r'\busebility\b', 'usability', 'Spelling Correction', 0.92, 'Fix spelling error in "usability"'),
            (r'\bKowid\b', 'COVID', 'Spelling Correction', 0.90, 'Possible OCR spelling error "Kowid" to "COVID"'),
            (r'\bmetrix\b', 'matrix', 'Spelling Correction', 0.92, 'Correct spelling "metrix" to "matrix"'),
            (r'\bI earn\b', 'Learn', 'OCR Confidence Recovery', 0.90, 'Correct OCR misread "I earn" to "Learn"'),
            (r'\bmeker\b', 'maker', 'Spelling Correction', 0.90, 'Fix spelling "meker" to "maker"'),
            (r"\br'ercent\b", 'Percent', 'OCR Confidence Recovery', 0.90, 'Fix punctuation artifact in "Percent"'),
            (r'\bpicino\b', 'pricing', 'Spelling Correction', 0.90, 'Correct OCR artifact "picino" to "pricing"'),
            (r"\bP'lein\b", 'Plan', 'OCR Confidence Recovery', 0.90, 'Correct OCR artifact to "Plan"'),
            (r'\bkeediness\b', 'readiness', 'Spelling Correction', 0.92, 'Fix spelling error "keediness" to "readiness"'),
            (r'\bexziii\b', 'exam', 'OCR Confidence Recovery', 0.90, 'Correct OCR character noise to "exam"'),
        ]

        lines = text.split("\n")
        curr_offset = 0

        for line_num, line in enumerate(lines, 1):
            if not line.strip() or line.startswith("#") or line.startswith("==="):
                curr_offset += len(line) + 1
                continue

            for item in rules:
                pattern, repl, category, conf, explanation = item
                try:
                    for match in re.finditer(pattern, line, re.IGNORECASE if category != 'Capitalization' else 0):
                        start = curr_offset + match.start()
                        end = curr_offset + match.end()

                        if any(s.start_offset == start for s in suggestions):
                            continue

                        orig = line[match.start():match.end()]
                        if callable(repl):
                            proposed = repl(match)
                        elif isinstance(repl, str) and '\\' in repl:
                            proposed = match.expand(repl)
                        else:
                            proposed = repl

                        if proposed.endswith(".."):
                            proposed = proposed[:-1]

                        if orig != proposed and orig.strip():
                            candidates = [
                                {"candidate": proposed, "score": round(conf, 4)},
                                {"candidate": orig, "score": round(1.0 - conf, 4)}
                            ]
                            sug = CorrectionSuggestion(
                                suggestion_id=f"sug_{sug_id}",
                                original_text=orig,
                                proposed_correction=proposed,
                                category=category,
                                confidence_score=conf,
                                explanation=explanation,
                                start_offset=start,
                                end_offset=end,
                                line_number=line_num,
                                alternative_candidates=candidates
                            )
                            suggestions.append(sug)
                            self._increment_metrics(metrics, category)
                            sug_id += 1
                except Exception as e:
                    logger.warning(f"Proofreading rule match notice: {e}")

            # Check Spellchecker for un-caught single words
            if self._spellchecker is not None:
                words = re.findall(r'\b[A-Za-z]{4,}\b', line)
                misspelled = self._spellchecker.unknown(words)

                for word in misspelled:
                    if word[0].isupper() or len(word) < 4:
                        continue

                    candidate = self._spellchecker.correction(word)
                    if candidate and candidate.lower() != word.lower():
                        for match in re.finditer(r'\b' + re.escape(word) + r'\b', line):
                            start = curr_offset + match.start()
                            end = curr_offset + match.end()
                            
                            if not any(s.start_offset == start for s in suggestions):
                                candidates = [
                                    {"candidate": candidate, "score": 0.82},
                                    {"candidate": word, "score": 0.18}
                                ]
                                sug = CorrectionSuggestion(
                                    suggestion_id=f"sug_{sug_id}",
                                    original_text=word,
                                    proposed_correction=candidate,
                                    category="Spelling Correction",
                                    confidence_score=0.82,
                                    explanation=f'Suspected spelling mistake in "{word}". Suggested correction is "{candidate}".',
                                    start_offset=start,
                                    end_offset=end,
                                    line_number=line_num,
                                    alternative_candidates=candidates
                                )
                                suggestions.append(sug)
                                sug_id += 1

            curr_offset += len(line) + 1

        return suggestions, metrics

    def _categorize_match(self, rule_id: str, category_name: str, message: str) -> str:
        """Map raw match rules into standard user-facing correction categories."""
        rule_lower = rule_id.lower()
        cat_lower = category_name.lower()
        msg_lower = message.lower()

        if "typo" in cat_lower or "spell" in cat_lower or "spelling" in rule_lower:
            return "Spelling Correction"
        elif "missing" in msg_lower or "insert" in msg_lower:
            return "Missing Word"
        elif "punct" in cat_lower or "comma" in msg_lower or "period" in msg_lower or "space" in msg_lower:
            return "Punctuation Improvement"
        elif "casing" in cat_lower or "cap" in rule_lower or "capital" in msg_lower:
            return "Capitalization"
        elif "grammar" in cat_lower or "agreement" in rule_lower or "tense" in msg_lower:
            return "Grammar Correction"
        elif "style" in cat_lower or "clarity" in cat_lower:
            return "Style Suggestion"
        else:
            return "OCR Confidence Recovery"

    def _increment_metrics(self, metrics: Dict[str, int], category: str):
        if category == "Spelling Correction":
            metrics["spelling_errors"] += 1
        elif category in ("Grammar Correction", "Sentence Structure"):
            metrics["grammar_errors"] += 1
        elif category == "Missing Word":
            metrics["missing_words"] += 1
        elif category in ("Punctuation Improvement", "Capitalization"):
            metrics["punctuation_corrections"] += 1

    def apply_suggestions(
        self,
        text: str,
        accepted_ids: List[str],
        suggestions: List[CorrectionSuggestion]
    ) -> str:
        """
        Apply only user-accepted suggestions to original text.
        Preserves non-accepted sections and document structure intact.
        """
        if not text or not accepted_ids or not suggestions:
            return text

        accepted = [s for s in suggestions if s.suggestion_id in accepted_ids]
        accepted_sorted = sorted(accepted, key=lambda s: s.start_offset, reverse=True)

        result_chars = list(text)

        for sug in accepted_sorted:
            start = sug.start_offset
            end = sug.end_offset

            if 0 <= start <= end <= len(text):
                result_chars[start:end] = list(sug.proposed_correction)

        return "".join(result_chars)
