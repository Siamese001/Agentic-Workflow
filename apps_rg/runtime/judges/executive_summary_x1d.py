"""X1D LLM-as-Judge panel for executive summary runtime slice.

Provider-backed judges with full normalization per X1D adapter spec.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import hashlib
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


JUDGE_RUBRIC_VERSION = "executive_summary_x1d_v1"
DEFAULT_THRESHOLD = 0.80

RUBRIC = """
You are evaluating one executive resume summary. Use the same rubric for every provider.
Return JSON only with: score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Rubric dimensions:
1. factual_support: claims appear supported by the provided claim ledger and source fact IDs.
2. executive_signal: SVP/CTO-level leadership, commercial impact, technical depth, and platform scale.
3. resume_voice: concise, credible, human-written executive style. No first person, filler, hype, or generic AI prose.
4. ats_alignment_without_keyword_stuffing: relevant to target role without stuffing or copying JD language.
5. anti_overfit: no JD-as-proof, no briefing-as-proof, no target company as candidate experience.
6. synthesis_quality: synthesizes facts into an executive summary, not bullet claims pasted into sentences.

Decisive failure triggers:
- unsupported business metric
- target company presented as candidate experience
- first-person narrative
- copied JD phrase longer than four words
- generic opener or hype/filler
- summary is mechanically sentence-stacked proof rather than narrative synthesis
""".strip()


@dataclass
class JudgeOutput:
    """Complete judge output with provider status tracking."""
    judge_id: str
    provider_name: str
    provider_key: str
    evaluator_mode: str  # MODEL_BACKED | MOCKED | BLOCKED_*
    provider_status: str  # MODEL_BACKED_PASS | MODEL_BACKED_FAIL | BLOCKED_*
    model_name: str
    provider_available: bool
    provider_blocked: bool  # True for BLOCKED_* modes, False otherwise
    exact_provider_error: str | None
    raw_response_ref: str | None = None  # Path to preserved raw response
    original_model: str | None = None  # For fallback tracking
    fallback_model: str | None = None  # For fallback tracking
    rubric_version: str = JUDGE_RUBRIC_VERSION
    input_hash: str = ""
    output_hash: str = ""
    score: float | None = None
    score_scale: str | None = None  # "0_to_5" or "0_to_1"
    normalized_score: float | None = None  # 0.0 to 1.0
    threshold: float = DEFAULT_THRESHOLD
    normalized_threshold: float | None = None  # 0.0 to 1.0
    pass_: bool = False
    decisive_failure: bool = False  # False for blocked providers
    findings: list[str] = field(default_factory=list)
    cited_sentence_indexes: list[int] = field(default_factory=list)
    remediation_suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


# Provider configuration
PROVIDERS = {
    "gemini_pro": {
        "provider_name": "Gemini Pro",
        "env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-1.5-pro",
    },
    "openai_chatgpt": {
        "provider_name": "OpenAI ChatGPT",
        "env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4o",
    },
    "anthropic_claude": {
        "provider_name": "Anthropic Claude",
        "env": "ANTHROPIC_API_KEY",
        "model_env": "APPS_RG_ANTHROPIC_JUDGE_MODEL",  # Specific judge model env
        "fallback_env": "ANTHROPIC_MODEL",  # Fallback to general model
        "default_model": "claude-3-5-sonnet-20241022",
    },
}


def _artifact_path(provider_key: str, suffix: str) -> Path:
    """Generate artifact path for provider artifacts."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:-3]
    base = Path("artifacts/apps_rg/runtime_proofs/executive_summary")
    base.mkdir(parents=True, exist_ok=True)
    return base / f"x1d_{provider_key}_{suffix}_{ts}.json"


