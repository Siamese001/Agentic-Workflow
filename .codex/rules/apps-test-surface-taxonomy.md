# Apps Test Surface Taxonomy — stub

> On-demand when adding/moving apps_* tests (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged. All `apps_<x>` tests live in 3 canonical surfaces — Unit `tests/unit/<app>/`, Integration `tests/<app>/`, Contract `tests/_apps_contract/test_<app>_*.py`; `apps_<x>/tests/` and `tests/integration/apps_<x>/` FORBIDDEN. Detail: sibling `apps-folder-taxonomy.md`. Enforced: `check_apps_folder_taxonomy.py` (T7r), `check_apps_test_surface_parity.py` (TSP1).
