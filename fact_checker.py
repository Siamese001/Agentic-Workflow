import json
import os
import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger("FactChecker")
logging.basicConfig(level=logging.INFO)

class HallucinationException(Exception):
    """Raised when the agent invents facts not in the golden record."""
    pass

class FactChecker:
    def __init__(self, record_path: str = "config/golden_record.json"):
        self.record_path = record_path
        self.data = self._load_record()
        # Normalize skills for case-insensitive comparison
        self.verified_skills = {s.lower() for s in self.data.get("profile", {}).get("verified_skills", [])}

    def _load_record(self) -> Dict:
        if not os.path.exists(self.record_path):
            logger.warning(f"Golden Record not found at {self.record_path}. Fact checking disabled.")
            return {}
        try:
            with open(self.record_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Golden Record: {e}")
            return {}

    def validate_skills(self, draft_text: str) -> bool:
        """
        Scans the draft for a 'Skills' section and verifies listed items.
        
        Strategy:
        1. Find the 'Skills' section (heuristic).
        2. Extract comma/bullet-separated items.
        3. Check if each item is in the verified_skills set.
        """
        if not self.verified_skills:
            return True # Fail open if no config

        # Simple heuristic: Look for lines starting with "Skills:" or inside a Skills section
        # This regex looks for a line starting with "Skills:" and captures the text after it
        skills_match = re.search(r"(?:Skills|Technologies|Stack)[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)", draft_text, re.IGNORECASE | re.DOTALL)
        
        if not skills_match:
            logger.info("No explicit 'Skills' section found to validate.")
            return True

        raw_skills_text = skills_match.group(1)
        # Split by comma, pipe, or bullet points
        candidates = re.split(r'[,|•\n]', raw_skills_text)
        
        hallucinations = []
        
        for candidate in candidates:
            clean_candidate = candidate.strip()
            if not clean_candidate:
                continue
                
            # Check if the candidate is contained in our verified list (fuzzy match)
            # We check if the candidate *contains* a verified skill, or IS a verified skill.
            # "Expert in Python" -> valid because "Python" is verified.
            # "Rust Programming" -> invalid if "Rust" is not verified.
            
            # Strict check: is the core noun in our list?
            # For this MVP, we check if the candidate string is present in our allowed set
            # OR if any allowed skill is a substring of the candidate.
            
            is_verified = False
            if clean_candidate.lower() in self.verified_skills:
                is_verified = True
            else:
                for v_skill in self.verified_skills:
                    if v_skill in clean_candidate.lower():
                        is_verified = True
                        break
            
            if not is_verified:
                # One last check: Is it just a filler word? (e.g. "and", "etc")
                if len(clean_candidate) > 2 and clean_candidate.lower() not in ["and", "etc", "various"]:
                    hallucinations.append(clean_candidate)

        if hallucinations:
            msg = f"Hallucinated skills detected: {hallucinations}"
            logger.warning(msg)
            raise HallucinationException(msg)
            
        return True

# Singleton
fact_checker = FactChecker()
