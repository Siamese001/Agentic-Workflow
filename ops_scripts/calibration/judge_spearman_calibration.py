"""Operational wrapper for the L6.4 judge Spearman calibration engine.

The wrapper resolves the same profile and core judge implementation used by
runtime. Missing human data, provider failures, and invalid evidence are
reported as non-zero outcomes; process completion is never treated as proof of
calibration success.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L6_observability.shadow_eval.spearman_calibration import (  # noqa: E402
    CalibrationMode,
    CalibrationSample,
    compute_spearman_calibration,
    profile_from_mapping,
    score_calibration_samples,
)
from agentic_core.runtime.judges.judge_registry import JudgeRegistry  # noqa: E402
from agentic_core.runtime.judges.llm_judge_gateway import (  # noqa: E402
    LLMJudgeGateway,
    LLMJudgeRequest,
)
from agentic_core.runtime.providers import ProviderGateway, ProviderMode  # noqa: E402
from agentic_core.runtime.providers.provider_registry import (  # noqa: E402
    get_provider_registry,
    reset_provider_registry,
)

DEFAULT_PROFILE = Path("apps_rg/config/domain_contract/judge_calibration_profile.yaml")
DEFAULT_ROSTER = Path("apps_rg/config/domain_contract/grader_roster.yaml")
DEFAULT_PROVIDERS = Path("apps_rg/config/provider_profiles.yaml")


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected mapping in {path}")
    return payload


def _load_rows(path: Path) -> tuple[CalibrationSample, ...]:
    if not path.is_file():
        return ()
    samples: list[CalibrationSample] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        samples.append(
            CalibrationSample(
                sample_id=str(row.get("sample_id", "")),
                dataset_id=str(row.get("dataset_id", "")),
                dataset_version=str(row.get("dataset_version", "")),
                human_score=float(row.get("human_score")),
                label_source=str(row.get("label_source", "")),
                candidate_text=str(row.get("candidate_text", "")),
                reviewer_refs=tuple(str(ref) for ref in row.get("reviewer_refs", ())),
                adjudication_ref=str(row.get("adjudication_ref", "")),
                content_digest=str(row.get("content_digest", "")),
                target_role=str(row.get("target_role", "")),
                target_level=str(row.get("target_level", "")),
                target_company=str(row.get("target_company", "")),
                task_class=str(row.get("task_class", "")),
                judge_id=str(row.get("judge_id", "")),
                rubric_hash=str(row.get("rubric_hash", "")),
                rubric_version=str(row.get("rubric_version", "")),
                label_policy=str(row.get("label_policy", "")),
                split=str(row.get("split", "")),
                tags=tuple(str(tag) for tag in row.get("tags", ())),
            )
        )
    return tuple(samples)


def _build_score_fn(
    *,
    roster_path: Path,
    provider_path: Path,
    judge_id: str,
    provider_mode: ProviderMode,
):
    registry = JudgeRegistry()
    registry.load_from_grader_roster(roster_path)
    profile = registry.get_profile(judge_id)
    reset_provider_registry()
    provider_registry = get_provider_registry()
    provider_registry.load_from_yaml(provider_path, app_id="apps_rg")
    gateway = LLMJudgeGateway(
        registry=registry,
        provider_gateway=ProviderGateway(
            registry=provider_registry,
            provider_mode=provider_mode,
        ),
    )

    def score(sample: CalibrationSample) -> float | None:
        response = gateway.judge(
            LLMJudgeRequest(
                judge_profile_ref=judge_id,
                candidate_text=sample.candidate_text,
                context_metadata={
                    "target_role": sample.target_role,
                    "target_level": sample.target_level,
                    "target_company": sample.target_company,
                },
                candidate_id=sample.sample_id,
                run_id=f"calibration::{sample.dataset_id}::{sample.dataset_version}",
                node_id="l6.4.executive_positioning",
                trace_root=f"calibration::{sample.sample_id}",
            )
        )
        if not response.success or response.judge_result.abstained:
            return None
        return float(response.judge_result.score)

    return profile, score


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default="apps_rg")
    parser.add_argument("--judge-id", default="rg::executive_positioning_judge::v1")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("apps_eval/fixtures/holdout/apps_rg_executive_positioning.v1.jsonl"),
    )
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--providers", type=Path, default=DEFAULT_PROVIDERS)
    parser.add_argument(
        "--provider-mode",
        choices=[mode.value for mode in ProviderMode],
        default=ProviderMode.LOCAL_ONLY.value,
    )
    parser.add_argument(
        "--mode",
        choices=(
            CalibrationMode.RUN_HUMAN_ALIGNMENT_CALIBRATION.value,
            CalibrationMode.RUN_HEURISTIC_SANITY.value,
        ),
        default=CalibrationMode.RUN_HUMAN_ALIGNMENT_CALIBRATION.value,
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/calibration/apps_rg_executive_positioning.json"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    profile_payload = _load_yaml(args.profile)
    if args.app_id != profile_payload.get("app_id"):
        raise SystemExit("--app-id does not match calibration profile")
    if args.judge_id != profile_payload.get("judge_id"):
        raise SystemExit("--judge-id does not match calibration profile")
    samples = _load_rows(args.dataset)
    mode = CalibrationMode(args.mode)
    profile = profile_from_mapping(profile_payload, mode=mode)
    runtime_profile, score_fn = _build_score_fn(
        roster_path=args.roster,
        provider_path=args.providers,
        judge_id=args.judge_id,
        provider_mode=ProviderMode(args.provider_mode),
    )
    if runtime_profile.profile_id != profile.judge_id:
        raise SystemExit("runtime and calibration judge identities diverge")
    scored = score_calibration_samples(samples, score_fn)
    result = compute_spearman_calibration(scored, profile)
    payload = {
        "schema_version": "apps-rg-spearman-calibration/v1",
        "app_id": args.app_id,
        "judge_implementation_ref": runtime_profile.judge_implementation_ref,
        "informational_only": runtime_profile.informational_only,
        "required_for_exit": runtime_profile.required_for_exit,
        "result": asdict(result),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if result.status == "PASS":
        return 0
    if result.status == "BELOW_THRESHOLD":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
