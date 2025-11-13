"""QA utilities for outreach validation."""

from .qa_validator import QAResult, QAValidator

__all__ = ["QAResult", "QAValidator"]


def _touch_exports() -> tuple[str, ...]:
    return tuple(__all__)


_touch_exports()
