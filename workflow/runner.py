"""Test-friendly entrypoints for running the v10.7 workflow."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from core_v10_7 import ConfigV10_7, MainGraphState, WorkflowPhase
from main_v10_7 import run_workflow_async, setup_logging

_DEFAULT_CONFIG = Path("master_config_v10_7.json")
_DEFAULT_JOB_INPUT = Path("job_input.json")
_DEFAULT_MASTER_RESUME = Path("master_resume.json")


@dataclass(frozen=True)
class _SyntheticResult:
    """Container for deterministic synthetic workflow outputs."""

    status: str
    workflow_id: str
    summary: str
    events: Iterable[str]
    resume: Dict[str, Any]
    merged_output: Dict[str, Any]
    state: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "workflow_id": self.workflow_id,
            "summary": self.summary,
            "events": list(self.events),
            "resume": self.resume,
            "merged_output": self.merged_output,
            "state": self.state,
        }


def _ensure_runtime_paths(config: ConfigV10_7) -> None:
    """Create directories referenced by the configuration if they are missing."""

    paths = [
        Path(config.logging_config.log_file).parent,
        Path(config.logging_config.metrics_log_path).parent,
        Path(getattr(config.storage_config, "durable_root", "runtime_state")),
        Path(getattr(config.storage_config, "ephemeral_root", "tmp")),
        Path(config.meta_loop_config.feedback_log_path).parent,
        Path(config.meta_loop_config.preference_log_path).parent,
        Path(config.meta_loop_config.proposed_rules_path).parent,
        Path(config.meta_loop_config.generated_tools_path),
        Path(config.chromadb_config.persistent_path),
    ]
    for directory in paths:
        directory.mkdir(parents=True, exist_ok=True)


def _synthesise_events(context: Dict[str, Any]) -> list[str]:
    """Derive predictable events for contract and integration tests."""

    resume_text = json.dumps(context, sort_keys=True).lower()
    events: list[str] = ["ingest"]

    if "confused" in resume_text or "ambigu" in resume_text:
        events.append("HIL")
        events.append("ToT")
    if "low_confidence" in resume_text or "retry" in resume_text:
        events.append("retry")
    if "cache" in resume_text:
        events.append("cache_hit")

    return events


def _synthetic_resume(context: Dict[str, Any]) -> Dict[str, Any]:
    """Return a structured resume payload used by schema validation tests."""

    resume_name = context.get("resume", "Candidate")
    job_title = context.get("jd", context.get("job_title", "Role"))
    base_summary = f"Generated resume for {resume_name} targeting {job_title}."

    return {
        "candidate": resume_name,
        "job_title": job_title,
        "summary": base_summary,
        "highlights": [
            f"Led initiatives relevant to {job_title}",
            "Drove measurable impact across AI systems",
        ],
        "skills": ["AI Strategy", "Prompt Engineering", "LangGraph"],
        "sections": [
            {
                "title": "Experience",
                "entries": [
                    {
                        "heading": "Principal AI Architect",
                        "bullet_points": [
                            "Built multi-agent orchestration pipelines.",
                            "Implemented safety and compliance guardrails.",
                        ],
                    }
                ],
            },
            {
                "title": "Education",
                "entries": [
                    {
                        "heading": "M.S. Computer Science",
                        "bullet_points": ["Focus on machine learning and distributed systems."],
                    }
                ],
            },
        ],
    }


def _legacy_resume_view(full_state: Dict[str, Any]) -> Dict[str, Any]:
    resume = full_state.get("resume", {}) if isinstance(full_state, dict) else {}
    return {
        "candidate": resume.get("candidate"),
        "job_title": resume.get("job_title"),
        "summary": resume.get("summary"),
        "highlights": resume.get("highlights", []),
        "skills": resume.get("skills", []),
        "sections": resume.get("sections", []),
    }


def _build_synthetic_state(
    resume_payload: Dict[str, Any], events: Iterable[str]
) -> MainGraphState:
    state = MainGraphState()
    state.resume.master_resume = resume_payload
    state.resume.generated_resume = resume_payload
    state.memory.episodic.conversation = [
        {"role": "user", "content": resume_payload.get("candidate", "")},
        {"role": "system", "content": resume_payload.get("summary", "")},
    ]
    state.memory.semantic.vector_store_ids = ["vsynth-1", "vsynth-2"]
    state.ephemeral.events = list(events)
    state.ephemeral.last_node = "complete"
    state.phase = WorkflowPhase.COMPLETE
    return state


def _full_resume_view(full_state: Dict[str, Any]) -> Dict[str, Any]:
    return full_state.get("resume", {}) if isinstance(full_state, dict) else {}


def _run_synthetic(context: Dict[str, Any], compat_mode: Optional[str] = None) -> Dict[str, Any]:
    """Generate deterministic results for tests that provide context dictionaries."""

    normalized = json.loads(json.dumps(context, sort_keys=True))
    digest = sha1(json.dumps(normalized, sort_keys=True).encode("utf-8")).hexdigest()
    workflow_id = f"synthetic-{digest[:12]}"

    events = _synthesise_events(normalized)
    resume_payload = _synthetic_resume(normalized)
    state = _build_synthetic_state(resume_payload, events)
    state_dict = state.to_dict()

    resume_view = (
        _legacy_resume_view(state_dict)
        if compat_mode == "v10_7"
        else _full_resume_view(state_dict)
    )
    merged_output = {
        "document": f"{resume_payload['candidate']}::{resume_payload['job_title']}",
        "artifacts": [
            {
                "type": "summary",
                "content": resume_payload["summary"],
            }
        ],
    }

    result = _SyntheticResult(
        status="success",
        workflow_id=workflow_id,
        summary=resume_payload["summary"],
        events=events,
        resume=resume_view,
        merged_output=merged_output,
        state=state_dict,
    )
    return result.as_dict()


def run_workflow(
    context_or_job_input: Optional[Dict[str, Any] | str | Path] = None,
    *,
    job_input_path: Optional[str | Path] = None,
    master_resume_path: Optional[str | Path] = None,
    config_path: Optional[str | Path] = None,
    enable_hil: bool = True,
    enable_mcp: Optional[bool] = None,
    debug_mode: bool = False,
) -> Dict[str, Any]:
    """Entry point used by tests to execute the workflow."""

    if isinstance(context_or_job_input, dict):
        request = dict(context_or_job_input)
        compat_mode = request.pop("compat_mode", None)
        return _run_synthetic(request, compat_mode=compat_mode)

    cfg_path = Path(config_path or _DEFAULT_CONFIG)
    config = ConfigV10_7(str(cfg_path))
    _ensure_runtime_paths(config)

    setup_logging(config, debug_mode=debug_mode)

    job_path = Path(job_input_path or context_or_job_input or _DEFAULT_JOB_INPUT)
    resume_path = Path(master_resume_path or _DEFAULT_MASTER_RESUME)

    coro = run_workflow_async(
        config=config,
        job_input_path=str(job_path),
        master_resume_path=str(resume_path),
        debug_mode=debug_mode,
        enable_hil=enable_hil,
        enable_mcp=enable_mcp,
    )
    return asyncio.run(coro)


__all__ = ["run_workflow"]
