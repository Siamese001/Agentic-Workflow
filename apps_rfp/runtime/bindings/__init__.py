"""apps_rfp runtime stage bindings — W2 one-spine migration.

All 7 stage binding functions live here. AppIngressRunner(profile=profile).run(payload)
sequences them; no app-owned dispatch callable.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P1
"""
from apps_rfp.runtime.bindings.u0_binding import rfp_u0
from apps_rfp.runtime.bindings.l1_binding import rfp_l1
from apps_rfp.runtime.bindings.l0_binding import rfp_l0
from apps_rfp.runtime.bindings.c0_binding import rfp_c0
from apps_rfp.runtime.bindings.pa_binding import rfp_pa
from apps_rfp.runtime.bindings.l2_binding import rfp_l2
from apps_rfp.runtime.bindings.exit_binding import rfp_exit

__all__ = ["rfp_u0", "rfp_l1", "rfp_l0", "rfp_c0", "rfp_pa", "rfp_l2", "rfp_exit"]
