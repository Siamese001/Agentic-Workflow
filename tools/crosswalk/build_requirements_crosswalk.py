"""Build the requirements ↔ ADG ↔ test crosswalk artifact.

W4.1 of plan ``assurance-p1-gates-ab4758``. Reads
``config/crosswalk/obligations.yaml``, validates each row, and writes
``artifacts/crosswalk/requirements_crosswalk.json``.

An obligation is "resolved" iff:

  1. ``gate_script`` exists on disk.
  2. Every entry in ``test_ids`` references an existing file (the part
     before any ``::``).

Unresolved obligations are reported but the JSON artifact is always
written so the downstream CI gate can summarize.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "config" / "crosswalk" / "obligations.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "crosswalk" / "requirements_crosswalk.json"


@dataclass
class ResolvedObligation:
    id: str
    source: str
    description: str
    gate_script: str
    test_ids: list[str]
    gate_script_resolved: bool
    unresolved_test_ids: list[str] = field(default_factory=list)

    @property
    def fully_resolved(self) -> bool:
        return self.gate_script_resolved and not self.unresolved_test_ids


def _test_path_part(test_id: str) -> str:
    """Strip pytest's ``::ClassName::test_method`` suffix from a node id."""
    return test_id.split("::", 1)[0]


def resolve(obligation: dict[str, Any], *, repo_root: Path) -> ResolvedObligation:
    gate = obligation.get("gate_script", "")
    tests = list(obligation.get("test_ids") or [])
    gate_path = repo_root / gate if gate else None
    gate_ok = bool(gate_path and gate_path.is_file())
    unresolved: list[str] = []
    for tid in tests:
        path_part = _test_path_part(tid)
        if not (repo_root / path_part).is_file():
            unresolved.append(tid)
    return ResolvedObligation(
        id=str(obligation.get("id", "")),
        source=str(obligation.get("source", "")),
        description=str(obligation.get("description", "")),
        gate_script=gate,
        test_ids=tests,
        gate_script_resolved=gate_ok,
        unresolved_test_ids=unresolved,
    )


def load_registry(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"obligations registry missing: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: top-level must be a mapping")
    obligations = raw.get("obligations") or []
    if not isinstance(obligations, list):
        raise ValueError(f"{path}: 'obligations' must be a list")
    return list(obligations)


def build_crosswalk(
    *,
    registry_path: Path = DEFAULT_REGISTRY,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    rows = load_registry(registry_path)
    resolved = [resolve(r, repo_root=repo_root) for r in rows]
    unresolved = [r for r in resolved if not r.fully_resolved]
    return {
        "schema_version": 1,
        "registry_path": str(registry_path.relative_to(repo_root)),
        "total_obligations": len(resolved),
        "resolved_count": len(resolved) - len(unresolved),
        "unresolved_count": len(unresolved),
        "ids_with_duplicates": _find_duplicate_ids(resolved),
        "obligations": [asdict(r) for r in resolved],
    }


def _find_duplicate_ids(rows: list[ResolvedObligation]) -> list[str]:
    seen: dict[str, int] = {}
    for r in rows:
        seen[r.id] = seen.get(r.id, 0) + 1
    return sorted(rid for rid, n in seen.items() if n > 1)


def write_crosswalk(
    crosswalk: dict[str, Any], output_path: Path = DEFAULT_OUTPUT
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(crosswalk, indent=2, sort_keys=True), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--no-write", action="store_true", help="Validate only; do not write artifact."
    )
    args = parser.parse_args(argv)

    try:
        crosswalk = build_crosswalk(registry_path=Path(args.registry))
    except (FileNotFoundError, ValueError) as exc:
        print(f"❌ crosswalk build failed: {exc}", file=sys.stderr)
        return 2

    if not args.no_write:
        write_crosswalk(crosswalk, Path(args.output))
        print(f"📄 wrote {args.output}")

    print(
        f"crosswalk: {crosswalk['resolved_count']}/{crosswalk['total_obligations']} "
        f"obligations fully resolved"
    )
    if crosswalk["unresolved_count"]:
        print(
            f"⚠️  {crosswalk['unresolved_count']} unresolved (run "
            f"check_requirements_adg_crosswalk.py for details)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
