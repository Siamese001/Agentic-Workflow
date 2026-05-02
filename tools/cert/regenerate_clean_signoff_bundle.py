"""Fort Knox v2 — Clean Bundle Orchestrator.

Regenerates the full Fort Knox sign-off bundle in one atomic run, in the
exact order required for integrity:

  1. compile_requirement_signoff.py
       -> final_requirement_signoff_report.json
       -> final_requirement_signoff_report.sha256
       -> final_requirement_signoff_report.merkle.json
       -> final_requirement_signoff_report.signature.json
  2. verify_final_requirement_signoff_bundle.py
       -> final_requirement_signoff_bundle_verification.json
  3. (FAIL-CLOSED GATE) refuse to emit Markdown / XLSX if verifier said FAIL.
  4. export_signoff_to_xlsx.py
       -> final_requirement_signoff_report.xlsx
  5. export_signoff_to_markdown.py
       -> final_requirement_signoff_report.md
         (the markdown exporter ALSO fails closed on bundle FAIL — defense
          in depth)

Why this exists:
- Pytest tamper-tests in tests/runtime/test_fort_knox_bundle_verifier.py
  intentionally tamper with the merkle sidecar to confirm the verifier
  catches it. Those tests restore the sidecar but NOT the
  bundle_verification.json on disk, so a clean run after pytest can leave
  a stale FAIL bundle_verification.json contradicting a clean sidecar.
- This orchestrator is the canonical "produce the clean bundle" path.
  Run it every wave (after evidence emission); never trust a partial
  rerun of these scripts in isolation.

Usage:
  python tools/cert/regenerate_clean_signoff_bundle.py

Exit codes:
  0  = clean bundle produced; verifier PASS; all 7 artifacts on disk
  1  = compiler failed
  2  = bundle verifier FAILed (Markdown / XLSX NOT regenerated)
  3  = xlsx export failed
  4  = markdown export failed
  5  = post-run sanity check failed (artifact missing or wrong)

This script does NOT regenerate fixture artifacts, evidence assertions,
or per-row evidence. Those are produced by the per-row emitters / fixture
builder upstream of compile. Run those FIRST as part of each wave's
execution, then run this orchestrator to bind the result into the
canonical 7-file bundle.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CERT_DIR = REPO_ROOT / "artifacts" / "certification"

COMPILER          = REPO_ROOT / "scripts" / "compile_requirement_signoff.py"
BUNDLE_VERIFIER   = REPO_ROOT / "scripts" / "verify_final_requirement_signoff_bundle.py"
EXPORTER_XLSX     = REPO_ROOT / "scripts" / "export_signoff_to_xlsx.py"
EXPORTER_MD       = REPO_ROOT / "scripts" / "export_signoff_to_markdown.py"

REPORT_PATH       = CERT_DIR / "final_requirement_signoff_report.json"
SHA256_PATH       = CERT_DIR / "final_requirement_signoff_report.sha256"
MERKLE_PATH       = CERT_DIR / "final_requirement_signoff_report.merkle.json"
SIG_PATH          = CERT_DIR / "final_requirement_signoff_report.signature.json"
VERIFY_PATH       = CERT_DIR / "final_requirement_signoff_bundle_verification.json"
MD_PATH           = CERT_DIR / "final_requirement_signoff_report.md"
XLSX_PATH         = CERT_DIR / "final_requirement_signoff_report.xlsx"

EXPECTED_ARTIFACTS = [
    REPORT_PATH, SHA256_PATH, MERKLE_PATH, SIG_PATH,
    VERIFY_PATH, MD_PATH, XLSX_PATH,
]


def run(label: str, cmd: list[str], timeout: int = 240) -> int:
    print(f"\n=== {label} ===")
    print(f"$ python {' '.join(str(c) for c in cmd)}")
    r = subprocess.run([sys.executable] + [str(c) for c in cmd],
                       cwd=REPO_ROOT, timeout=timeout)
    print(f"  exit_code: {r.returncode}")
    return r.returncode


def main() -> int:
    print("[regenerate_clean_signoff_bundle] starting clean bundle production")

    # 1. Compile (writes report.json + sha256 + merkle.json + signature.json)
    rc = run("1/4 compile_requirement_signoff", [COMPILER])
    if rc != 0:
        print(f"FATAL: compiler failed with exit {rc}", file=sys.stderr)
        return 1

    # Read merkle root + report sha for the integrity contract banner
    if not MERKLE_PATH.exists():
        print(f"FATAL: compiler did not produce {MERKLE_PATH.name}", file=sys.stderr)
        return 1
    merkle = json.loads(MERKLE_PATH.read_text(encoding="utf-8"))
    merkle_root = merkle.get("root", "")
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8")) if REPORT_PATH.exists() else {}

    # 2. Verify the bundle (writes bundle_verification.json)
    rc = run("2/4 verify_final_requirement_signoff_bundle", [BUNDLE_VERIFIER])
    if not VERIFY_PATH.exists():
        print(f"FATAL: verifier did not produce {VERIFY_PATH.name}", file=sys.stderr)
        return 2
    bv = json.loads(VERIFY_PATH.read_text(encoding="utf-8"))
    bv_status = bv.get("bundle_verification_status")
    if bv_status != "PASS":
        print(f"\nFATAL: bundle verifier returned status={bv_status!r}; "
              f"refusing to regenerate Markdown / XLSX.", file=sys.stderr)
        for f in (bv.get("failures") or [])[:10]:
            print(f"  failure: {f}", file=sys.stderr)
        return 2

    # 3. XLSX (read-only view; honest because verifier already PASSed)
    rc = run("3/4 export_signoff_to_xlsx", [EXPORTER_XLSX])
    if rc != 0:
        print(f"FATAL: xlsx exporter failed with exit {rc}", file=sys.stderr)
        return 3

    # 4. Markdown (read-only view; the exporter itself ALSO fails closed
    #    on bundle FAIL — this is defense in depth)
    rc = run("4/4 export_signoff_to_markdown", [EXPORTER_MD])
    if rc != 0:
        print(f"FATAL: markdown exporter failed with exit {rc}", file=sys.stderr)
        return 4

    # 5. Post-run sanity: all 7 artifacts present
    missing = [str(p.relative_to(REPO_ROOT)).replace("\\", "/")
               for p in EXPECTED_ARTIFACTS if not p.exists()]
    if missing:
        print(f"FATAL: post-run sanity failed; missing artifacts:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 5

    # Banner
    print("\n" + "=" * 72)
    print("[regenerate_clean_signoff_bundle] CLEAN BUNDLE READY")
    print("=" * 72)
    summary = report.get("summary", {})
    print(f"  trust_level:              {report.get('trust_level')}")
    print(f"  signature:                {bv.get('signature_verification_status')}")
    print(f"  signed_off:               {summary.get('signed_off')}")
    print(f"  blocked:                  {summary.get('blocked')}")
    print(f"  not_verified:             {summary.get('not_verified')}")
    print(f"  total:                    {summary.get('total')}")
    print(f"  merkle_root:              {merkle_root}")
    print(f"  report_sha256:            {bv.get('report_sha256')}")
    print(f"  bundle_verification:      {bv_status} ({bv.get('checks_run')} checks, "
          f"{len(bv.get('failures') or [])} failures)")
    print()
    print("  Artifacts on disk:")
    for p in EXPECTED_ARTIFACTS:
        rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        print(f"    {p.stat().st_size:>9} bytes  {rel}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
