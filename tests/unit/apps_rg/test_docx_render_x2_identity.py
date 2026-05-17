"""DOCX X2 — verbatim candidate_identity checks (plaintext vs final_resume)."""
from __future__ import annotations

from apps_rg.runtime.render.docx_render_x2 import candidate_identity_docx_verdict


def test_identity_gate_skips_when_blob_missing() -> None:
    ok, fail, obs = candidate_identity_docx_verdict("anything", None)
    assert ok is True
    assert fail is None
    assert obs == "skipped_no_candidate_identity"


def test_identity_gate_skips_when_no_name_or_contact() -> None:
    ok, fail, obs = candidate_identity_docx_verdict("", {"candidate_name": ""})
    assert ok is True
    assert obs == "skipped_empty_identity_fields"


def test_identity_gate_requires_verbatim_name() -> None:
    hay = "Jane Q. Public\np | e"
    ok, fail, _obs = candidate_identity_docx_verdict(
        hay,
        {"candidate_name": "Jane Q. Public", "header_contact": {"phone": "p", "email": "e"}},
    )
    assert ok is True
    assert fail is None
    ok2, fail2, _ = candidate_identity_docx_verdict(
        hay,
        {"candidate_name": "Jane Q Public", "header_contact": {"phone": "p"}},
    )
    assert ok2 is False
    assert fail2 == "candidate_name not found verbatim"


def test_identity_gate_requires_contact_fragments_in_order() -> None:
    hay_wrong = "Name\nsecond | first"
    ok, fail, _ = candidate_identity_docx_verdict(
        hay_wrong,
        {"candidate_name": "Name", "header_contact": {"phone": "first", "email": "second"}},
    )
    assert ok is False
    assert fail == "header_contact fields not found in document order"
    hay_ok = "Name\nfirst | second"
    ok2, fail2, _ = candidate_identity_docx_verdict(
        hay_ok,
        {"candidate_name": "Name", "header_contact": {"phone": "first", "email": "second"}},
    )
    assert ok2 is True
    assert fail2 is None
