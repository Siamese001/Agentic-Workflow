"""Fort Knox certification path SSOT (repo layout migration 2026-05-24).

Compiler inputs live under ``data/certification/``. JSON Schemas under
``config/certification/schemas/``. Runtime outputs and review mirrors under
``artifacts/certification/``.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CERT_DATA_DIR = REPO_ROOT / "data" / "certification"
CERT_SCHEMAS_DIR = REPO_ROOT / "config" / "certification" / "schemas"
CERT_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
CERT_REVIEW_AGENTIC_DIR = CERT_ARTIFACTS_DIR / "review" / "agentic_core"
CERT_REVIEW_APPS_DIR = CERT_ARTIFACTS_DIR / "review" / "apps"

REQS_PATH = CERT_DATA_DIR / "requirements_source.json"
ASSERTIONS_PATH = CERT_DATA_DIR / "evidence_assertions.jsonl"
EVIDENCE_MANIFEST_PATH = CERT_DATA_DIR / "evidence_manifest.jsonl"
SIGNOFF_SCHEMA_PATH = CERT_DATA_DIR / "requirement_signoff_schema.json"

APPS_REQS_PATH = CERT_DATA_DIR / "apps_e2e_requirements_source.json"
APPS_ASSERTIONS_PATH = CERT_DATA_DIR / "apps_evidence_assertions.jsonl"
APPS_DOMAIN_ASSERTIONS_PATH = CERT_DATA_DIR / "apps_domain_evidence_assertions.jsonl"
APPS_NEGATIVE_ASSERTIONS_PATH = CERT_DATA_DIR / "apps_negative_control_assertions.jsonl"

REQS_SCHEMA = CERT_SCHEMAS_DIR / "requirements_source.schema.json"
ASSERTION_SCHEMA = CERT_SCHEMAS_DIR / "evidence_assertion.schema.json"
REPORT_SCHEMA = CERT_SCHEMAS_DIR / "final_requirement_signoff_report.schema.json"
APPS_REQS_SCHEMA = CERT_SCHEMAS_DIR / "apps_e2e_requirements.schema.json"
APPS_ASSERTION_SCHEMA = CERT_SCHEMAS_DIR / "apps_evidence_assertion.schema.json"
APPS_REPORT_SCHEMA = CERT_SCHEMAS_DIR / "apps_e2e_signoff_report.schema.json"

INTEGRATED_RUNTIME_DIR = CERT_ARTIFACTS_DIR / "integrated_runtime"

FINAL_SIGNOFF_REPORT = CERT_ARTIFACTS_DIR / "final_requirement_signoff_report.json"
FINAL_SIGNOFF_SHA256 = CERT_ARTIFACTS_DIR / "final_requirement_signoff_report.sha256"
FINAL_SIGNOFF_MERKLE = CERT_ARTIFACTS_DIR / "final_requirement_signoff_report.merkle.json"
FINAL_SIGNOFF_SIGNATURE = CERT_ARTIFACTS_DIR / "final_requirement_signoff_report.signature.json"
FINAL_SIGNOFF_BUNDLE_VERIFICATION = (
    CERT_ARTIFACTS_DIR / "final_requirement_signoff_bundle_verification.json"
)

COMPILE_SIGNOFF_SCRIPT = REPO_ROOT / "tools" / "cert" / "compile_requirement_signoff.py"
VERIFY_SIGNOFF_BUNDLE_SCRIPT = (
    REPO_ROOT / "ops_scripts" / "ci" / "verify_final_requirement_signoff_bundle.py"
)
