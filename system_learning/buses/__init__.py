"""Meta-learning buses (BUS_T, BUS_P, BUS_U).

Per the v34 process map and ADR-050:

  - **BUS_T** (Telemetry): receives observability + metric signals from
    completed runs. Always-on read; future-run-only consumer.
  - **BUS_P** (Preference / Eval): receives preference + evaluation
    signals (rubric scores, judge calibration, HITL accept/reject).
    Always-on read; future-run-only consumer.
  - **BUS_U** (UWG-gated): receives promotion / mutation proposals.
    DEFAULT-DENY publish — every BUS_U publish requires a UWG receipt
    referencing a completed-run sealed artifact.

Hard invariants enforced by every bus:

  1. ``publish(record)`` rejects if ``record.run_id == current_run_id``
     (no current-run feedback).
  2. ``publish(record)`` on BUS_U rejects if ``record.uwg_receipt`` is
     missing, malformed, or refers to a non-sealed run.
  3. Buses NEVER mutate the records they receive; storage is append-only.
"""
from system_learning.buses.bus_t import BusT, TelemetryRecord
from system_learning.buses.bus_p import BusP, PreferenceRecord
from system_learning.buses.bus_u import (
    BusU,
    PromotionRecord,
    UWGGateError,
    UWGReceipt,
)

__all__ = [
    "BusT",
    "BusP",
    "BusU",
    "TelemetryRecord",
    "PreferenceRecord",
    "PromotionRecord",
    "UWGReceipt",
    "UWGGateError",
]


__layer__ = "L6"
__l6_chapter__ = "06.1"
