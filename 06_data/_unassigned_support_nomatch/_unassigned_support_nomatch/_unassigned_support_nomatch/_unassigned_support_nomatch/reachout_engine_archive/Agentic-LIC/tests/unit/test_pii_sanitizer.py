from src.lic_agentic.safety.pii_sanitizer import SanitizedInputs, sanitize_pii


class _Inputs:
    def __init__(self, prompt: str, company_id: str | None = None, contact_id: str | None = None):
        self.prompt = prompt
        self.company_id = company_id
        self.contact_id = contact_id


def test_email_and_phone_masking():
    prompt = "Reach out to alice@example.com or call +1 555 123 4567 for help"
    sanitized, mapping = sanitize_pii(_Inputs(prompt, company_id="ACME", contact_id="C1"))
    assert isinstance(sanitized, SanitizedInputs)
    assert sanitized.prompt.count("<PII_") == 2
    assert sanitized.company_id == "ACME"
    assert sanitized.contact_id == "C1"
    assert all(value in prompt for value in mapping.values())


def test_no_pii_returns_original_prompt():
    prompt = "Hello team"
    sanitized, mapping = sanitize_pii(_Inputs(prompt))
    assert sanitized.prompt == prompt
    assert mapping == {}
