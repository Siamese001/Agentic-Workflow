"""Narrow CLI: bounded role-family fact selection into SelectedRoleFactSet artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="apps_rg.fact_inventory.select_role_facts",
        description="Emit deterministic selected_role_fact_set JSON+MD artifacts (selection only; no generation).",
    )
    root = _repo_root_from_here()
    p.add_argument("--target-role", required=True)
    p.add_argument("--target-company", required=True)
    p.add_argument("--jd-file", type=Path, required=True)
    p.add_argument("--briefing-file", type=Path, required=True)
    p.add_argument(
        "--ledger",
        type=Path,
        default=root / "artifacts" / "apps_rg" / "fact_inventory" / "master_candidate_skills_fact_ledger_20260518T1100Z.json",
    )
    p.add_argument(
        "--taxonomy",
        type=Path,
        default=root / "apps_rg" / "config" / "domain_contract" / "master_role_family_taxonomy.yaml",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Defaults to artifacts/apps_rg/fact_inventory/",
    )
    p.add_argument(
        "--timestamp",
        dest="stamp",
        default=None,
        help="UTC slug for filenames (defaults to deterministic selection emitted selected_at)",
    )

    ns = p.parse_args(argv)

    jd_text = Path(ns.jd_file).read_text(encoding="utf-8")
    brief_text = Path(ns.briefing_file).read_text(encoding="utf-8")

    import json

    import yaml

    from apps_rg.fact_inventory.candidate_fact_ledger import load_master_candidate_fact_ledger

    ledger = load_master_candidate_fact_ledger(path=Path(ns.ledger))

    taxonomy = yaml.safe_load(Path(ns.taxonomy).read_text(encoding="utf-8"))
    from apps_rg.fact_inventory.selected_role_fact_set import (
        select_candidate_facts_for_role,
        utc_timestamp_slug,
        write_selected_role_fact_set_artifacts,
    )

    slug = ns.stamp or utc_timestamp_slug()
    srfs = select_candidate_facts_for_role(
        target_company=ns.target_company,
        target_role=ns.target_role,
        jd_text=jd_text,
        briefing_text=brief_text,
        ledger=ledger,
        taxonomy=taxonomy,
        source_ledger_path=str(Path(ns.ledger).resolve()),
        taxonomy_ref=str(Path(ns.taxonomy).resolve()),
        now_slug=slug,
        repo_root=root,
    )
    jpath, mdpath = write_selected_role_fact_set_artifacts(
        srfs,
        repo_root=root,
        timestamp_slug=slug,
        fact_inventory_dir=ns.out_dir,
    )

    sys.stdout.write(f"WRITE_JSON={jpath.resolve()}\nWRITE_MD={mdpath.resolve()}\nSELECTION_ID={srfs.selection_id}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
