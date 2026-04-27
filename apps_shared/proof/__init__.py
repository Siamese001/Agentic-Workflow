"""apps_shared.proof — runtime proof harness for apps_*.

Closes plan ``apps-runtime-proof-harness-9d4c2a``. Every ``apps_*`` run that
flows through the governed spine must emit a verifiable
:class:`~apps_shared.proof.proof_contracts.AppRunEvidencePacket`.

Public surface (W1 foundation):

* :mod:`apps_shared.proof.proof_contracts` — evidence packet + hashing
* :mod:`apps_shared.proof.app_inventory` — ADG-driven app discovery
* :mod:`apps_shared.proof.adg_queries` — bypass-class queries
* :mod:`apps_shared.proof.bypass_validator` — PASS/FAIL gate over ADG
* :mod:`apps_shared.proof.proof_runner` — CLI entrypoint

Per-app scenarios, replay, negative controls, and tests are scaffolded in
W2..W4 of the plan.
"""

from __future__ import annotations

# Submodules are imported lazily by callers; declaring them in __all__ would
# require eager imports and trigger import-time work on every package import.
__all__: list[str] = []
