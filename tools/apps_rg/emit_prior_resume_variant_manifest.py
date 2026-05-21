"""Emit prior résumé variant extraction manifest (claim-sized atoms only)."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.runtime.c0.prior_resume_variant_extractor import write_prior_resume_extraction_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zip",
        type=Path,
        default=Path(
            r"C:\Users\amita\Downloads\Phase I Resumes Archive\AI and Data Governance - Amit Ayer.zip"
        ),
        help="Source zip of prior résumé variants",
    )
    parser.add_argument(
        "--staging",
        type=Path,
        default=_REPO / "artifacts/apps_rg/c0/_prior_resume_extract_staging",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_REPO / "artifacts/apps_rg/c0/prior_resume_variant_fact_extraction_manifest.json",
    )
    args = parser.parse_args()
    staging = args.staging
    staging.mkdir(parents=True, exist_ok=True)
    if args.zip.is_file():
        with zipfile.ZipFile(args.zip) as zf:
            for info in zf.infolist():
                if info.filename.lower().endswith(".docx") and not info.filename.startswith("__"):
                    name = Path(info.filename).name
                    target = staging / name
                    target.write_bytes(zf.read(info))
    dest = write_prior_resume_extraction_manifest(
        repo_root=_REPO,
        source_dir=staging,
        out_path=args.out,
    )
    payload = dest.read_text(encoding="utf-8")
    print(dest)
    print(f"rows={payload.count('candidate_fact_atom')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
