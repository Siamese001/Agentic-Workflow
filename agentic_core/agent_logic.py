import ast
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json # Added for handling JSON-encoded AST error strings

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
        # Initialize database manager
        self.db_manager = HybridDatabaseManager(
            redis_host=redis_host,
            redis_port=redis_port,
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port
        )

        # Get semantic gatekeeper for advanced operations
        self.gatekeeper = get_gatekeeper()

        # Learning thresholds
        self.promotion_threshold = 3
        self.failure_threshold = 5

        logger.info("CanonValidator initialized with hybrid cache")

    def _generate_entry(self, code: str, metadata: Optional[Dict[str, Any]] = None) -> CanonEntry:
        """
        Generates a CanonEntry from code and metadata.
        This helper method encapsulates the logic for creating a CanonEntry,
        including AST parsing and embedding generation.
        """
        ast_representation: str
        try:
            tree = ast.parse(code)
            ast_representation = ast.dump(tree)
        except SyntaxError as e:
            # Store syntax error as a JSON string
            ast_representation = json.dumps({"error": str(e)})
            logger.error(f"Syntax error parsing code for CanonEntry: {e}")
        except Exception as e:
            # Store other AST parsing errors as a JSON string
            ast_representation = json.dumps({"error": f"Unexpected AST parsing error: {e}"})
            logger.error(f"Unexpected error parsing code for CanonEntry: {e}")

        embedding: List[float]
        try:
            embedding = self.gatekeeper.embed_text(code)
        except Exception as e:
            embedding = []  # Fallback
            logger.error(f"Error generating embedding for CanonEntry: {e}")

        entry_metadata = metadata or {}
        entry_metadata.update({
            "embedding_generated_at": datetime.now(timezone.utc).isoformat()
        })

        # Generate a unique ID for the entry
        entry_id = f"entry_{hash(code)}_{datetime.now().timestamp()}"

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

        new_entry = self._generate_entry(new_code, metadata) # Modified to use internal helper

        # Query L1 (Redis) - fast working memory
        l1_results, l2_results = self.db_manager.search_patterns(
            query_vector=new_entry.embedding,
            l1_threshold=0.9,
            l2_threshold=0.7,
            filter_failures=True
        )

        result = {
            "is_valid": True,  # Default to valid
            "confidence": 1.0,
            "matched_pattern": None,
            "source": "no_match",
            "ast_match": False,
            "recommendation": "Code appears to be new and valid"
        }

        # Check L1 results
        if l1_results:
            best_match = l1_results[0]
            validation = self._validate_ast_match(new_entry, best_match)

            result.update({
                "matched_pattern": best_match.id,
                "source": "L1_Redis",
                "ast_match": validation["is_match"],
                "confidence": validation["confidence"],
                "is_valid": validation["is_valid"],
                "recommendation": validation["recommendation"]
            })

            logger.info(f"L1 match found: {best_match.id}")

        # Check L2 results if no L1 match
        elif l2_results:
            best_match = l2_results[0]
            validation = self._validate_ast_match(new_entry, best_match)

            result.update({
                "matched_pattern": best_match.id,
                "source": "L2_Qdrant",
                "ast_match": validation["is_match"],
                "confidence": validation["confidence"],
                "is_valid": validation["is_valid"],
                "recommendation": validation["recommendation"]
            })

            logger.info(f"L2 match found: {best_match.id}")

            # Promote to L1 if valid
            if validation["is_valid"]:
                self.db_manager.promote_to_l2(best_match)

        # Store the new pattern in L1 for future learning
        self.db_manager.store_pattern(new_entry, store_in_l2=False)

        return result

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
        # Extract AST structures (which are string representations)
        new_ast_str = new_entry.ast_structure
        existing_ast_str = existing_entry.ast_structure

        # Check for errors by attempting to parse JSON error strings
        new_ast_error: Optional[str] = None
        if new_ast_str.startswith('{"error":'):
            try:
                error_dict = json.loads(new_ast_str)
                new_ast_error = error_dict.get("error")
            except json.JSONDecodeError:
                pass # Malformed error string, treat as no error

        existing_ast_error: Optional[str] = None
        if existing_ast_str.startswith('{"error":'):
            try:
                error_dict = json.loads(existing_ast_str)
                existing_ast_error = error_dict.get("error")
            except json.JSONDecodeError:
                pass # Malformed error string, treat as no error

        if new_ast_error:
            return {
                "is_match": False,
                "is_valid": False,
                "confidence": 0.0,
                "recommendation": f"Syntax error in new code: {new_ast_error}"
            }

        if existing_ast_error:
            return {
                "is_match": False,
                "is_valid": False,
                "confidence": 0.0,
                "recommendation": f"Reference pattern has syntax error: {existing_ast_error}"
            }

        # Compare AST patterns
        similarity = self._calculate_ast_similarity(new_ast_str, existing_ast_str)

        # Check if existing pattern is successful
        success_rate = existing_entry.get_success_rate()

        # Determine validity
        is_valid = similarity > 0.7 and success_rate > 0.5

        return {
            "is_match": similarity > 0.7,
            "is_valid": is_valid,
            "confidence": similarity,
            "recommendation": self._generate_recommendation(similarity, success_rate)
        }

    def _get_ast_node_types_from_tree(self, tree: ast.AST) -> set[str]:
        """
        Helper method to extract unique node types from an AST tree.
        Reduces nesting depth in _calculate_ast_similarity.
        """
        return set(type(node).__name__ for node in ast.walk(tree))

    def _calculate_ast_similarity(self, ast1_str: str, ast2_str: str) -> float:
        """
        Calculate similarity between two AST structures.

        Simple implementation based on structural comparison.
        In production, this would use more sophisticated algorithms.

        Args:
            ast1_str: First AST structure as a string
            ast2_str: Second AST structure as a string

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Parse AST strings to compare structure
            tree1 = ast.parse(ast1_str)
            tree2 = ast.parse(ast2_str)

            # Get unique node types using the helper method
            types1 = self._get_ast_node_types_from_tree(tree1)
            types2 = self._get_ast_node_types_from_tree(tree2)

            # Calculate Jaccard similarity of node types
            intersection = len(types1.intersection(types2))
            union = len(types1.union(types2))

            return intersection / union if union > 0 else 0.0

        except SyntaxError as e:
            logger.error(f"Syntax error encountered while parsing AST strings for similarity: {e}")
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

    def update_learning(self, entry_id: str, outcome: str, error_trace: Optional[str] = None):
        """
        Update learning based on execution outcome.

        Args:
            entry_id: ID of the pattern to update
            outcome: "SUCCESS" or "FAILURE"
            error_trace: Optional error trace for failures
        """
        # Retrieve entry from Redis
        entry = self.db_manager.redis.get_entry(entry_id)
        if not entry:
            logger.warning(f"Entry {entry_id} not found for learning update")
            return

        # Update based on outcome
        if outcome.upper() == "FAILURE":
            entry.update_failure()
            logger.info(f"Recorded failure for pattern {entry_id}")

            # If too many failures, consider blocking
            if entry.failure_count >= self.failure_threshold:
                logger.warning(
                    f"Pattern {entry_id} exceeded failure threshold")

        elif outcome.upper() == "SUCCESS":
            entry.update_success()
            logger.info(f"Recorded success for pattern {entry_id}")

            # Check for promotion to L2
            if entry.success_count >= self.promotion_threshold:
                self.db_manager.promote_to_l2(entry)
                logger.info(f"Promoted pattern {entry_id} to L2")

        # Update the entry in Redis
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
        # Generate entry for search
        entry = self._generate_entry(code) # Modified to use internal helper

        # Search both caches
        l1_results, l2_results = self.db_manager.search_patterns(
            query_vector=entry.embedding,
            filter_failures=not include_failures
        )

        # Combine and format results
        all_results = l1_results + l2_results[:max_results - len(l1_results)]

        formatted = []
        for result in all_results[:max_results]:
            formatted.append(self._format_search_result(result))

        return formatted