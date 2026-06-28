"""Provider-neutral offline-contract-stub runtime status marker for apps_rg.

Relocated from the retired ``PROVIDER_MODEL_offline_contract_stub`` module (PROVIDER_MODEL/external model removal).
The offline contract stub is permanently disabled for product runs — apps_rg requires
a live external generation provider. This module keeps only the runtime-status constant
(woven into X2/X3 gates and proof accounting) plus the always-false enabled predicate,
so gate semantics are preserved without any PROVIDER_MODEL coupling.
"""
from __future__ import annotations

# Proof/gate runtime status marker. Value preserved verbatim so X2/X3 and proof-accounting
# comparisons that key on this string remain byte-stable across the PROVIDER_MODEL removal.
OFFLINE_CONTRACT_STUB_RUNTIME_STATUS = "OFFLINE_CONTRACT_STUB"


def offline_contract_stub_enabled() -> bool:
    """Offline contract stub is permanently disabled for apps_rg product runs."""
    return False


def effective_offline_contract_stub_enabled() -> bool:
    return False


__all__ = [
    "OFFLINE_CONTRACT_STUB_RUNTIME_STATUS",
    "effective_offline_contract_stub_enabled",
    "offline_contract_stub_enabled",
]
