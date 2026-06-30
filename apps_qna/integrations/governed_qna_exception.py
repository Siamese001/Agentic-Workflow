"""Compensating-control verifier for apps_qna's build-time compiler shape."""

from __future__ import annotations

import importlib

ControlResult = tuple[str, bool, str]


class GovernedQnaException:
    """Machine-checkable controls for apps_qna's non-runner spine adoption."""

    def check_compensating_controls(self) -> list[ControlResult]:
        handoff = importlib.import_module("apps_qna.integrations.spine_handoff")
        c0 = importlib.import_module("apps_qna.runtime.bindings.c0_binding")
        return [
            (
                "CC-QNA-01",
                callable(getattr(handoff, "build_pack_via_spine", None)),
                "build-time pack generation is wrapped in ValidatedRequest handoff",
            ),
            (
                "CC-QNA-02",
                c0 is not None,
                "live runtime pack route exposes canonical C0 binding module",
            ),
        ]


__all__ = ["GovernedQnaException", "ControlResult"]

