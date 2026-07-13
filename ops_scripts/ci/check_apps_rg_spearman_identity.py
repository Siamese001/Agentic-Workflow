"""RG-SPEARMAN-IDENTITY: enforce one executable apps_rg judge identity."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.judges.judge_registry import JudgeRegistry  # noqa: E402
from agentic_core.runtime.judges.resume_judges.executive_positioning import (  # noqa: E402
    ExecutivePositioningJudge,
)
from agentic_core.runtime.providers.provider_registry import ProviderRegistry  # noqa: E402
from apps_rg.runtime.bindings.judge_calibration_baseline import (  # noqa: E402
    APPS_RG_EXEC_POSITIONING_CALIBRATION_IDENTITY,
)
from apps_shared.judge_registry import resolve_judge  # noqa: E402
from ops_scripts.ci._apps_rg_spearman_gate_common import (  # noqa: E402
    PROFILE_PATH,
    PROVIDERS_PATH,
    ROSTER_PATH,
    finish,
    load_yaml,
)

CORE_IMPLEMENTATION = (
    "agentic_core.runtime.judges.resume_judges.executive_positioning:ExecutivePositioningJudge"
)


def validate_identity(
    *,
    profile_path: Path = PROFILE_PATH,
    roster_path: Path = ROSTER_PATH,
    providers_path: Path = PROVIDERS_PATH,
) -> list[str]:
    errors: list[str] = []
    try:
        profile = load_yaml(profile_path)
        roster_payload = load_yaml(roster_path)
        entries = roster_payload if isinstance(roster_payload, list) else []
    except (OSError, ValueError) as exc:
        return [str(exc)]
    if not entries:
        return [f"expected roster list in {roster_path}"]

    judge_id = str(profile.get("judge_id", ""))
    implementation_ref = str(profile.get("judge_implementation_ref", ""))
    if implementation_ref != CORE_IMPLEMENTATION:
        errors.append("calibration profile does not target the canonical core judge")
    if ExecutivePositioningJudge.GRADER_REF != judge_id:
        errors.append("core GRADER_REF differs from calibration judge_id")
    for key, value in APPS_RG_EXEC_POSITIONING_CALIBRATION_IDENTITY.items():
        if profile.get(key) != value:
            errors.append(f"app runtime/calibration profile {key} mismatch")

    entry = next(
        (item for item in entries if isinstance(item, dict) and item.get("app_id") == "apps_rg"),
        None,
    )
    if entry is None:
        return [*errors, "apps_rg grader roster entry is missing"]
    policies = entry.get("judge_policies") or {}
    policy: dict[str, Any] = policies.get(judge_id) or {}
    for key in ("judge_implementation_ref", "provider_profile_ref"):
        if str(policy.get(key, "")) != str(profile.get(key, "")):
            errors.append(f"roster/profile {key} mismatch")
    if bool(policy.get("informational_only")) is not True:
        errors.append("judge must remain informational_only=true")
    if bool(policy.get("required_for_exit", True)) is not False:
        errors.append("judge must remain required_for_exit=false")

    rubric_files = profile.get("rubric_files") or []
    try:
        rubric_parts = [(REPO_ROOT / str(path)).read_text(encoding="utf-8").strip() for path in rubric_files]
        rubric_text = "\n\n".join(rubric_parts)
    except OSError as exc:
        errors.append(f"rubric bundle unreadable: {exc}")
    else:
        digest = hashlib.sha256(rubric_text.encode("utf-8")).hexdigest()
        if digest != str(profile.get("rubric_hash", "")):
            errors.append("profile rubric_hash does not digest the declared rubric bundle")
        runtime_prompt = ExecutivePositioningJudge().build_prompt(
            candidate_text="identity probe",
            context_metadata={},
        )
        if (
            len(rubric_parts) != 2
            or runtime_prompt.system_prompt.strip() != rubric_parts[0]
            or rubric_parts[1] not in runtime_prompt.user_prompt
        ):
            errors.append("runtime judge rubric bundle differs from calibration bundle")

    registry = JudgeRegistry()
    if registry.load_from_grader_roster(roster_path) != 1:
        errors.append("grader roster did not resolve exactly one judge")
    else:
        runtime = registry.get_profile(judge_id)
        if runtime.judge_implementation_ref != implementation_ref:
            errors.append("runtime registry implementation differs from calibration")
        if runtime.provider_profile_ref != str(profile.get("provider_profile_ref", "")):
            errors.append("runtime registry provider differs from calibration")

    providers = ProviderRegistry()
    try:
        providers.load_from_yaml(providers_path, app_id="apps_rg")
        providers.get_profile(str(profile.get("provider_profile_ref", "")))
    except (OSError, KeyError, ValueError) as exc:
        errors.append(f"provider profile is not executable: {exc}")

    shared = resolve_judge("apps_rg", "executive_positioning")
    if not shared.importable or f"{shared.import_path}:ExecutivePositioningJudge" != implementation_ref:
        errors.append("apps_shared registry differs from the core judge identity")

    scan_roots = [REPO_ROOT / "apps_rg", REPO_ROOT / "ops_scripts/calibration"]
    for root in scan_roots:
        for path in root.rglob("*.py"):
            if "apps_rg.engines.judges" in path.read_text(encoding="utf-8"):
                errors.append(f"obsolete app-local judge authority import in {path.relative_to(REPO_ROOT)}")
    return errors


def main() -> int:
    return finish(
        "RG-SPEARMAN-IDENTITY",
        validate_identity(),
        fail_closed_env="APPS_RG_SPEARMAN_IDENTITY_FAIL_CLOSED",
    )


if __name__ == "__main__":
    raise SystemExit(main())
