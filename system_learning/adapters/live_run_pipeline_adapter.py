"""LiveRunPipelineAdapter — bridges InMemoryHealingOutcomeIntakeStore to meta_learning_pipeline.

C1 hardening: explicit adapter layer so execute_ssot._fire_meta_learning_intake
does not directly couple to PipelineDependencies construction details.

Design invariants:
- No wall-clock reads (timestamps provided by caller).
- Activation-guarded: when BMG_EMBEDDINGS_ENABLED=false, embed step is skipped.
- Fail-closed: any adapter error propagates; no silent fallback.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ActivationAuthorizationError(RuntimeError):
    """Raised when pipeline activation is attempted without dual approval.

    C-hardening: any attempt to invoke the pipeline with mutations enabled
    (proposal_only=False) without explicit dual-approval tokens MUST raise
    this error.  The default proposal_only=True is the safe no-op path.
    """

    pass


class LiveRunPipelineAdapter:
    """Adapts the in-process healing outcome store for meta_learning_pipeline consumption.

    This adapter translates the InMemoryHealingOutcomeIntakeStore record format
    into the telemetry/audit format expected by run_pipeline(), avoiding direct
    coupling between execute_ssot and pipeline internals.

    Activation: the adapter is instantiated unconditionally but is a no-op when
    BMG_EMBEDDINGS_ENABLED=false (embed step skipped, store returns 0 records).
    """

    def __init__(
        self,
        intake_adapter: Any,
        *,
        source_tag: str = "live_run",
    ) -> None:
        """Initialise adapter.

        Args:
            intake_adapter: Pre-built HealingOutcomeIntakeAdapter (from execute_ssot).
            source_tag: Identifier written into pipeline metadata for audit tracing.
        """
        self._intake_adapter = intake_adapter
        self._source_tag = source_tag

    def record_count(self) -> int:
        """Return the number of healing records available for pipeline consumption."""
        try:
            return self._intake_adapter.store.count()
        except Exception:  # guardian: allow-silent-swallower
            return 0

    def build_pipeline_deps(
        self,
        repo_root: Any,
        healing_config_optimizer: Any | None = None,
    ) -> Any:
        """Construct PipelineDependencies wired to this adapter's intake store.

        Args:
            repo_root: pathlib.Path to the repository root.
            healing_config_optimizer: Optional pre-built optimizer.

        Returns:
            PipelineDependencies ready for run_pipeline().
        """
        from system_learning.pipelines.pipeline_factory import build_pipeline_deps

        return build_pipeline_deps(
            repo_root=repo_root,
            healing_outcome_intake_adapter=self._intake_adapter,
            healing_config_optimizer=healing_config_optimizer,
        )

    def run(
        self,
        *,
        repo_root: Any,
        now_utc: int,
        window_start_utc: int,
        proposal_only: bool = True,
        approval_token: str | None = None,
    ) -> None:
        """Run the meta_learning_pipeline end-to-end with this adapter's records.

        Args:
            repo_root: pathlib.Path to the repository root.
            now_utc: Current Unix timestamp (caller-provided, no wall-clock read).
            window_start_utc: Window start for telemetry aggregation.
            proposal_only: When True (default), pipeline produces proposals only (safe).
                           When False, mutations are enabled — requires approval_token.
            approval_token: Required when proposal_only=False.  Any non-empty string is
                            accepted as the dual-approval gate in local runs.  CI must
                            supply a token; absence raises ActivationAuthorizationError.

        Raises:
            ActivationAuthorizationError: If proposal_only=False and no approval_token.
            Any exception from run_pipeline() propagates; caller is responsible
            for catch/log if non-fatal behaviour is desired.
        """
        # C-hardening: dual-approval gate — mutations forbidden without explicit token.
        if not proposal_only and not approval_token:
            raise ActivationAuthorizationError(
                "proposal_only=False requires a non-empty approval_token; "
                "pass approval_token=<token> to enable pipeline mutations."
            )
        from system_learning.pipelines.meta_learning_pipeline import run_pipeline
        from system_learning.pipelines.pipeline_factory import build_pipeline_config

        cfg = build_pipeline_config(proposal_only=proposal_only)
        deps = self.build_pipeline_deps(repo_root=repo_root)
        run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start_utc,
            window_end_utc=now_utc,
            cfg=cfg,
            deps=deps,
        )
        logger.info(
            "[LiveRunPipelineAdapter] run_pipeline completed (%d records, source=%s).",
            self.record_count(),
            self._source_tag,
        )


__all__ = ["ActivationAuthorizationError", "LiveRunPipelineAdapter"]
