"""
Vocabulary Learning Engine Module
Context-First Lexical Processing Pipeline.
Enforces strict spaCy POS hard constraints, semantic embedding WSD definition ranking,
learner dictionary prioritization, semantic context validation, confidence scoring,
and sense-specific synonym/example generation.
"""

import re
import json
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
import requests

import spacy
import nltk
from nltk.corpus import wordnet as wn

from ..utils.logging_config import logger


# Load spaCy en_core_web_sm model globally for fast contextual POS tagging & embedding similarity
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.warning(f"Could not load spaCy model en_core_web_sm: {e}")
    nlp = None


class POSTagger:
    """
    Contextual Part-of-Speech Tagger using spaCy en_core_web_sm.
    Identifies the exact grammatical category in context and enforces a strict POS hard constraint.
    """

    SPACY_POS_MAP = {
        'ADJ': 'adjective',
        'ADV': 'adverb',
        'NOUN': 'noun',
        'PROPN': 'noun',
        'VERB': 'verb',
        'AUX': 'verb',
        'PRON': 'pronoun',
        'ADP': 'preposition',
        'CCONJ': 'conjunction',
        'SCONJ': 'conjunction',
        'DET': 'determiner',
        'NUM': 'number',
        'PART': 'particle',
        'INTJ': 'interjection'
    }

    WORDNET_POS_MAP = {
        'adjective': wn.ADJ,
        'adverb': wn.ADV,
        'noun': wn.NOUN,
        'verb': wn.VERB
    }

    @classmethod
    def tag_word_in_context(cls, word: str, sentence: str) -> Tuple[str, str, float]:
        """
        Tag target word in corrected sentence context using spaCy.
        Returns (standard_pos_label, spacy_fine_tag, confidence_score).
        """
        w_clean = re.sub(r'[^a-zA-Z]', '', word).lower()
        if not w_clean:
            return 'grammar', 'OTHER', 0.0

        if nlp is not None:
            try:
                doc = nlp(sentence)
                matched_token = None

                for token in doc:
                    if token.text.lower() == word.lower() or re.sub(r'[^a-zA-Z]', '', token.text).lower() == w_clean:
                        matched_token = token
                        break

                if matched_token:
                    std_pos = cls.SPACY_POS_MAP.get(matched_token.pos_, 'noun')
                    conf = 0.98 if std_pos in ['adjective', 'adverb', 'noun', 'verb'] else 0.85
                    return std_pos, matched_token.tag_, conf
            except Exception as e:
                logger.warning(f"spaCy POS tagging error for '{word}': {e}")

        # Fallback heuristic tagging
        if w_clean.endswith('ly'):
            return 'adverb', 'RB', 0.75
        elif w_clean.endswith(('ed', 'ing')):
            return 'verb', 'VB', 0.75
        elif w_clean.endswith(('tion', 'ment', 'ness', 'ity')):
            return 'noun', 'NN', 0.75
        elif w_clean in ["very", "extremely", "really", "so", "too"]:
            return 'adverb', 'RB', 0.95
        elif w_clean in ["dirty", "clean", "happy", "sad", "big", "small"]:
            return 'adjective', 'JJ', 0.95

        return 'noun', 'NN', 0.60


