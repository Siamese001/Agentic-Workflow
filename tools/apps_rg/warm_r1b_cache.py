"""R1B semantic cache warm-up script for apps_rg.

Pre-seeds the R1B semantic cache with synthetic intent stubs for a configurable
list of (target_company, target_role) pairs so that cold-start requests for
common pairs receive a cache hit without a real pipeline run.

Usage::

    python tools/apps_rg/warm_r1b_cache.py [--pairs-file PATH] [--top N]
        [--policy-hash HASH] [--blueprint-hash HASH] [--tenant-id ID]
        [--dry-run]

Pairs are read from (in priority order):
1. ``--pairs-file`` JSON/YAML file  [{company, role, level?}]
2. Built-in TOP_PAIRS fallback list (top 20 common pairs)

Each pair produces a synthetic cache entry with a placeholder ``output_chunks``
body. The entry encodes the current ``policy_hash`` and ``blueprint_hash`` so
stale entries are invalidated automatically when hashes rotate.

Run time: < 5 min for 20 pairs without actual model inference (stub path).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Any

# Ensure repo root is on sys.path when script is run directly
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default top-20 pairs (override with --pairs-file)
# ---------------------------------------------------------------------------

TOP_PAIRS: list[dict[str, str]] = [
    {"company": "Google", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Google", "role": "Staff Software Engineer", "level": "staff"},
    {"company": "Meta", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Meta", "role": "Engineering Manager", "level": "manager"},
    {"company": "Amazon", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Amazon", "role": "Principal Engineer", "level": "principal"},
    {"company": "Microsoft", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Microsoft", "role": "Principal Software Engineer", "level": "principal"},
    {"company": "Apple", "role": "Software Engineer", "level": "mid"},
    {"company": "Apple", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Netflix", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Netflix", "role": "Staff Engineer", "level": "staff"},
    {"company": "Stripe", "role": "Software Engineer", "level": "mid"},
    {"company": "Stripe", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Airbnb", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Airbnb", "role": "Staff Software Engineer", "level": "staff"},
    {"company": "Uber", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Lyft", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "Databricks", "role": "Senior Software Engineer", "level": "senior"},
    {"company": "OpenAI", "role": "Software Engineer", "level": "senior"},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        stream=sys.stdout,
    )


def _load_from_registry(app_name: str = "apps_rg") -> list[dict[str, str]]:
    """Load warm-up pairs from <app_name>/config/warmup_pairs.yaml.

    Falls back to TOP_PAIRS if the file is absent or malformed.
    """
    registry_path = _REPO_ROOT / app_name / "config" / "warmup_pairs.yaml"
    if not registry_path.exists():
        _log.warning(
            "warmup_pairs.yaml not found at %s — falling back to built-in TOP_PAIRS",
            registry_path,
        )
        return TOP_PAIRS
    try:
        import yaml  # type: ignore[import-untyped]

        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "pairs" not in data:
            _log.warning("warmup_pairs.yaml missing 'pairs' key — falling back to TOP_PAIRS")
            return TOP_PAIRS
        pairs = data["pairs"]
        if not isinstance(pairs, list) or not pairs:
            _log.warning("warmup_pairs.yaml 'pairs' is empty — falling back to TOP_PAIRS")
            return TOP_PAIRS
        _log.info("Loaded %d pairs from %s", len(pairs), registry_path)
        return [
            {
                "company": str(p.get("company", "")).strip(),
                "role": str(p.get("role", "")).strip(),
                "level": str(p.get("level", "mid")).strip(),
            }
            for p in pairs
            if isinstance(p, dict)
        ]
    except Exception as exc:  # guardian: allow-broad-exception -- fail-soft registry read
        _log.warning("Failed to load warmup_pairs.yaml (%s) — falling back to TOP_PAIRS", exc)
        return TOP_PAIRS


def _load_pairs_file(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore[import-untyped]
            data = yaml.safe_load(text)
        except ImportError:
            raise SystemExit("PyYAML required to read .yaml pairs file: pip install pyyaml")
    else:
        data = json.loads(text)
    if not isinstance(data, list):
        raise SystemExit(f"pairs file must be a JSON/YAML array, got {type(data).__name__}")
    return data


def _make_synthetic_output(company: str, role: str) -> list[dict[str, Any]]:
    """Placeholder output stub — real runs will overwrite this entry."""
    return [
        {
            "_warm_stub": True,
            "summary": f"Pre-warmed placeholder for {role} at {company}.",
            "sections": [],
            "warm_run_id": str(uuid.uuid4()),
        }
    ]


# ---------------------------------------------------------------------------
# Core warm-up logic
# ---------------------------------------------------------------------------


def _make_stub_profile(tmp_dir: Path, company: str, role: str) -> Path:
    """Write a minimal YAML profile stub and return its path."""
    stub_path = tmp_dir / f"stub_{company[:8]}_{role[:8]}.yaml".replace(" ", "_")
    stub_path.write_text(
        f"name: WarmupStub\nrole: {role}\ncompany: {company}\n",
        encoding="utf-8",
    )
    return stub_path


def warm_pair(
    company: str,
    role: str,
    level: str,
    policy_hash: str,
    blueprint_hash: str,
    tenant_id: str,
    dry_run: bool,
    tmp_dir: Path | None = None,
) -> bool:
    """Pre-seed R1B cache for one (company, role) pair.

    Returns True on success (or dry-run), False on failure.
    """
    try:
        import tempfile

        from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter
        from apps_rg.utils.intent_builder import build_intent_from_request

        # Write a minimal stub profile so _hash_file() succeeds without real data.
        # Caller (run_warmup) passes a shared tmp_dir; standalone callers get a fresh one.
        _tmp = tmp_dir if tmp_dir is not None else Path(tempfile.mkdtemp(prefix="r1b_warmup_single_"))
        stub_path = _make_stub_profile(_tmp, company, role)

        intent = build_intent_from_request(
            candidate_profile_path=stub_path,
            target_company=company,
            target_role=role,
            target_level=level,
            policy_hash=policy_hash,
            blueprint_hash=blueprint_hash,
            tenant_id=tenant_id,
            request_id=f"warm_{uuid.uuid4().hex[:8]}",
        )
        output_chunks = _make_synthetic_output(company, role)

        if dry_run:
            _log.info(
                "[dry-run] Would warm: %s / %s (level=%s)  hash=%s",
                company, role, level, intent.to_cache_key_dict().get("source_resume_hash", "n/a")[:8],
            )
            return True

        adapter = AppsRgR1BCacheAdapter(tenant_id=tenant_id)
        entry_id = adapter.store_intent_and_output(
            intent=intent,
            output_chunks=output_chunks,
            run_context={
                "run_id": f"warm_{uuid.uuid4().hex[:8]}",
                "exit_disposition": "warm_stub",
                "uwg_commit_receipt": None,
                "policy_hash": policy_hash,
                "blueprint_hash": blueprint_hash,
            },
        )
        if entry_id:
            _log.info("Warmed: %s / %s  entry_id=%s", company, role, entry_id)
        else:
            _log.warning("Store returned None for: %s / %s", company, role)
        return entry_id is not None

    except Exception as exc:  # guardian: allow-broad-exception -- warm-up is fully fail-soft
        _log.warning("Failed to warm %s / %s: %s", company, role, exc)
        return False


def run_warmup(
    pairs: list[dict[str, str]],
    policy_hash: str,
    blueprint_hash: str,
    tenant_id: str,
    dry_run: bool,
    top: int,
) -> dict[str, int]:
    """Run warm-up for up to ``top`` pairs. Returns summary dict."""
    import shutil
    import tempfile

    selected = pairs[:top]
    summary = {"total": len(selected), "succeeded": 0, "failed": 0, "skipped": 0}

    if not selected:
        _log.warning("No pairs to warm — check --pairs-file or TOP_PAIRS list.")
        return summary

    _log.info(
        "Starting R1B cache warm-up: %d pairs  policy=%s  blueprint=%s  dry_run=%s",
        len(selected), policy_hash[:8], blueprint_hash[:8], dry_run,
    )

    tmp_dir = Path(tempfile.mkdtemp(prefix="r1b_warmup_"))
    try:
        for i, pair in enumerate(selected, 1):
            company = pair.get("company", "").strip()
            role = pair.get("role", "").strip()
            level = pair.get("level", "mid").strip()

            if not company or not role:
                _log.warning("Pair %d missing company or role — skipping: %s", i, pair)
                summary["skipped"] += 1
                continue

            ok = warm_pair(
                company, role, level, policy_hash, blueprint_hash, tenant_id, dry_run,
                tmp_dir=tmp_dir,
            )
            if ok:
                summary["succeeded"] += 1
            else:
                summary["failed"] += 1
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    _setup_logging()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pairs-file",
        default=None,
        help="Path to JSON or YAML file containing [{company, role, level?}] pairs",
    )
    parser.add_argument(
        "--from-registry",
        action="store_true",
        help="Load pairs from apps_rg/config/warmup_pairs.yaml (falls back to TOP_PAIRS if absent)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Maximum number of pairs to warm (default: 20)",
    )
    parser.add_argument(
        "--policy-hash",
        default=os.environ.get("APPS_RG_POLICY_HASH", "policy_v1"),
        help="Policy hash to embed in warm entries (default: APPS_RG_POLICY_HASH env or 'policy_v1')",
    )
    parser.add_argument(
        "--blueprint-hash",
        default=os.environ.get("APPS_RG_BLUEPRINT_HASH", "blueprint_v1"),
        help="Blueprint hash to embed in warm entries",
    )
    parser.add_argument(
        "--tenant-id",
        default="default",
        help="Tenant ID for cache namespace (default: 'default')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be warmed without writing to cache",
    )
    args = parser.parse_args(argv)

    if args.pairs_file:
        pairs_path = Path(args.pairs_file)
        if not pairs_path.exists():
            _log.error("pairs-file not found: %s", pairs_path)
            return 1
        pairs = _load_pairs_file(pairs_path)
    elif args.from_registry:
        pairs = _load_from_registry()
    else:
        pairs = TOP_PAIRS

    summary = run_warmup(
        pairs=pairs,
        policy_hash=args.policy_hash,
        blueprint_hash=args.blueprint_hash,
        tenant_id=args.tenant_id,
        dry_run=args.dry_run,
        top=args.top,
    )

    _log.info(
        "Warm-up complete.  total=%d  succeeded=%d  failed=%d  skipped=%d",
        summary["total"], summary["succeeded"], summary["failed"], summary["skipped"],
    )
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
