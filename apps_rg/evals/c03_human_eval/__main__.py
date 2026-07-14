"""CLI for building and validating C0.3 human-review packets."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import Sequence

from .export import export_adjudicated_evaluation
from ._io import (
    controlled_path_error,
    file_digest,
    path_within,
    paths_refer_same,
    repo_root_from_module,
    write_json,
)
from .packet import (
    CANONICAL_TARGET_MANIFEST_SHA256,
    DEFAULT_TARGET_MANIFEST,
    assess_source_bundle_readiness,
    build_packet,
)
from .source_bundle import build_source_freeze_receipt, freeze_allocation_source_bundle
from .validation import (
    build_prelabel_packet_receipt,
    validate_completed_packet,
    validate_prelabel_packet,
)


def _read_blinding_nonce_file(path: Path) -> str:
    """Read a 256-bit nonce without accepting a public/symlinked secret file."""

    source = path.expanduser()
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(source, flags)
    except OSError as exc:
        raise ValueError(
            "blinding nonce file is missing, inaccessible, or a symlink"
        ) from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("blinding nonce file must be a regular file")
        if metadata.st_uid != os.getuid():
            raise ValueError("blinding nonce file must be owned by the current user")
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ValueError(
                "blinding nonce file permissions must be owner-only (0600 or stricter)"
            )
        with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
            descriptor = -1
            nonce = stream.read().strip()
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if len(nonce) != 64 or any(char not in "0123456789abcdef" for char in nonce):
        raise ValueError("blinding nonce file must contain exactly 64 lowercase hex characters")
    return nonce


def _verify_frozen_checkout(repo_root: Path, source_commit_sha: str) -> None:
    """Require source provenance to match a clean checked-out commit."""

    commands = (
        (["git", "rev-parse", "HEAD"], "source checkout HEAD"),
        (
            ["git", "status", "--porcelain", "--untracked-files=all"],
            "source checkout status",
        ),
    )
    results: list[str] = []
    for argv, label in commands:
        completed = subprocess.run(  # guardian: allow-chokepoint-bypass -- bounded read-only W6 provenance check
            argv,
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            raise ValueError(f"unable to verify {label}: exit {completed.returncode}")
        results.append(completed.stdout.strip())
    if results[0] != source_commit_sha:
        raise ValueError(
            "source_commit_sha must equal the checked-out HEAD before freezing"
        )
    if results[1]:
        raise ValueError("source checkout must be clean before freezing")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze = subparsers.add_parser(
        "freeze-source",
        help="freeze all six allocator cases from a clean source commit",
    )
    freeze.add_argument("--source-commit-sha", required=True)
    freeze.add_argument("--out", type=Path, required=True)
    freeze.add_argument("--receipt-out", type=Path, required=True)
    freeze.add_argument("--target-manifest", type=Path, default=DEFAULT_TARGET_MANIFEST)
    freeze.add_argument("--repo-root", type=Path, default=repo_root_from_module())

    readiness = subparsers.add_parser("readiness", help="validate a source bundle without publishing")
    readiness.add_argument("--source-bundle", type=Path, required=True)
    readiness.add_argument("--freeze-receipt", type=Path, required=True)
    readiness.add_argument("--expected-freeze-receipt-digest", required=True)
    readiness.add_argument("--blinding-nonce-file", type=Path, required=True)
    readiness.add_argument("--target-manifest", type=Path, default=DEFAULT_TARGET_MANIFEST)
    readiness.add_argument("--repo-root", type=Path)
    readiness.add_argument("--require-w9", action="store_true")

    build = subparsers.add_parser("build", help="build a frozen prelabel packet")
    build.add_argument("--source-bundle", type=Path, required=True)
    build.add_argument("--freeze-receipt", type=Path, required=True)
    build.add_argument("--expected-freeze-receipt-digest", required=True)
    build.add_argument("--out", type=Path, required=True)
    build.add_argument("--blinding-nonce-file", type=Path, required=True)
    build.add_argument("--target-manifest", type=Path, default=DEFAULT_TARGET_MANIFEST)
    build.add_argument("--repo-root", type=Path)
    build.add_argument("--require-w9", action="store_true")

    validate = subparsers.add_parser("validate", help="validate prelabel or completed packet")
    validate.add_argument("--packet", type=Path, required=True)
    validate.add_argument("--phase", choices=("prelabel", "completed"), required=True)
    validate.add_argument("--labels-dir", type=Path)
    validate.add_argument("--require-w9", action="store_true")
    validate.add_argument("--expected-freeze-receipt-digest", required=True)
    validate.add_argument("--expected-prelabel-manifest-sha256")
    validate.add_argument("--human-review-authority-receipt", type=Path)
    validate.add_argument("--expected-human-review-authority-receipt-sha256")

    prelabel_receipt = subparsers.add_parser(
        "seal-prelabel", help="write the out-of-band packet receipt before review"
    )
    prelabel_receipt.add_argument("--packet", type=Path, required=True)
    prelabel_receipt.add_argument("--receipt-out", type=Path, required=True)
    prelabel_receipt.add_argument("--expected-freeze-receipt-digest", required=True)
    prelabel_receipt.add_argument("--require-w9", action="store_true")

    export = subparsers.add_parser("export", help="export the sealed adjudicated W6 dataset")
    export.add_argument("--packet", type=Path, required=True)
    export.add_argument("--labels-dir", type=Path, required=True)
    export.add_argument("--out", type=Path)
    export.add_argument(
        "--receipt-out",
        type=Path,
        help="trusted export receipt path; defaults beside --out as <dataset>.receipt.json",
    )
    export.add_argument("--require-w9", action="store_true")
    export.add_argument("--expected-freeze-receipt-digest", required=True)
    export.add_argument("--expected-prelabel-manifest-sha256", required=True)
    export.add_argument("--human-review-authority-receipt", type=Path, required=True)
    export.add_argument(
        "--expected-human-review-authority-receipt-sha256", required=True
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "freeze-source":
        try:
            repo_root = args.repo_root.resolve()
            if repo_root != repo_root_from_module().resolve():
                raise ValueError(
                    "official freeze-source requires the canonical repository root"
                )
            target_path = args.target_manifest.resolve()
            if args.target_manifest.is_symlink() or target_path != DEFAULT_TARGET_MANIFEST.resolve():
                raise ValueError(
                    "official freeze-source requires the canonical committed target manifest path"
                )
            if file_digest(target_path) != CANONICAL_TARGET_MANIFEST_SHA256:
                raise ValueError("canonical target manifest digest mismatch")
            for label, destination in (
                ("source bundle output", args.out),
                ("source freeze receipt output", args.receipt_out),
            ):
                path_error = controlled_path_error(destination, repo_root=repo_root)
                if path_error:
                    raise ValueError(f"official {label} {path_error}")
            if paths_refer_same(args.out, args.receipt_out):
                raise ValueError(
                    "source bundle output and freeze receipt output must be distinct"
                )
            _verify_frozen_checkout(repo_root, args.source_commit_sha)
            source_bundle = freeze_allocation_source_bundle(
                repo_root=repo_root,
                target_cases_manifest=args.target_manifest,
                source_commit_sha=args.source_commit_sha,
            )
            write_json(args.out, source_bundle)
            freeze_receipt = build_source_freeze_receipt(
                source_bundle_path=args.out,
                source_bundle=source_bundle,
                target_manifest_path=args.target_manifest,
            )
            write_json(args.receipt_out, freeze_receipt)
            claims = [
                claim
                for case in source_bundle["cases"]
                for claim in case["claims"]
            ]
            result = {
                "schema_version": "apps_rg.c03_human_eval.freeze_source_result.v1",
                "status": "PASS",
                "source_bundle_path": str(args.out.resolve()),
                "source_bundle_sha256": file_digest(args.out.resolve()),
                "source_freeze_receipt_path": str(args.receipt_out.resolve()),
                "source_freeze_receipt_sha256": file_digest(
                    args.receipt_out.resolve()
                ),
                "source_freeze_receipt_digest": freeze_receipt["receipt_digest"],
                "source_commit_sha": args.source_commit_sha,
                "graph_digest": source_bundle["graph_digest"],
                "policy_digest": source_bundle["policy_digest"],
                "case_count": len(source_bundle["cases"]),
                "claim_count": len(claims),
                "retrieval_frontier_count": sum(
                    "candidate_frontier" in claim for claim in claims
                ),
            }
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
            print(
                json.dumps(
                    {
                        "schema_version": "apps_rg.c03_human_eval.freeze_source_result.v1",
                        "status": "FAIL",
                        "errors": [str(exc)],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
    if args.command == "readiness":
        try:
            nonce = _read_blinding_nonce_file(args.blinding_nonce_file)
            result = assess_source_bundle_readiness(
                source_bundle=args.source_bundle,
                source_freeze_receipt=args.freeze_receipt,
                trusted_source_freeze_receipt_digest=(
                    args.expected_freeze_receipt_digest
                ),
                blinding_nonce=nonce,
                target_manifest_path=args.target_manifest,
                repo_root=args.repo_root,
                require_w9=args.require_w9,
            )
        except (OSError, ValueError, TypeError) as exc:
            result = {
                "schema_version": "apps_rg.c03_human_eval.source_readiness.v1",
                "status": "FAIL",
                "packet_build_ready": False,
                "errors": [str(exc)],
            }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["packet_build_ready"] else 1
    if args.command == "build":
        try:
            nonce = _read_blinding_nonce_file(args.blinding_nonce_file)
            manifest = build_packet(
                source_bundle=args.source_bundle,
                source_freeze_receipt=args.freeze_receipt,
                trusted_source_freeze_receipt_digest=(
                    args.expected_freeze_receipt_digest
                ),
                out_dir=args.out,
                blinding_nonce=nonce,
                target_manifest_path=args.target_manifest,
                repo_root=args.repo_root,
                require_w9=args.require_w9,
            )
            result = {
                "schema_version": "apps_rg.c03_human_eval.build_result.v1",
                "status": "PASS",
                "packet_created": True,
                "packet_path": str(args.out.resolve()),
                "packet_id": manifest["packet_id"],
                "source_freeze_receipt_digest": manifest[
                    "source_freeze_receipt_digest"
                ],
                "coverage": manifest["coverage"],
            }
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        except (OSError, ValueError, TypeError) as exc:
            print(
                json.dumps(
                    {
                        "schema_version": "apps_rg.c03_human_eval.build_result.v1",
                        "status": "FAIL",
                        "packet_created": False,
                        "errors": [str(exc)],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
    if args.command == "export":
        try:
            result = export_adjudicated_evaluation(
                packet_dir=args.packet,
                labels_dir=args.labels_dir,
                out_path=args.out,
                receipt_path=args.receipt_out,
                require_w9=args.require_w9,
                trusted_source_freeze_receipt_digest=(
                    args.expected_freeze_receipt_digest
                ),
                trusted_prelabel_packet_manifest_sha256=(
                    args.expected_prelabel_manifest_sha256
                ),
                human_review_authority_receipt=args.human_review_authority_receipt,
                trusted_human_review_authority_receipt_sha256=(
                    args.expected_human_review_authority_receipt_sha256
                ),
            )
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        except (OSError, ValueError, TypeError) as exc:
            print(
                json.dumps(
                    {
                        "schema_version": "apps_rg.c03_human_eval.adjudicated_export_receipt.v1",
                        "status": "FAIL",
                        "errors": [str(exc)],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
    if args.command == "seal-prelabel":
        try:
            repository = repo_root_from_module()
            for label, controlled in (
                ("packet", args.packet),
                ("prelabel receipt output", args.receipt_out),
            ):
                path_error = controlled_path_error(controlled, repo_root=repository)
                if path_error:
                    raise ValueError(f"official {label} {path_error}")
            if path_within(args.receipt_out, args.packet):
                raise ValueError(
                    "prelabel receipt must be stored out-of-band outside the packet"
                )
            result = build_prelabel_packet_receipt(
                args.packet,
                trusted_source_freeze_receipt_digest=(
                    args.expected_freeze_receipt_digest
                ),
                require_w9=args.require_w9,
            )
            write_json(args.receipt_out, result)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        except (OSError, ValueError, TypeError) as exc:
            print(
                json.dumps(
                    {
                        "schema_version": (
                            "apps_rg.c03_human_eval.prelabel_packet_receipt.v1"
                        ),
                        "status": "FAIL",
                        "errors": [str(exc)],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
    if args.phase == "completed":
        if args.labels_dir is None:
            print(
                json.dumps(
                    {
                        "schema_version": "apps_rg.c03_human_eval.completed_validation.v1",
                        "status": "FAIL",
                        "pass": False,
                        "errors": ["--labels-dir is required for completed validation"],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
        result = validate_completed_packet(
            args.packet,
            args.labels_dir,
            require_w9=args.require_w9,
            trusted_source_freeze_receipt_digest=(
                args.expected_freeze_receipt_digest
            ),
            trusted_prelabel_packet_manifest_sha256=(
                args.expected_prelabel_manifest_sha256
            ),
            human_review_authority_receipt=args.human_review_authority_receipt,
            trusted_human_review_authority_receipt_sha256=(
                args.expected_human_review_authority_receipt_sha256
            ),
        )
    else:
        result = validate_prelabel_packet(
            args.packet,
            require_w9=args.require_w9,
            trusted_source_freeze_receipt_digest=(
                args.expected_freeze_receipt_digest
            ),
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
