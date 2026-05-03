"""apps_rg outputs -> ExperienceLibrary adapter.

apps_rg (resume generator) emits a YAML resume bank under `apps_rg/data/`.
As of Wave 3 of plan apps-cross-app-precursors-c94c71 a sibling
`<name>.envelope.json` (ResumeBankEnvelope) is the preferred contract;
the raw YAML path is retained as fallback with DeprecationWarning.

YAML schema (fallback):

    points:
      - title: "..."
        one_liner: "..."
        technical_depth_tags: ["agentic", "governance"]
    star_bank:
      stories:
        - name: "..."
          situation: "..."
          task: "..."
          action: "..."
          result: "..."
          lesson: "..."
          tags: ["governance"]
    rca_bank:
      - name: "..."
        situation: "..."
        task: "..."
        root_cause: "..."
        action: "..."
        result: "..."
        operating_model_change: "..."

If apps_rg gains a structured emission contract later, swap this loader for
that contract; the typed return shape stays stable.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import yaml

from apps_qna.types.qna_types import ExperienceLibrary
from apps_shared.contracts.cross_app import (
    EnvelopeLoadError,
    ResumeBankEnvelope,
)


def _envelope_for(path: Path) -> Path:
    return path.with_name(path.stem + ".envelope.json")


def _library_from_envelope(env: ResumeBankEnvelope) -> ExperienceLibrary:
    raw = {
        "points": list(env.payload.points),
        "star_bank": dict(env.payload.star_bank),
        "rca_bank": list(env.payload.rca_bank),
    }
    return ExperienceLibrary.model_validate(raw)


def load_experience_yaml(path: Path) -> ExperienceLibrary:
    """Load and validate an experience bank.

    Prefers `<path>.envelope.json` (typed + sealed + lineage); falls back to
    raw YAML with DeprecationWarning.
    """
    envelope_path = _envelope_for(path)
    if envelope_path.is_file():
        try:
            env = ResumeBankEnvelope.load(envelope_path)
            return _library_from_envelope(env)
        except EnvelopeLoadError as exc:
            warnings.warn(
                f"Envelope at {envelope_path} failed to load ({exc}); "
                "falling back to raw YAML.",
                DeprecationWarning,
                stacklevel=2,
            )

    if not path.is_file():
        raise FileNotFoundError(f"Experience YAML not found: {path}")

    warnings.warn(
        f"Envelope missing at {envelope_path}; falling back to raw YAML. "
        f"Run `python -m apps_rg.outputs.envelope_emitter --bank {path}` to "
        "produce the envelope.",
        DeprecationWarning,
        stacklevel=2,
    )

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ExperienceLibrary.model_validate(raw)


def empty_library() -> ExperienceLibrary:
    """Return an empty (but valid) ExperienceLibrary for placeholder runs."""
    return ExperienceLibrary()
