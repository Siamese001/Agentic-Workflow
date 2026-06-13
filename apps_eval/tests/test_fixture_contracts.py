from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_eval.registry import load_suites_registry


def _stable_hash(data: dict) -> str:
    snapshot = dict(data)
    snapshot.pop("deterministic_hash", None)
    raw = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def test_dev_fixtures_have_required_contract_files() -> None:
    suites = load_suites_registry()
    for suite_id, suite in suites.items():
        if suite["split"] != "dev":
            continue
        root = Path(suite["fixture_root"])
        for scenario_id in suite["scenarios"]:
            scenario_root = root / scenario_id
            assert (scenario_root / "scenario.yaml").is_file(), suite_id
            assert (scenario_root / "input" / "request.json").is_file(), suite_id
            assert (scenario_root / "expected" / "expectations.json").is_file(), suite_id
            assert (scenario_root / "snapshots" / "app_output_snapshot.json").is_file(), suite_id
            assert (scenario_root / "snapshots" / "artifacts").is_dir(), suite_id


def test_snapshot_hashes_match_fixture_content() -> None:
    suites = load_suites_registry()
    for suite in suites.values():
        if suite["split"] != "dev":
            continue
        for scenario_id in suite["scenarios"]:
            path = Path(suite["fixture_root"]) / scenario_id / "snapshots" / "app_output_snapshot.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data["deterministic_hash"] == _stable_hash(data)
