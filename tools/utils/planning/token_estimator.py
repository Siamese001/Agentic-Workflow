"""
Context Window Estimator for Kimi K2.5

Deterministic token estimation for planning phases and waves.
Ensures every step stays safely within the 262K context window.
"""

import copy
import hashlib
import logging
import math
import re
from dataclasses import dataclass, field
from typing import Any

# Import from YAML SSOT
from agentic_core.config.token_budget_loader import DEFAULT_TOKEN_BUDGET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TokenBudget:
    """Token budget configuration for Kimi K2.5"""

    # Load defaults from YAML SSOT
    HARD_MAX_CONTEXT: int = DEFAULT_TOKEN_BUDGET.hard_max_context
    SAFE_OPERATING_CAP: int = DEFAULT_TOKEN_BUDGET.safe_operating_cap
    WARNING_THRESHOLD: int = DEFAULT_TOKEN_BUDGET.warning_threshold
    DEFAULT_RESERVED_OUTPUT: int = DEFAULT_TOKEN_BUDGET.default_reserved_output
    DEFAULT_SAFETY_BUFFER: int = DEFAULT_TOKEN_BUDGET.default_safety_buffer
    DEFAULT_MAX_INPUT_TARGET: int = DEFAULT_TOKEN_BUDGET.warning_threshold

    def __post_init__(self) -> None:
        if self.HARD_MAX_CONTEXT <= 0:
            raise ValueError("HARD_MAX_CONTEXT must be > 0")
        if not (0 < self.WARNING_THRESHOLD <= self.SAFE_OPERATING_CAP <= self.HARD_MAX_CONTEXT):
            raise ValueError(
                "Budget invariants violated: WARNING_THRESHOLD <= SAFE_OPERATING_CAP <= HARD_MAX_CONTEXT",
            )
        if self.DEFAULT_RESERVED_OUTPUT < 0 or self.DEFAULT_SAFETY_BUFFER < 0:
            raise ValueError("Reserved output and safety buffer must be >= 0")


@dataclass
class ContextSource:
    """Represents a source of context tokens"""

    source_type: str
    content: str
    tokens: int = 0
    compressed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def content_fingerprint(self) -> str:
        normalized = self.content.strip().encode("utf-8", errors="ignore")
        return hashlib.sha256(normalized).hexdigest()


@dataclass
class TokenEstimate:
    """Token estimation result for a plan step"""

    plan_step: str
    estimated_input_tokens: int
    reserved_output_tokens: int
    safety_buffer_tokens: int
    total_projected_tokens: int
    status: str  # green, yellow, red
    action: str  # proceed, compress, block
    top_contributors: list[dict[str, Any]]
    recommended_reductions: list[str]
    compression_applied: list[str] = field(default_factory=list)


