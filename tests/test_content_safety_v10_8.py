from l5_content_safety import detect_bias, detect_pii
from l5_constitutional_engine import ConstitutionalEngine
from l5_safety_gateway import SafetyGateway


def test_detect_pii_email():
    result = detect_pii("Contact me at test@example.com")

    assert result["pii_found"] is True
    assert "email-like" in result["instances"]


def test_detect_pii_phone():
    number = "123-456-7890"
    result = detect_pii(f"Call {number} for info")

    assert result["pii_found"] is True
    assert number in result["instances"]


def test_detect_bias_keywords():
    result = detect_bias("This text mentions gender and race considerations.")

    assert result["bias_found"] is True
    assert set(result["categories"]) == {"gender", "race"}


def test_safety_gateway_includes_content_safety():
    gateway = SafetyGateway(constitutional_engine=ConstitutionalEngine())

    payload = {"content": "Email gender topic @ example.com"}
    patch = gateway.evaluate(payload)

    content_safety = patch["safety_gateway"]["content_safety"]
    assert content_safety["pii"]["pii_found"] is True
    assert content_safety["bias"]["bias_found"] is True
