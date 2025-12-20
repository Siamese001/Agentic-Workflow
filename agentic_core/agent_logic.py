I have carefully reviewed the provided Python code, focusing on syntax, style (PEP 8), and logical consistency, especially concerning the AST comparison.

Here's a summary of the issues found and the fixes applied:

1.  **AST Comparison Logic Error**:
    *   **Problem**: The `_calculate_ast_similarity` method was attempting to parse `ast.dump(tree)` output (a string representation of an AST) as if it were actual Python code using `ast.parse()`. This is incorrect and would lead to `SyntaxError` unless the `ast.dump` output coincidentally happened to be valid Python code.
    *   **Fix**:
        *   Modified `_calculate_ast_similarity` to accept `code1: str, code2: str` (the original Python code snippets) instead of `ast1_str, ast2_str` (the `ast.dump` outputs).
        *   Updated `_validate_ast_match` to pass `new_entry.code_snippet` and `existing_entry.code_snippet` to `_calculate_ast_similarity`.
        *   The `ast_structure` field in `CanonEntry` still stores `ast.dump(tree)` or an error JSON, which is correctly used by `_handle_ast_parsing_errors` for initial error checks.

2.  **Unique ID Generation**:
    *   **Problem**: The `_generate_entry` method used `hash(code)` and `datetime.now().timestamp()` to create `entry_id`. `hash(code)` is not guaranteed to be consistent across different Python runs or processes, and `timestamp()` might not be unique enough for rapid calls.
    *   **Fix**: Imported the `uuid` module and changed `entry_id` generation to `str(uuid.uuid4())` for a universally unique identifier.

3.  **Logging and Clarity**:
    *   **Improvement**: Enhanced several `logger.info` and `logger.warning` messages to provide more context, such as including specific counts or threshold values.
    *   **Example**: `Recorded failure for pattern {entry.id}. Failure count: {entry.failure_count}`.

4.  **Consistency in `search_patterns` Thresholds**:
    *   **Problem**: The `l1_threshold` in `check_and_learn` was initially `0.0` in the `search_patterns` call, while the docstring mentioned `similarity > 0.9`.
    *   **Fix**: Aligned `l1_threshold` to `0.9` in both `check_and_learn` and `search_similar_patterns` for consistency with the stated intent of L1 being for high-similarity matches.

5.  **Robustness in JSON Parsing**:
    *   **Improvement**: Added `.strip()` to the `ast_str` check in `_extract_ast_error_message` to handle potential leading/trailing whitespace before checking for the `{"error":` prefix.

6.  **Handling Unknown Outcomes**:
    *   **Improvement**: Added an `else` block in `update_learning` to log a warning if an unknown `outcome` string is provided.

7.  **Ambiguity of `promote_to_l2`**:
    *   **Note**: The method `self.db_manager.promote_to_l2(entry)` is called in contexts that suggest promoting an entry *to* L2 (Qdrant) or *to* L1 (Redis) for faster access. The name `promote_to_l2` is ambiguous if L2 is Qdrant and L1 is Redis. I've kept the original calls but added comments to highlight this potential ambiguity, as resolving it would require understanding the exact implementation of `HybridDatabaseManager`.

The refactored code is provided below:

import ast
import json
import logging
import uuid  # Added for unique ID generation
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from db_manager import HybridDatabaseManager

from core.semantic_gatekeeper import get_gatekeeper
from schemas import CanonEntry

logger = logging.getLogger(__name__)


