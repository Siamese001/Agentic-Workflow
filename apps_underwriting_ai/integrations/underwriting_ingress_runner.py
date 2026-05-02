"""UnderwritingIngressRunner — file/stdin ingress for apps_underwriting_ai.

Reads an underwriting request from a YAML or JSON file and dispatches via
the governed run. Used by ``__main__.py`` as the CLI entry point.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from apps_underwriting_ai.integrations.governed_underwriting_run import (
    governed_underwriting_run,
)
from apps_underwriting_ai.types.underwriting_types import UnderwritingResult


class UnderwritingIngressRunner:
    """Reads underwriting requests from disk and dispatches them."""

    def run_from_file(
        self,
        path: Path | str,
        *,
        trace_id: str | None = None,
    ) -> UnderwritingResult:
        """Run the pipeline against a request loaded from `path`.

        Args:
            path: Path to a YAML (`.yaml`, `.yml`) or JSON (`.json`) file
                containing the inbound request fields.
            trace_id: Optional trace stamp applied to the result. When
                provided, overrides any ``trace_id`` embedded in the
                payload; when ``None``, falls back to the payload's
                ``trace_id`` field (or the empty default).

        Returns:
            UnderwritingResult.

        Raises:
            FileNotFoundError: If `path` does not exist.
            ValueError: If the file extension is unsupported or the payload
                is missing required fields.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"underwriting request file not found: {path}")
        text = p.read_text(encoding="utf-8")
        if p.suffix in {".yaml", ".yml"}:
            payload: dict[str, Any] = yaml.safe_load(text) or {}
        elif p.suffix == ".json":
            payload = json.loads(text)
        else:
            raise ValueError(
                f"unsupported request file extension: {p.suffix} "
                "(expected .yaml/.yml/.json)"
            )

        for required in ("request_id", "applicant_id", "product_class"):
            if required not in payload:
                raise ValueError(
                    f"underwriting request missing required field: {required}"
                )

        effective_trace_id = (
            trace_id
            if trace_id is not None
            else str(payload.get("trace_id", "") or "")
        )
        return governed_underwriting_run(
            request_id=payload["request_id"],
            applicant_id=payload["applicant_id"],
            product_class=payload["product_class"],
            documents=tuple(payload.get("documents", ())),
            metadata=payload.get("metadata") or {},
            trace_id=effective_trace_id,
        )
