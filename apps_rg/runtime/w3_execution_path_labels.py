"""W3 execution-path classification — child plan ``apps-rg-agentic-core-boundary-remediation-child-f8e3c1``.

Buckets match wave W3 acceptance (exact strings for manifests and static checks):

1. ``governed_pa_l2_exit`` — package-driven PA/L2/Exit spine (core gateways / adapters).
2. ``test_dev_only`` — harnesses, demos, or tests only; not a production default.
3. ``quarantine`` — legacy or fenced slice pending removal/convergence.
4. ``declared_temporary_slice`` — working runtime proof / section seam outside the default spine;
   carries proof obligations until converged or promoted.

Import-time ``validate_bucket`` is a cheap guard against typos or unlabeled surfaces.
"""

from __future__ import annotations

PLAN_SLUG = "apps-rg-agentic-core-boundary-remediation-child-f8e3c1"

BUCKET_GOVERNED_PA_L2_EXIT = "governed_pa_l2_exit"
BUCKET_TEST_DEV_ONLY = "test_dev_only"
BUCKET_QUARANTINE = "quarantine"
BUCKET_DECLARED_TEMPORARY_SLICE = "declared_temporary_slice"

ALL_BUCKETS = frozenset(
    {
        BUCKET_GOVERNED_PA_L2_EXIT,
        BUCKET_TEST_DEV_ONLY,
        BUCKET_QUARANTINE,
        BUCKET_DECLARED_TEMPORARY_SLICE,
    }
)


def validate_bucket(bucket: str, *, context: str) -> None:
    """Raise if *bucket* is not one of the four W3 buckets."""
    if bucket not in ALL_BUCKETS:
        raise ValueError(f"Invalid W3 execution-path bucket {bucket!r} for {context}")
