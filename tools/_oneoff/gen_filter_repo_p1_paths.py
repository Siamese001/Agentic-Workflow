"""Generate git-filter-repo --invert-paths manifest for P1 history purge."""
from __future__ import annotations

import subprocess
from pathlib import Path

KEEP_PREFIXES = (
    "artifacts/requirements/proof_bundles/",
    "artifacts/apps_rg/prompt_authority/",
)
SKIP_TOP = frozenset({"apps_rg", "requirements"})

def main() -> None:
    rev = subprocess.run(
        ["git", "rev-list", "--objects", "--all"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()

    children: set[str] = set()
    root_files: set[str] = set()
    req_siblings: set[str] = set()

    for raw in rev:
        parts = raw.split(maxsplit=1)
        if len(parts) < 2:
            continue
        path = parts[1].replace("\\", "/")
        if path == ".venv" or path.startswith(".venv/"):
            continue
        if not path.startswith("artifacts/"):
            continue
        if any(path.startswith(k) for k in KEEP_PREFIXES):
            continue
        if path.startswith("artifacts/requirements/"):
            if path == "artifacts/requirements/proof_bundles" or path.startswith(
                "artifacts/requirements/proof_bundles/"
            ):
                continue
            req_siblings.add(path)
            continue
        rest = path[len("artifacts/") :]
        if "/" in rest:
            top = rest.split("/")[0]
            if top not in SKIP_TOP:
                children.add(f"artifacts/{top}")
        elif rest and rest not in SKIP_TOP:
            root_files.add(f"artifacts/{rest}")

    lines = [
        "# P1 historical purge (git-filter-repo --invert-paths)",
        "# KEEP: artifacts/requirements/proof_bundles/, artifacts/apps_rg/prompt_authority/",
        ".venv",
        "artifacts/plan_lifecycle",
        *sorted(children),
        *sorted(root_files),
        *sorted(req_siblings),
    ]
    out = Path(__file__).with_name("filter_repo_p1_purge_paths.txt")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    body = [ln for ln in lines if not ln.startswith("#")]
    assert not any("proof_bundles" in ln for ln in body)
    assert "artifacts/requirements" not in body
    assert "artifacts/apps_rg" not in body
    print(f"wrote {len(lines) - 3} purge entries -> {out}")

if __name__ == "__main__":
    main()
