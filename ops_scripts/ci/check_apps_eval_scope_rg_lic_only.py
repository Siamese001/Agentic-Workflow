"""CI gate: apps_eval scope is limited to apps_rg and apps_lic."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPS_EVAL = ROOT / "apps_eval"
ALLOWED_APPS = {"apps_rg", "apps_lic"}
EXPECTED_SUITES = {
    "apps_rg.dev.resume_generation",
    "apps_rg.holdout.resume_generation",
    "apps_lic.dev.outreach_message",
    "apps_lic.holdout.outreach_message",
}


def _load_registry(name: str) -> dict:
    return json.loads((APPS_EVAL / "registry" / name).read_text(encoding="utf-8"))


def _allowed_token(token: str) -> bool:
    return token == "apps_eval" or token in ALLOWED_APPS or token.startswith("apps_rg_") or token.startswith("apps_lic_")


def main() -> int:
    failures: list[str] = []
    apps = _load_registry("apps.yaml").get("apps", {})
    suites = _load_registry("suites.yaml").get("suites", {})
    if set(apps) != ALLOWED_APPS:
        failures.append(f"apps registry keys must be {sorted(ALLOWED_APPS)}, got {sorted(apps)}")
    if set(suites) != EXPECTED_SUITES:
        failures.append(f"suite registry keys must be {sorted(EXPECTED_SUITES)}, got {sorted(suites)}")
    for suite_id, suite in suites.items():
        if suite.get("app_id") not in ALLOWED_APPS:
            failures.append(f"{suite_id} targets unsupported app {suite.get('app_id')}")

    token_re = re.compile(r"\bapps_[a-z0-9_]+\b")
    for path in APPS_EVAL.rglob("*"):
        if path.is_dir() or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in sorted(set(token_re.findall(text))):
            if not _allowed_token(token):
                rel = path.relative_to(ROOT).as_posix()
                failures.append(f"unsupported app token {token} in {rel}")

    if failures:
        print("apps_eval scope gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS: apps_eval registry and text scope are limited to apps_rg/apps_lic")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
