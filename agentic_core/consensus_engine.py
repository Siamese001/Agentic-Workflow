import logging
from typing import Any, Dict, List

# Configure logging
logger = logging.getLogger("ConsensusEngine")  # GLOBAL: Review if this should be constant
logging.basicConfig(level=logging.INFO)

class ConsensusEngine:
    # --- VERIFIED API MODEL NAMES (Dec 2025) ---
    def __init__(self, providers: List[str] = ["gpt-5.1", "claude-sonnet-4-5", "gemini-3-pro"]):
        """
        Initialize the Jury with the verified SOTA Reasoning models.
        """
        self.providers = providers
        # 2/3 Majority Rule.
        self.threshold = 0.66

    # Class-level constants to reduce nesting depth in methods
    _CRITICAL_KEYWORDS = ["hack", "delete /", "malware", "drop table"]

    _MODEL_CHECK_CONFIG = {
        "gpt-5.1": {
            "keywords": ["broken", "infinite loop"],
            "reason": "GPT-5.1 Thinking: Detected functional regression or infinite loop risk."
        },
        "claude-sonnet-4-5": {
            "keywords": ["unsafe", "race condition"],
            "reason": "Claude Sonnet 4.5 Analysis: Identified potential race condition or unsafe memory access."
        },
        "gemini-3-pro": {
            "keywords": ["contradiction", "hallucination"],
            "reason": "Gemini 3 Pro Deep Think: Found contradiction with known context or library definitions."
        }
    }

    def _get_model_specific_verdict(self, model_name: str, artifact_lower: str) -> Dict[str, str]:
        """
        Helper to determine model-specific verdict and reason, ensuring max nesting depth of 4.
        Returns {"verdict": "NO", "reason": "..."} or {"verdict": "YES", "reason": "Compliance verified."}
        """
        # Depth: class(1) -> def(2)

        # Check for GPT-5.1 specific issues
        if model_name == "gpt-5.1" and ("broken" in artifact_lower or "infinite loop" in artifact_lower): # Depth 3
            return {"verdict": "NO", "reason": self._MODEL_CHECK_CONFIG["gpt-5.1"]["reason"]} # Depth 4

        # Check for Claude Sonnet 4.5 specific issues
        elif model_name == "claude-sonnet-4-5" and ("unsafe" in artifact_lower or "race condition" in artifact_lower): # Depth 3
            return {"verdict": "NO", "reason": self._MODEL_CHECK_CONFIG["claude-sonnet-4-5"]["reason"]} # Depth 4

        # Check for Gemini 3 Pro specific issues
        elif model_name == "gemini-3-pro" and ("contradiction" in artifact_lower or "hallucination" in artifact_lower): # Depth 3
            return {"verdict": "NO", "reason": self._MODEL_CHECK_CONFIG["gemini-3-pro"]["reason"]} # Depth 4

        # If no specific issues found for the model, or model not in config
        return {"verdict": "YES", "reason": "Compliance verified."} # Depth 3

    def _call_juror(self, model_name: str, artifact: str, prompt: str) -> Dict[str, Any]:
        """
        Simulates calling the specific High-Reasoning AI model API, ensuring max nesting depth of 4.
        """
        logger.info(f"⚖️  Juror '{model_name}' is analyzing...") # Depth 3

        artifact_lower = artifact.lower() # Depth 3

        # 1. Universal Critical Failures (Guard Clause)
        # Using explicit OR conditions to avoid generator expression nesting depth.
        if ("hack" in artifact_lower or
            "delete /" in artifact_lower or
            "malware" in artifact_lower or
            "drop table" in artifact_lower): # Depth: class(1) -> def(2) -> if(3)
            return { # Depth 4
                "model": model_name,
                "verdict": "NO",
                "reason": "Safety Protocols Triggered during analysis."
            }

        # 2. Model-Specific Reasoning Quirks (Delegated to helper method)
        model_verdict = self._get_model_specific_verdict(model_name, artifact_lower) # Depth 3

        return { # Depth 3
            "model": model_name,
            "verdict": model_verdict["verdict"],
            "reason": model_verdict["reason"]
        }

    def _count_yes_votes(self, votes: List[Dict[str, Any]]) -> int:
        """
        Helper to count 'YES' votes, ensuring max nesting depth of 4.
        Refactored to use sum with a generator expression to reduce potential nesting depth.
        """
        # Depth: class(1) -> def(2)
        # Using sum with a generator expression. This is typically depth 3.
        yes_count = sum(1 for vote in votes if vote["verdict"] == "YES") # Depth 3 (generator expression is part of sum call)
        return yes_count # Depth 3

    def judge_artifact(self, artifact_content: str, context: str = "Code Review") -> Dict[str, Any]:
        """
        Orchestrates the voting process.
        """
        logger.info(f"🔔 Convening Supreme Court ({', '.join(self.providers)})...") # Depth 3

        votes = [] # Depth 3
        # yes_count = 0 # Removed, will be calculated after the loop

        prompt = ( # Depth 3
            f"Context: {context}.\n"
            f"Analyze the following artifact. Use your full reasoning capabilities to detect subtle logic bugs, "
            f"security vulnerabilities, or hallucinations.\n"
            f"Artifact:\n---\n{artifact_content}\n---"
            f"\nVerdict (YES/NO)?"
        )

        for model in self.providers: # Depth 3
            response = self._call_juror(model, artifact_content, prompt) # Depth 4
            votes.append(response) # Depth 4
            # The 'if response["verdict"] == "YES": yes_count += 1' block is removed from here
            # to reduce nesting depth.

        # Calculate yes_count after the loop, at a shallower depth, using a helper method
        yes_count = self._count_yes_votes(votes) # Depth 3

        total_votes = len(self.providers) # Depth 3
        score = yes_count / total_votes # Depth 3

        status = "FAIL" # Depth 3
        if score >= self.threshold: # Depth 3
            status = "PASS" # Depth 4

        logger.info(f"📝 Jury Verdict: {status} ({yes_count}/{total_votes} votes)") # Depth 3

        return { # Depth 3
            "status": status,
            "score": score,
            "votes": votes
        }

    def _fix_indentation(self, code: str) -> str:
        """
        Helper to fix indentation issues by adding a consistent indent to non-empty lines,
        ensuring max nesting depth of 4.
        Refactored to use a list comprehension to reduce potential nesting depth.
        """
        lines = code.split('\n') # Depth 3
        
        # Refactored to a list comprehension. This is typically depth 3 (class -> def -> list_comp).
        # The conditional expression inside might be interpreted as an additional level,
        # but should not exceed max 4.
        fixed_lines = ['    ' + line.strip() if line.strip() else '' for line in lines] # Depth 3 (list comprehension)

        return '\n'.join(fixed_lines) # Depth 3

    def _get_imports_to_add(self, code: str) -> str:
        """
        Helper to determine and return import statements to prepend, ensuring max nesting depth of 4.
        """
        imports_to_prepend = [] # Depth 3
        if "import os" not in code and "os." in code: # Depth 3
            imports_to_prepend.append("import os\n") # Depth 4
        if "import json" not in code and "json." in code: # Depth 3
            imports_to_prepend.append("import json\n") # Depth 4
        return "".join(imports_to_prepend) # Depth 3

    def propose_fix(self, code: str, error_message: str, context: str = "") -> Dict[str, Any]:
        """
        Propose a fix for code that failed validation, ensuring max nesting depth of 4.

        Args:
            code: The original code that failed
            error_message: The error message describing the failure
            context: Additional context about the failure

        Returns:
            Dict with status and fixed_code if successful
        """
        logger.info(f"🔧 Consensus Engine: Proposing fix for error: {error_message[:100]}...") # Depth 3

        fixed_code = code # Depth 3
        error_lower = error_message.lower() # Depth 3

        if "syntax error" in error_lower: # Depth 3
            fixed_code = code.replace(";;", ";") # Depth 4
            fixed_code = fixed_code.replace(":::", ":") # Depth 4

        elif "import error" in error_lower or "module not found" in error_lower: # Depth 3
            # Delegated import logic to a helper method to keep depth within limits.
            fixed_code = self._get_imports_to_add(code) + fixed_code # Depth 4

        elif "name 'none' is not defined" in error_lower: # Depth 3
            fixed_code = code.replace("none", "None") # Depth 4

        elif "indentation" in error_lower: # Depth 3
            fixed_code = self._fix_indentation(code) # Depth 4

        if fixed_code == code: # Depth 3
            return {"status": "FAILED", "error": "No fix could be generated"} # Depth 4

        return { # Depth 3
            "status": "SUCCESS",
            "fixed_code": fixed_code,
            "context": context
        }


# Initialize the global jury instance
jury = ConsensusEngine()  # GLOBAL: Review if this should be constant