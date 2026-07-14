"""Run the apps_rg W6 resume-graph evaluation and offline calibration.

Exit codes are fail-closed: 0 means the labelled evaluation targets pass,
1 means valid evidence was evaluated but a target failed, and 2 means human
evidence is missing or insufficient.  A passing run still does not activate a
runtime threshold; the emitted threshold is a future-run candidate only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.evals.resume_graph_evaluation import (  # noqa: E402
    FAIL,
    PASS,
    build_sanitized_ci_receipt,
    evaluate_file,
)
from apps_rg.evals.c03_human_eval._io import (  # noqa: E402
    ensure_private_directory,
    write_private_text,
)


DEFAULT_PROFILE = Path("apps_rg/config/domain_contract/resume_graph_evaluation_profile.yaml")


def _repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _load_profile(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected a mapping in profile {path}")
    return payload


def _write_atomic_ci_text(path: Path, text: str) -> None:
    """Atomically publish the sanitized receipt without following a symlink."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError(f"sanitized CI receipt must not be a symlink: {path}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    temporary: Path | None = None
    descriptor = -1
    try:
        for _ in range(32):
            candidate = path.parent / f".{path.name}.ci-{secrets.token_hex(12)}.tmp"
            try:
                descriptor = os.open(candidate, flags, 0o644)
                temporary = candidate
                break
            except FileExistsError:
                continue
        if temporary is None:
            raise FileExistsError(f"unable to allocate CI receipt temporary for {path}")
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _same_file_or_resolved(left: Path, right: Path) -> bool:
    if left.resolve() == right.resolve():
        return True
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def _controlled_input_inventory(paths: list[Path]) -> dict[Path, str]:
    inventory: dict[Path, str] = {}
    for raw in paths:
        path = raw.resolve()
        candidates = [path]
        if path.is_dir():
            candidates = sorted(
                (candidate for candidate in path.rglob("*") if candidate.is_file()),
                key=lambda candidate: str(candidate),
            )
        for candidate in candidates:
            if candidate.is_file():
                inventory[candidate.resolve()] = hashlib.sha256(
                    candidate.read_bytes()
                ).hexdigest()
    return inventory


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="JSONL evidence path; defaults to profile.dataset.dataset_path",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="protected full-report path; defaults to profile.output.protected_artifact_path",
    )
    parser.add_argument(
        "--ci-receipt-out",
        type=Path,
        default=None,
        help="sanitized aggregate receipt path; defaults to profile.output.artifact_path",
    )
    parser.add_argument(
        "--export-receipt",
        type=Path,
        help="digest-bound receipt emitted by c03_human_eval export",
    )
    parser.add_argument(
        "--trusted-export-receipt-sha256",
        help="out-of-band trusted SHA-256 of --export-receipt",
    )
    parser.add_argument(
        "--trusted-prelabel-packet-manifest-sha256",
        help="out-of-band SHA-256 pin captured from packet_manifest.json before review",
    )
    parser.add_argument(
        "--human-review-authority-receipt",
        type=Path,
        help="owner-only out-of-band reviewer roster and assignment authority receipt",
    )
    parser.add_argument(
        "--trusted-human-review-authority-receipt-sha256",
        help="out-of-band trusted SHA-256 of --human-review-authority-receipt",
    )
    parser.add_argument(
        "--packet",
        type=Path,
        help="controlled human-evaluation packet root used by the export",
    )
    parser.add_argument(
        "--labels-dir",
        type=Path,
        help="controlled completed human-label root used by the export",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    profile_path = _repo_path(args.profile)
    try:
        profile = _load_profile(profile_path)
        dataset_setting = args.dataset or Path(str(profile["dataset"]["dataset_path"]))
        output_profile = profile["output"]
        protected_setting = output_profile.get("protected_artifact_path")
        if args.out is None and (
            not isinstance(protected_setting, str) or not protected_setting.strip()
        ):
            raise ValueError(
                "--out is required and must name controlled storage outside the repository"
            )
        output_setting = args.out or Path(str(protected_setting))
        ci_receipt_setting = args.ci_receipt_out or Path(
            str(output_profile["artifact_path"])
        )
        dataset_path = _repo_path(dataset_setting)
        output_path = _repo_path(output_setting)
        ci_receipt_path = _repo_path(ci_receipt_setting)
        if _same_file_or_resolved(output_path, ci_receipt_path):
            raise ValueError(
                "protected full report and sanitized CI receipt must use distinct paths"
            )
        protected_inputs = [dataset_path, profile_path]
        if args.export_receipt is not None:
            protected_inputs.append(_repo_path(args.export_receipt))
        if args.human_review_authority_receipt is not None:
            protected_inputs.append(_repo_path(args.human_review_authority_receipt))
        for destination in (output_path, ci_receipt_path):
            if any(
                _same_file_or_resolved(destination, source)
                for source in protected_inputs
            ):
                raise ValueError(
                    "W6 output paths must not alias dataset or evidence inputs"
                )
            for controlled_root in (
                _repo_path(args.packet) if args.packet is not None else None,
                _repo_path(args.labels_dir) if args.labels_dir is not None else None,
            ):
                if controlled_root is None:
                    continue
                try:
                    destination.resolve().relative_to(controlled_root.resolve())
                except ValueError:
                    continue
                raise ValueError(
                    "W6 output paths must remain outside packet and label roots"
                )
        controlled_roots = [*protected_inputs]
        if args.packet is not None:
            controlled_roots.append(_repo_path(args.packet))
        if args.labels_dir is not None:
            controlled_roots.append(_repo_path(args.labels_dir))
        input_inventory = _controlled_input_inventory(controlled_roots)
        for destination in (output_path, ci_receipt_path):
            if any(
                _same_file_or_resolved(destination, controlled_file)
                for controlled_file in input_inventory
            ):
                raise ValueError(
                    "W6 output paths must not alias any controlled evidence file"
                )
        source_ref = str(dataset_setting)
        report = evaluate_file(
            dataset_path,
            profile,
            source_ref=source_ref,
            export_receipt_path=(
                _repo_path(args.export_receipt)
                if args.export_receipt is not None
                else None
            ),
            trusted_export_receipt_sha256=args.trusted_export_receipt_sha256,
            trusted_prelabel_packet_manifest_sha256=(
                args.trusted_prelabel_packet_manifest_sha256
            ),
            human_review_authority_receipt_path=(
                _repo_path(args.human_review_authority_receipt)
                if args.human_review_authority_receipt is not None
                else None
            ),
            trusted_human_review_authority_receipt_sha256=(
                args.trusted_human_review_authority_receipt_sha256
            ),
            packet_dir=_repo_path(args.packet) if args.packet is not None else None,
            labels_dir=(
                _repo_path(args.labels_dir) if args.labels_dir is not None else None
            ),
        )
        if any(
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
            for path, digest in input_inventory.items()
        ):
            raise ValueError(
                "controlled W6 evidence changed during evaluation before output"
            )
    except (KeyError, OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(json.dumps({"status": "INSUFFICIENT", "error": str(exc)}, sort_keys=True))
        return 2

    contains_controlled_details = bool(report.get("per_sample_results")) or bool(
        isinstance(report.get("calibration"), dict)
        and report["calibration"].get("model") is not None
    )
    try:
        output_path.resolve().relative_to(REPO_ROOT.resolve())
        full_report_in_checkout = True
    except ValueError:
        full_report_in_checkout = False
    if contains_controlled_details and full_report_in_checkout:
        print(
            json.dumps(
                {
                    "status": "INSUFFICIENT",
                    "error": (
                        "protected W6 full report must be written outside the repository; "
                        "only the sanitized aggregate receipt may enter CI artifacts"
                    ),
                },
                sort_keys=True,
            )
        )
        return 2

    ensure_private_directory(output_path.parent)
    write_private_text(
        output_path,
        json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + "\n",
    )
    full_report_sha256 = hashlib.sha256(output_path.read_bytes()).hexdigest()
    ci_receipt = build_sanitized_ci_receipt(
        report,
        protected_full_report_sha256=full_report_sha256,
    )
    _write_atomic_ci_text(
        ci_receipt_path,
        json.dumps(ci_receipt, allow_nan=False, indent=2, sort_keys=True) + "\n",
    )
    if hashlib.sha256(output_path.read_bytes()).hexdigest() != full_report_sha256:
        print(
            json.dumps(
                {
                    "status": "INSUFFICIENT",
                    "error": "protected full report changed while writing sanitized receipt",
                },
                sort_keys=True,
            )
        )
        return 2
    if any(
        not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        for path, digest in input_inventory.items()
    ):
        print(
            json.dumps(
                {
                    "status": "INSUFFICIENT",
                    "error": "controlled W6 evidence changed while writing outputs",
                },
                sort_keys=True,
            )
        )
        return 2
    ci_receipt_sha256 = hashlib.sha256(ci_receipt_path.read_bytes()).hexdigest()
    print(
        json.dumps(
            {
                "artifact": str(ci_receipt_setting),
                "protected_full_report": str(output_setting),
                "protected_full_report_sha256": full_report_sha256,
                "ci_receipt_record_digest": ci_receipt["record_digest"],
                "ci_receipt_sha256": ci_receipt_sha256,
                "deterministic_digest": report["deterministic_digest"],
                "evaluation_gate_pass": report["evaluation_gate_pass"],
                "promotion_eligible": report["promotion_eligible"],
                "status": report["status"],
            },
            sort_keys=True,
        )
    )
    if report["status"] == PASS:
        return 0
    if report["status"] == FAIL:
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
