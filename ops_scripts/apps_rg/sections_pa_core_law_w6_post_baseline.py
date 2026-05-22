#!/usr/bin/env python3
"""Post-rollout compile-only fingerprints (W6.2) — compare against W0 baseline."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from ops_scripts.apps_rg.core_law_rollout_w0_baseline import (  # noqa: E402
    TARGET_COMPANY,
    TARGET_ROLE,
    _analyze_compiled,
    _compile_competencies,
    _compile_headline,
    _compile_ibm_bullets,
    _compile_ibm_narrative,
    _compile_unify_bullets,
    _compile_unify_narrative,
    _load_brown_targeting,
    _markdown_table,
    _utc_ts,
)

ROLLout_SECTIONS: tuple[tuple[str, object], ...] = (
    ("headline", _compile_headline),
    ("competencies", _compile_competencies),
    ("unify_bullets", _compile_unify_bullets),
    ("unify_narrative", _compile_unify_narrative),
    ("ibm_bullets", _compile_ibm_bullets),
    ("ibm_narrative", _compile_ibm_narrative),
)


def _run_inner() -> int:
    ts = _utc_ts()
    jd, brief = _load_brown_targeting()
    w0_path = _REPO / "docs/reports/apps_rg/sections_pa_core_law_rollout_w0_baseline.json"
    w0 = json.loads(w0_path.read_text(encoding="utf-8")) if w0_path.is_file() else {"lanes": []}
    w0_by = {r["section"]: r for r in w0.get("lanes") or []}

    rows: list[dict] = []
    for section, fn in ROLLout_SECTIONS:
        content = fn(jd, brief)  # type: ignore[operator]
        post = _analyze_compiled(section, content)
        prior = w0_by.get(section) or {}
        prior_tokens = int(prior.get("compiled_tokens") or 0)
        post_tokens = int(post.get("compiled_tokens_estimate") or 0)
        delta = prior_tokens - post_tokens if prior_tokens else None
        rows.append(
            {
                "section": section,
                "w0_compiled_tokens": prior_tokens,
                "post_compiled_tokens": post_tokens,
                "delta_tokens": delta,
                "w0_static_ssot_chars": prior.get("static_ssot_chars"),
                "x2_static_w0": prior.get("x2_static"),
                "x2_static_post": post.get("count_x2_in_static_slots"),
                "product_shape_present": post.get("product_shape_present"),
            }
        )

    payload = {
        "wave": "W6_post_baseline",
        "plan_id": "sections-pa-core-law-rollout-c3a8f1",
        "timestamp": ts,
        "targeting": {"company": TARGET_COMPANY, "role": TARGET_ROLE},
        "comparison": rows,
    }
    out_json = _REPO / "docs/reports/apps_rg/sections_pa_core_law_rollout_w6_post_baseline.json"
    out_md = _REPO / "docs/reports/apps_rg/sections_pa_core_law_rollout_w6_post_baseline.md"
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def _cmp_table(data: list[dict]) -> str:
        headers = [
            "section",
            "w0_compiled_tokens",
            "post_compiled_tokens",
            "delta_tokens",
            "product_shape_present",
        ]
        out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        for r in data:
            out.append("| " + " | ".join(str(r.get(h, "")) for h in headers) + " |")
        return "\n".join(out) + "\n"

    lines = [
        "# Sections PA Core-Law — Post-Rollout Compile Baseline (W6.2)",
        "",
        f"**Generated:** {ts} (UTC)",
        "",
        "## W0 vs post-rollout compiled tokens (compile-only, Brown targeting)",
        "",
        _cmp_table(rows),
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_md}")
    return 0


def main() -> int:
    import os

    from apps_rg.runtime.section_front_spine_bridge import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    os.environ.setdefault("PYTEST_CURRENT_TEST", "ops_scripts.apps_rg.sections_pa_core_law_w6_post_baseline")
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        return _run_inner()
    finally:
        deactivate_fixture_dev_bypass()


if __name__ == "__main__":
    raise SystemExit(main())
