import os
import re
import json
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from ..models import Flashcard, FlashcardDeck
from ..utils.logging_config import logger, Timer
from .vocabulary_engine import VocabularyLearningEngine

class ChildFriendlyLexicalEngine:
    """
    Intelligent child-friendly lexical generator.
    Produces age-appropriate, children's dictionary definitions, natural 8-20 word example sentences,
    part-of-speech tags, synonyms, antonyms, and phonetic hints for target vocabulary terms.
    Skips non-dictionary items like proper nouns, numbers, URLs, and pure functional grammar edits.
    """

    FUNCTIONAL_GRAMMAR_WORDS = {
        "a", "an", "the", "is", "are", "am", "was", "were", "be", "been", "being",
        "has", "have", "had", "do", "does", "did", "and", "but", "or", "so", "if",
        "in", "on", "at", "to", "for", "with", "by", "from", "of", "up", "out",
        "it", "its", "this", "that", "these", "those", "they", "them", "their", "we", "us", "our"
    }

    CHILD_DICTIONARY: Dict[str, Dict[str, Any]] = {
        "beautiful": {
            "pos": "adjective",
            "child_def": "Very pleasing to look at; something that looks lovely or attractive.",
            "example": "The sunset over the mountains was beautiful.",
            "synonyms": ["lovely", "pretty", "attractive"],
            "antonyms": ["ugly", "unattractive"],
            "phonetic": "/ˈbjuː.tɪ.fəl/"
        },
        "adventure": {
            "pos": "noun",
            "child_def": "An exciting experience or journey where something new or unusual happens.",
            "example": "Our weekend camping trip turned into an exciting adventure.",
            "synonyms": ["journey", "trip", "exploration"],
            "antonyms": ["routine", "boredom"],
            "phonetic": "/ədˈven.tʃər/"
        },
        "generous": {
            "pos": "adjective",
            "child_def": "Someone who likes to help others and willingly shares what they have.",
            "example": "The generous girl shared her delicious lunch with her classmate.",
            "synonyms": ["kind", "giving", "helpful"],
            "antonyms": ["selfish", "greedy"],
            "phonetic": "/ˈdʒen.ər.əs/"
        },
        "receive": {
            "pos": "verb",
            "child_def": "To get or accept something that is given, sent, or awarded to you.",
            "example": "Maya was thrilled to receive a special prize for her story.",
            "synonyms": ["get", "accept", "obtain"],
            "antonyms": ["give", "send"],
            "phonetic": "/rɪˈsiːv/"
        },
        "received": {
            "pos": "verb",
            "child_def": "To get or accept something that was given, sent, or awarded to you.",
            "example": "The student received highest honors for her hard work.",
            "synonyms": ["got", "accepted", "obtained"],
            "antonyms": ["gave", "sent"],
            "phonetic": "/rɪˈsiːvd/"
        },
        "incredible": {
            "pos": "adjective",
            "child_def": "So amazing or extraordinary that it is hard to believe.",
            "example": "The magician performed an incredible trick that amazed the audience.",
            "synonyms": ["amazing", "wonderful", "extraordinary"],
            "antonyms": ["ordinary", "believable"],
            "phonetic": "/ɪnˈkred.ə.bəl/"
        },
        "accommodation": {
            "pos": "noun",
            "child_def": "A comfortable place to live, stay, or sleep, such as a house or hotel room.",
            "example": "Our family booked comfortable accommodation near the beach for vacation.",
            "synonyms": ["housing", "lodging", "shelter"],
            "antonyms": [],
            "phonetic": "/əˌkɒm.əˈdeɪ.ʃən/"
        },
        "environment": {
            "pos": "noun",
            "child_def": "The natural world of land, water, air, and living things around us.",
            "example": "Planting green trees helps keep our natural environment clean and healthy.",
            "synonyms": ["nature", "surroundings", "habitat"],
            "antonyms": [],
            "phonetic": "/ɪnˈvaɪ.rən.mənt/"
        },
        "definitely": {
            "pos": "adverb",
            "child_def": "Without any doubt at all; completely sure or certain.",
            "example": "We will definitely visit the science museum during our class trip.",
            "synonyms": ["surely", "certainly", "clearly"],
            "antonyms": ["maybe", "doubtfully"],
            "phonetic": "/ˈdef.ɪ.nət.li/"
        },
        "necessary": {
            "pos": "adjective",
            "child_def": "Something that is needed or essential to complete a task.",
            "example": "Drinking plenty of water is necessary for staying healthy during sports.",
            "synonyms": ["needed", "essential", "required"],
            "antonyms": ["unnecessary", "optional"],
            "phonetic": "/ˈnes.ə.ser.i/"
        },
        "separate": {
            "pos": "adjective",
            "child_def": "Kept apart from other things; not joined or connected together.",
            "example": "Please put your clean clothes into separate wooden drawers.",
            "synonyms": ["apart", "distinct", "individual"],
            "antonyms": ["joined", "together"],
            "phonetic": "/ˈsep.ər.ət/"
        },
        "embarrass": {
            "pos": "verb",
            "child_def": "To make someone feel shy, awkward, or self-conscious in front of others.",
            "example": "He did not want to embarrass his friend during the game.",
            "synonyms": ["fluster", "shame", "upset"],
            "antonyms": ["comfort", "reassure"],
            "phonetic": "/ɪmˈbær.əs/"
        },
        "occurrence": {
            "pos": "noun",
            "child_def": "An event or incident that happens in a particular time or place.",
            "example": "Seeing a shooting star is a rare and exciting occurrence.",
            "synonyms": ["event", "incident", "happening"],
            "antonyms": [],
            "phonetic": "/əˈkʌr.əns/"
        },
        "government": {
            "pos": "noun",
            "child_def": "The group of leaders who make laws and guide a country or city.",
            "example": "The local government built a brand new public park for children.",
            "synonyms": ["leadership", "authority", "administration"],
            "antonyms": [],
            "phonetic": "/ˈɡʌv.ən.mənt/"
        },
        "knowledge": {
            "pos": "noun",
            "child_def": "Information, facts, and understanding gained through learning and reading.",
            "example": "Reading good books every day expands your knowledge of the world.",
            "synonyms": ["understanding", "learning", "wisdom"],
            "antonyms": ["ignorance"],
            "phonetic": "/ˈnɒl.ɪdʒ/"
        },
        "development": {
            "pos": "noun",
            "child_def": "The process of growing, learning, or improving over time.",
            "example": "Regular practice is important for the skill development of young artists.",
            "synonyms": ["growth", "progress", "improvement"],
            "antonyms": ["decline"],
            "phonetic": "/dɪˈvel.əp.mənt/"
        },
        "achievement": {
            "pos": "noun",
            "child_def": "Something great that you succeed in doing through hard work and effort.",
            "example": "Winning the spelling bee was a wonderful achievement for the student.",
            "synonyms": ["success", "accomplishment", "triumph"],
            "antonyms": ["failure"],
            "phonetic": "/əˈtʃiːv.mənt/"
        },
        "success": {
            "pos": "noun",
            "child_def": "Reaching a good result or goal that you worked hard for.",
            "example": "Hard work and practice are the keys to school success.",
            "synonyms": ["victory", "achievement", "triumph"],
            "antonyms": ["failure"],
            "phonetic": "/səkˈses/"
        },
        "recommend": {
            "pos": "verb",
            "child_def": "To suggest something to someone because you think it is very good.",
            "example": "I strongly recommend reading this fun storybook to your friends.",
            "synonyms": ["suggest", "advise", "endorse"],
            "antonyms": ["discourage"],
            "phonetic": "/ˌrek.əˈmend/"
        },
        "pronunciation": {
            "pos": "noun",
            "child_def": "The correct way to say or speak a word aloud.",
            "example": "Listening carefully helps you master the correct pronunciation of new words.",
            "synonyms": ["speech", "articulation", "saying"],
            "antonyms": [],
            "phonetic": "/prəˌnʌn.siˈeɪ.ʃən/"
        },
        "independent": {
            "pos": "adjective",
            "child_def": "Able to do things on your own without needing help from others.",
            "example": "She felt proud when she became an independent reader this year.",
            "synonyms": ["self-reliant", "free", "autonomous"],
            "antonyms": ["dependent"],
            "phonetic": "/ˌɪn.dɪˈpen.dənt/"
        },
        "privilege": {
            "pos": "noun",
            "child_def": "A special honor or advantage given to a person or group.",
            "example": "It was a great privilege to lead the school science fair.",
            "synonyms": ["honor", "advantage", "opportunity"],
            "antonyms": [],
            "phonetic": "/ˈprɪv.əl.ɪdʒ/"
        },
        "rhythm": {
            "pos": "noun",
            "child_def": "A regular, repeating pattern of beats, sounds, or musical notes.",
            "example": "The steady rhythm of the drum set kept everyone dancing happily.",
            "synonyms": ["beat", "tempo", "cadence"],
            "antonyms": [],
            "phonetic": "/ˈrɪð.əm/"
        },
        "writing": {
            "pos": "noun",
            "child_def": "The activity of creating words and stories on paper or computers.",
            "example": "Creative writing allows students to express their ideas and imagination.",
            "synonyms": ["script", "text", "authorship"],
            "antonyms": [],
            "phonetic": "/ˈraɪ.tɪŋ/"
        },
        "written": {
            "pos": "adjective",
            "child_def": "Expressed in letters and words on paper rather than spoken aloud.",
            "example": "The teacher gave clear written instructions on the chalkboard.",
            "synonyms": ["printed", "in script", "recorded"],
            "antonyms": ["spoken", "verbal"],
            "phonetic": "/ˈrɪt.ən/"
        },
        "language": {
            "pos": "noun",
            "child_def": "The words and signs that people use to talk and communicate with each other.",
            "example": "Learning a new language opens up exciting opportunities to make friends.",
            "synonyms": ["speech", "tongue", "communication"],
            "antonyms": [],
            "phonetic": "/ˈlæŋ.ɡwɪdʒ/"
        },
        "grammar": {
            "pos": "noun",
            "child_def": "The rules that show how words work together to make correct sentences.",
            "example": "Good grammar makes your stories easy and clear for everyone to read.",
            "synonyms": ["rules", "syntax", "structure"],
            "antonyms": [],
            "phonetic": "/ˈɡræm.ər/"
        },
        "spelling": {
            "pos": "noun",
            "child_def": "Writing or naming the letters of a word in the correct order.",
            "example": "Double-check your essay to fix any small spelling mistakes.",
            "synonyms": ["orthography", "lettering"],
            "antonyms": [],
            "phonetic": "/ˈspel.ɪŋ/"
        },
        "vocabulary": {
            "pos": "noun",
            "child_def": "All the words used and understood by a person in a language.",
            "example": "Reading stories every day helps expand your vocabulary with fun words.",
            "synonyms": ["words", "lexicon", "phrases"],
            "antonyms": [],
            "phonetic": "/vəˈkæb.jə.lər.i/"
        },
        "sentence": {
            "pos": "noun",
            "child_def": "A group of words that expresses a full and complete thought.",
            "example": "Every complete sentence should start with a capital letter.",
            "synonyms": ["phrase", "statement", "clause"],
            "antonyms": [],
            "phonetic": "/ˈsen.təns/"
        },
        "punctuation": {
            "pos": "noun",
            "child_def": "Special marks like periods and commas that make sentences easy to read.",
            "example": "Using proper punctuation helps readers know when to pause.",
            "synonyms": ["marks", "pointing", "symbols"],
            "antonyms": [],
            "phonetic": "/ˌpʌŋk.tʃuˈeɪ.ʃən/"
        },
        "capitalization": {
            "pos": "noun",
            "child_def": "Writing the first letter of a word as a big capital letter.",
            "example": "Capitalization is required for names and at the start of sentences.",
            "synonyms": ["uppercase formatting"],
            "antonyms": ["lowercase"],
            "phonetic": "/ˌkæp.ɪ.təl.aɪˈzeɪ.ʃən/"
        },
        "academic": {
            "pos": "adjective",
            "child_def": "Relating to school, learning, subjects, and studying.",
            "example": "She worked hard to reach her academic goals this term.",
            "synonyms": ["scholarly", "educational", "studious"],
            "antonyms": ["non-academic"],
            "phonetic": "/ˌæk.əˈdem.ɪk/"
        },
        "air": {
            "pos": "noun",
            "child_def": "The invisible gas all around us that we breathe to stay alive.",
            "example": "Fresh mountain air felt cool and clean on her face.",
            "synonyms": ["atmosphere", "breeze", "wind"],
            "antonyms": [],
            "phonetic": "/eər/"
        },
        "water": {
            "pos": "noun",
            "child_def": "The clear liquid that falls as rain and that people drink to live.",
            "example": "Clean drinking water is essential for keeping our bodies healthy.",
            "synonyms": ["liquid", "aqua", "moisture"],
            "antonyms": [],
            "phonetic": "/ˈwɔː.tər/"
        },
        "food": {
            "pos": "noun",
            "child_def": "Things that people and animals eat to get energy and grow.",
            "example": "Eating healthy food gives you energy to run and play.",
            "synonyms": ["nourishment", "meals", "groceries"],
            "antonyms": [],
            "phonetic": "/fuːd/"
        },
        "live": {
            "pos": "verb",
            "child_def": "To stay alive or make your home in a specific place.",
            "example": "Many friendly animals live in the green forest near our town.",
            "synonyms": ["reside", "dwell", "inhabit"],
            "antonyms": ["die"],
            "phonetic": "/lɪv/"
        },
        "give": {
            "pos": "verb",
            "child_def": "To hand over something to someone as a gift or help.",
            "example": "Kind friends give help to classmates who need a hand.",
            "synonyms": ["offer", "provide", "present"],
            "antonyms": ["take", "keep"],
            "phonetic": "/ɡɪv/"
        },
        "gives": {
            "pos": "verb",
            "child_def": "Hands over or provides something helpful to someone else.",
            "example": "Nature gives us fresh air, clean water, and healthy food.",
            "synonyms": ["provides", "offers", "supplies"],
            "antonyms": ["takes"],
            "phonetic": "/ɡɪvz/"
        },
        "provide": {
            "pos": "verb",
            "child_def": "To supply or give something that is needed.",
            "example": "Trees provide shade and clean air for everyone in the park.",
            "synonyms": ["supply", "give", "furnish"],
            "antonyms": ["withhold"],
            "phonetic": "/prəˈvaɪd/"
        },
        "cautious": {
            "pos": "adjective",
            "child_def": "Being very careful to avoid danger, mistakes, or surprises.",
            "example": "The cautious kitten looked around carefully before crossing the quiet room.",
            "synonyms": ["careful", "watchful", "guarded"],
            "antonyms": ["careless", "reckless"],
            "phonetic": "/ˈkɔː.ʃəs/"
        },
        "eager": {
            "pos": "adjective",
            "child_def": "Wanting to do or try something very much with excitement.",
            "example": "The eager students raised their hands happily to answer the question.",
            "synonyms": ["excited", "keen", "enthusiastic"],
            "antonyms": ["uninterested", "reluctant"],
            "phonetic": "/ˈiː.ɡər/"
        },
        "ancient": {
            "pos": "adjective",
            "child_def": "Belonging to a time long ago in history; very old.",
            "example": "The historical museum displays ancient golden coins from long ago.",
            "synonyms": ["old", "historic", "antique"],
            "antonyms": ["modern", "new"],
            "phonetic": "/ˈeɪn.ʃənt/"
        },
        "gigantic": {
            "pos": "adjective",
            "child_def": "Extremely huge, giant, or much larger than normal size.",
            "example": "A gigantic blue whale swam gracefully beside our boat in the ocean.",
            "synonyms": ["huge", "enormous", "giant"],
            "antonyms": ["tiny", "small"],
            "phonetic": "/dʒaɪˈɡæn.tɪk/"
        },
        "fragile": {
            "pos": "adjective",
            "child_def": "Easy to break or damage if not handled with gentle care.",
            "example": "Please carry the glass vase gently because it is very fragile.",
            "synonyms": ["delicate", "breakable", "weak"],
            "antonyms": ["sturdy", "strong"],
            "phonetic": "/ˈfrædʒ.aɪl/"
        }
    }

    @classmethod
    def is_vocabulary_word(
        cls,
        orig_word: str,
        prop_word: str,
        category: str,
        explanation: str
    ) -> bool:
        """
        Determine if the item is a true vocabulary/spelling word.
        Returns False for proper nouns, numbers, URLs, symbols, and pure functional grammar edits.
        """
        w_orig = orig_word.strip()
        w_prop = prop_word.strip()
        w_clean = re.sub(r'[^a-zA-Z]', '', w_prop).lower()

        if not w_clean:
            return False

        # Pure functional grammar words check
        if w_clean in cls.FUNCTIONAL_GRAMMAR_WORDS:
            return False

        # Punctuation / Symbol / Digit check
        if re.search(r'[\d@#\$%\^&\*\(\)_\+=\[\]\{\}<>\\/|]', w_prop):
            return False

        # Category / Explanation check for functional grammar edits
        expl_lower = explanation.lower()
        if "article" in expl_lower or "subject-verb" in expl_lower or "preposition" in expl_lower:
            return False
        if "comma" in expl_lower or "period" in expl_lower or "punctuation" in expl_lower:
            return False

        # Proper Noun / Name check (Capitalized non-dictionary term or acronym)
        if len(w_prop) > 1 and w_prop[0].isupper() and w_prop.isupper():
            return False

        # If length is at least 2 letters and not purely functional grammar, treat as vocabulary word
        return len(w_clean) >= 2

    @classmethod
    def get_lexical_data(
        cls,
        orig_word: str,
        prop_word: str,
        category: str,
        explanation: str,
        orig_sent: str
    ) -> Dict[str, Any]:
        """
        Extract child-friendly dictionary definition, part of speech, natural 8-20 word example sentence,
        synonyms, antonyms, and phonetics.
        """
        is_vocab = cls.is_vocabulary_word(orig_word, prop_word, category, explanation)
        w_clean = re.sub(r'[^a-zA-Z]', '', prop_word).lower()

        if not is_vocab or not w_clean:
            return {
                "is_vocabulary_word": False,
                "child_friendly_definition": "",
                "dictionary_meaning": "",
                "contextual_meaning": "",
                "example_sentence": "",
                "part_of_speech": "grammar",
                "synonyms": [],
                "antonyms": [],
                "pronunciation": ""
            }

        # Check explicit child dictionary map
        dict_entry = cls.CHILD_DICTIONARY.get(w_clean)
        if not dict_entry:
            # Check singular or stem
            if w_clean.endswith("s") and w_clean[:-1] in cls.CHILD_DICTIONARY:
                dict_entry = cls.CHILD_DICTIONARY[w_clean[:-1]]
            elif w_clean.endswith("ed") and w_clean[:-2] in cls.CHILD_DICTIONARY:
                dict_entry = cls.CHILD_DICTIONARY[w_clean[:-2]]
            elif w_clean.endswith("ing") and w_clean[:-3] in cls.CHILD_DICTIONARY:
                dict_entry = cls.CHILD_DICTIONARY[w_clean[:-3]]

        if dict_entry:
            pos = dict_entry["pos"]
            c_def = dict_entry["child_def"]
            ex_sent = dict_entry["example"]
            syns = dict_entry["synonyms"]
            ants = dict_entry["antonyms"]
            phon = dict_entry["phonetic"]
        else:
            # Morphological inference & Child-Friendly Synthesis
            if w_clean.endswith("ly"):
                pos = "adverb"
                c_def = f"In a way that is {w_clean[:-2]}; doing something with care or specific manner."
                ex_sent = f"The student worked {w_clean} to finish the school assignment on time."
                syns = [f"manner of {w_clean[:-2]}", "clearly"]
                ants = []
            elif w_clean.endswith(("tion", "ment", "ness", "ity", "ance", "ence")):
                pos = "noun"
                c_def = f"The state, quality, or process of being {w_clean} in context."
                ex_sent = f"Our class discussed the importance of {w_clean} during morning lesson."
                syns = ["quality", "state", "concept"]
                ants = []
            elif w_clean.endswith(("ive", "ous", "able", "ible", "al", "ic", "ful")):
                pos = "adjective"
                c_def = f"Having the quality of {w_clean}; full of specific features or traits."
                ex_sent = f"The teacher shared a very {w_clean} idea with the whole classroom today."
                syns = ["quality", "trait", "feature"]
                ants = []
            elif w_clean.endswith(("ed", "ing", "ize", "ate")):
                pos = "verb"
                c_def = f"To perform or carry out the action of {w_clean} thoughtfully."
                ex_sent = f"They decided to {w_clean} together after finishing their daily homework assignments."
                syns = ["action", "perform", "do"]
                ants = []
            else:
                pos = "noun" if len(w_clean) <= 6 else "adjective"
                c_def = f"A meaningful English word used to express clear thoughts and ideas."
                ex_sent = f"Using the word {prop_word} makes your sentence sound clear and intelligent."
                syns = ["expression", "term"]
                ants = []

            phon = f"/{w_clean}/"

        # Ensure sentence length is strictly 8-20 words
        ex_words = ex_sent.split()
        if len(ex_words) < 8:
            ex_sent = f"{ex_sent} It is very helpful for learning."
        elif len(ex_words) > 20:
            ex_sent = " ".join(ex_words[:18]) + "."

        return {
            "is_vocabulary_word": True,
            "child_friendly_definition": c_def,
            "dictionary_meaning": c_def,
            "contextual_meaning": f"In this sentence, '{prop_word}' ({pos}) means: {c_def}",
            "example_sentence": ex_sent,
            "part_of_speech": pos,
            "synonyms": syns,
            "antonyms": ants,
            "pronunciation": phon
        }


