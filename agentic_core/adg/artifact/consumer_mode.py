"""ADG consumer mode declaration spec (W4).

Every file that reads or queries the ADG MUST declare its consumer mode
via a module-level constant ``__adg_consumer_mode__``. The constant
records WHICH of the three canonical views the file's queries are
authoritative for:

    proof      → reads ``proof_view`` only; output may drive enforcement,
                 promotion, blast-radius claims, and architectural
                 verdicts
    risk       → reads ``risk_view`` (or both proof_view and risk_view);
                 output is a SIGNAL, never a verdict — drives ratchets,
                 alerts, hygiene reports
    inventory  → reads ``inventory_view`` (or any view) for SIZING ONLY;
                 output never drives policy or enforcement

The CI gate ``ops_scripts/ci/check_consumer_mode_declared.py`` enforces
the declaration, and the gate's mode-mismatch logic flags consumers that
read views inconsistent with their declared mode.

Doctrinal source: 2026-04-29 user directive — "W4 Consumer audit + CI
gate".
"""

from __future__ import annotations

from typing import Final

CONSUMER_MODE_PROOF: Final[str] = "proof"
CONSUMER_MODE_RISK: Final[str] = "risk"
CONSUMER_MODE_INVENTORY: Final[str] = "inventory"

ALL_CONSUMER_MODES: Final[frozenset[str]] = frozenset(
    {CONSUMER_MODE_PROOF, CONSUMER_MODE_RISK, CONSUMER_MODE_INVENTORY}
)

# View name → minimum mode required to read that view.
# A consumer reading proof_view in inventory mode is a violation; a
# consumer reading risk_view declared as proof is also a violation
# (declares more authority than it has).
VIEW_TO_REQUIRED_MODE: Final[dict[str, str]] = {
    "proof_view": CONSUMER_MODE_PROOF,
    "risk_view": CONSUMER_MODE_RISK,
    "inventory_view": CONSUMER_MODE_INVENTORY,
    # Legacy aliases (W1 back-compat).
    "mv_verified_dependencies": CONSUMER_MODE_PROOF,
    "mv_unresolved_dependencies": CONSUMER_MODE_RISK,
    "mv_governance_dependencies": CONSUMER_MODE_RISK,
}

# Mode authority order: proof > risk > inventory. A consumer declared at
# a HIGHER authority level may read views at lower levels (proof can
# read risk_view to fold a hint into a verdict). A consumer at LOWER
# level reading a higher view = mode-mismatch violation.
MODE_AUTHORITY_RANK: Final[dict[str, int]] = {
    CONSUMER_MODE_INVENTORY: 0,
    CONSUMER_MODE_RISK: 1,
    CONSUMER_MODE_PROOF: 2,
}


def is_valid_mode(mode: str) -> bool:
    """Return True iff ``mode`` is one of the three canonical modes."""
    return mode in ALL_CONSUMER_MODES


def is_mode_compatible_with_view(*, declared_mode: str, view_name: str) -> bool:
    """Return True iff a consumer in ``declared_mode`` may read ``view_name``.

    Authority rule:
        proof  may read proof_view, risk_view, inventory_view
        risk   may read risk_view, inventory_view  (NOT proof_view)
        inventory may read inventory_view only
    """
    if declared_mode not in MODE_AUTHORITY_RANK:
        return False
    required = VIEW_TO_REQUIRED_MODE.get(view_name)
    if required is None:
        # Unknown view — be conservative; only proof-mode consumers may
        # touch unknown views (they are the only mode allowed to make
        # verdicts, so they bear the cost of false positives).
        return declared_mode == CONSUMER_MODE_PROOF
    return MODE_AUTHORITY_RANK[declared_mode] >= MODE_AUTHORITY_RANK[required]


# Standard module-level constant name consumers MUST set.
DECLARATION_NAME: Final[str] = "__adg_consumer_mode__"
