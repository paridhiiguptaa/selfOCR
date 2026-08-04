import re
import time
import json
from typing import List, Dict, Any, Optional
from ..utils.logging_config import logger

class SubjectDetectionModule:
    """
    Analyzes document headings, titles, keywords, and text content
    to classify educational document subjects and load subject-specific language priors.
    """

    SUBJECT_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
        "Science": {
            "display_name": "Elementary & Middle School Science",
            "keywords": [
                "science", "matter", "solid", "liquid", "gas", "gases", "volume", "density",
                "mass", "evaporation", "condensation", "melting", "freezing", "experiment",
                "observation", "hypothesis", "conclusion", "property", "properties", "transparent",
                "opaque", "translucent", "energy", "force", "motion", "gravity", "friction",
                "magnet", "magnetic", "circuit", "light", "shadow", "reflection", "temperature",
                "thermometer", "heat", "boiling", "solution", "mixture", "dissolve"
            ],
            "title_patterns": [
                r'properties\s+of\s+matter', r'states\s+of\s+matter', r'light\s+shadow',
                r'science\s+notes?', r'chapter\s*\d*\s*:?\s*science'
            ],
            "sample_patterns": [
                "Everything around us is made of matter.",
                "Matter exists in three states: solid, liquid and gases.",
                "Solids have a fixed shape and volume."
            ]
        },
        "Mathematics": {
            "display_name": "Mathematics & Geometry",
            "keywords": [
                "math", "mathematics", "equation", "fraction", "numerator", "denominator",
                "variable", "algebra", "geometry", "triangle", "rectangle", "square", "circle",
                "radius", "diameter", "perimeter", "area", "volume", "angle", "hypotenuse",
                "pythagoras", "theorem", "sum", "difference", "product", "quotient", "ratio",
                "percentage", "decimal", "integer", "polynomial", "function", "graph", "axis",
                "slope", "derivative", "integral", "matrix", "vector", "probability", "statistics"
            ],
            "title_patterns": [
                r'math(?:ematics)?\s+notes?', r'algebra', r'geometry', r'fraction', r'equation'
            ],
            "sample_patterns": [
                "Solve the linear equation for x.",
                "The perimeter of a rectangle is 2*(length + width).",
                "Calculate the area of the circle."
            ]
        },
        "Physics": {
            "display_name": "Physics",
            "keywords": [
                "physics", "velocity", "acceleration", "force", "newton", "gravity", "mass",
                "momentum", "kinetic", "potential", "energy", "work", "power", "joule", "watt",
                "inertia", "friction", "vector", "scalar", "displacement", "speed", "wave",
                "frequency", "wavelength", "amplitude", "optics", "refraction", "diffraction",
                "current", "voltage", "resistance", "ohm", "ampere", "magnetic", "field"
            ],
            "title_patterns": [
                r'physics', r'laws?\s+of\s+motion', r'work\s+and\s+energy', r'electricity'
            ],
            "sample_patterns": [
                "Force equals mass times acceleration.",
                "Energy can neither be created nor destroyed.",
                "Speed is defined as distance divided by time."
            ]
        },
        "Chemistry": {
            "display_name": "Chemistry",
            "keywords": [
                "chemistry", "atom", "atomic", "molecule", "molecular", "element", "compound",
                "reaction", "reactant", "product", "chemical", "acid", "base", "ph", "salt",
                "solution", "solute", "solvent", "concentration", "molarity", "valence",
                "electron", "proton", "neutron", "ion", "ionic", "covalent", "bond", "bonding",
                "periodic", "table", "oxidation", "reduction", "catalyst", "isotope"
            ],
            "title_patterns": [
                r'chemistry', r'chemical\s+reactions?', r'acids?\s+and\s+bases?', r'atomic\s+structure'
            ],
            "sample_patterns": [
                "An atom consists of protons, neutrons, and electrons.",
                "Acids react with bases to form salt and water.",
                "Chemical reactions involve breaking and forming bonds."
            ]
        },
        "Biology": {
            "display_name": "Biology & Life Sciences",
            "keywords": [
                "biology", "cell", "cellular", "photosynthesis", "chlorophyll", "plant",
                "animal", "organism", "ecosystem", "respiration", "tissue", "organ", "nucleus",
                "dna", "rna", "gene", "genetics", "enzyme", "membrane", "mitochondria", "leaf",
                "stem", "root", "blood", "heart", "circulatory", "digestive", "nervous", "species"
            ],
            "title_patterns": [
                r'biology', r'life\s+processes', r'plants?\s+and\s+animals?', r'cell\s+structure'
            ],
            "sample_patterns": [
                "Plants prepare their food by photosynthesis.",
                "Leaves contain a green pigment called chlorophyll.",
                "The cell is the basic structural unit of life."
            ]
        },
        "Geography": {
            "display_name": "Geography & Earth Sciences",
            "keywords": [
                "geography", "latitude", "longitude", "equator", "hemisphere", "continent",
                "ocean", "climate", "weather", "erosion", "weathering", "atmosphere", "crust",
                "mantle", "core", "volcano", "earthquake", "glacier", "topography", "map",
                "river", "mountain", "plateau", "plain", "sediment", "soil", "tropic", "poles"
            ],
            "title_patterns": [
                r'geography', r'earth\s+science', r'climate\s+and\s+weather', r'maps?\s+and\s+globes?'
            ],
            "sample_patterns": [
                "Latitude lines run horizontally parallel to the equator.",
                "Erosion is the wearing away of the Earth's surface by wind or water.",
                "The Earth is divided into seven major continents."
            ]
        },
        "History": {
            "display_name": "History & Social Studies",
            "keywords": [
                "history", "century", "empire", "emperor", "king", "queen", "dynasty", "revolution",
                "treaty", "war", "battle", "independence", "reign", "civilization", "constitution",
                "colony", "colonial", "movement", "charter", "monarchy", "republic", "ancient", "medieval"
            ],
            "title_patterns": [
                r'history', r'social\s+studies', r'ancient\s+civilization', r'freedom\s+movement'
            ],
            "sample_patterns": [
                "The empire expanded across multiple continents during the 18th century.",
                "The treaty was signed following the end of the conflict.",
                "The constitution established democratic governance."
            ]
        },
        "Computer Science": {
            "display_name": "Computer Science & Information Technology",
            "keywords": [
                "computer", "code", "coding", "algorithm", "programming", "python", "java",
                "variable", "function", "loop", "iteration", "array", "binary", "compiler",
                "network", "database", "memory", "cpu", "software", "hardware", "internet", "protocol"
            ],
            "title_patterns": [
                r'computer\s+science', r'programming', r'data\s+structures?', r'python'
            ],
            "sample_patterns": [
                "An algorithm is a step-by-step set of instructions.",
                "Variables store data values in memory.",
                "Loops execute a block of code repeatedly until a condition is met."
            ]
        },
        "English": {
            "display_name": "English Language & Literature",
            "keywords": [
                "english", "grammar", "noun", "verb", "adjective", "adverb", "pronoun",
                "preposition", "conjunction", "interjection", "sentence", "paragraph", "essay",
                "prose", "poetry", "poem", "stanza", "rhyme", "metaphor", "simile", "alliteration",
                "synonym", "antonym", "punctuation", "comprehension", "summary", "character"
            ],
            "title_patterns": [
                r'english', r'grammar', r'literature', r'reading\s+comprehension', r'poetry'
            ],
            "sample_patterns": [
                "Nouns are words that name a person, place, thing, or idea.",
                "A metaphor is a figure of speech comparing two unlike things.",
                "Identify the main theme of the story."
            ]
        }
    }

    def detect_subject(
        self,
        text: str,
        document_title: Optional[str] = None,
        headings: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze text content, title, and headings to classify subject domain.
        Returns:
        {
          "subject": str,
          "display_name": str,
          "confidence": float,
          "keywords": List[str],
          "sample_patterns": List[str]
        }
        """
        if not text and not document_title and not headings:
            return self._default_result()

        combined_text = (document_title or "") + " " + " ".join(headings or []) + " " + (text or "")
        text_lower = combined_text.lower()

        scores: Dict[str, float] = {}

        for subject_key, info in self.SUBJECT_KNOWLEDGE_BASE.items():
            score = 0.0

            # 1. Title pattern match (High weight)
            for pat in info["title_patterns"]:
                if re.search(pat, text_lower):
                    score += 0.40

            # 2. Keyword frequency match
            kw_matches = sum(1 for kw in info["keywords"] if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
            if kw_matches > 0:
                score += min(0.50, kw_matches * 0.06)

            scores[subject_key] = score

        best_subject = "General"
        max_score = 0.0

        for subj, sc in scores.items():
            if sc > max_score:
                max_score = sc
                best_subject = subj

        if max_score < 0.15:
            return self._default_result()

        conf = min(0.98, max(0.55, max_score))
        info = self.SUBJECT_KNOWLEDGE_BASE[best_subject]

        logger.info(f"Subject Detection: Identified '{best_subject}' (Confidence: {conf:.2f})")

        return {
            "subject": best_subject,
            "display_name": info["display_name"],
            "confidence": round(conf, 4),
            "keywords": info["keywords"],
            "sample_patterns": info["sample_patterns"]
        }

    def _default_result(self) -> Dict[str, Any]:
        return {
            "subject": "General",
            "display_name": "General Educational Notebook",
            "confidence": 0.50,
            "keywords": [],
            "sample_patterns": []
        }
