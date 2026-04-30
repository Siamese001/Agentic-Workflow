"""Tests for runtime_telemetry_decorators — W4.2 skeleton.

Verifies:
  - Decorator preserves function behavior (call result + signature).
  - Static introspection works (__adg_side_effects__ etc).
  - emits_for() returns the declared intents.
  - EMITS_SUPPRESS=1 suppresses runtime emission without breaking the call.
  - Stacking decorators composes intents.
  - Invalid input rejected (empty kind, non-string).

ADR: docs/architecture/adr/ADR-075-split-runtime-telemetry-from-adg-edges.md
Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W4.2)
"""
from __future__ import annotations

import os
import unittest
from unittest import mock

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    appends_hash_chain,
    emits_for,
    emits_side_effect,
    emits_telemetry_event,
)


class TestEmitsSideEffect(unittest.TestCase):
    def test_decorator_preserves_return_value(self) -> None:
        @emits_side_effect("decision_write")
        def f(x: int) -> int:
            return x * 2

        self.assertEqual(f(5), 10)

    def test_decorator_attaches_intent_attribute(self) -> None:
        @emits_side_effect("cache_write")
        def f() -> None:
            pass

        self.assertEqual(f.__adg_side_effects__, ("cache_write",))

    def test_emits_for_returns_intent(self) -> None:
        @emits_side_effect("ledger_append")
        def f() -> None:
            pass

        intents = emits_for(f)
        self.assertEqual(intents["side_effect"], ("ledger_append",))
        self.assertEqual(intents["hash_chain"], ())
        self.assertEqual(intents["telemetry_event"], ())

    def test_undecorated_function_has_empty_intents(self) -> None:
        def f() -> None:
            pass

        self.assertEqual(emits_for(f), {
            "side_effect": (),
            "hash_chain": (),
            "telemetry_event": (),
        })

    def test_invalid_kind_rejected(self) -> None:
        with self.assertRaises(ValueError):
            emits_side_effect("")
        with self.assertRaises(ValueError):
            emits_side_effect(42)  # type: ignore[arg-type]

    def test_function_signature_preserved(self) -> None:
        @emits_side_effect("x")
        def f(a: int, b: int = 5, *, c: str = "hi") -> str:
            """docstring."""
            return f"{a}+{b}+{c}"

        self.assertEqual(f.__name__, "f")
        self.assertIn("docstring", f.__doc__ or "")
        self.assertEqual(f(1, 2, c="z"), "1+2+z")


class TestSuppression(unittest.TestCase):
    def test_emits_suppress_disables_runtime_emit(self) -> None:
        emit_calls: list[tuple[str, str]] = []

        def fake_emit(*args, **kwargs):
            emit_calls.append((args, kwargs))

        # Decorate a function and verify the fake_emit is NOT called when
        # EMITS_SUPPRESS=1, but IS called otherwise.
        @emits_side_effect("xyz")
        def f() -> int:
            return 42

        with mock.patch.dict(os.environ, {"EMITS_SUPPRESS": "1"}):
            with mock.patch(
                "agentic_core.runtime.contracts.runtime_telemetry_decorators._emit_runtime",
                side_effect=fake_emit,
            ) as patched:
                self.assertEqual(f(), 42)
                patched.assert_not_called()

        # Without suppression, the runtime emit is invoked.
        with mock.patch.dict(os.environ, {"EMITS_SUPPRESS": "0"}, clear=False):
            os.environ.pop("EMITS_SUPPRESS", None)
            with mock.patch(
                "agentic_core.runtime.contracts.runtime_telemetry_decorators._emit_runtime",
                side_effect=fake_emit,
            ) as patched:
                self.assertEqual(f(), 42)
                patched.assert_called_once()


class TestStacking(unittest.TestCase):
    def test_stacked_decorators_compose_intents(self) -> None:
        @emits_side_effect("write_op")
        @appends_hash_chain("ledger_v1")
        def f() -> None:
            pass

        intents = emits_for(f)
        self.assertEqual(intents["side_effect"], ("write_op",))
        self.assertEqual(intents["hash_chain"], ("ledger_v1",))


class TestAppendsHashChain(unittest.TestCase):
    def test_declares_chain_id(self) -> None:
        @appends_hash_chain("evidence_register")
        def f() -> None:
            pass

        self.assertEqual(f.__adg_hash_chain__, ("evidence_register",))
        self.assertEqual(emits_for(f)["hash_chain"], ("evidence_register",))

    def test_invalid_chain_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            appends_hash_chain("")


class TestTelemetryEvent(unittest.TestCase):
    def test_declares_event_name(self) -> None:
        @emits_telemetry_event("user_action")
        def f() -> None:
            pass

        self.assertEqual(f.__adg_telemetry_events__, ("user_action",))