class ContextWindowEstimator:
    """
    Deterministic context window estimator for SWE 1.5

    Estimates tokens from the actual assembled payload before each model call.
    Uses conservative approximation with high bias to avoid underestimation.
    """

    def __init__(self, budget: TokenBudget | None = None):
        self.budget = budget or TokenBudget()
        self.compression_policies = self._init_compression_policies()
        self._error_pattern = re.compile(r"(?i)(error|traceback|exception|failed)")

        # Conservative token estimation rates (chars -> tokens, biased high)
        self.token_rates = {
            "code": 0.35,  # ~3 chars per token for code
            "text": 0.4,  # ~2.5 chars per token for text
            "json": 0.33,  # ~3 chars per token for JSON
            "diff": 0.3,  # ~3.3 chars per token for diffs
            "log": 0.38,  # ~2.6 chars per token for logs
            "system": 0.42,  # ~2.4 chars per token for system prompts
        }
        self.min_tokens_by_type = {
            "system": 8,
            "user_prompt": 8,
            "file": 4,
            "diff": 4,
            "log": 4,
            "retrieval": 4,
            "prior_step": 4,
        }

    def _init_compression_policies(self) -> dict[str, Any]:
        """Initialize compression policies for different content types"""
        return {
            "compression_order": [
                "remove_duplicates",
                "trim_retry_history",
                "summarize_files",
                "trim_logs_to_errors",
                "reduce_retrieval_chunks",
                "diff_or_file_not_both",
                "drop_low_relevance_files",
            ],
            "max_log_lines": 50,
            "max_retry_history": 3,
            "max_retrieval_chunks": 10,
            "file_summary_threshold": 1000,  # lines
            "duplicate_detection": True,
        }

    def estimate_step_tokens(
        self,
        plan_step: str,
        system_prompt: str,
        user_prompt: str,
        files: list[dict[str, Any]],
        diffs: list[dict[str, Any]],
        logs: list[dict[str, Any]],
        retrieved_context: list[dict[str, Any]],
        prior_steps: list[str],
        reserved_output: int | None = None,
        safety_buffer: int | None = None,
    ) -> TokenEstimate:
        """
        Estimate tokens for a complete plan step payload

        Args:
            plan_step: Name/description of the plan step
            system_prompt: System and scaffold prompt content
            user_prompt: User/task prompt content
            files: List of file contents with metadata
            diffs: List of diff contents with metadata
            logs: List of log outputs with metadata
            retrieved_context: List of retrieved context chunks
            prior_steps: List of prior step contents to carry forward
            reserved_output: Reserved output tokens (uses default if None)
            safety_buffer: Safety buffer tokens (uses default if None)

        Returns:
            TokenEstimate with detailed breakdown and recommendations
        """
        # Defensive initialization for potential None inputs
        files = files or []
        diffs = diffs or []
        logs = logs or []
        retrieved_context = retrieved_context or []
        prior_steps = prior_steps or []

        # Use defaults if not provided
        reserved_output = self.budget.DEFAULT_RESERVED_OUTPUT if reserved_output is None else reserved_output
        safety_buffer = self.budget.DEFAULT_SAFETY_BUFFER if safety_buffer is None else safety_buffer
        if reserved_output < 0 or safety_buffer < 0:
            raise ValueError("reserved_output and safety_buffer must be >= 0")

        # Collect all context sources
        sources = []

        # Add system prompts
        if system_prompt:
            sources.append(
                ContextSource(
                    "system_prompt",
                    system_prompt,
                    self._estimate_source_tokens("system_prompt", system_prompt, "system"),
                    metadata={"type": "system"},
                )
            )

        # Add user prompt
        if user_prompt:
            sources.append(
                ContextSource(
                    "user_prompt",
                    user_prompt,
                    self._estimate_source_tokens("user_prompt", user_prompt, "text"),
                    metadata={"type": "prompt"},
                )
            )

        # Add files
        for file_info in files:
            content = file_info.get("content", "")
            file_type = self._detect_content_type(content, file_info.get("path", ""))
            sources.append(
                ContextSource(
                    "file",
                    content,
                    self._estimate_source_tokens("file", content, file_type),
                    metadata={
                        "path": file_info.get("path", ""),
                        "type": file_type,
                        "size": len(content),
                        "lines": len(content.splitlines()),
                    },
                )
            )

        # Add diffs
        for diff_info in diffs:
            content = diff_info.get("content", "")
            sources.append(
                ContextSource(
                    "diff",
                    content,
                    self._estimate_source_tokens("diff", content, "diff"),
                    metadata={
                        "path": diff_info.get("path", ""),
                        "lines_added": self._count_diff_lines(content, prefix="+"),
                        "lines_removed": self._count_diff_lines(content, prefix="-"),
                        "hunks": content.count("@@"),
                    },
                )
            )

        # Add logs
        for log_info in logs:
            content = log_info.get("content", "")
            sources.append(
                ContextSource(
                    "log",
                    content,
                    self._estimate_source_tokens("log", content, "log"),
                    metadata={
                        "source": log_info.get("source", ""),
                        "lines": len(content.splitlines()),
                        "has_errors": bool(self._error_pattern.search(content)),
                    },
                )
            )

        # Add retrieved context
        for ctx_info in retrieved_context:
            content = ctx_info.get("content", "")
            sources.append(
                ContextSource(
                    "retrieval",
                    content,
                    self._estimate_source_tokens("retrieval", content, "text"),
                    metadata={
                        "source": ctx_info.get("source", ""),
                        "chunk_id": ctx_info.get("chunk_id", ""),
                        "overlap": ctx_info.get("overlap", False),
                    },
                )
            )

        # Add prior steps
        for i, step_content in enumerate(prior_steps):
            if step_content:
                sources.append(
                    ContextSource(
                        "prior_step",
                        step_content,
                        self._estimate_source_tokens("prior_step", step_content, "text"),
                        metadata={"step_index": i},
                    )
                )

        # Calculate totals
        input_tokens = sum(s.tokens for s in sources)
        total_projected = input_tokens + reserved_output + safety_buffer

        # Determine status and action
        status, action = self._determine_status_action(total_projected)

        # Get top contributors
        top_contributors = self._get_top_contributors(sources)

        # Generate recommendations
        recommended_reductions = self._generate_recommendations(
            sources,
            status,
            total_projected,
        )

        # Create estimate
        estimate = TokenEstimate(
            plan_step=plan_step,
            estimated_input_tokens=input_tokens,
            reserved_output_tokens=reserved_output,
            safety_buffer_tokens=safety_buffer,
            total_projected_tokens=total_projected,
            status=status,
            action=action,
            top_contributors=top_contributors,
            recommended_reductions=recommended_reductions,
        )

        # Apply compression if needed
        if action in ["compress", "block"]:
            estimate = self._apply_compression(estimate, sources)

        return estimate

    def _estimate_tokens(self, text: str, content_type: str) -> int:
        """
        Estimate tokens for text content

        Uses conservative rates biased high to avoid underestimation.
        """
        if not text:
            return 0

        # Get appropriate token rate
        rate = self.token_rates.get(content_type, self.token_rates["text"])

        # Apply conservative multiplier (bias high)
        conservative_multiplier = 1.1

        # Calculate estimated tokens
        estimated = math.ceil(len(text) * rate * conservative_multiplier)

        # Minimum of 1 token for non-empty content
        return max(1, estimated)

    def _estimate_source_tokens(self, source_type: str, text: str, content_type: str) -> int:
        estimated = self._estimate_tokens(text, content_type)
        minimum = self.min_tokens_by_type.get(source_type, 1)
        return max(minimum, estimated)

    def _count_diff_lines(self, content: str, prefix: str) -> int:
        count = 0
        for line in content.splitlines():
            if line.startswith(prefix) and not line.startswith(prefix * 3):
                count += 1
        return count

    def _detect_content_type(self, content: str, file_path: str) -> str:
        """Detect content type based on file path and content"""
        path_lower = file_path.lower()

        # Check file extension
        if path_lower.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
            return "code"
        elif path_lower.endswith(".json"):
            return "json"
        elif "diff" in path_lower or content.startswith("diff "):
            return "diff"
        elif any(keyword in content.lower() for keyword in ["error", "traceback", "exception"]):
            return "log"
        else:
            return "text"

    def _determine_status_action(self, total_tokens: int) -> tuple[str, str]:
        """Determine status and action based on token count"""
        if total_tokens > self.budget.HARD_MAX_CONTEXT:
            return "red", "block"
        if total_tokens <= self.budget.WARNING_THRESHOLD:
            return "green", "proceed"
        elif total_tokens <= self.budget.SAFE_OPERATING_CAP:
            return "yellow", "compress"
        else:
            return "red", "block"

    def _get_top_contributors(self, sources: list[ContextSource]) -> list[dict[str, Any]]:
        """Get top contributors to token count"""
        # Group by source type
        type_totals: dict[str, int] = {}
        for source in sources:
            type_totals[source.source_type] = type_totals.get(source.source_type, 0) + source.tokens

        # Sort by token count
        sorted_contributors = sorted(
            type_totals.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # Return top contributors
        return [{"type": ctype, "tokens": tokens} for ctype, tokens in sorted_contributors[:5]]

    def _generate_recommendations(
        self, sources: list[ContextSource], status: str, total_tokens: int
    ) -> list[str]:
        """Generate reduction recommendations based on analysis"""
        recommendations: list[str] = []

        if status == "green":
            return recommendations

        # Analyze sources for reduction opportunities
        type_totals: dict[str, int] = {}
        for source in sources:
            type_totals[source.source_type] = type_totals.get(source.source_type, 0) + source.tokens

        # Check for large files
        large_files = [s for s in sources if s.source_type == "file" and s.metadata.get("lines", 0) > 500]
        if large_files:
            recommendations.append(f"Summarize {len(large_files)} large files (>500 lines)")

        # Check for verbose logs
        log_sources = [s for s in sources if s.source_type == "log"]
        if log_sources:
            total_log_lines = sum(s.metadata.get("lines", 0) for s in log_sources)
            if total_log_lines > 100:
                recommendations.append(f"Trim logs to errors only ({total_log_lines} lines)")

        # Check for duplicates
        if len([s for s in sources if s.source_type == "file"]) > 10:
            recommendations.append("Remove duplicate or similar file content")

        # Check for retrieval chunks
        retrieval_sources = [s for s in sources if s.source_type == "retrieval"]
        if len(retrieval_sources) > 15:
            recommendations.append(f"Reduce retrieval chunks ({len(retrieval_sources)} → 10)")

        # Check for diff + file both present
        file_paths = {s.metadata.get("path", "") for s in sources if s.source_type == "file"}
        diff_paths = {s.metadata.get("path", "") for s in sources if s.source_type == "diff"}
        overlap = file_paths & diff_paths
        if overlap:
            recommendations.append(f"Use diff OR full file for {len(overlap)} files, not both")

        # Check prior steps
        prior_steps = [s for s in sources if s.source_type == "prior_step"]
        if len(prior_steps) > 3:
            recommendations.append("Reduce prior step carry-forward (keep only last 2-3)")

        # General recommendation based on how far over budget
        if total_tokens > self.budget.SAFE_OPERATING_CAP:
            recommendations.append(
                "Critical: Reduce context by at least "
                + f"{total_tokens - self.budget.SAFE_OPERATING_CAP} tokens"
            )
        elif total_tokens > self.budget.WARNING_THRESHOLD:
            recommendations.append(
                "Moderate: Reduce context by " + f"{total_tokens - self.budget.WARNING_THRESHOLD} tokens"
            )

        return recommendations

    def _apply_compression(self, estimate: TokenEstimate, sources: list[ContextSource]) -> TokenEstimate:
        """Apply compression policies to reduce token count"""
        compressed_sources = copy.deepcopy(sources)
        compression_applied = []

        # Apply compression in order
        for policy in self.compression_policies["compression_order"]:
            if estimate.total_projected_tokens <= self.budget.WARNING_THRESHOLD:
                break

            if policy == "remove_duplicates":
                compressed_sources, applied = self._remove_duplicates(compressed_sources)
                if applied:
                    compression_applied.append("removed_duplicates")

            elif policy == "trim_retry_history":
                compressed_sources, applied = self._trim_retry_history(compressed_sources)
                if applied:
                    compression_applied.append("trimmed_retry_history")

            elif policy == "summarize_files":
                compressed_sources, applied = self._summarize_large_files(compressed_sources)
                if applied:
                    compression_applied.append("summarized_large_files")

            elif policy == "trim_logs_to_errors":
                compressed_sources, applied = self._trim_logs_to_errors(compressed_sources)
                if applied:
                    compression_applied.append("trimmed_logs_to_errors")

            elif policy == "reduce_retrieval_chunks":
                compressed_sources, applied = self._reduce_retrieval_chunks(compressed_sources)
                if applied:
                    compression_applied.append("reduced_retrieval_chunks")

            elif policy == "diff_or_file_not_both":
                compressed_sources, applied = self._prefer_diff_over_file(compressed_sources)
                if applied:
                    compression_applied.append("preferred_diff_over_file")

            elif policy == "drop_low_relevance_files":
                compressed_sources, applied = self._drop_low_relevance_files(compressed_sources)
                if applied:
                    compression_applied.append("dropped_low_relevance_files")

            # Recalculate totals
            new_input_tokens = sum(s.tokens for s in compressed_sources)
            estimate.estimated_input_tokens = new_input_tokens
            estimate.total_projected_tokens = (
                new_input_tokens + estimate.reserved_output_tokens + estimate.safety_buffer_tokens
            )

            # Update status and action
            estimate.status, estimate.action = self._determine_status_action(
                estimate.total_projected_tokens,
            )

        estimate.compression_applied = compression_applied
        estimate.top_contributors = self._get_top_contributors(compressed_sources)
        estimate.recommended_reductions = self._generate_recommendations(
            compressed_sources,
            estimate.status,
            estimate.total_projected_tokens,
        )
        return estimate

    def _remove_duplicates(self, sources: list[ContextSource]) -> tuple[list[ContextSource], bool]:
        """Remove duplicate content"""
        seen_content = set()
        filtered_sources = []

        for source in sources:
            content_hash = source.content_fingerprint()
            identity = (
                source.source_type,
                source.metadata.get("path", ""),
                source.metadata.get("chunk_id", ""),
                content_hash,
            )
            if identity not in seen_content:
                seen_content.add(identity)
                filtered_sources.append(source)

        return filtered_sources, len(filtered_sources) < len(sources)

    def _trim_retry_history(self, sources: list[ContextSource]) -> tuple[list[ContextSource], bool]:
        """Trim retry history in logs"""
        trimmed = False
        for source in sources:
            if source.source_type == "log":
                lines = source.content.splitlines()
                # Keep only last N lines for retry history
                if len(lines) > self.compression_policies["max_retry_history"] * 10:
                    source.content = "\n".join(lines[-self.compression_policies["max_retry_history"] * 10 :])
                    source.tokens = self._estimate_tokens(source.content, "log")
                    trimmed = True

        return sources, trimmed

    def _summarize_large_files(self, sources: list[ContextSource]) -> tuple[list[ContextSource], bool]:
        """Summarize large files"""
        summarized = False
        threshold = self.compression_policies["file_summary_threshold"]

        for source in sources:
            if source.source_type == "file" and source.metadata.get("lines", 0) > threshold:
                # Create summary
                lines = source.content.splitlines()
                summary = f"# File: {source.metadata.get('path', 'unknown')}\n"
                summary += f"# Lines: {len(lines)}\n"
                summary += f"# Size: {len(source.content)} chars\n"
                summary += "# Summary: Large file truncated for token budget\n"
                summary += "# Key sections:\n"

                # Keep first 20 lines and last 20 lines
                if len(lines) > 40:
                    summary += "\n".join(lines[:20])
                    summary += f"\n# ... [truncated {len(lines) - 40} lines] ...\n"
                    summary += "\n".join(lines[-20:])
                else:
                    summary = source.content  # Keep as-is if not too large

                source.content = summary
                source.tokens = self._estimate_tokens(summary, "text")
                source.compressed = True
                summarized = True

        return sources, summarized

    def _trim_logs_to_errors(self, sources: list[ContextSource]) -> tuple[list[ContextSource], bool]:
        """Trim logs to show only errors"""
        trimmed = False

        for source in sources:
            if source.source_type == "log":
                lines = source.content.splitlines()

                # Fast pre-check to avoid processing if no errors exist
                if not self._error_pattern.search(source.content):
                    continue

                trimmed_lines = []
                for i, line in enumerate(lines):
                    if self._error_pattern.search(line):
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        trimmed_lines.extend(lines[start:end])

                if trimmed_lines:
                    unique_lines = list(dict.fromkeys(trimmed_lines))
                    if len(unique_lines) > self.compression_policies["max_log_lines"]:
                        unique_lines = unique_lines[: self.compression_policies["max_log_lines"]]

                    source.content = "\n".join(unique_lines)
                    source.tokens = self._estimate_tokens(source.content, "log")
                    trimmed = True

        return sources, trimmed

    def _reduce_retrieval_chunks(self, sources: list[ContextSource]) -> tuple[list[ContextSource], bool]:
        """Reduce number of retrieval chunks"""
        retrieval_sources = [s for s in sources if s.source_type == "retrieval"]
        max_chunks = self.compression_policies["max_retrieval_chunks"]

        if len(retrieval_sources) <= max_chunks:
            return sources, False

        # Keep highest scoring chunks (assuming first ones are most relevant)
        ranked = sorted(
            retrieval_sources,
            key=lambda s: (
                float(s.metadata.get("score", 0.0)),
                not bool(s.metadata.get("overlap", False)),
            ),
            reverse=True,
        )
        kept_chunks = ranked[:max_chunks]
        kept_ids = {id(s) for s in kept_chunks}

        # Remove removed chunks from sources
        filtered_sources = [s for s in sources if s.source_type != "retrieval" or id(s) in kept_ids]

        return filtered_sources, True

    def _prefer_diff_over_file(self, sources: list[ContextSource]) -> tuple[list[ContextSource], bool]:
        """Prefer diff over full file when both present"""
        file_paths = {}
        diff_paths = {}

        # Index files and diffs by path
        for i, source in enumerate(sources):
            path = source.metadata.get("path", "")
            if source.source_type == "file":
                file_paths[path] = i
            elif source.source_type == "diff":
                diff_paths[path] = i

        # Find overlaps and remove files
        overlap_paths = {p for p in set(file_paths.keys()) & set(diff_paths.keys()) if p}
        if overlap_paths:
            # Remove full files, keep diffs
            filtered_sources = [
                s
                for s in sources
                if not (s.source_type == "file" and s.metadata.get("path", "") in overlap_paths)
            ]
            return filtered_sources, True

        return sources, False

    def _drop_low_relevance_files(self, sources: list[ContextSource]) -> tuple[list[ContextSource], bool]:
        """Drop low relevance files (generated files, lock files, etc.)"""
        low_relevance_patterns = [
            ".lock",
            ".log",
            ".tmp",
            ".cache",
            "__pycache__",
            "node_modules",
            ".git",
            "package-lock.json",
            "yarn.lock",
        ]

        filtered_sources = []
        dropped = False

        for source in sources:
            if source.source_type == "file":
                path = source.metadata.get("path", "").lower()
                is_low_relevance = any(pattern in path for pattern in low_relevance_patterns)

                if not is_low_relevance:
                    filtered_sources.append(source)
                else:
                    dropped = True
            else:
                filtered_sources.append(source)

        return filtered_sources, dropped

    def to_dict(self, estimate: TokenEstimate) -> dict[str, Any]:
        """Convert estimate to dictionary for JSON serialization"""
        return {
            "plan_step": estimate.plan_step,
            "estimated_input_tokens": estimate.estimated_input_tokens,
            "reserved_output_tokens": estimate.reserved_output_tokens,
            "safety_buffer_tokens": estimate.safety_buffer_tokens,
            "total_projected_tokens": estimate.total_projected_tokens,
            "status": estimate.status,
            "action": estimate.action,
            "top_contributors": estimate.top_contributors,
            "recommended_reductions": estimate.recommended_reductions,
            "compression_applied": estimate.compression_applied,
        }

    def print_report(self, estimate: TokenEstimate) -> None:
        """Print a formatted token budget report"""
        status_colors = {
            "green": "\033[92m",  # Bright green
            "yellow": "\033[93m",  # Bright yellow
            "red": "\033[91m",  # Bright red
        }
        reset_color = "\033[0m"

        color = status_colors.get(estimate.status, "")

        print(f"\n{color}=== Token Budget Report ==={reset_color}")
        print(f"Plan Step: {estimate.plan_step}")
        print(f"Status: {color}{estimate.status.upper()}{reset_color}")
        print(f"Action: {estimate.action}")
        print(f"Input Tokens: {estimate.estimated_input_tokens:,}")
        print(f"Reserved Output: {estimate.reserved_output_tokens:,}")
        print(f"Safety Buffer: {estimate.safety_buffer_tokens:,}")
        print(f"Total Projected: {color}{estimate.total_projected_tokens:,}{reset_color}")

        print("\nTop Contributors:")
        for contributor in estimate.top_contributors:
            print(f"  - {contributor['type']}: {contributor['tokens']:,} tokens")

        if estimate.recommended_reductions:
            print("\nRecommended Reductions:")
            for reduction in estimate.recommended_reductions:
                print(f"  - {reduction}")

        if estimate.compression_applied:
            print("\nCompression Applied:")
            for compression in estimate.compression_applied:
                print(f"  - {compression}")

        print("=" * 30)

    def estimate_with_breakdown(
        self,
        plan_step: str,
        system_prompt: str,
        user_prompt: str,
        files: list[dict[str, Any]],
        diffs: list[dict[str, Any]],
        logs: list[dict[str, Any]],
        retrieved_context: list[dict[str, Any]],
        prior_steps: list[str],
        reserved_output: int | None = None,
        safety_buffer: int | None = None,
    ) -> dict[str, Any]:
        estimate = self.estimate_step_tokens(
            plan_step=plan_step,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            files=files,
            diffs=diffs,
            logs=logs,
            retrieved_context=retrieved_context,
            prior_steps=prior_steps,
            reserved_output=reserved_output,
            safety_buffer=safety_buffer,
        )
        return {
            "estimate": self.to_dict(estimate),
            "budget": {
                "hard_max_context": self.budget.HARD_MAX_CONTEXT,
                "safe_operating_cap": self.budget.SAFE_OPERATING_CAP,
                "warning_threshold": self.budget.WARNING_THRESHOLD,
            },
        }


def main() -> None:
    """CLI entry point for token estimator"""
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description="Context Window Estimator for Kimi K2.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m agentic_core.planning.token_estimator --help
  python -m agentic_core.planning.token_estimator --demo
        """,
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a demo estimation",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output demo results as JSON",
    )
    parser.add_argument(
        "--budget",
        action="store_true",
        help="Show default budget configuration",
    )

    args = parser.parse_args()
    estimator = ContextWindowEstimator()

    if args.budget:
        budget_info = {
            "HARD_MAX_CONTEXT": estimator.budget.HARD_MAX_CONTEXT,
            "SAFE_OPERATING_CAP": estimator.budget.SAFE_OPERATING_CAP,
            "WARNING_THRESHOLD": estimator.budget.WARNING_THRESHOLD,
            "DEFAULT_RESERVED_OUTPUT": estimator.budget.DEFAULT_RESERVED_OUTPUT,
            "DEFAULT_SAFETY_BUFFER": estimator.budget.DEFAULT_SAFETY_BUFFER,
        }
        print(json.dumps(budget_info, indent=2))
        sys.exit(0)

    if args.demo:
        result = estimator.estimate_with_breakdown(
            plan_step="demo_estimation",
            system_prompt="You are a helpful assistant.",
            user_prompt="Estimate tokens for this request.",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[],
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            estimator.print_report(
                estimator.estimate_step_tokens(
                    plan_step="demo_estimation",
                    system_prompt="You are a helpful assistant.",
                    user_prompt="Estimate tokens for this request.",
                    files=[],
                    diffs=[],
                    logs=[],
                    retrieved_context=[],
                    prior_steps=[],
                )
            )
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
