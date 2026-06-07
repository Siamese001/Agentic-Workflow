"""tools.apps_proof — anti-cheat proof harness CLI surface.

Three entrypoints, one canonical layout:

    python -m tools.apps_proof.run_app_proof --app <app_name> --fixture <path> \
        --proof-root artifacts/apps_proof --require-otel --require-replay --require-adg

    python -m tools.apps_proof.verify_app_proof --proof-dir artifacts/apps_proof/<app>/<run_id>

    python -m tools.apps_proof.adg_app_inspector --adg <snapshot> \
        --apps-glob "apps_*" --out artifacts/apps_proof/adg_apps_baseline.json

This package is a thin CLI surface on top of ``apps_shared.proof``. Runtime
logic lives in ``apps_shared.proof.scenario_base``; the verifier enforces
the §10 anti-cheat principle from the master plan.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-proof-anticheat-harness-7e2c1d.md``
"""

from __future__ import annotations

__all__: tuple[str, ...] = ()