from .vocabulary_engine import VocabularyLearningEngine
from .learning_opportunity_detector import LearningOpportunityDetector

class FlashcardGeneratorEngine:
    """
    AI-powered Flashcard Generation Engine.
    Transforms corrected documents and accepted proofreading history into personalized,
    active-recall educational study decks using sequence alignment and structured learning opportunity detection.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir is None:
            # Default storage directory in user workspace data
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            storage_dir = os.path.join(base_dir, "data", "learning_library")
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.opportunity_detector = LearningOpportunityDetector()

    def generate_deck(
        self,
        exported_text: str,
        accepted_suggestions: List[Dict[str, Any]],
        document_title: str = "Untitled Document",
        document_id: Optional[str] = None,
        include_rejected: bool = False,
        all_suggestions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured FlashcardDeck from exported text and proofreading corrections.
        """
        start_time = time.time()
        doc_id = document_id or f"doc_{uuid.uuid4().hex[:8]}"
        deck_id = f"deck_{uuid.uuid4().hex[:10]}"

        # 1. Filter target corrections
        target_suggestions = list(accepted_suggestions) if accepted_suggestions else []

        if include_rejected and all_suggestions:
            accepted_ids = {s.get("suggestion_id") for s in target_suggestions}
            for sug in all_suggestions:
                if sug.get("suggestion_id") not in accepted_ids:
                    target_suggestions.append(sug)

        logger.info(f"Flashcard Generator started for '{document_title}' with {len(target_suggestions)} target corrections.")

        # 1b. Run Learning Opportunity Detection Stage
        opportunities = self.opportunity_detector.align_and_detect(
            exported_text=exported_text,
            accepted_suggestions=target_suggestions
        )

        processed_count = len(target_suggestions)
        duplicates_removed = 0
        unconvertible_count = 0

        # 2. Extract sentences & build cards
        raw_cards: List[Flashcard] = []
        concept_map: Dict[str, List[Tuple[Dict[str, Any], str, str]]] = {}

        for sug in target_suggestions:
            orig_text = sug.get("original_text", "").strip()
            prop_text = sug.get("proposed_correction", "").strip()
            category = sug.get("category", "Grammar Correction")
            explanation = sug.get("explanation", "")
            confidence = sug.get("confidence_score", 0.90)

            if not orig_text or not prop_text or orig_text == prop_text:
                unconvertible_count += 1
                continue

            # Context sentence extraction
            orig_sent, corr_sent = self._extract_context_sentences(exported_text, sug)

            # Normalized concept key for deduplication & concept merging
            concept_key = f"{category.lower()}:{orig_text.lower()}->{prop_text.lower()}"
            if concept_key not in concept_map:
                concept_map[concept_key] = []
            concept_map[concept_key].append((sug, orig_sent, corr_sent))

        # 3. Process merged concepts into final Flashcards
        for concept_key, items in concept_map.items():
            if len(items) > 1:
                duplicates_removed += (len(items) - 1)

            first_sug, primary_orig_sent, primary_corr_sent = items[0]
            extra_examples = [corr_s for _, _, corr_s in items[1:]]

            card = self._build_single_flashcard(
                sug=first_sug,
                orig_sent=primary_orig_sent,
                corr_sent=primary_corr_sent,
                doc_id=doc_id,
                doc_title=document_title,
                extra_examples=extra_examples
            )
            raw_cards.append(card)

        # 4. Calculate Distributions & Telemetry
        cat_dist: Dict[str, int] = {}
        diff_dist: Dict[str, int] = {"Easy": 0, "Medium": 0, "Hard": 0}

        for c in raw_cards:
            cat_dist[c.category] = cat_dist.get(c.category, 0) + 1
            diff_dist[c.difficulty] = diff_dist.get(c.difficulty, 0) + 1

        total_cards = len(raw_cards)
        # Estimated study time: ~1.5 mins per flashcard
        est_study_time = max(1, round(total_cards * 1.5))

        now_iso = datetime.utcnow().isoformat() + "Z"

        deck = FlashcardDeck(
            deck_id=deck_id,
            source_document_id=doc_id,
            source_document_title=document_title,
            exported_document_text=exported_text,
            created_at=now_iso,
            total_flashcards=total_cards,
            categories_distribution=cat_dist,
            difficulty_distribution=diff_dist,
            estimated_study_time_min=est_study_time,
            mastery_percentage=0.0,
            study_progress={
                "cards_completed": 0,
                "cards_mastered": 0,
                "cards_bookmarked": 0,
                "last_studied_at": None
            },
            cards=raw_cards
        )

        # 5. Persist deck in personal learning library
        self.save_deck(deck)

        elapsed = time.time() - start_time
        logger.info(f"Flashcard deck '{deck_id}' generated successfully with {total_cards} cards in {elapsed:.3f}s.")

        telemetry = {
            "processing_time_sec": round(elapsed, 3),
            "accepted_corrections_processed": processed_count,
            "duplicate_cards_removed": duplicates_removed,
            "flashcards_generated": total_cards,
            "category_distribution": cat_dist,
            "difficulty_distribution": diff_dist,
            "unconvertible_corrections": unconvertible_count,
            "confidence_statistics": {
                "mean_confidence": round(sum(c.confidence_score for c in raw_cards) / max(1, total_cards), 4)
            }
        }

        return {
            "deck": deck.to_dict(),
            "telemetry": telemetry
        }

    def _clean_sentence_spacing(self, sentence: str) -> str:
        """Ensure proper spacing between all words and after punctuation marks."""
        if not sentence:
            return ""
        # Convert newlines and tabs to space
        s = re.sub(r'[\r\n\t]+', ' ', sentence)
        # Add space after punctuation if missing before a word character
        s = re.sub(r'([,.:;!?])([a-zA-Z0-9])', r'\1 \2', s)
        # Add space between concatenated word boundaries (e.g. "word1word2" or camelCase)
        s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
        # Collapse multi-spaces
        s = re.sub(r' +', ' ', s)
        return s.strip()

    def _extract_context_sentences(self, full_text: str, sug: Dict[str, Any]) -> Tuple[str, str]:
        """Extract full original sentence and corrected sentence around suggestion offsets with clean spacing."""
        start = sug.get("start_offset", -1)
        end = sug.get("end_offset", -1)
        orig_word = sug.get("original_text", "").strip()
        prop_word = sug.get("proposed_correction", "").strip()

        if start >= 0 and end <= len(full_text) and start < end:
            # Find sentence boundaries
            left_chunk = full_text[:start]
            right_chunk = full_text[end:]

            # Backward boundary
            left_delims = [m.start() for m in re.finditer(r'[.!?\n]', left_chunk)]
            sent_start = left_delims[-1] + 1 if left_delims else 0

            # Forward boundary
            right_delims = [m.start() for m in re.finditer(r'[.!?\n]', right_chunk)]
            sent_end = end + right_delims[0] if right_delims else len(full_text)

            raw_orig_sent = full_text[sent_start:sent_end].strip()

            # Construct corrected sentence cleanly ensuring spaces
            left_sub = left_chunk[sent_start:]
            right_sub = right_chunk[:sent_end - end]

            if orig_word and orig_word in raw_orig_sent:
                raw_corr_sent = re.sub(r'\b' + re.escape(orig_word) + r'\b', prop_word, raw_orig_sent, count=1)
                if raw_corr_sent == raw_orig_sent:
                    raw_corr_sent = raw_orig_sent.replace(orig_word, prop_word, 1)
            else:
                left_space = " " if (left_sub and not left_sub.endswith(" ")) else ""
                right_space = " " if (right_sub and not right_sub.startswith((" ", ",", ".", "!", "?", ";", ":"))) else ""
                raw_corr_sent = left_sub + left_space + prop_word + right_space + right_sub

            orig_sent = self._clean_sentence_spacing(raw_orig_sent)
            corr_sent = self._clean_sentence_spacing(raw_corr_sent)

            if orig_sent:
                return orig_sent, corr_sent

        # Fallback if offsets are missing
        orig_sent = self._clean_sentence_spacing(f"The sentence contained '{orig_word}'.")
        corr_sent = self._clean_sentence_spacing(f"The sentence was corrected to '{prop_word}'.")
        return orig_sent, corr_sent


    def _build_single_flashcard(
        self,
        sug: Dict[str, Any],
        orig_sent: str,
        corr_sent: str,
        doc_id: str,
        doc_title: str,
        extra_examples: List[str]
    ) -> Flashcard:
        """Construct a single Flashcard object with card style, rules, explanations, and tags."""
        card_id = f"fc_{uuid.uuid4().hex[:8]}"
        category = sug.get("category", "Grammar Correction")
        orig_word = sug.get("original_text", "").strip()
        prop_word = sug.get("proposed_correction", "").strip()
        explanation = sug.get("explanation", "")
        confidence = float(sug.get("confidence_score", 0.90))

        card_style, mapped_category = self._resolve_card_style_and_category(category, orig_word, prop_word, explanation)
        difficulty = self._estimate_difficulty(card_style, orig_word, prop_word, orig_sent, explanation)
        tags = self._generate_tags(mapped_category, card_style, orig_word, prop_word, explanation)
        rule = self._generate_rule(mapped_category, card_style, orig_word, prop_word)
        objective = self._generate_learning_objective(mapped_category, card_style, orig_word, prop_word)
        educational_explanation = self._craft_educational_explanation(mapped_category, orig_word, prop_word, explanation, rule)

        lexical_info = VocabularyLearningEngine.process_correction(
            orig_word=orig_word,
            prop_word=prop_word,
            corrected_sentence=corr_sent,
            category=mapped_category,
            explanation=explanation
        )

        front, back = self._build_front_back_content(
            card_style=card_style,
            category=mapped_category,
            orig_word=orig_word,
            prop_word=prop_word,
            orig_sent=orig_sent,
            corr_sent=corr_sent,
            rule=rule,
            explanation=educational_explanation,
            extra_examples=extra_examples,
            lexical_info=lexical_info
        )

        now_iso = datetime.utcnow().isoformat() + "Z"

        return Flashcard(
            id=card_id,
            category=mapped_category,
            card_style=card_style,
            original_sentence=orig_sent,
            corrected_sentence=corr_sent,
            front=front,
            back=back,
            accepted_correction={"original": orig_word, "proposed": prop_word},
            explanation=educational_explanation,
            rule=rule,
            learning_objective=objective,
            difficulty=difficulty,
            confidence_score=confidence,
            source_document_id=doc_id,
            source_document_title=doc_title,
            created_at=now_iso,
            tags=tags,
            child_friendly_definition=lexical_info.get("simplified_child_definition", ""),
            dictionary_meaning=lexical_info.get("official_dictionary_definition", ""),
            contextual_meaning=f"In context ({lexical_info.get('detected_pos', 'word')}): {lexical_info.get('simplified_child_definition', '')}",
            example_sentence=lexical_info.get("generated_example_sentence", ""),
            part_of_speech=lexical_info.get("detected_pos", "noun"),
            synonyms=lexical_info.get("synonyms", []),
            antonyms=lexical_info.get("antonyms", []),
            difficulty_level=difficulty,
            pronunciation=lexical_info.get("pronunciation", ""),
            detected_pos=lexical_info.get("detected_pos", ""),
            identified_word_sense=lexical_info.get("identified_word_sense", ""),
            official_dictionary_definition=lexical_info.get("official_dictionary_definition", ""),
            simplified_child_definition=lexical_info.get("simplified_child_definition", ""),
            generated_example_sentence=lexical_info.get("generated_example_sentence", ""),
            dictionary_source=lexical_info.get("dictionary_source", ""),
            requires_manual_verification=lexical_info.get("requires_manual_verification", False)
        )


    def _resolve_card_style_and_category(
        self,
        category: str,
        orig_word: str,
        prop_word: str,
        explanation: str
    ) -> Tuple[str, str]:
        """Map correction metadata to card style and normalized educational category."""
        cat_lower = category.lower()
        expl_lower = explanation.lower()

        if "spelling" in cat_lower or "typo" in cat_lower or "spell" in expl_lower:
            return "spelling", "Spelling Correction"
        elif "missing" in cat_lower or "omitted" in cat_lower or "missing" in expl_lower:
            return "fill_in_blank", "Missing Word"
        elif "punctuation" in cat_lower or "comma" in cat_lower or "period" in cat_lower:
            return "punctuation_practice", "Punctuation"
        elif "capital" in cat_lower or orig_word.lower() == prop_word.lower():
            return "capitalization_rule", "Capitalization"
        elif "vocab" in cat_lower or "style" in cat_lower or "word choice" in expl_lower:
            return "vocabulary", "Vocabulary Improvement"
        elif "structure" in cat_lower or "restructur" in cat_lower or len(orig_word.split()) > 3:
            return "sentence_reconstruction", "Sentence Structure"
        else:
            return "grammar_explanation", "Grammar Correction"

    def _estimate_difficulty(
        self,
        card_style: str,
        orig_word: str,
        prop_word: str,
        orig_sent: str,
        explanation: str
    ) -> str:
        """Estimate card difficulty: Easy, Medium, or Hard."""
        if card_style in ("spelling", "capitalization_rule"):
            if len(orig_word) <= 6 and abs(len(orig_word) - len(prop_word)) <= 1:
                return "Easy"
            return "Medium"

        if card_style in ("fill_in_blank", "punctuation_practice"):
            if len(orig_sent.split()) <= 8:
                return "Easy"
            return "Medium"

        if card_style == "vocabulary":
            if len(prop_word) >= 9 or "academic" in explanation.lower():
                return "Hard"
            return "Medium"

        if card_style == "sentence_reconstruction":
            if len(orig_sent.split()) > 12:
                return "Hard"
            return "Medium"

        # Grammar default rules
        if "subj" in explanation.lower() or "tense" in explanation.lower() or "clause" in explanation.lower():
            return "Medium"
        if len(orig_sent.split()) > 15:
            return "Hard"

        return "Easy"

    def _generate_tags(
        self,
        category: str,
        card_style: str,
        orig_word: str,
        prop_word: str,
        explanation: str
    ) -> List[str]:
        """Generate automatic tags for searching, filtering, and adaptive learning."""
        tags = set()
        tags.add(category)

        expl_lower = explanation.lower()
        if "verb" in expl_lower or "tense" in expl_lower:
            tags.add("Verb Tense")
        if "subject" in expl_lower or "agreement" in expl_lower:
            tags.add("Subject-Verb Agreement")
        if "article" in expl_lower or orig_word.lower() in ("a", "an", "the"):
            tags.add("Articles")
        if "prep" in expl_lower or orig_word.lower() in ("in", "on", "at", "to", "for", "with", "by", "from"):
            tags.add("Prepositions")
        if card_style == "vocabulary" or len(prop_word) >= 8:
            tags.add("Academic Vocabulary")
        if "ocr" in expl_lower:
            tags.add("OCR Recovery")
        if card_style == "sentence_reconstruction":
            tags.add("Sentence Structure")

        return list(tags)

    def _generate_rule(
        self,
        category: str,
        card_style: str,
        orig_word: str,
        prop_word: str
    ) -> str:
        """Construct the core spelling, grammar, or punctuation rule."""
        if card_style == "spelling":
            return f"Spelling Rule: Ensure correct letter patterns and suffixes when writing '{prop_word}'."
        elif card_style == "fill_in_blank":
            return f"Contextual Completeness: Ensure all necessary syntax components such as '{prop_word}' are included for grammatical precision."
        elif card_style == "grammar_explanation":
            return f"Grammatical Rule: Maintain subject-verb agreement, consistent tense usage, and correct word forms."
        elif card_style == "punctuation_practice":
            return f"Punctuation Rule: Use punctuation marks correctly to delineate clauses and improve readability."
        elif card_style == "capitalization_rule":
            return f"Capitalization Rule: Always capitalize proper nouns, the pronoun 'I', and the first word of a sentence."
        elif card_style == "vocabulary":
            return f"Vocabulary Elevation: Upgrade informal or plain words ('{orig_word}') to precise academic vocabulary ('{prop_word}')."
        elif card_style == "sentence_reconstruction":
            return f"Sentence Structure Rule: Organize clauses logically for clear syntactic flow."
        return "Standard English Language Conventions Rule."

    def _generate_learning_objective(
        self,
        category: str,
        card_style: str,
        orig_word: str,
        prop_word: str
    ) -> str:
        """Construct objective statement for active recall learning."""
        if card_style == "spelling":
            return f"Master accurate spelling of '{prop_word}' and avoid common typos."
        elif card_style == "fill_in_blank":
            return f"Identify missing contextual words like '{prop_word}' to complete sentence structures."
        elif card_style == "grammar_explanation":
            return f"Recognize and correct grammatical errors involving '{orig_word}' -> '{prop_word}'."
        elif card_style == "punctuation_practice":
            return f"Apply correct punctuation conventions within sentence context."
        elif card_style == "capitalization_rule":
            return f"Master standard capitalization rules for '{prop_word}'."
        elif card_style == "vocabulary":
            return f"Expand academic vocabulary by learning the usage and synonyms of '{prop_word}'."
        elif card_style == "sentence_reconstruction":
            return f"Reconstruct flawed sentence patterns into clear, well-formed statements."
        return "Enhance written document quality through targeted error recognition."

    def _craft_educational_explanation(
        self,
        category: str,
        orig_word: str,
        prop_word: str,
        raw_expl: str,
        rule: str
    ) -> str:
        """Format an educational explanation explaining WHY the correction is right."""
        if raw_expl and len(raw_expl) > 10:
            return f"{raw_expl} {rule}"
        return f"Replacing '{orig_word}' with '{prop_word}' ensures grammatical accuracy and clarity. {rule}"


    def _build_front_back_content(
        self,
        card_style: str,
        category: str,
        orig_word: str,
        prop_word: str,
        orig_sent: str,
        corr_sent: str,
        rule: str,
        explanation: str,
        extra_examples: List[str],
        lexical_info: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate structured front and back side content tailored for interactive study modes."""
        part_of_speech = lexical_info.get("detected_pos") or lexical_info.get("part_of_speech", "word")
        child_def = lexical_info.get("simplified_child_definition") or lexical_info.get("child_friendly_definition", "")
        official_def = lexical_info.get("official_dictionary_definition") or lexical_info.get("dictionary_meaning", "")
        word_meaning = child_def
        usage_example = lexical_info.get("generated_example_sentence") or lexical_info.get("example_sentence", "")
        phonetic_hint = lexical_info.get("pronunciation", f"/{prop_word.lower()}/")
        synonyms = lexical_info.get("synonyms", [])
        antonyms = lexical_info.get("antonyms", [])
        dict_source = lexical_info.get("dictionary_source", "WordNet / Dictionary API")
        word_sense = lexical_info.get("identified_word_sense", "")
        req_verify = lexical_info.get("requires_manual_verification", False)

        if card_style == "spelling":
            distractor = self._generate_spelling_distractor(orig_word, prop_word)
            options = [prop_word, distractor] if distractor != prop_word else [prop_word, f"{prop_word}e"]

            front = {
                "title": "Spelling Challenge",
                "prompt": f"Identify or type the correct spelling for the highlighted word in context:",
                "context_sentence": orig_sent,
                "target_word": orig_word,
                "options": options,
                "study_type": "spelling_choice_or_input"
            }
            back = {
                "correct_answer": prop_word,
                "part_of_speech": part_of_speech,
                "detected_pos": part_of_speech,
                "child_friendly_definition": child_def,
                "official_dictionary_definition": official_def,
                "dictionary_meaning": official_def,
                "dictionary_source": dict_source,
                "identified_word_sense": word_sense,
                "requires_manual_verification": req_verify,
                "usage_example": usage_example,
                "example_sentence": usage_example,
                "phonetic_hint": phonetic_hint,
                "synonyms": synonyms,
                "antonyms": antonyms,
                "explanation": explanation,
                "rule": rule,
                "original_sentence": orig_sent,
                "corrected_sentence": corr_sent,
                "extra_examples": extra_examples,
                "tip": f"Remember: '{prop_word}' ({part_of_speech}) is spelled correctly here."
            }

        elif card_style == "fill_in_blank":
            sentence_with_blank = corr_sent.replace(prop_word, "[ _____ ]", 1)
            if "[ _____ ]" not in sentence_with_blank:
                sentence_with_blank = orig_sent.replace(orig_word, "[ _____ ]", 1)

            front = {
                "title": "Fill in the Blank",
                "prompt": "Choose or type the missing word to complete the sentence correctly:",
                "sentence_with_blank": sentence_with_blank,
                "hint": f"Initial letter: {prop_word[0].upper()}" if prop_word else "",
                "options": [prop_word, "and", "which", "however"],
                "study_type": "fill_blank"
            }
            back = {
                "correct_answer": prop_word,
                "part_of_speech": part_of_speech,
                "child_friendly_definition": word_meaning,
                "dictionary_meaning": word_meaning,
                "usage_example": usage_example,
                "example_sentence": usage_example,
                "phonetic_hint": phonetic_hint,
                "synonyms": synonyms,
                "antonyms": antonyms,
                "full_sentence": corr_sent,
                "explanation": explanation,
                "rule": rule,
                "original_sentence": orig_sent,
                "corrected_sentence": corr_sent,
                "extra_examples": extra_examples,
                "tip": f"The word '{prop_word}' ({part_of_speech}) completes the syntactic meaning."
            }

        elif card_style == "grammar_explanation":
            front = {
                "title": "Grammar Error Spotter",
                "prompt": "Analyze the sentence below. Identify the grammatical error before revealing the rule:",
                "context_sentence": orig_sent,
                "highlighted_error": orig_word,
                "options": [
                    f"Change '{orig_word}' to '{prop_word}'",
                    f"Remove '{orig_word}' entirely",
                    f"Move '{orig_word}' to end of sentence"
                ],
                "study_type": "grammar_spotter"
            }
            back = {
                "correct_answer": f"Change '{orig_word}' to '{prop_word}'",
                "part_of_speech": part_of_speech,
                "child_friendly_definition": word_meaning,
                "dictionary_meaning": word_meaning,
                "usage_example": usage_example,
                "example_sentence": usage_example,
                "phonetic_hint": phonetic_hint,
                "synonyms": synonyms,
                "antonyms": antonyms,
                "error_found": orig_word,
                "corrected_form": prop_word,
                "explanation": explanation,
                "rule": rule,
                "original_sentence": orig_sent,
                "corrected_sentence": corr_sent,
                "extra_examples": extra_examples,
                "tip": "Check for subject-verb agreement and tense consistency."
            }

        elif card_style == "punctuation_practice":
            front = {
                "title": "Punctuation Practice",
                "prompt": "Examine this sentence. Where is punctuation missing or incorrect?",
                "context_sentence": orig_sent,
                "study_type": "punctuation"
            }
            back = {
                "correct_answer": corr_sent,
                "part_of_speech": part_of_speech,
                "child_friendly_definition": word_meaning,
                "dictionary_meaning": word_meaning,
                "usage_example": usage_example,
                "example_sentence": usage_example,
                "explanation": explanation,
                "rule": rule,
                "original_sentence": orig_sent,
                "corrected_sentence": corr_sent,
                "extra_examples": extra_examples,
                "tip": "Punctuation separates distinct ideas and prevents run-on sentences."
            }

        elif card_style == "capitalization_rule":
            front = {
                "title": "Capitalization Mastery",
                "prompt": "Identify the word that requires proper capitalization in this sentence:",
                "context_sentence": orig_sent,
                "target_word": orig_word,
                "study_type": "capitalization"
            }
            back = {
                "correct_answer": prop_word,
                "part_of_speech": part_of_speech,
                "child_friendly_definition": word_meaning,
                "dictionary_meaning": word_meaning,
                "usage_example": usage_example,
                "example_sentence": usage_example,
                "explanation": explanation,
                "rule": rule,
                "original_sentence": orig_sent,
                "corrected_sentence": corr_sent,
                "extra_examples": extra_examples,
                "tip": "Proper nouns and sentence origins must always be capitalized."
            }

        elif card_style == "vocabulary":
            front = {
                "title": "Vocabulary Elevation",
                "prompt": f"How can you improve the phrase '{orig_word}' in context?",
                "context_sentence": orig_sent,
                "target_word": prop_word,
                "study_type": "vocabulary"
            }
            back = {
                "correct_answer": prop_word,
                "part_of_speech": part_of_speech,
                "child_friendly_definition": word_meaning,
                "dictionary_meaning": word_meaning,
                "usage_example": usage_example,
                "example_sentence": usage_example,
                "phonetic_hint": phonetic_hint,
                "synonyms": synonyms if synonyms else [prop_word, "enhanced", "elevated"],
                "antonyms": antonyms if antonyms else [orig_word],
                "explanation": explanation,
                "rule": rule,
                "original_sentence": orig_sent,
                "corrected_sentence": corr_sent,
                "extra_examples": extra_examples,
                "tip": f"Using '{prop_word}' ({part_of_speech}) demonstrates academic writing style."
            }

        else: # sentence_reconstruction
            words = corr_sent.split()
            front = {
                "title": "Sentence Reconstruction",
                "prompt": "Rebuild the corrected sentence from its original flawed version:",
                "original_sentence": orig_sent,
                "scrambled_tokens": words,
                "study_type": "reconstruction"
            }
            back = {
                "correct_answer": corr_sent,
                "part_of_speech": part_of_speech,
                "child_friendly_definition": word_meaning,
                "dictionary_meaning": word_meaning,
                "usage_example": usage_example,
                "example_sentence": usage_example,
                "explanation": explanation,
                "rule": rule,
                "original_sentence": orig_sent,
                "corrected_sentence": corr_sent,
                "extra_examples": extra_examples,
                "tip": "Focus on clear subject-verb arrangement."
            }

        return front, back


    def _generate_spelling_distractor(self, orig_word: str, prop_word: str) -> str:
        """Helper to generate a plausible spelling distractor if original equals proposed."""
        if orig_word != prop_word:
            return orig_word
        if len(prop_word) > 4:
            return prop_word[:-1]
        return f"{prop_word}s"

    # --- Persistent Learning Library Storage Methods ---

    def save_deck(self, deck: FlashcardDeck):
        """Save deck as a JSON file in learning library storage directory."""
        filepath = os.path.join(self.storage_dir, f"{deck.deck_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(deck.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Deck saved to library: {filepath}")

    def list_decks(self) -> List[Dict[str, Any]]:
        """List all saved decks metadata from personal learning library."""
        decks_meta = []
        if not os.path.exists(self.storage_dir):
            return decks_meta

        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(self.storage_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        decks_meta.append({
                            "deck_id": data.get("deck_id"),
                            "source_document_id": data.get("source_document_id"),
                            "source_document_title": data.get("source_document_title"),
                            "created_at": data.get("created_at"),
                            "total_flashcards": data.get("total_flashcards"),
                            "categories_distribution": data.get("categories_distribution"),
                            "difficulty_distribution": data.get("difficulty_distribution"),
                            "estimated_study_time_min": data.get("estimated_study_time_min"),
                            "mastery_percentage": data.get("mastery_percentage", 0.0),
                            "study_progress": data.get("study_progress", {})
                        })
                except Exception as e:
                    logger.warning(f"Failed to read deck file '{fname}': {e}")

        # Sort by creation date descending
        decks_meta.sort(key=lambda d: d.get("created_at", ""), reverse=True)
        return decks_meta

    def get_deck(self, deck_id: str) -> Optional[Dict[str, Any]]:
        """Get full deck details by ID."""
        fpath = os.path.join(self.storage_dir, f"{deck_id}.json")
        if not os.path.exists(fpath):
            return None
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading deck '{deck_id}': {e}")
            return None

    def update_deck_progress(self, deck_id: str, card_updates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Update card flags (is_mastered, is_bookmarked, needs_review) and re-calculate deck mastery stats.
        """
        deck_data = self.get_deck(deck_id)
        if not deck_data:
            return None

        update_map = {u["id"]: u for u in card_updates if "id" in u}
        cards = deck_data.get("cards", [])

        mastered_count = 0
        bookmarked_count = 0

        for card in cards:
            cid = card.get("id")
            if cid in update_map:
                u = update_map[cid]
                if "is_mastered" in u:
                    card["is_mastered"] = bool(u["is_mastered"])
                if "is_bookmarked" in u:
                    card["is_bookmarked"] = bool(u["is_bookmarked"])
                if "needs_review" in u:
                    card["needs_review"] = bool(u["needs_review"])

            if card.get("is_mastered"):
                mastered_count += 1
            if card.get("is_bookmarked"):
                bookmarked_count += 1

        total_cards = len(cards)
        mastery_pct = (mastered_count / total_cards * 100.0) if total_cards > 0 else 0.0

        deck_data["mastery_percentage"] = round(mastery_pct, 1)
        deck_data["study_progress"] = {
            "cards_completed": total_cards,
            "cards_mastered": mastered_count,
            "cards_bookmarked": bookmarked_count,
            "last_studied_at": datetime.utcnow().isoformat() + "Z"
        }

        # Save updated file
        fpath = os.path.join(self.storage_dir, f"{deck_id}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(deck_data, f, indent=2, ensure_ascii=False)

        return deck_data

    def delete_deck(self, deck_id: str) -> bool:
        """Delete a deck from personal learning library."""
        fpath = os.path.join(self.storage_dir, f"{deck_id}.json")
        if os.path.exists(fpath):
            os.remove(fpath)
            logger.info(f"Deleted deck '{deck_id}' from learning library.")
            return True
        return False