class CanonValidator:
    """
    The L5 Meta-Learner that validates code against the Canon.

    This class implements the core logic for:
    1. Querying L1 (Redis) for similar patterns
    2. Falling back to L2 (Qdrant) if needed
    3. Comparing AST structures for validation
    4. Updating learning based on outcomes
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333
    ):
        """Initialize the Canon Validator with hybrid cache."""
        self.db_manager = HybridDatabaseManager(
            redis_host=redis_host,
            redis_port=redis_port,
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port
        )

        self.gatekeeper = get_gatekeeper()

        self.promotion_threshold = 3
        self.failure_threshold = 5

        logger.info("CanonValidator initialized with hybrid cache")

    def _safe_parse_ast(self, code: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Safely parses code into an AST string representation.
        Returns (ast_string, error_message)
        """
        try:
            tree = ast.parse(code)
            return ast.dump(tree), None
        except SyntaxError as e:
            return None, str(e)
        except Exception as e:
            # Catching a broader exception for unexpected issues during parsing
            return None, f"Unexpected AST parsing error: {e}"

    def _generate_entry(self, code: str, metadata: Optional[Dict[str, Any]] = None) -> CanonEntry:
        """
        Generates a CanonEntry from code and metadata.
        This helper method encapsulates the logic for creating a CanonEntry,
        including AST parsing and embedding generation.
        """
        ast_representation: str
        ast_dump_str, ast_error = self._safe_parse_ast(code)
        if ast_error:
            # Store error message in AST representation if parsing failed
            ast_representation = json.dumps({"error": ast_error})
            logger.error(f"Error parsing code for CanonEntry: {ast_error}")
        else:
            ast_representation = ast_dump_str

        embedding: List[float]
        try:
            embedding = self.gatekeeper.embed_text(code)
        except Exception as e:
            embedding = []  # Fallback to empty list if embedding fails
            logger.error(f"Error generating embedding for CanonEntry: {e}")

        entry_metadata = metadata or {}
        entry_metadata.update({
            "embedding_generated_at": datetime.now(timezone.utc).isoformat()
        })

        # Generate a unique ID for the entry using uuid.uuid4()
        # This ensures uniqueness and consistency across runs/processes.
        entry_id = str(uuid.uuid4())

        return CanonEntry(
            id=entry_id,
            code_snippet=code,
            embedding=embedding,
            ast_structure=ast_representation,
            metadata=entry_metadata
        )

    def check_and_learn(self, new_code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check code against the Canon and learn from results.

        Process:
        1. Generate embedding/AST for new_code
        2. Query L1 (Redis) with similarity > 0.9 and filter failures
        3. If miss, query L2 (Qdrant)
        4. Compare AST structures if hit found
        5. Return validation result

        Args:
            new_code: Python code to validate
            context: Optional context information

        Returns:
            Dictionary with validation result and metadata
        """
        # Generate entry for new code
        metadata = context or {}
        metadata.update({
            "canon_rule_id": metadata.get("canon_rule_id", "validation"),
            "project_context": metadata.get("project_context", "validation"),
            "validation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        new_entry = self._generate_entry(new_code, metadata)

        # Query L1 (Redis) - fast working memory
        # L1 is for very high similarity matches, typically > 0.9
        l1_results, l2_results = self.db_manager.search_patterns(
            query_vector=new_entry.embedding,
            l1_threshold=0.9,
            l2_threshold=0.7,
            filter_failures=True
        )

        # Initialize default result
        result = self._initialize_validation_result()

        # Process matches using extracted helpers
        if l1_results:
            # Assuming l1_results are sorted by similarity, take the best match
            result.update(self._process_l1_match(new_entry, l1_results[0]))
        elif l2_results:
            # Assuming l2_results are sorted by similarity, take the best match
            result.update(self._process_l2_match(new_entry, l2_results[0]))

        # Store the new pattern in L1 for future learning, regardless of match
        # This allows new patterns to be quickly available for subsequent checks.
        self.db_manager.store_pattern(new_entry, store_in_l2=False)

        return result

    def _parse_json_safely(self, json_str: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to safely parse a JSON string.
        Reduces nesting depth in _extract_ast_error_message.
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.debug("Malformed JSON string encountered (JSONDecodeError).")
            return None
        except Exception as e:
            logger.debug(f"Unexpected error during JSON parsing: {e}")
            return None

    def _extract_ast_error_message(self, ast_str: str) -> Optional[str]:
        """
        Extracts an error message from a potential JSON-encoded AST error string.
        Returns the error message if found and valid, otherwise None.
        """
        # Check if the string looks like a JSON error object
        if not ast_str.strip().startswith('{"error":'):
            return None

        error_dict = self._parse_json_safely(ast_str)

        if error_dict and isinstance(error_dict, dict) and "error" in error_dict:
            return error_dict["error"]

        return None

    def _handle_ast_parsing_errors(self, new_ast_str: str, existing_ast_str: str) -> Optional[Dict[str, Any]]:
        """
        Checks for AST parsing errors in new and existing AST strings.
        Returns a validation result dictionary if an error is found, otherwise None.
        """
        new_ast_error = self._extract_ast_error_message(new_ast_str)
        if new_ast_error:
            return {
                "is_match": False,
                "is_valid": False,
                "confidence": 0.0,
                "recommendation": f"Syntax error in new code: {new_ast_error}"
            }

        existing_ast_error = self._extract_ast_error_message(existing_ast_str)
        if existing_ast_error:
            return {
                "is_match": False,
                "is_valid": False,
                "confidence": 0.0,
                "recommendation": f"Reference pattern has syntax error: {existing_ast_error}"
            }
        return None

    def _validate_ast_match(
        self,
        new_entry: CanonEntry,
        existing_entry: CanonEntry
    ) -> Dict[str, Any]:
        """
        Validate AST structures between two entries.

        Compares structural patterns to determine if the code
        follows the same pattern as a known good/bad example.

        Args:
            new_entry: New code entry
            existing_entry: Existing pattern entry

        Returns:
            Validation result with match details
        """
        # Extract AST structures (which are string representations, potentially error JSONs)
        new_ast_str = new_entry.ast_structure
        existing_ast_str = existing_entry.ast_structure

        # Check for errors by attempting to parse JSON error strings
        error_result = self._handle_ast_parsing_errors(new_ast_str, existing_ast_str)
        if error_result:
            return error_result

        # Calculate AST similarity using the original code snippets
        # FIX: Pass code_snippet instead of ast_dump_str to _calculate_ast_similarity
        similarity = self._calculate_ast_similarity(new_entry.code_snippet, existing_entry.code_snippet)

        # Check if existing pattern is successful
        success_rate = existing_entry.get_success_rate()

        # Determine validity based on similarity and success rate
        # A similarity threshold of 0.7 and success rate > 0.5 are used as examples.
        # These thresholds might need tuning.
        is_valid = similarity > 0.7 and success_rate > 0.5

        return {
            "is_match": similarity > 0.7,  # Indicates if ASTs are structurally similar
            "is_valid": is_valid,          # Indicates if the pattern is considered valid based on history
            "confidence": similarity,
            "recommendation": self._generate_recommendation(similarity, success_rate)
        }

    def _get_ast_node_types_from_tree(self, tree: ast.AST) -> Set[str]:
        """
        Helper method to extract unique node types from an AST tree.
        Reduces nesting depth in _calculate_ast_similarity.
        """
        return set(type(node).__name__ for node in ast.walk(tree))

    def _calculate_ast_similarity(self, code1: str, code2: str) -> float:
        """
        Calculate similarity between two AST structures by parsing their original code.

        Simple implementation based on Jaccard similarity of unique node types.
        In production, this would use more sophisticated algorithms (e.g., tree edit distance,
        or more advanced AST comparison libraries).

        Args:
            code1: First Python code string
            code2: Second Python code string

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Parse original code strings to AST trees
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)

            # Get unique node types using the helper method
            types1 = self._get_ast_node_types_from_tree(tree1)
            types2 = self._get_ast_node_types_from_tree(tree2)

            # Calculate Jaccard similarity of node types
            intersection = len(types1.intersection(types2))
            union = len(types1.union(types2))

            return intersection / union if union > 0 else 0.0

        except SyntaxError as e:
            logger.error(f"Syntax error encountered while parsing code for AST similarity: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Unexpected error during AST similarity calculation: {e}")
            return 0.0

    def _generate_recommendation(self, similarity: float, success_rate: float) -> str:
        """Generate recommendation based on similarity and success rate."""
        if similarity > 0.8 and success_rate > 0.8:
            return "Code matches a highly successful pattern - proceed"
        elif similarity > 0.7 and success_rate > 0.5:
            return "Code matches a known pattern - use with caution"
        elif similarity > 0.7 and success_rate <= 0.5:
            return "Code matches a pattern with mixed results - review carefully"
        else:
            return "Code appears to be unique - validate thoroughly"

    def _initialize_validation_result(self) -> Dict[str, Any]:
        """Initialize default validation result structure."""
        return {
            "is_valid": True,
            "confidence": 1.0,
            "matched_pattern": None,
            "source": "no_match",
            "ast_match": False,
            "recommendation": "Code appears to be new and valid"
        }

    def _process_l1_match(self, new_entry: CanonEntry, best_match: CanonEntry) -> Dict[str, Any]:
        """Process L1 Redis match and return validation result."""
        validation = self._validate_ast_match(new_entry, best_match)

        result = {
            "matched_pattern": best_match.id,
            "source": "L1_Redis",
            "ast_match": validation["is_match"],
            "confidence": validation["confidence"],
            "is_valid": validation["is_valid"],
            "recommendation": validation["recommendation"]
        }

        logger.info(f"L1 match found: {best_match.id}. Is valid: {validation['is_valid']}")
        return result

    def _process_l2_match(self, new_entry: CanonEntry, best_match: CanonEntry) -> Dict[str, Any]:
        """Process L2 Qdrant match, promote if valid, and return validation result."""
        validation = self._validate_ast_match(new_entry, best_match)

        result = {
            "matched_pattern": best_match.id,
            "source": "L2_Qdrant",
            "ast_match": validation["is_match"],
            "confidence": validation["confidence"],
            "is_valid": validation["is_valid"],
            "recommendation": validation["recommendation"]
        }

        logger.info(f"L2 match found: {best_match.id}. Is valid: {validation['is_valid']}")

        # Promote to L1 if valid and meets promotion criteria (e.g., sufficient success count)
        # The `promote_to_l2` method in db_manager might handle the actual promotion logic
        # based on success counts, but here we're just indicating a valid L2 match.
        # If the intent is to promote a *Qdrant* entry to *Redis* (L1), the method name is misleading.
        # Assuming `promote_to_l2` actually means "promote to L1 (Redis) for faster access"
        # or "update its status in L2 to reflect its validity".
        if validation["is_valid"]:
            self.db_manager.promote_to_l2(best_match)

        return result

    def _handle_failure_outcome(self, entry: CanonEntry) -> None:
        """Helper to handle failure outcome for an entry."""
        entry.update_failure()
        logger.info(f"Recorded failure for pattern {entry.id}. Failure count: {entry.failure_count}")

        # If too many failures, consider blocking or further action
        if entry.failure_count >= self.failure_threshold:
            logger.warning(f"Pattern {entry.id} exceeded failure threshold ({self.failure_threshold}).")

    def _handle_success_outcome(self, entry: CanonEntry) -> None:
        """Helper to handle success outcome for an entry."""
        entry.update_success()
        logger.info(f"Recorded success for pattern {entry.id}. Success count: {entry.success_count}")

        # Check for promotion to L2 (Qdrant) if it meets the threshold
        # This implies moving it from L1 (Redis) to L2 (Qdrant) or updating its status in L2.
        if entry.success_count >= self.promotion_threshold:
            self.db_manager.promote_to_l2(entry) # This method name is still ambiguous.
            logger.info(f"Pattern {entry.id} promoted to L2 (Qdrant) due to success threshold ({self.promotion_threshold}).")

    def update_learning(self, entry_id: str, outcome: str, error_trace: Optional[str] = None) -> None:
        """
        Update learning based on execution outcome.

        Args:
            entry_id: ID of the pattern to update
            outcome: "SUCCESS" or "FAILURE"
            error_trace: Optional error trace for failures
        """
        # Retrieve entry from Redis (L1 cache)
        entry = self.db_manager.redis.get_entry(entry_id)

        if not entry:
            logger.warning(f"Entry {entry_id} not found in L1 for learning update.")
            # Optionally, try to retrieve from L2 if not found in L1
            # entry = self.db_manager.qdrant.get_entry(entry_id)
            # if not entry:
            #     logger.warning(f"Entry {entry_id} not found in L2 either.")
            return

        # Update based on outcome
        if outcome.upper() == "FAILURE":
            self._handle_failure_outcome(entry)
        elif outcome.upper() == "SUCCESS":
            self._handle_success_outcome(entry)
        else:
            logger.warning(f"Unknown outcome '{outcome}' for entry {entry_id}. No update performed.")
            return

        # Update the entry in Redis (L1)
        self.db_manager.redis.update_entry(entry)

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics."""
        stats = self.db_manager.get_stats()

        # Add additional learning metrics
        stats.update({
            "promotion_threshold": self.promotion_threshold,
            "failure_threshold": self.failure_threshold,
            "learning_active": True
        })

        return stats

    def _format_search_result(self, result: CanonEntry) -> Dict[str, Any]:
        """
        Helper method to format a single CanonEntry into a dictionary
        for search results, reducing nesting in search_similar_patterns.
        """
        return {
            "id": result.id,
            "success_count": result.metadata.get("success_count", 0),
            "failure_count": result.metadata.get("failure_count", 0),
            "success_rate": result.get_success_rate(),
            "project": result.metadata.get("project_context", "unknown"),
            "last_validated": result.metadata.get("last_validated"),
            "is_golden": result.metadata.get("is_golden_pattern", False)
        }

    def search_similar_patterns(
        self,
        code: str,
        max_results: int = 10,
        include_failures: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for similar patterns in the Canon.

        Args:
            code: Code to search for
            max_results: Maximum results to return
            include_failures: Whether to include failed patterns

        Returns:
            List of similar patterns with metadata
        """
        # Generate entry for search query
        query_entry = self._generate_entry(code)

        # Search both caches
        # L1 threshold is set to 0.9 to retrieve high-similarity L1 matches.
        l1_results, l2_results = self.db_manager.search_patterns(
            query_vector=query_entry.embedding,
            l1_threshold=0.9,
            l2_threshold=0.7,
            filter_failures=not include_failures
        )

        # Combine and format results, prioritizing L1 results
        all_results = l1_results + l2_results

        formatted: List[Dict[str, Any]] = []
        for result in all_results[:max_results]: # Take up to max_results from combined list
            formatted.append(self._format_search_result(result))

        return formatted