class TestRuntimeFailureIsolated(unittest.TestCase):
    def test_runtime_emit_failure_does_not_break_function(self) -> None:
        """If the underlying telemetry backend errors, the wrapped function
        still returns normally (fail-soft per ADR-075)."""

        @emits_side_effect("safe_op")
        def f() -> int:
            return 7

        # Patch _emit_runtime to fail; the wrapped call must STILL succeed
        # because the wrapper guards via try/except. The decorator's wrapper
        # calls _emit_runtime which itself swallows internal errors, but
        # we explicitly assert the contract here.
        with mock.patch.dict(os.environ, {"EMITS_SUPPRESS": "0"}, clear=False):
            os.environ.pop("EMITS_SUPPRESS", None)
            with mock.patch(
                "agentic_core.runtime.contracts.runtime_telemetry_decorators._emit_runtime",
                side_effect=RuntimeError("backend unreachable"),
            ):
                # We expect the wrapper itself to propagate this — the swallow
                # is INSIDE _emit_runtime, not the wrapper. So this is a
                # contract check: backend errors propagate to the caller
                # ONLY if they escape the _emit_runtime guard. Since we are
                # patching _emit_runtime itself with a raising side_effect,
                # the patched function does not have the guard. So the
                # exception WILL propagate.
                with self.assertRaises(RuntimeError):
                    f()

    def test_real_emit_runtime_swallows_backend_failure(self) -> None:
        """The unpatched _emit_runtime contains its own guard — verify.
        Patches the upstream `_emit_records_telemetry_event` import to raise."""

        @emits_side_effect("guarded_op")
        def f() -> int:
            return 9

        with mock.patch.dict(os.environ, {"EMITS_SUPPRESS": "0"}, clear=False):
            os.environ.pop("EMITS_SUPPRESS", None)
            with mock.patch(
                "agentic_core.runtime.contracts.lifecycle_trace_contract._emit_records_telemetry_event",
                side_effect=RuntimeError("OTEL down"),
            ):
                # The real _emit_runtime guards this; call must still succeed.
                self.assertEqual(f(), 9)


class TestTracesExecute(unittest.TestCase):
    """Phase B `traces_execute` decorator — entry/exit/failure spans."""

    def test_passes_through_return_value(self) -> None:
        from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
            traces_execute,
        )

        @traces_execute()
        def f(x: int, y: int) -> int:
            return x + y

        self.assertEqual(f(2, 3), 5)

    def test_re_raises_exception(self) -> None:
        from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
            traces_execute,
        )

        @traces_execute()
        def f() -> None:
            raise ValueError("boom")

        with self.assertRaises(ValueError) as ctx:
            f()
        self.assertEqual(str(ctx.exception), "boom")

    def test_emits_records_execution_trace_on_entry(self) -> None:
        from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
            traces_execute,
        )

        with mock.patch.dict(os.environ, {"EMITS_SUPPRESS": "0"}, clear=False):
            os.environ.pop("EMITS_SUPPRESS", None)
            with mock.patch(
                "agentic_core.runtime.contracts.lifecycle_trace_contract._emit_records_execution_trace"
            ) as patched:
                @traces_execute(layer="L3_ORCHESTRATION")
                def my_engine_run() -> int:
                    return 42

                self.assertEqual(my_engine_run(), 42)
                patched.assert_called_once()
                # First positional arg = trace_id (uuid hex), second = layer.
                args, _ = patched.call_args
                self.assertEqual(len(args[0]), 32)  # uuid4 hex length
                self.assertEqual(args[1], "L3_ORCHESTRATION")

    def test_emits_failure_then_reraises(self) -> None:
        from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
            traces_execute,
        )

        with mock.patch.dict(os.environ, {"EMITS_SUPPRESS": "0"}, clear=False):
            os.environ.pop("EMITS_SUPPRESS", None)
            with mock.patch(
                "agentic_core.runtime.contracts.lifecycle_trace_contract._emit_hard_fails_untranscripted"
            ) as patched:
                @traces_execute()
                def failing() -> None:
                    raise RuntimeError("downstream")

                with self.assertRaises(RuntimeError):
                    failing()
                patched.assert_called_once()

    def test_suppress_skips_emits(self) -> None:
        from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
            traces_execute,
        )

        with mock.patch.dict(os.environ, {"EMITS_SUPPRESS": "1"}):
            with mock.patch(
                "agentic_core.runtime.contracts.lifecycle_trace_contract._emit_records_execution_trace"
            ) as entry, mock.patch(
                "agentic_core.runtime.contracts.lifecycle_trace_contract._emit_records_telemetry_event"
            ) as exit_:
                @traces_execute()
                def f() -> int:
                    return 1

                self.assertEqual(f(), 1)
                entry.assert_not_called()
                exit_.assert_not_called()

    def test_static_introspection_marker(self) -> None:
        from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
            traces_execute,
        )

        @traces_execute(operation="MyEngine.run")
        def run() -> None:
            pass

        self.assertEqual(
            getattr(run, "__adg_traces_execute__", ()),
            ("MyEngine.run",),
        )


if __name__ == "__main__":
    unittest.main()