def _write_artifact(path: Path, data: Any) -> str:
    """Write artifact and return path string."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return str(path)


def _extract_json_from_text(text: str) -> dict[str, Any] | None:
    """Robust JSON extraction from text with markdown code blocks."""
    text = text.strip()
    
    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try removing markdown code blocks
    patterns = [
        r"```json\s*(.*?)\s*```",
        r"```\s*(.*?)\s*```",
        r"`\s*(.*?)\s*`",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON object boundaries
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
    except json.JSONDecodeError:
        pass
    
    return None


def _make_blocked_output(
    provider_key: str,
    input_hash: str,
    evaluator_mode: str,
    provider_status: str,
    error: str,
    raw_response_ref: str | None = None,
    model_name: str = "",
    original_model: str | None = None,
    fallback_model: str | None = None,
) -> JudgeOutput:
    """Create a blocked judge output with full context."""
    meta = PROVIDERS.get(provider_key, {
        "provider_name": provider_key,
        "default_model": model_name or "unknown",
    })
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_exec_summary",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode=evaluator_mode,
        provider_status=provider_status,
        model_name=model_name or meta.get("default_model", "unknown"),
        provider_available=False,
        provider_blocked=True,  # Blocked providers are marked as such
        exact_provider_error=error,
        raw_response_ref=raw_response_ref,
        original_model=original_model,
        fallback_model=fallback_model,
        rubric_version=JUDGE_RUBRIC_VERSION,
        input_hash=input_hash,
        output_hash="",
        score=None,
        score_scale=None,
        normalized_score=None,
        threshold=DEFAULT_THRESHOLD,
        normalized_threshold=None,
        pass_=False,
        decisive_failure=False,  # Blocked providers are NOT decisive failures
        findings=["Judge blocked - see exact_provider_error and raw_response_ref for details."],
        cited_sentence_indexes=[],
        remediation_suggestions=["Review provider configuration and raw response artifact."],
    )


def _make_model_backed_output(
    provider_key: str,
    input_hash: str,
    model_name: str,
    result: dict[str, Any],
    raw_response_ref: str | None = None,
    original_model: str | None = None,
    fallback_model: str | None = None,
) -> JudgeOutput:
    """Create a model-backed judge output from parsed result."""
    score = float(result.get("score", 0.0))
    threshold = float(result.get("threshold", DEFAULT_THRESHOLD))
    decisive = bool(result.get("decisive_failure", False))
    passed = bool(result.get("pass", score >= threshold and not decisive))
    output_hash = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:16]
    meta = PROVIDERS[provider_key]
    
    provider_status = "MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL"
    
    # Detect score scale and normalize
    # If threshold is around 4.0 and score is around 4-5, it's likely 0-5 scale
    # If threshold is around 0.8 and score is around 0-1, it's likely 0-1 scale
    if threshold > 1.5 or score > 1.5:
        score_scale = "0_to_5"
        normalized_score = score / 5.0
        normalized_threshold = threshold / 5.0
    else:
        score_scale = "0_to_1"
        normalized_score = score
        normalized_threshold = threshold
    
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_exec_summary",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode="MODEL_BACKED",
        provider_status=provider_status,
        model_name=model_name,
        provider_available=True,
        provider_blocked=False,  # Model-backed providers are not blocked
        exact_provider_error=None,
        raw_response_ref=raw_response_ref,
        original_model=original_model,
        fallback_model=fallback_model,
        rubric_version=JUDGE_RUBRIC_VERSION,
        input_hash=input_hash,
        output_hash=output_hash,
        score=score,
        score_scale=score_scale,
        normalized_score=normalized_score,
        threshold=threshold,
        normalized_threshold=normalized_threshold,
        pass_=passed,
        decisive_failure=decisive,
        findings=list(result.get("findings", [])),
        cited_sentence_indexes=list(result.get("cited_sentence_indexes", [])),
        remediation_suggestions=list(result.get("remediation_suggestions", [])),
    )


def _call_openai(api_key: str, prompt: str, model: str, input_hash: str, provider_key: str) -> JudgeOutput:
    """Call OpenAI API with full artifact preservation."""
    # Build request payload
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a strict executive resume judge. Return JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    # gpt-5.x models use max_completion_tokens
    if model.startswith("gpt-5"):
        payload["max_completion_tokens"] = 900
    else:
        payload["max_tokens"] = 900
        payload["response_format"] = {"type": "json_object"}
    
    # Write request artifact
    req_path = _artifact_path(provider_key, "provider_request")
    _write_artifact(req_path, {"payload": payload, "input_hash": input_hash, "timestamp": datetime.now(timezone.utc).isoformat()})
    
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        # Write error response artifact
        err_path = _artifact_path(provider_key, "provider_response_raw")
        _write_artifact(err_path, {"error": True, "status_code": e.code, "body": error_body, "input_hash": input_hash})
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE", f"OpenAI API error {e.code}: {error_body}",
            raw_response_ref=str(err_path), model_name=model
        )
    
    # Write raw response artifact
    raw_path = _artifact_path(provider_key, "provider_response_raw")
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    
    # Parse response
    try:
        data = json.loads(raw_response)
        content = data["choices"][0]["message"]["content"]
    except (json.JSONDecodeError, KeyError) as e:
        # Write parse error artifact
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {"error": "response_structure", "detail": str(e), "raw_response_ref": str(raw_path)})
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", f"OpenAI response parse error: {e}",
            raw_response_ref=str(raw_path), model_name=model
        )
    
    # Extract JSON from content
    result = _extract_json_from_text(content)
    
    if result is None:
        # Write extraction error artifact
        extract_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(extract_err_path, {
            "error": "json_extraction",
            "content_preview": content[:500],
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", "Failed to extract JSON from OpenAI response",
            raw_response_ref=str(raw_path), model_name=model
        )
    
    # Validate required fields
    required_fields = ["score", "threshold", "pass"]
    missing = [f for f in required_fields if f not in result]
    if missing:
        schema_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(schema_err_path, {
            "error": "schema_validation",
            "missing_fields": missing,
            "result_keys": list(result.keys()),
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR", f"Missing required fields: {missing}",
            raw_response_ref=str(raw_path), model_name=model
        )
    
    # Write success parse result
    parse_path = _artifact_path(provider_key, "provider_parse_result")
    _write_artifact(parse_path, {"result": result, "raw_response_ref": str(raw_path)})
    
    return _make_model_backed_output(provider_key, input_hash, model, result, raw_response_ref=str(raw_path))


def _call_anthropic(api_key: str, prompt: str, model: str, input_hash: str, provider_key: str) -> JudgeOutput:
    """Call Anthropic API with full artifact preservation and model fallback handling."""
    original_model = model
    fallback_model = None
    
    # Check for fallback permission
    allow_fallback = os.environ.get("APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK", "").lower() == "true"
    
    # Build request payload
    payload = {
        "model": model,
        "max_tokens": 900,
        "messages": [{"role": "user", "content": prompt + "\n\nReturn JSON only."}],
        "temperature": 0.1,
    }
    
    # Write request artifact
    req_path = _artifact_path(provider_key, "provider_request")
    _write_artifact(req_path, {
        "payload": payload,
        "input_hash": input_hash,
        "original_model": original_model,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        
        # Check for 404 model not found
        if e.code == 404 or "not_found_error" in error_body:
            err_path = _artifact_path(provider_key, "provider_response_raw")
            _write_artifact(err_path, {
                "error": True,
                "status_code": e.code,
                "requested_model": model,
                "body": error_body,
                "input_hash": input_hash
            })
            
            # Try fallback if allowed
            if allow_fallback:
                fallback = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
                if fallback != model:
                    fallback_model = fallback
                    # Recursively call with fallback (one level only)
                    return _call_anthropic_fallback(
                        api_key, prompt, fallback_model, input_hash, provider_key,
                        original_model, fallback_model
                    )
            
            return _make_blocked_output(
                provider_key, input_hash, "BLOCKED_MODEL_NOT_FOUND",
                "BLOCKED_MODEL_NOT_FOUND", f"Model not found: {model}",
                raw_response_ref=str(err_path), model_name=model,
                original_model=original_model, fallback_model=fallback_model
            )
        
        # Other HTTP errors
        err_path = _artifact_path(provider_key, "provider_response_raw")
        _write_artifact(err_path, {"error": True, "status_code": e.code, "body": error_body, "input_hash": input_hash})
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE", f"Anthropic API error {e.code}: {error_body}",
            raw_response_ref=str(err_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Write raw response artifact
    raw_path = _artifact_path(provider_key, "provider_response_raw")
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    
    # Parse response
    try:
        data = json.loads(raw_response)
        text = data["content"][0]["text"]
    except (json.JSONDecodeError, KeyError) as e:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {"error": "response_structure", "detail": str(e), "raw_response_ref": str(raw_path)})
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", f"Anthropic response parse error: {e}",
            raw_response_ref=str(raw_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Extract JSON from text
    result = _extract_json_from_text(text)
    
    if result is None:
        extract_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(extract_err_path, {
            "error": "json_extraction",
            "text_preview": text[:500],
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", "Failed to extract JSON from Anthropic response",
            raw_response_ref=str(raw_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Validate required fields
    required_fields = ["score", "threshold", "pass"]
    missing = [f for f in required_fields if f not in result]
    if missing:
        schema_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(schema_err_path, {
            "error": "schema_validation",
            "missing_fields": missing,
            "result_keys": list(result.keys()),
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR", f"Missing required fields: {missing}",
            raw_response_ref=str(raw_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Write success parse result
    parse_path = _artifact_path(provider_key, "provider_parse_result")
    _write_artifact(parse_path, {"result": result, "raw_response_ref": str(raw_path)})
    
    return _make_model_backed_output(
        provider_key, input_hash, model, result,
        raw_response_ref=str(raw_path),
        original_model=original_model,
        fallback_model=fallback_model
    )


def _call_anthropic_fallback(
    api_key: str, prompt: str, model: str, input_hash: str, provider_key: str,
    original_model: str, fallback_model: str
) -> JudgeOutput:
    """Fallback call for Anthropic when original model not found."""
    payload = {
        "model": model,
        "max_tokens": 900,
        "messages": [{"role": "user", "content": prompt + "\n\nReturn JSON only."}],
        "temperature": 0.1,
    }
    
    req_path = _artifact_path(provider_key, "provider_request")
    _write_artifact(req_path, {
        "payload": payload,
        "input_hash": input_hash,
        "original_model": original_model,
        "fallback_model": fallback_model,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        err_path = _artifact_path(provider_key, "provider_response_raw")
        _write_artifact(err_path, {
            "error": True,
            "status_code": e.code,
            "original_model": original_model,
            "fallback_model": fallback_model,
            "body": error_body,
            "input_hash": input_hash
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_MODEL_NOT_FOUND",
            "BLOCKED_MODEL_NOT_FOUND", f"Fallback model also failed: {e.code}: {error_body}",
            raw_response_ref=str(err_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Write raw response artifact
    raw_path = _artifact_path(provider_key, "provider_response_raw")
    _write_artifact(raw_path, {
        "raw_response": raw_response,
        "original_model": original_model,
        "fallback_model": fallback_model,
        "input_hash": input_hash
    })
    
    # Parse response
    try:
        data = json.loads(raw_response)
        text = data["content"][0]["text"]
    except (json.JSONDecodeError, KeyError) as e:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(e),
            "original_model": original_model,
            "fallback_model": fallback_model,
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", f"Fallback response parse error: {e}",
            raw_response_ref=str(raw_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Extract JSON
    result = _extract_json_from_text(text)
    
    if result is None:
        extract_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(extract_err_path, {
            "error": "json_extraction",
            "text_preview": text[:500],
            "original_model": original_model,
            "fallback_model": fallback_model,
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", "Failed to extract JSON from fallback response",
            raw_response_ref=str(raw_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Validate required fields
    required_fields = ["score", "threshold", "pass"]
    missing = [f for f in required_fields if f not in result]
    if missing:
        schema_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(schema_err_path, {
            "error": "schema_validation",
            "missing_fields": missing,
            "original_model": original_model,
            "fallback_model": fallback_model,
            "result_keys": list(result.keys()),
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR", f"Fallback missing required fields: {missing}",
            raw_response_ref=str(raw_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Write success parse result
    parse_path = _artifact_path(provider_key, "provider_parse_result")
    _write_artifact(parse_path, {
        "result": result,
        "original_model": original_model,
        "fallback_model": fallback_model,
        "raw_response_ref": str(raw_path)
    })
    
    return _make_model_backed_output(
        provider_key, input_hash, model, result,
        raw_response_ref=str(raw_path),
        original_model=original_model,
        fallback_model=fallback_model
    )


def _call_gemini(api_key: str, prompt: str, model: str, input_hash: str, provider_key: str) -> JudgeOutput:
    """Call Gemini API with full artifact preservation."""
    payload = {
        "contents": [{"parts": [{"text": prompt + "\n\nReturn JSON only."}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 900},
    }
    
    # Use v1 endpoint for stable models, v1beta for preview models
    endpoint_version = "v1" if "-pro" in model and "preview" not in model else "v1beta"
    url = f"https://generativelanguage.googleapis.com/{endpoint_version}/models/{model}:generateContent?key={api_key}"
    
    # Write request artifact
    req_path = _artifact_path(provider_key, "provider_request")
    _write_artifact(req_path, {
        "payload": payload,
        "url": url,
        "input_hash": input_hash,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        err_path = _artifact_path(provider_key, "provider_response_raw")
        _write_artifact(err_path, {"error": True, "status_code": e.code, "body": error_body, "input_hash": input_hash})
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE", f"Gemini API error {e.code}: {error_body}",
            raw_response_ref=str(err_path), model_name=model
        )
    
    # Write raw response artifact
    raw_path = _artifact_path(provider_key, "provider_response_raw")
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    
    # Parse response
    try:
        data = json.loads(raw_response)
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (json.JSONDecodeError, KeyError) as e:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(e),
            "raw_response_preview": raw_response[:1000],
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", f"Gemini response parse error: {e}",
            raw_response_ref=str(raw_path), model_name=model
        )
    
    # Extract JSON from text
    result = _extract_json_from_text(text)
    
    if result is None:
        extract_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(extract_err_path, {
            "error": "json_extraction",
            "text_preview": text[:500],
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", "Failed to extract JSON from Gemini response",
            raw_response_ref=str(raw_path), model_name=model
        )
    
    # Validate required fields
    required_fields = ["score", "threshold", "pass"]
    missing = [f for f in required_fields if f not in result]
    if missing:
        schema_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(schema_err_path, {
            "error": "schema_validation",
            "missing_fields": missing,
            "result_keys": list(result.keys()),
            "raw_response_ref": str(raw_path)
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR", f"Missing required fields: {missing}",
            raw_response_ref=str(raw_path), model_name=model
        )
    
    # Write success parse result
    parse_path = _artifact_path(provider_key, "provider_parse_result")
    _write_artifact(parse_path, {"result": result, "raw_response_ref": str(raw_path)})
    
    return _make_model_backed_output(provider_key, input_hash, model, result, raw_response_ref=str(raw_path))


def _mocked_output(provider_key: str, input_hash: str) -> JudgeOutput:
    """Create a mocked judge output."""
    meta = PROVIDERS[provider_key]
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_exec_summary",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode="MOCKED",
        provider_status="MOCKED",
        model_name=meta.get("default_model", "unknown"),
        provider_available=False,
        provider_blocked=False,  # Mocked is not blocked
        exact_provider_error=None,
        raw_response_ref=None,
        rubric_version=JUDGE_RUBRIC_VERSION,
        input_hash=input_hash,
        output_hash="mocked-output",
        score=0.80,
        score_scale="0_to_1",
        normalized_score=0.80,
        threshold=DEFAULT_THRESHOLD,
        normalized_threshold=0.80,
        pass_=True,
        decisive_failure=False,
        findings=["MOCKED plumbing judge. Not valid for X3_ALLOW."],
        cited_sentence_indexes=[],
        remediation_suggestions=[],
    )


def run_llm_judges(
    *,
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    mode: str = "blocked_if_unavailable",
) -> list[JudgeOutput]:
    """Run or block the requested provider judges.

    mode values:
    - blocked_if_unavailable: attempt real providers only when credentials exist, otherwise block.
    - mocked: emit clearly mocked rows for plumbing tests.
    """
    input_payload = {"resume_display_text": resume_display_text, "claim_ledger": claim_ledger, "rubric": RUBRIC}
    input_hash = hashlib.sha256(json.dumps(input_payload, sort_keys=True).encode()).hexdigest()[:16]
    prompt = f"{RUBRIC}\n\nRESUME_DISPLAY_TEXT:\n{resume_display_text}\n\nCLAIM_LEDGER:\n{json.dumps(claim_ledger, indent=2)}"

    outputs: list[JudgeOutput] = []
    for key in judge_keys:
        if key not in PROVIDERS:
            outputs.append(_make_blocked_output(
                key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE", f"Unknown judge provider key: {key}"
            ))
            continue
        
        if mode == "mocked":
            outputs.append(_mocked_output(key, input_hash))
            continue
        
        meta = PROVIDERS[key]
        api_key = os.environ.get(str(meta["env"]), "")
        if not api_key:
            outputs.append(_make_blocked_output(
                key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE", f"{meta['env']} environment variable not set"
            ))
            continue
        
        # Get model name
        model_env = meta.get("model_env", meta["env"].replace("_API_KEY", "_MODEL"))
        model = os.environ.get(model_env, "")
        if not model:
            # Try fallback env if defined
            fallback_env = meta.get("fallback_env")
            if fallback_env:
                model = os.environ.get(fallback_env, "")
        if not model:
            model = meta.get("default_model", "unknown")
        
        try:
            if key == "openai_chatgpt":
                output = _call_openai(api_key, prompt, model, input_hash, key)
            elif key == "anthropic_claude":
                output = _call_anthropic(api_key, prompt, model, input_hash, key)
            else:
                output = _call_gemini(api_key, prompt, model, input_hash, key)
            outputs.append(output)
        except Exception as exc:  # noqa: BLE001
            # Catch any unexpected errors and mark as blocked
            outputs.append(_make_blocked_output(
                key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE", f"{meta['provider_name']} judge call failed: {type(exc).__name__}: {exc}",
                model_name=model
            ))
    
    return outputs
