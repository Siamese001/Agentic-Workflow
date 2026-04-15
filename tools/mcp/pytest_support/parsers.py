from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)


def cleanup_file(path: Path) -> None:
    """Best-effort file cleanup that never masks the real outcome."""
    try:
        path.unlink(missing_ok=True)
    except TypeError:
        if path.exists():
            path.unlink()
    except OSError as exc:
        logger.warning("Failed to remove temporary file %s: %s", path, exc)


def parse_junit_summary(junit_xml: Path) -> str:
    """Handle both <testsuite> and <testsuites> roots."""
    try:
        root = ET.parse(junit_xml).getroot()
    except ET.ParseError as exc:
        logger.warning("Failed to parse JUnit XML %s: %s", junit_xml, exc)
        return ""

    if root.tag == "testsuite":
        suites = [root]
    else:
        suites = root.findall(".//testsuite")
        if not suites and root.tag == "testsuites":
            suites = list(root)

    tests = sum(int(suite.get("tests", 0) or 0) for suite in suites)
    failures = sum(int(suite.get("failures", 0) or 0) for suite in suites)
    errors = sum(int(suite.get("errors", 0) or 0) for suite in suites)
    skipped = sum(int(suite.get("skipped", 0) or 0) for suite in suites)
    time_taken = sum(float(suite.get("time", 0) or 0.0) for suite in suites)

    return (
        "\nJUnit XML Results:\n"
        f"Tests: {tests}\n"
        f"Failures: {failures}\n"
        f"Errors: {errors}\n"
        f"Skipped: {skipped}\n"
        f"Time: {time_taken:.2f}s\n"
    )


__all__ = ["cleanup_file", "parse_junit_summary"]
