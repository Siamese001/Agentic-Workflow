from __future__ import annotations

"""
[PHASE 13] Cognitive Batch Processor - High-Volume AI Audit Management.

Manages API rate limits, checkpointing, and batch execution for large-scale
architectural audits using Gemini LLM.

Features:
- Rate limiting with configurable delays
- Progress checkpointing for resumable execution
- Exponential backoff for API errors
- Batch processing with periodic saves

Responsibilities:
- Process large batches of violations (2,160+)
- Save progress every N items to prevent data loss
- Skip already-processed items on resume
- Handle API rate limits and errors gracefully

[SSOT] Integrates with CognitiveDispositionAgent for AI-powered triage.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


class CognitiveBatchProcessor:
    """
    Batch processor for high-volume cognitive disposition analysis.

    Manages rate limiting, checkpointing, and resumable execution for
    processing large numbers of architectural violations.

    Attributes:
        agent: CognitiveDispositionAgent instance
        checkpoint_file: Path to checkpoint file for progress tracking
        rate_limit_delay: Seconds to wait between API calls
        checkpoint_interval: Save checkpoint every N items
        max_retries: Maximum retry attempts for failed items
    """

    def __init__(
        self,
        agent: Any,  # CognitiveDispositionAgent
        checkpoint_file: str | Path = "cognitive_checkpoint.json",
        rate_limit_delay: float = 1.0,
        checkpoint_interval: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize the Cognitive Batch Processor.

        Args:
            agent: CognitiveDispositionAgent instance
            checkpoint_file: Path to checkpoint file
            rate_limit_delay: Seconds between API calls
            checkpoint_interval: Save progress every N items
            max_retries: Maximum retry attempts per item
        """
        self.agent = agent
        self.checkpoint_file = Path(checkpoint_file)
        self.rate_limit_delay = rate_limit_delay
        self.checkpoint_interval = checkpoint_interval
        self.max_retries = max_retries

        # Load existing checkpoint or start fresh
        self.results: dict[str, Any] = self._load_checkpoint()
        self.retry_counts: dict[str, int] = {}

        Logger.info(f"[BATCH] Initialized with checkpoint: {self.checkpoint_file}")
        if self.results:
            Logger.info(f"[BATCH] Loaded {len(self.results)} existing results from checkpoint")

    def _load_checkpoint(self) -> dict[str, Any]:
        """
        Load checkpoint from file if it exists.

        Returns:
            Dictionary of file_path -> disposition results
        """
        if self.checkpoint_file.exists():
            try:
                data = json.loads(self.checkpoint_file.read_text(encoding="utf-8"))
                Logger.info(f"[BATCH] Checkpoint loaded: {len(data)} items")
                return data
            except Exception as e:
                Logger.warning(f"[BATCH] Failed to load checkpoint: {e}")
                return {}
        return {}

    def _save_checkpoint(self) -> None:
        """Save current progress to checkpoint file."""
        try:
            self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
            self.checkpoint_file.write_text(
                json.dumps(self.results, indent=2),
                encoding="utf-8",
            )
            Logger.debug(f"[BATCH] Checkpoint saved: {len(self.results)} items")
        except Exception as e:
            Logger.error(f"[BATCH] Failed to save checkpoint: {e}")

    def process_batch(
        self,
        violations: list[Any],
        auto_execute: bool = False,
    ) -> dict[str, int]:
        """
        Process a batch of violations with rate limiting and checkpointing.

        Args:
            violations: List of violation objects to process
            auto_execute: If True, execute disposition actions (not just analyze)

        Returns:
            Statistics dictionary with counts
        """
        stats = {
            "PROCESSED": 0,
            "SKIPPED": 0,
            "ERRORS": 0,
            "TOTAL": len(violations),
        }

        Logger.info("=" * 60)
        Logger.info("[BATCH] Starting Cognitive Batch Processing")
        Logger.info(f"[BATCH] Queue Size: {len(violations)} violations")
        Logger.info(f"[BATCH] Rate Limit: {self.rate_limit_delay}s between calls")
        Logger.info(f"[BATCH] Checkpoint Interval: Every {self.checkpoint_interval} items")
        Logger.info("=" * 60)

        for i, violation in enumerate(violations, 1):
            # Extract file path from violation
            file_path = self._get_file_path(violation)
            if not file_path:
                Logger.warning(f"[BATCH] [{i}/{len(violations)}] No file path in violation")
                stats["ERRORS"] += 1
                continue

            file_path_str = str(file_path)

            # Skip if already processed in checkpoint
            if file_path_str in self.results:
                Logger.debug(f"[BATCH] [{i}/{len(violations)}] Skipping (cached): {Path(file_path).name}")
                stats["SKIPPED"] += 1
                continue

            # Process the violation
            Logger.info(f"[BATCH] [{i}/{len(violations)}] Processing: {Path(file_path).name}")

            success = self._process_single_violation(violation, file_path_str)

            if success:
                stats["PROCESSED"] += 1
            else:
                stats["ERRORS"] += 1

            # Save checkpoint periodically
            if i % self.checkpoint_interval == 0:
                self._save_checkpoint()
                Logger.info(f"[BATCH] Checkpoint saved at item {i}/{len(violations)}")

            # Rate limiting
            if i < len(violations):  # Don't sleep after last item
                time.sleep(self.rate_limit_delay)

        # Final checkpoint save
        self._save_checkpoint()

        Logger.info("=" * 60)
        Logger.info("[BATCH] Batch Processing Complete")
        Logger.info(f"[BATCH] Processed: {stats['PROCESSED']}")
        Logger.info(f"[BATCH] Skipped (cached): {stats['SKIPPED']}")
        Logger.info(f"[BATCH] Errors: {stats['ERRORS']}")
        Logger.info("=" * 60)

        return stats

    def _get_file_path(self, violation: Any) -> Path | None:
        """
        Extract file path from violation object.

        Args:
            violation: Violation object (dict or object with attributes)

        Returns:
            Path to file or None
        """
        if hasattr(violation, "file_path"):
            return Path(violation.file_path)
        elif isinstance(violation, dict):
            file = violation.get("file")
            if file:
                return Path(file)
        return None

    def _process_single_violation(
        self,
        violation: Any,
        file_path_str: str,
    ) -> bool:
        """
        Process a single violation with retry logic.

        Args:
            violation: Violation object
            file_path_str: String path to file

        Returns:
            True if successful, False otherwise
        """
        # Get violation type
        v_type = self._get_violation_type(violation)

        # Retry loop with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                # Analyze violation
                decision = self.agent.analyze_violation(file_path_str, v_type)

                # Store result
                self.results[file_path_str] = {
                    "action": decision.action,
                    "target_path": decision.target_path,
                    "reason": decision.reason,
                    "confidence": decision.confidence,
                    "violation_type": v_type,
                }

                Logger.info(
                    f"    Decision: {decision.action} -> {decision.target_path or 'N/A'} ({decision.confidence:.2f})"
                )
                return True

            except Exception as e:
                Logger.warning(f"    Attempt {attempt}/{self.max_retries} failed: {e}")

                if attempt < self.max_retries:
                    # Exponential backoff
                    backoff_delay = self.rate_limit_delay * (2 ** (attempt - 1))
                    Logger.info(f"    Retrying in {backoff_delay:.1f}s...")
                    time.sleep(backoff_delay)
                else:
                    # Max retries exceeded
                    Logger.error(f"    Max retries exceeded for {Path(file_path_str).name}")
                    self.results[file_path_str] = {
                        "action": "ERROR",
                        "target_path": None,
                        "reason": f"Processing failed after {self.max_retries} attempts: {e}",
                        "confidence": 0.0,
                        "violation_type": v_type,
                    }
                    return False

        return False

    def _get_violation_type(self, violation: Any) -> str:
        """
        Extract violation type from violation object.

        Args:
            violation: Violation object

        Returns:
            Violation type string
        """
        if hasattr(violation, "violation_type"):
            v_type = violation.violation_type
            if hasattr(v_type, "name"):
                return v_type.name
            return str(v_type)
        elif isinstance(violation, dict):
            return violation.get("type", "UNKNOWN")
        return "UNKNOWN"

    def get_results(self) -> dict[str, Any]:
        """
        Get all processed results.

        Returns:
            Dictionary of file_path -> disposition results
        """
        return self.results

    def get_statistics(self) -> dict[str, Any]:
        """
        Get processing statistics.

        Returns:
            Statistics dictionary
        """
        if not self.results:
            return {
                "total": 0,
                "by_action": {},
                "avg_confidence": 0.0,
            }

        by_action: dict[str, int] = {}
        confidences = []

        for result in self.results.values():
            action = result.get("action", "UNKNOWN")
            by_action[action] = by_action.get(action, 0) + 1

            confidence = result.get("confidence", 0.0)
            if isinstance(confidence, int | float):
                confidences.append(confidence)

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "total": len(self.results),
            "by_action": by_action,
            "avg_confidence": avg_confidence,
        }

    def clear_checkpoint(self) -> None:
        """Clear the checkpoint file and reset results."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            Logger.info("[BATCH] Checkpoint cleared")
        self.results = {}
        self.retry_counts = {}