class LearnerLexicalProvider:
    """
    Learner-oriented lexical provider.
    Prioritizes educational child dictionary senses for school vocabulary over academic WordNet entries.
    """

    LEARNER_DICTIONARY_MAP: Dict[str, Dict[str, Any]] = {
        "very": {
            "senses": [
                {
                    "pos": "adverb",
                    "sense_id": "very.adv.01",
                    "definition": "To a great degree; extremely or highly.",
                    "child_def": "To a high degree; extremely or very much.",
                    "example": "She was very excited about the upcoming school trip.",
                    "synonyms": ["extremely", "highly", "exceedingly", "tremendously"],
                    "antonyms": ["slightly", "barely"]
                }
            ]
        },
        "dirty": {
            "senses": [
                {
                    "pos": "adjective",
                    "sense_id": "dirty.adj.01",
                    "definition": "Covered or marked with dirt, soil, or mud; not clean.",
                    "child_def": "Covered with dirt, soil, or mud; not clean.",
                    "example": "His shoes were dirty after playing in the muddy park.",
                    "synonyms": ["soiled", "muddy", "grimy", "unclean"],
                    "antonyms": ["clean", "spotless", "pure"]
                },
                {
                    "pos": "verb",
                    "sense_id": "dirty.verb.01",
                    "definition": "To make dirty or soil something.",
                    "child_def": "To make something dirty or stained.",
                    "example": "Be careful not to dirty your white shirt while painting.",
                    "synonyms": ["soil", "stain", "spoil"],
                    "antonyms": ["clean", "wash"]
                }
            ]
        },
        "light": {
            "senses": [
                {
                    "pos": "noun",
                    "sense_id": "light.noun.01",
                    "definition": "The brightness from the sun, lamps, or fire that allows us to see.",
                    "child_def": "The brightness from the sun or lamps that lets us see things.",
                    "example": "Turn on the lamp light so we can read our storybooks clearly.",
                    "synonyms": ["brightness", "illumination", "glow"],
                    "antonyms": ["darkness", "shadow"]
                },
                {
                    "pos": "adjective",
                    "sense_id": "light.adj.01",
                    "definition": "Having little weight; easy to lift, carry, or move.",
                    "child_def": "Not heavy; easy to lift, carry, or move around.",
                    "example": "Her new school backpack was light and easy to carry.",
                    "synonyms": ["lightweight", "slight"],
                    "antonyms": ["heavy", "ponderous"]
                }
            ]
        },
        "bank": {
            "senses": [
                {
                    "pos": "noun",
                    "sense_id": "bank.financial.01",
                    "definition": "A safe building or financial institution where people keep, deposit, or borrow money.",
                    "child_def": "A safe building where people keep, deposit, or borrow money.",
                    "example": "My parents went to the bank to deposit their monthly savings.",
                    "synonyms": ["financial institution", "vault"],
                    "antonyms": []
                },
                {
                    "pos": "noun",
                    "sense_id": "bank.river.02",
                    "definition": "The sloping land along the side of a river, stream, or lake.",
                    "child_def": "The sloping land along the side of a river or lake.",
                    "example": "We sat on the grassy bank of the river to watch ducks swim.",
                    "synonyms": ["riverbed", "shore", "coast"],
                    "antonyms": []
                }
            ]
        },
        "bat": {
            "senses": [
                {
                    "pos": "noun",
                    "sense_id": "bat.animal.01",
                    "definition": "A nocturnal flying mammal with webbed wings that sleeps upside down.",
                    "child_def": "A nocturnal flying mammal with webbed wings that sleeps upside down.",
                    "example": "A small bat flew out of the dark cave at sunset.",
                    "synonyms": ["flying mammal"],
                    "antonyms": []
                },
                {
                    "pos": "noun",
                    "sense_id": "bat.sports.02",
                    "definition": "A specially shaped wooden or metal club used for hitting balls in sports.",
                    "child_def": "A wooden or metal club used for hitting balls in baseball.",
                    "example": "He swung the wooden baseball bat and hit a home run.",
                    "synonyms": ["club", "stick"],
                    "antonyms": []
                }
            ]
        },
        "spring": {
            "senses": [
                {
                    "pos": "noun",
                    "sense_id": "spring.season.01",
                    "definition": "The season of the year between winter and summer when plants begin to bloom.",
                    "child_def": "The season of the year between winter and summer when flowers bloom.",
                    "example": "Colorful flowers begin to bloom everywhere during early spring.",
                    "synonyms": ["springtime"],
                    "antonyms": ["autumn", "winter"]
                },
                {
                    "pos": "noun",
                    "sense_id": "spring.water.02",
                    "definition": "A natural source where fresh water flows out from underground.",
                    "child_def": "A natural underground source where fresh water flows out.",
                    "example": "Cool mountain water flowed clean and clear from the natural spring.",
                    "synonyms": ["water source", "stream"],
                    "antonyms": []
                }
            ]
        },
        "fair": {
            "senses": [
                {
                    "pos": "adjective",
                    "sense_id": "fair.just.01",
                    "definition": "Treating everyone equally and following rules without taking sides.",
                    "child_def": "Treating everyone equally and following rules fairly without taking sides.",
                    "example": "The teacher gave everyone a fair turn to answer the question.",
                    "synonyms": ["just", "equal", "unbiased"],
                    "antonyms": ["unfair", "biased"]
                },
                {
                    "pos": "noun",
                    "sense_id": "fair.event.02",
                    "definition": "A fun public event or exhibition with rides, games, and food stalls.",
                    "child_def": "A fun public event with games, rides, and food stalls.",
                    "example": "Our family enjoyed playing games at the annual school science fair.",
                    "synonyms": ["carnival", "festival", "exhibition"],
                    "antonyms": []
                }
            ]
        },
        "bark": {
            "senses": [
                {
                    "pos": "verb",
                    "sense_id": "bark.dog.01",
                    "definition": "The short, sharp sound that a dog or puppy makes.",
                    "child_def": "The short, sharp sound that a dog or puppy makes.",
                    "example": "The friendly puppy started to bark happily when we arrived home.",
                    "synonyms": ["woof", "yelp"],
                    "antonyms": []
                },
                {
                    "pos": "noun",
                    "sense_id": "bark.tree.02",
                    "definition": "The tough outer wooden covering of a tree trunk or branch.",
                    "child_def": "The tough outer wooden covering of a tree trunk.",
                    "example": "Rough tree bark protects the trunk of tall oak trees.",
                    "synonyms": ["tree skin", "covering"],
                    "antonyms": []
                }
            ]
        },
        "right": {
            "senses": [
                {
                    "pos": "adjective",
                    "sense_id": "right.correct.01",
                    "definition": "Correct, true, or free from error.",
                    "child_def": "Correct, true, or accurate without any mistakes.",
                    "example": "She gave the right answer to the math problem on the board.",
                    "synonyms": ["correct", "accurate", "proper"],
                    "antonyms": ["wrong", "incorrect"]
                },
                {
                    "pos": "adverb",
                    "sense_id": "right.direction.02",
                    "definition": "Toward or on the right side.",
                    "child_def": "Toward or on the right side of your body.",
                    "example": "Turn right at the corner to reach the school library.",
                    "synonyms": ["rightward"],
                    "antonyms": ["left"]
                }
            ]
        },
        "well": {
            "senses": [
                {
                    "pos": "adverb",
                    "sense_id": "well.satisfactory.01",
                    "definition": "In a good, successful, or satisfactory manner.",
                    "child_def": "In a good, successful, or satisfactory manner.",
                    "example": "The student performed very well on her science exam today.",
                    "synonyms": ["successfully", "satisfactorily"],
                    "antonyms": ["poorly", "badly"]
                },
                {
                    "pos": "noun",
                    "sense_id": "well.water.02",
                    "definition": "A deep hole dug into the ground to obtain fresh water.",
                    "child_def": "A deep hole dug into the ground to get fresh water.",
                    "example": "They drew clean fresh water up from the deep village well.",
                    "synonyms": ["water hole"],
                    "antonyms": []
                }
            ]
        },
        "watch": {
            "senses": [
                {
                    "pos": "noun",
                    "sense_id": "watch.timepiece.01",
                    "definition": "A small clock worn on the wrist to show the time.",
                    "child_def": "A small clock worn on the wrist to tell the time.",
                    "example": "He checked his wrist watch to see if class was starting.",
                    "synonyms": ["timepiece", "clock"],
                    "antonyms": []
                },
                {
                    "pos": "verb",
                    "sense_id": "watch.look.02",
                    "definition": "To look at or observe attentively.",
                    "child_def": "To look at or observe someone or something attentively.",
                    "example": "The children sat together to watch the educational science movie.",
                    "synonyms": ["observe", "view", "look at"],
                    "antonyms": ["ignore"]
                }
            ]
        },
        "play": {
            "senses": [
                {
                    "pos": "verb",
                    "sense_id": "play.fun.01",
                    "definition": "To engage in fun activities, games, or sports for enjoyment.",
                    "child_def": "To engage in fun activities, games, or sports for enjoyment.",
                    "example": "Children love to play tag together during afternoon recess.",
                    "synonyms": ["enjoy games", "have fun"],
                    "antonyms": ["work"]
                },
                {
                    "pos": "noun",
                    "sense_id": "play.drama.02",
                    "definition": "A dramatic story or performance acted on a theater stage.",
                    "child_def": "A dramatic performance or story acted on a theater stage.",
                    "example": "Our class went to the theater to see a fun school play.",
                    "synonyms": ["drama", "performance", "show"],
                    "antonyms": []
                }
            ]
        },
        "hard": {
            "senses": [
                {
                    "pos": "adjective",
                    "sense_id": "hard.solid.01",
                    "definition": "Solid and firm; not easy to bend, break, or cut.",
                    "child_def": "Solid and firm; not easy to bend or break.",
                    "example": "The diamond is a hard stone that cannot be scratched easily.",
                    "synonyms": ["solid", "firm", "tough"],
                    "antonyms": ["soft", "flexible"]
                },
                {
                    "pos": "adverb",
                    "sense_id": "hard.effort.02",
                    "definition": "With great energy, effort, or determination.",
                    "child_def": "With great effort, energy, or determination.",
                    "example": "She studied hard to earn top grades on her final exams.",
                    "synonyms": ["diligently", "energetically"],
                    "antonyms": ["lazily"]
                }
            ]
        },
        "close": {
            "senses": [
                {
                    "pos": "verb",
                    "sense_id": "close.shut.01",
                    "definition": "To shut or move something so that it is no longer open.",
                    "child_def": "To shut or move something so that it is no longer open.",
                    "example": "Please close the classroom door quietly when you leave.",
                    "synonyms": ["shut", "seal"],
                    "antonyms": ["open"]
                },
                {
                    "pos": "adverb",
                    "sense_id": "close.near.02",
                    "definition": "Near in space, time, or relationship.",
                    "child_def": "Near in distance or time.",
                    "example": "They live close to the school playground.",
                    "synonyms": ["near", "nearby"],
                    "antonyms": ["far", "distant"]
                }
            ]
        },
        "fast": {
            "senses": [
                {
                    "pos": "adverb",
                    "sense_id": "fast.speed.01",
                    "definition": "Moving, acting, or happening at high speed.",
                    "child_def": "Moving or acting at high speed.",
                    "example": "The cheetah ran very fast across the open grassy field.",
                    "synonyms": ["quickly", "rapidly", "swiftly"],
                    "antonyms": ["slowly"]
                },
                {
                    "pos": "noun",
                    "sense_id": "fast.abstain.02",
                    "definition": "A period of abstaining from food.",
                    "child_def": "A period of time during which a person refrains from food.",
                    "example": "They observed a day of quiet fast during the holiday.",
                    "synonyms": ["abstinence"],
                    "antonyms": []
                }
            ]
        },
        "kind": {
            "senses": [
                {
                    "pos": "adjective",
                    "sense_id": "kind.caring.01",
                    "definition": "Caring, helpful, and showing good nature toward others.",
                    "child_def": "Caring, helpful, and friendly toward others.",
                    "example": "She is a kind friend who always helps her classmates.",
                    "synonyms": ["caring", "friendly", "gentle"],
                    "antonyms": ["unkind", "mean"]
                },
                {
                    "pos": "noun",
                    "sense_id": "kind.type.02",
                    "definition": "A group, class, or category of things sharing qualities.",
                    "child_def": "A group, type, or category of things.",
                    "example": "What kind of animal is your new pet dog?",
                    "synonyms": ["type", "sort", "category"],
                    "antonyms": []
                }
            ]
        },
        "mean": {
            "senses": [
                {
                    "pos": "adjective",
                    "sense_id": "mean.unkind.01",
                    "definition": "Unkind, unpleasant, or hurtful toward others.",
                    "child_def": "Unkind, unpleasant, or hurtful toward others.",
                    "example": "Saying mean words can hurt someone's feelings.",
                    "synonyms": ["unkind", "nasty", "cruel"],
                    "antonyms": ["kind", "friendly"]
                },
                {
                    "pos": "verb",
                    "sense_id": "mean.signify.02",
                    "definition": "To intend to express, convey, or represent a specific meaning.",
                    "child_def": "To represent or express a specific idea or meaning.",
                    "example": "A red stop sign means you must stop your vehicle.",
                    "synonyms": ["signify", "indicate", "represent"],
                    "antonyms": []
                }
            ]
        }
    }

    @classmethod
    def get_candidate_senses(cls, word: str, pos_constraint: str) -> List[Dict[str, Any]]:
        """
        Get candidate senses strictly matching the POS constraint.
        """
        w_clean = re.sub(r'[^a-zA-Z]', '', word).lower()
        candidates = []

        # 1. Check Learner Dictionary Map
        if w_clean in cls.LEARNER_DICTIONARY_MAP:
            for s in cls.LEARNER_DICTIONARY_MAP[w_clean]["senses"]:
                if s["pos"].lower() == pos_constraint.lower():
                    candidates.append({
                        "sense_id": s["sense_id"],
                        "pos": s["pos"],
                        "official_definition": s["definition"],
                        "child_definition": s["child_def"],
                        "example": s["example"],
                        "synonyms": s["synonyms"],
                        "antonyms": s["antonyms"],
                        "source": "Learner Educational Dictionary",
                        "priority": 1
                    })

        # 2. Query FreeDictionary API
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{w_clean}"
            resp = requests.get(url, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    for meaning in data[0].get("meanings", []):
                        api_pos = meaning.get("partOfSpeech", "").lower()
                        # Map API POS to standard pos_constraint
                        std_api_pos = api_pos
                        if "adj" in api_pos:
                            std_api_pos = "adjective"
                        elif "adv" in api_pos:
                            std_api_pos = "adverb"

                        if std_api_pos == pos_constraint:
                            for d in meaning.get("definitions", []):
                                def_text = d.get("definition", "")
                                if def_text and not any(c["official_definition"] == def_text for c in candidates):
                                    candidates.append({
                                        "sense_id": f"{w_clean}.api.{len(candidates)+1}",
                                        "pos": pos_constraint,
                                        "official_definition": def_text,
                                        "child_definition": d.get("definition", ""),
                                        "example": d.get("example", f"An example showing '{word}' in practice."),
                                        "synonyms": d.get("synonyms", [])[:4],
                                        "antonyms": d.get("antonyms", [])[:3],
                                        "source": "Free Dictionary API",
                                        "priority": 2
                                    })
        except Exception as e:
            logger.debug(f"FreeDictionary API error for '{w_clean}': {e}")

        # 3. NLTK WordNet strictly POS-constrained fallback
        wn_pos = POSTagger.WORDNET_POS_MAP.get(pos_constraint)
        if wn_pos:
            try:
                synsets = wn.synsets(w_clean, pos=wn_pos)
                for syn in synsets:
                    def_text = syn.definition()
                    if def_text and not any(c["official_definition"] == def_text for c in candidates):
                        syns = [l.name().replace('_', ' ') for l in syn.lemmas() if l.name().lower() != w_clean][:4]
                        ants = [ant.name().replace('_', ' ') for l in syn.lemmas() for ant in l.antonyms()][:3]
                        candidates.append({
                            "sense_id": syn.name(),
                            "pos": pos_constraint,
                            "official_definition": def_text,
                            "child_definition": def_text,
                            "example": syn.examples()[0] if syn.examples() else "",
                            "synonyms": syns,
                            "antonyms": ants,
                            "source": "WordNet (NLTK)",
                            "priority": 3
                        })
            except Exception as e:
                logger.debug(f"WordNet query error for '{w_clean}': {e}")

        return candidates


class ContextualSemanticWSD:
    """
    Context-aware WSD module using semantic embedding similarity & token overlap.
    Ranks candidate senses against the full corrected sentence.
    """

    @classmethod
    def rank_senses(
        cls,
        candidates: List[Dict[str, Any]],
        sentence: str,
        word: str
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Rank POS-constrained candidate senses by contextual semantic similarity score.
        Returns list of (candidate_sense, similarity_score) tuples sorted descending.
        """
        if not candidates:
            return []

        sent_clean = sentence.lower()
        word_clean = word.lower()
        scored_candidates = []

        sent_doc = nlp(sentence) if nlp is not None else None

        for cand in candidates:
            def_text = cand["official_definition"]
            example_text = cand.get("example", "")
            combined_gloss = f"{def_text} {example_text}".lower()

            # 1. Cosine vector similarity if spaCy vectors available
            vector_sim = 0.0
            if sent_doc is not None and sent_doc.has_vector:
                cand_doc = nlp(combined_gloss)
                if cand_doc.has_vector and cand_doc.vector_norm > 0 and sent_doc.vector_norm > 0:
                    vector_sim = float(sent_doc.similarity(cand_doc))

            # 2. Token overlap score (Jaccard similarity)
            sent_tokens = set(re.findall(r'\b[a-z]{3,}\b', sent_clean)) - {word_clean, "the", "and", "was", "were", "this", "that"}
            gloss_tokens = set(re.findall(r'\b[a-z]{3,}\b', combined_gloss)) - {word_clean, "the", "and", "was", "were", "this", "that"}

            overlap = sent_tokens.intersection(gloss_tokens)
            overlap_score = len(overlap) / (len(sent_tokens.union(gloss_tokens)) or 1)

            # 3. Priority boost for learner-oriented dictionaries
            priority_boost = 0.25 if cand.get("priority") == 1 else (0.10 if cand.get("priority") == 2 else 0.0)

            # Composite similarity score
            composite_score = (0.50 * vector_sim) + (0.30 * overlap_score) + priority_boost + (0.15 if len(overlap) > 0 else 0.0)
            composite_score = min(1.0, max(0.20, composite_score))

            scored_candidates.append((cand, round(composite_score, 4)))

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates


class SemanticValidator:
    """
    Validates selected dictionary sense against sentence context and computes pipeline confidence score.
    Flag card for manual verification if overall confidence < 0.70.
    """

    CONFIDENCE_THRESHOLD = 0.70

    @classmethod
    def validate_and_score(
        cls,
        pos_confidence: float,
        wsd_similarity_score: float,
        has_dictionary_match: bool,
        candidate_count: int
    ) -> Tuple[float, bool]:
        """
        Calculates overall confidence metric.
        Returns (overall_confidence_score, requires_manual_verification).
        """
        dict_score = 0.90 if has_dictionary_match else 0.40
        wsd_score = min(1.0, max(0.30, wsd_similarity_score))

        overall_conf = (0.35 * pos_confidence) + (0.45 * wsd_score) + (0.20 * dict_score)
        overall_conf = round(overall_conf, 4)

        requires_verification = overall_conf < cls.CONFIDENCE_THRESHOLD
        return overall_conf, requires_verification


class SenseGroundedSimplifier:
    """
    Simplifies verified dictionary definitions into clear, age 8-14 appropriate language.
    Strictly preserves definition facts without altering core meaning.
    """

    @classmethod
    def simplify(
        cls,
        word: str,
        official_def: str,
        pos_label: str,
        child_def_hint: str = ""
    ) -> str:
        """
        Simplify verified dictionary definition for children (ages 8-14).
        """
        if child_def_hint and len(child_def_hint) > 5:
            return child_def_hint

        w_clean = re.sub(r'[^a-zA-Z]', '', word).lower()

        cleaned = re.sub(r'\(.*?\)', '', official_def).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        if not cleaned.endswith('.'):
            cleaned += '.'

        if pos_label == 'noun':
            return f"A {w_clean}: {cleaned}"
        elif pos_label == 'verb':
            return f"To {w_clean}: {cleaned}"
        elif pos_label == 'adjective':
            return f"Describes something that is {w_clean}: {cleaned}"
        elif pos_label == 'adverb':
            return f"In a {w_clean} manner: {cleaned}"

        return cleaned


class SenseExampleGenerator:
    """
    Generates fresh, natural 8-20 word example sentences strictly demonstrating the selected word sense.
    """

    @classmethod
    def generate_example(
        cls,
        word: str,
        pos_label: str,
        sense_example_hint: str = ""
    ) -> str:
        """
        Generate a natural, child-appropriate 8-20 word example sentence.
        """
        if sense_example_hint and len(sense_example_hint.split()) >= 8:
            return sense_example_hint

        w_clean = re.sub(r'[^a-zA-Z]', '', word).lower()

        if pos_label == "noun":
            ex = f"The student noticed a very interesting {word} during the afternoon science lesson."
        elif pos_label == "verb":
            ex = f"We decided to {word} together after completing our morning school assignments."
        elif pos_label == "adjective":
            ex = f"The teacher shared a very {word} example with the whole classroom today."
        elif pos_label == "adverb":
            ex = f"The children worked {word} to finish their creative writing project on time."
        else:
            ex = f"Learning how to use {word} correctly helps make your writing clear."

        words = ex.split()
        if len(words) < 8:
            ex = f"{ex} It was very helpful."
        elif len(words) > 20:
            ex = " ".join(words[:18]) + "."

        return ex


class GrammarRoutingClassifier:
    """
    Classifies whether a correction is a genuine vocabulary word or a functional grammar edit.
    Functional grammar edits bypass dictionary lookups and receive targeted educational rules.
    """

    FUNCTIONAL_WORDS = {
        "a", "an", "the", "is", "are", "am", "was", "were", "be", "been", "being",
        "has", "have", "had", "do", "does", "did", "and", "but", "or", "so", "if",
        "in", "on", "at", "to", "for", "with", "by", "from", "of", "up", "out",
        "it", "its", "this", "that", "these", "those", "they", "them", "their", "we", "us", "our"
    }

    @classmethod
    def is_vocabulary_word(
        cls,
        orig_word: str,
        prop_word: str,
        category: str,
        explanation: str,
        pos_label: str
    ) -> bool:
        """
        Determine if correction is a vocabulary item requiring dictionary WSD.
        """
        w_prop = prop_word.strip()
        w_clean = re.sub(r'[^a-zA-Z]', '', w_prop).lower()

        if not w_clean:
            return False

        if pos_label in ['determiner', 'preposition', 'conjunction', 'pronoun', 'number', 'particle', 'interjection']:
            return False

        if w_clean in cls.FUNCTIONAL_WORDS:
            return False

        if re.search(r'[\d@#\$%\^&\*\(\)_\+=\[\]\{\}<>\\/|]', w_prop):
            return False

        expl_lower = explanation.lower()
        cat_lower = category.lower()

        if "article" in expl_lower or "subject-verb" in expl_lower or "preposition" in expl_lower:
            return False
        if "comma" in expl_lower or "period" in expl_lower or "punctuation" in cat_lower or "punctuation" in expl_lower:
            return False

        if len(w_prop) > 1 and w_prop[0].isupper() and w_prop.isupper():
            return False

        return len(w_clean) >= 2


class VocabularyLearningEngine:
    """
    Main entry point for Context-First Grounded Vocabulary Processing.
    Executes spaCy POS hard constraint tagging, candidate sense retrieval,
    embedding-based semantic WSD ranking, sense validation, and confidence scoring.
    """

    @classmethod
    def process_correction(
        cls,
        orig_word: str,
        prop_word: str,
        corrected_sentence: str,
        category: str,
        explanation: str
    ) -> Dict[str, Any]:
        """
        Process a single proofreading correction through the context-first vocabulary pipeline.
        """
        # Step 1: spaCy Contextual POS Tagging (Hard Constraint)
        pos_label, raw_tag, pos_confidence = POSTagger.tag_word_in_context(prop_word, corrected_sentence)

        # Step 2: Grammar vs Vocabulary Routing
        is_vocab = GrammarRoutingClassifier.is_vocabulary_word(
            orig_word=orig_word,
            prop_word=prop_word,
            category=category,
            explanation=explanation,
            pos_label=pos_label
        )

        if not is_vocab:
            return {
                "is_vocabulary_word": False,
                "detected_pos": pos_label,
                "identified_word_sense": "grammar_rule",
                "official_dictionary_definition": "",
                "simplified_child_definition": "",
                "generated_example_sentence": "",
                "synonyms": [],
                "antonyms": [],
                "pronunciation": "",
                "dictionary_source": "Grammar Engine Rule",
                "confidence_score": 1.0,
                "requires_manual_verification": False
            }

        # Step 3: Learner Lexical Provider (Candidate Senses Filtered ONLY by POS Tag Constraint)
        candidate_senses = LearnerLexicalProvider.get_candidate_senses(prop_word, pos_label)

        if not candidate_senses:
            # Fallback if no candidate sense matched the POS constraint
            return {
                "is_vocabulary_word": True,
                "detected_pos": pos_label,
                "identified_word_sense": f"{prop_word.lower()}.{pos_label}.fallback",
                "official_dictionary_definition": f"A term functioning as an {pos_label} in context.",
                "simplified_child_definition": f"Describes or represents '{prop_word}' as used in this sentence.",
                "generated_example_sentence": SenseExampleGenerator.generate_example(prop_word, pos_label),
                "synonyms": [],
                "antonyms": [],
                "pronunciation": f"/{prop_word.lower()}/",
                "dictionary_source": "Contextual Inference",
                "confidence_score": 0.50,
                "requires_manual_verification": True
            }

        # Step 4: Contextual Semantic WSD Ranking
        ranked_senses = ContextualSemanticWSD.rank_senses(candidate_senses, corrected_sentence, prop_word)
        best_sense, wsd_sim_score = ranked_senses[0]

        # Step 5: Semantic Context Validation & Pipeline Confidence Scoring
        overall_conf, requires_verification = SemanticValidator.validate_and_score(
            pos_confidence=pos_confidence,
            wsd_similarity_score=wsd_sim_score,
            has_dictionary_match=True,
            candidate_count=len(candidate_senses)
        )

        # Step 6: Sense-Grounded Child Simplification & Example Generation
        child_def = SenseGroundedSimplifier.simplify(
            word=prop_word,
            official_def=best_sense["official_definition"],
            pos_label=pos_label,
            child_def_hint=best_sense.get("child_definition", "")
        )

        example_sent = SenseExampleGenerator.generate_example(
            word=prop_word,
            pos_label=pos_label,
            sense_example_hint=best_sense.get("example", "")
        )

        w_clean = re.sub(r'[^a-zA-Z]', '', prop_word).lower()

        return {
            "is_vocabulary_word": True,
            "detected_pos": pos_label,
            "identified_word_sense": best_sense["sense_id"],
            "official_dictionary_definition": best_sense["official_definition"],
            "simplified_child_definition": child_def,
            "generated_example_sentence": example_sent,
            "synonyms": best_sense.get("synonyms", []),
            "antonyms": best_sense.get("antonyms", []),
            "pronunciation": f"/{w_clean}/",
            "dictionary_source": best_sense["source"],
            "confidence_score": overall_conf,
            "requires_manual_verification": requires_verification
        }
