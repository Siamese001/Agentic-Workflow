"""L2 E1 PREP stage — load suite config, scenario defs, freeze run directory."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PrepResult:
    ok: bool = False
    failure_reason: str | None = None
    suite_ids: list[str] = field(default_factory=list)
    scenario_filter: str = ""
    baseline_mode: bool = False
    out_dir: Path = field(default_factory=lambda: Path("artifacts/apps_eval/runs"))
    deterministic_only: bool = False
    cache_strategy: str = "exact"
    suite_configs: list[dict] = field(default_factory=list)
    scenarios: list[dict] = field(default_factory=list)
    content_hashes: dict[str, str] = field(default_factory=dict)
    run_dir: Path | None = None
    replay_key: str | None = None
    idempotency_key: str | None = None


class EvalPrepStage:
    """Prepare evaluation run: load configs, scenarios, freeze directory."""

    def __init__(
        self,
        suite_ids: list[str],
        scenario_filter: str,
        baseline_mode: bool,
        out_dir: str,
        deterministic_only: bool,
        cache_strategy: str,
    ):
        self.suite_ids = suite_ids
        self.scenario_filter = scenario_filter
        self.baseline_mode = baseline_mode
        self.out_dir = Path(out_dir)
        self.deterministic_only = deterministic_only
        self.cache_strategy = cache_strategy

    def run(self) -> PrepResult:
        result = PrepResult(
            suite_ids=self.suite_ids,
            scenario_filter=self.scenario_filter,
            baseline_mode=self.baseline_mode,
            out_dir=self.out_dir,
            deterministic_only=self.deterministic_only,
            cache_strategy=self.cache_strategy,
        )

        # Load suite configs
        suite_configs = self._load_suite_configs()
        if not suite_configs:
            result.failure_reason = "no_suites_found"
            return result
        result.suite_configs = suite_configs

        # Load scenarios
        scenarios = self._load_scenarios(suite_configs)
        if not scenarios:
            result.failure_reason = "no_scenarios_match_filter"
            return result
        result.scenarios = scenarios

        # Compute content hashes
        result.content_hashes = self._compute_hashes(suite_configs, scenarios)

        # Freeze run directory
        result.run_dir = self._freeze_run_dir()

        # Create replay key
        result.replay_key = self._create_replay_key(result.content_hashes)
        result.idempotency_key = result.replay_key

        result.ok = True
        return result

    def _load_suite_configs(self) -> list[dict]:
        """Load suite configurations from eval_policies.yaml or registry."""
        # TODO: Implement YAML loading (deferred)
        return [{"id": sid, "active": True} for sid in self.suite_ids]

    def _load_scenarios(self, suite_configs: list[dict]) -> list[dict]:
        """Load scenarios from evaluation_prompts.json."""
        # TODO: Implement JSON loading (deferred)
        return [{"id": f"scenario_{i}", "suite": s["id"]} for i, s in enumerate(suite_configs)]

    def _compute_hashes(self, suite_configs: list[dict], scenarios: list[dict]) -> dict[str, str]:
        """Compute SHA256 hashes for policy, scenarios, thresholds."""
        import hashlib

        policy_str = json.dumps(suite_configs, sort_keys=True)
        scenario_str = json.dumps(scenarios, sort_keys=True)
        return {
            "policy": hashlib.sha256(policy_str.encode()).hexdigest()[:16],
            "scenarios": hashlib.sha256(scenario_str.encode()).hexdigest()[:16],
        }

    def _freeze_run_dir(self) -> Path:
        """Create timestamped run directory for artifacts."""
        from datetime import datetime

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.out_dir / ts
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _create_replay_key(self, content_hashes: dict[str, str]) -> str:
        """Create deterministic replay key from content hashes."""
        import hashlib

        key_str = json.dumps(content_hashes, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]
