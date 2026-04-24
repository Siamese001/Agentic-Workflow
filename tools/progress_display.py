"""
tools/progress_display.py — Canonical progress bar implementation.

Constitutional Rule §16: all operations >5s MUST display a colored progress bar.
This module provides ProgressReporter as the canonical implementation.
tqdm is used as the underlying engine.

Usage:
    from tools.progress_display import ProgressReporter

    reporter = ProgressReporter(total=len(items), label="Scanning modules")
    for item in items:
        process(item)
        reporter.update(label=f"Scanned {item}")
    reporter.done()
"""

from __future__ import annotations

import sys
from typing import Optional

try:
    from tqdm import tqdm as _tqdm

    _TQDM_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TQDM_AVAILABLE = False


class ProgressReporter:
    """
    Colored progress bar reporter wrapping tqdm.

    Falls back to plain stderr output when tqdm is unavailable.
    Compliant with Constitutional Rule §16 progress bar format.
    """

    def __init__(
        self,
        total: int,
        label: str = "Processing",
        unit: str = "item",
        colour: str = "green",
        ncols: int = 72,
        file: object = None,
    ) -> None:
        import time as _time
        self._total = total
        self._label = label
        self._count = 0
        self._done_flag = False
        self._start_monotonic = _time.monotonic()
        self._ledger_event_id = ""

        # W4.2 — progress_eta ledger: emit prediction row with total and caller
        try:
            from tools.ledgers.hook_helpers import emit_ledger_event
            # Resolve caller location (file:line) best-effort using already-imported sys
            frame = sys._getframe(1) if hasattr(sys, "_getframe") else None  # noqa: SLF001
            caller = ""
            if frame is not None:
                caller = f"{frame.f_code.co_filename}:{frame.f_lineno}"
            self._ledger_event_id = emit_ledger_event(
                ledger="progress_eta",
                event_kind="eta_predicted",
                prediction={
                    "operation_name": label,
                    "predicted_total": total,
                    "caller_location": caller,
                },
                repo_area="tools/progress_display.py",
            )
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- ledger emit fail-soft
            self._ledger_event_id = ""

        if _TQDM_AVAILABLE:
            self._bar: Optional[_tqdm] = _tqdm(  # type: ignore[type-arg]
                total=total,
                desc=label,
                unit=unit,
                colour=colour,
                ncols=ncols,
                file=file or sys.stderr,
                dynamic_ncols=False,
            )
        else:
            self._bar = None
            print(f"[progress] {label} (0/{total})", file=sys.stderr)

    def update(self, n: int = 1, label: Optional[str] = None) -> None:
        """Advance the bar by n steps, optionally updating the description."""
        self._count += n
        if self._bar is not None:
            if label:
                self._bar.set_description(label)
            self._bar.update(n)
        else:
            pct = int(self._count / self._total * 100) if self._total else 0
            print(
                f"[progress] {label or self._label} ({self._count}/{self._total}) {pct}%",
                file=sys.stderr,
            )

    def done(self) -> None:
        """Mark the operation complete and close the bar."""
        self._done_flag = True
        if self._bar is not None:
            self._bar.close()
        else:
            print(f"[progress] {self._label} complete ({self._total}/{self._total})", file=sys.stderr)
        self._bind_ledger_outcome(failed=False)

    def fail(self, message: str) -> None:
        """Mark the operation as failed with a message and close the bar."""
        if self._bar is not None:
            self._bar.set_description(f"FAILED: {message}")
            self._bar.colour = "red"
            self._bar.close()
        else:
            print(f"[progress] FAILED: {message}", file=sys.stderr)
        self._bind_ledger_outcome(failed=True, message=message)

    def _bind_ledger_outcome(self, failed: bool, message: str = "") -> None:
        """W4.2 — bind progress_eta outcome row on done() or fail()."""
        if not getattr(self, "_ledger_event_id", ""):
            return
        try:
            import time as _time
            from tools.ledgers.hook_helpers import bind_ledger_outcome
            duration_s = _time.monotonic() - self._start_monotonic
            overrun_ratio = duration_s / max(self._total, 1) if self._total else None
            if overrun_ratio is None:
                band = "unknown"
            elif 0.8 <= overrun_ratio <= 1.2:
                band = "accurate"
            elif overrun_ratio > 1.2:
                band = "slow"
            else:
                band = "fast"
            bind_ledger_outcome(
                ledger="progress_eta",
                event_id=self._ledger_event_id,
                outcome={
                    "actual_duration_s": duration_s,
                    "actual_items_processed": self._count,
                    "overrun_ratio": overrun_ratio,
                    "failed": failed,
                    "message": message,
                },
                score_band=band if not failed else "fast",
                score_numeric=duration_s,
                latency_ms=int(duration_s * 1000),
            )
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- ledger bind fail-soft
            pass

    def __enter__(self) -> "ProgressReporter":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if exc_type is not None:
            self.fail(str(exc_val))
        else:
            if not self._done_flag:
                self.done()
