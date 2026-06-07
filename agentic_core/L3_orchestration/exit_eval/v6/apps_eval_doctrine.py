"""W6 — Apps_* Evaluation Harness Parity — doctrinal fence posts (out-of-scope).

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-parity-f8d4a2.md`` Wave 6.

This module is intentionally declarative. It declares the boundary of the
harness-parity plan so Author-Gate reviewers can reject scope-creep
proposals against this plan. It has no runtime behavior.

Any proposal to breach a fence requires a separate plan with its own
Author-Gate decision packet. These fences cannot be lifted inside the
apps-eval-harness-parity plan.

Fence posts
===========

W6.P1 — No change to architectural authority rules
--------------------------------------------------
Apps_* remain domain intent producers. L2 keeps bounded-execution authority.
L5 keeps certification-evidence authority. UWG remains the sole durable-write
path. L4 mutation remains exclusive to UWG. Nothing in the harness parity
work widens or alters these authorities — grader registration is read-only,
Exit is the enforcer, and the five 5-surface boundaries (Execution / Write /
Security / State / Observability) remain unchanged.

W6.P2 — No new apps_* domains introduced
----------------------------------------
Scope is harness parity for the existing eight runtime apps
(``apps_rg``, ``apps_lic``, ``apps_rfp``, ``apps_qna``, ``apps_research``,
``apps_exec``, ``apps_underwriting_ai``) plus the meta domain ``apps_eval``.
No new ``apps_*`` directory may be introduced by this plan.

W6.P3 — No rubric dimension deletion
-------------------------------------
A published rubric dimension may be flipped (``status`` draft → active),
tuned (``min_required_score`` raised), demoted to ``tracked_metric_only``,
or have a grader registered. It may NOT be deleted. Deletion creates
historical-comparability loss and breaks downstream calibration ledgers.

W6.P4 — ``apps_shared`` remains library scope
----------------------------------------------
No domain rubric is appropriate for shared library code. ``apps_shared``
has no domain product output — any attempt to register a domain rubric
against it is forbidden.

W6.P5 — No runtime SIGNED_OFF certification claims from this plan
------------------------------------------------------------------
Fort Knox certification remains governed by Constitutional §32's two-arm
pipeline (``agentic_core`` arm + ``apps_e2e`` arm). This plan feeds
evidence INTO that pipeline but does not itself emit ``RTC-REQ-*`` or
``APPS-REQ-*`` claims. ``compile_requirement_signoff.py`` and
``compile_apps_e2e_signoff.py`` remain the only producers.

W6.P6 — No widening of apps_* authority
----------------------------------------
apps_* must not gain route authority, final-approval authority, durable-write
authority, or L4-mutation authority as a side effect of harness wiring.
Grader registration is read-only. Exit is the enforcer. No route-table
membership changes, no UWG direct-write paths, no L4 durable-state writes.
"""

from __future__ import annotations

__all__ = ["FENCE_POSTS"]


# Machine-readable record of the fences for introspection / CI hooks.
# Consumers that want to assert "did this plan breach a fence?" can import
# this dict and cross-reference against the diff.
FENCE_POSTS: "tuple[dict[str, str], ...]" = (
    {
        "id": "W6.P1",
        "title": "No change to architectural authority rules",
        "forbids": "route_authority_change, l4_mutation_authority_change, uwg_bypass",
    },
    {
        "id": "W6.P2",
        "title": "No new apps_* domains introduced",
        "forbids": "new apps_*/ directory under repo root",
    },
    {
        "id": "W6.P3",
        "title": "No rubric dimension deletion",
        "forbids": "removing entries from eval_rubrics.yaml score_dimensions",
    },
    {
        "id": "W6.P4",
        "title": "apps_shared remains library scope",
        "forbids": "registering a domain rubric against apps_shared",
    },
    {
        "id": "W6.P5",
        "title": "No runtime SIGNED_OFF certification claims from this plan",
        "forbids": "emitting RTC-REQ-* / APPS-REQ-* claims outside the §32 two-arm pipeline",
    },
    {
        "id": "W6.P6",
        "title": "No widening of apps_* authority",
        "forbids": "apps_* gaining route/approval/durable-write/L4-mutation authority",
    },
)
