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
VALID_SCORE_SCALES = frozenset({"0_to_1", "0_to_5"})
JUDGE_REQUIRED_FIELDS = ("score_scale", "score", "threshold", "pass")
GEMINI_JUDGE_MAX_OUTPUT_TOKENS = int(os.environ.get("APPS_RG_GEMINI_JUDGE_MAX_OUTPUT_TOKENS", "4096"))
ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS = int(os.environ.get("APPS_RG_ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS", "1024"))

JUDGE_COMPACT_OUTPUT = """
Return ONLY one compact JSON object. No markdown fences, no prose before or after, no nested objects.
Required shape (findings and remediation_suggestions must be arrays of short strings only):
{"score_scale":"0_to_5","score":0.0,"threshold":4.0,"pass":true,"decisive_failure":false,"findings":["..."],"cited_sentence_indexes":[1],"remediation_suggestions":[]}
At most 6 short strings in findings and 4 in remediation_suggestions.
""".strip()

JUDGE_COMPACT_SYSTEM = (
    "You are a strict executive resume judge. Output a single compact JSON object only. "
    "No markdown fences, no explanatory prose, no nested finding objects."
)

GEMINI_JUDGE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "score_scale": {"type": "string", "enum": ["0_to_1", "0_to_5"]},
        "score": {"type": "number"},
        "threshold": {"type": "number"},
        "pass": {"type": "boolean"},
        "decisive_failure": {"type": "boolean"},
        "findings": {"type": "array", "items": {"type": "string"}},
        "cited_sentence_indexes": {"type": "array", "items": {"type": "integer"}},
        "remediation_suggestions": {"type": "array", "items": {"type": "string"}},
    },
    "required": list(JUDGE_REQUIRED_FIELDS)
    + ["decisive_failure", "findings", "cited_sentence_indexes", "remediation_suggestions"],
}

JUDGE_SCORE_SCHEMA = """
Score contract (mandatory — every judge response MUST comply):
- Include score_scale as exactly one of: "0_to_1" or "0_to_5". Do not omit score_scale.
- If score_scale is "0_to_1": score and threshold MUST each be a number from 0.0 through 1.0 inclusive.
- If score_scale is "0_to_5": score and threshold MUST each be a number from 0.0 through 5.0 inclusive.
- Forbidden: 0_to_10 scales, percentage scores (0–100), or values like score=9.2 with threshold=8.0.
- Do not infer scale from magnitude; declare score_scale explicitly and keep score/threshold within that scale.
""".strip()

RUBRIC = f"""
You are evaluating one executive resume summary. Use the same rubric for every provider.
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

{JUDGE_SCORE_SCHEMA}

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
        "model_env": "APPS_RG_GEMINI_JUDGE_MODEL",
        "fallback_env": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash",
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


def _validate_judge_score_contract(
    raw_score: float,
    raw_threshold: float,
    declared: str | None,
) -> tuple[str | None, str | None]:
    """Validate declared score_scale and numeric ranges; never infer scale from magnitude."""
    if not declared or declared not in VALID_SCORE_SCALES:
        return None, (
            f"Invalid or missing score_scale: {declared!r}; "
            f"must be one of {sorted(VALID_SCORE_SCALES)}"
        )
    if declared == "0_to_1":
        if not (0.0 <= raw_score <= 1.0 and 0.0 <= raw_threshold <= 1.0):
            return None, (
                f"score/threshold out of range for 0_to_1: score={raw_score}, threshold={raw_threshold}"
            )
    elif declared == "0_to_5":
        if not (0.0 <= raw_score <= 5.0 and 0.0 <= raw_threshold <= 5.0):
            return None, (
                f"score/threshold out of range for 0_to_5: score={raw_score}, threshold={raw_threshold}"
            )
    return declared, None


def _compute_normalized(
    raw_score: float,
    raw_threshold: float,
    score_scale: str,
) -> tuple[float, float]:
    """Map raw judge score/threshold to 0..1 using an explicit scale."""
    if score_scale == "0_to_1":
        return raw_score, raw_threshold
    if score_scale == "0_to_5":
        return raw_score / 5.0, raw_threshold / 5.0
    raise ValueError(f"invalid score_scale: {score_scale}")


def _resolve_gemini_model(meta: dict[str, Any]) -> tuple[str, str]:
    """Resolve Gemini judge model; APPS_RG_GEMINI_JUDGE_MODEL overrides GEMINI_MODEL."""
    judge_model = os.environ.get("APPS_RG_GEMINI_JUDGE_MODEL", "").strip()
    if judge_model:
        return judge_model, "APPS_RG_GEMINI_JUDGE_MODEL"
    general = os.environ.get("GEMINI_MODEL", "").strip()
    if general:
        return general, "GEMINI_MODEL"
    return str(meta.get("default_model", "gemini-2.0-flash")), "default"


def _resolve_anthropic_model(meta: dict[str, Any]) -> tuple[str, str]:
    """Resolve Anthropic judge model from env without silent API substitution."""
    judge_model = os.environ.get("APPS_RG_ANTHROPIC_JUDGE_MODEL", "").strip()
    if judge_model:
        return judge_model, "APPS_RG_ANTHROPIC_JUDGE_MODEL"
    general = os.environ.get("ANTHROPIC_MODEL", "").strip()
    if general:
        return general, "ANTHROPIC_MODEL"
    default = str(meta.get("default_model", "claude-3-5-sonnet-20241022"))
    return default, "default"


def _normalize_judge_result(raw: dict[str, Any]) -> dict[str, Any]:
    """Coerce provider-native judge JSON into the executive_summary_x1d schema."""
    result = dict(raw)
    result["score"] = float(result.get("score", 0.0))
    result["threshold"] = float(result.get("threshold", DEFAULT_THRESHOLD))

    decisive = result.get("decisive_failure", False)
    if isinstance(decisive, str):
        result["decisive_failure"] = decisive.strip().lower() not in ("", "false", "none", "[]", "{}")
    else:
        result["decisive_failure"] = bool(decisive)

    findings = result.get("findings", [])
    if isinstance(findings, dict):
        flat: list[str] = []
        for key, value in findings.items():
            if isinstance(value, dict):
                note = value.get("notes") or value.get("note") or json.dumps(value, sort_keys=True)
                flat.append(f"{key}: {note}")
            else:
                flat.append(f"{key}: {value}")
        result["findings"] = flat
    elif not isinstance(findings, list):
        result["findings"] = [str(findings)] if findings else []

    cited = result.get("cited_sentence_indexes", [])
    if isinstance(cited, dict):
        result["cited_sentence_indexes"] = [int(k) if str(k).isdigit() else k for k in cited.keys()]
    elif not isinstance(cited, list):
        result["cited_sentence_indexes"] = []

    remed = result.get("remediation_suggestions", [])
    if not isinstance(remed, list):
        result["remediation_suggestions"] = [remed] if remed else []

    if "pass" not in result:
        result["pass"] = (
            float(result["score"]) >= float(result["threshold"]) and not result["decisive_failure"]
        )
    return result


def _build_judge_user_prompt(resume_display_text: str, claim_ledger: list[dict[str, Any]]) -> str:
    """Build provider judge user prompt with compact JSON-only output contract."""
    return (
        f"{RUBRIC}\n\n{JUDGE_COMPACT_OUTPUT}\n\n"
        f"RESUME_DISPLAY_TEXT:\n{resume_display_text}\n\n"
        f"CLAIM_LEDGER:\n{json.dumps(claim_ledger, separators=(',', ':'))}"
    )


def _gemini_generation_config() -> dict[str, Any]:
    """Gemini generationConfig for compact schema-valid judge JSON."""
    return {
        "temperature": 0.1,
        "maxOutputTokens": GEMINI_JUDGE_MAX_OUTPUT_TOKENS,
        "responseMimeType": "application/json",
        "responseSchema": GEMINI_JUDGE_RESPONSE_SCHEMA,
    }


def _extract_anthropic_message_text(data: dict[str, Any]) -> str:
    """Extract assistant text from Anthropic messages API content blocks."""
    chunks: list[str] = []
    for block in data.get("content") or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and block.get("text"):
            chunks.append(str(block["text"]))
    return "".join(chunks)


def _extract_gemini_text(data: dict[str, Any]) -> tuple[str, str | None]:
    """Extract model text and finishReason from a Gemini generateContent response."""
    finish_reason = None
    candidates = data.get("candidates") or []
    if not candidates:
        return "", "NO_CANDIDATES"
    candidate = candidates[0]
    finish_reason = candidate.get("finishReason")
    content = candidate.get("content") or {}
    parts = content.get("parts") or []
    text_chunks: list[str] = []
    for part in parts:
        if isinstance(part, dict) and part.get("text"):
            text_chunks.append(str(part["text"]))
    return "".join(text_chunks), finish_reason


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
    result = _normalize_judge_result(result)
    raw_score = float(result.get("score", 0.0))
    raw_threshold = float(result.get("threshold", DEFAULT_THRESHOLD))
    declared_scale = result.get("score_scale")
    declared = declared_scale.strip() if isinstance(declared_scale, str) else None
    score_scale, err = _validate_judge_score_contract(raw_score, raw_threshold, declared)
    if err:
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            err,
            raw_response_ref=raw_response_ref,
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    assert score_scale is not None  # validated above
    try:
        normalized_score, normalized_threshold = _compute_normalized(
            raw_score, raw_threshold, score_scale
        )
    except ValueError as exc:
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            str(exc),
            raw_response_ref=raw_response_ref,
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    decisive = bool(result.get("decisive_failure", False))
    passed = normalized_score >= normalized_threshold and not decisive
    output_hash = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:16]
    meta = PROVIDERS[provider_key]

    provider_status = "MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL"

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
        score=raw_score,
        score_scale=score_scale,
        normalized_score=normalized_score,
        threshold=raw_threshold,
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
            {
                "role": "system",
                "content": (
                    "You are a strict executive resume judge. Return JSON only.\n\n"
                    f"{JUDGE_SCORE_SCHEMA}"
                ),
            },
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
    
    blocked = _validate_judge_parse_result(
        provider_key, input_hash, model, result, str(raw_path)
    )
    if blocked is not None:
        return blocked

    parse_path = _artifact_path(provider_key, "provider_parse_result")
    _write_artifact(parse_path, {"result": result, "raw_response_ref": str(raw_path)})

    return _make_model_backed_output(provider_key, input_hash, model, result, raw_response_ref=str(raw_path))


def _validate_judge_parse_result(
    provider_key: str,
    input_hash: str,
    model_name: str,
    result: dict[str, Any],
    raw_response_ref: str,
) -> JudgeOutput | None:
    """Return a blocked JudgeOutput when required judge fields are missing; else None."""
    missing = [f for f in JUDGE_REQUIRED_FIELDS if f not in result]
    if missing:
        schema_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(
            schema_err_path,
            {
                "error": "schema_validation",
                "missing_fields": missing,
                "result_keys": list(result.keys()),
                "raw_response_ref": raw_response_ref,
            },
        )
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            f"Missing required fields: {missing}",
            raw_response_ref=raw_response_ref,
            model_name=model_name,
        )
    return None


def _call_anthropic(
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    provider_key: str,
    *,
    model_source: str = "unknown",
) -> JudgeOutput:
    """Call Anthropic API with full artifact preservation and model fallback handling."""
    original_model = model
    fallback_model = None
    
    # Check for fallback permission
    allow_fallback = os.environ.get("APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK", "").lower() == "true"
    
    payload = {
        "model": model,
        "max_tokens": ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS,
        "system": JUDGE_COMPACT_SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }
    
    # Write request artifact
    req_path = _artifact_path(provider_key, "provider_request")
    _write_artifact(req_path, {
        "payload": payload,
        "input_hash": input_hash,
        "original_model": original_model,
        "resolved_model": model,
        "resolved_model_source": model_source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
            
            if allow_fallback:
                fallback_candidates = [
                    os.environ.get("ANTHROPIC_MODEL", "").strip(),
                    str(PROVIDERS["anthropic_claude"]["default_model"]),
                ]
                for fallback in fallback_candidates:
                    if fallback and fallback != model:
                        return _call_anthropic_fallback(
                            api_key,
                            prompt,
                            fallback,
                            input_hash,
                            provider_key,
                            original_model,
                            fallback,
                            "APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK=true after 404 not_found",
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
    
    try:
        data = json.loads(raw_response)
        text = _extract_anthropic_message_text(data)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(exc),
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Anthropic response parse error: {exc}",
            raw_response_ref=str(raw_path),
            model_name=model,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    return _finish_judge_text_parse(
        provider_key=provider_key,
        input_hash=input_hash,
        model_name=model,
        raw_path=raw_path,
        text=text,
        original_model=original_model,
        fallback_model=fallback_model,
    )


def _call_anthropic_fallback(
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    provider_key: str,
    original_model: str,
    fallback_model: str,
    fallback_reason: str,
) -> JudgeOutput:
    """Fallback call for Anthropic when original model not found."""
    payload = {
        "model": model,
        "max_tokens": ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS,
        "system": JUDGE_COMPACT_SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }

    req_path = _artifact_path(provider_key, "provider_request")
    _write_artifact(req_path, {
        "payload": payload,
        "input_hash": input_hash,
        "original_model": original_model,
        "fallback_model": fallback_model,
        "fallback_reason": fallback_reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "fallback_reason": fallback_reason,
            "body": error_body,
            "input_hash": input_hash,
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_MODEL_NOT_FOUND",
            "BLOCKED_MODEL_NOT_FOUND", f"Fallback model also failed: {e.code}: {error_body}",
            raw_response_ref=str(err_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )

    raw_path = _artifact_path(provider_key, "provider_response_raw")
    _write_artifact(raw_path, {
        "raw_response": raw_response,
        "original_model": original_model,
        "fallback_model": fallback_model,
        "input_hash": input_hash,
    })

    try:
        data = json.loads(raw_response)
        text = _extract_anthropic_message_text(data)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(exc),
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Fallback response parse error: {exc}",
            raw_response_ref=str(raw_path),
            model_name=model,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    return _finish_judge_text_parse(
        provider_key=provider_key,
        input_hash=input_hash,
        model_name=model,
        raw_path=raw_path,
        text=text,
        original_model=original_model,
        fallback_model=fallback_model,
    )


def _finish_judge_text_parse(
    *,
    provider_key: str,
    input_hash: str,
    model_name: str,
    raw_path: Path,
    text: str,
    finish_reason: str | None = None,
    original_model: str | None = None,
    fallback_model: str | None = None,
) -> JudgeOutput:
    """Parse extracted judge text into JudgeOutput or blocked status."""
    if finish_reason and str(finish_reason).upper() not in ("STOP",):
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {
            "error": "finish_reason",
            "finish_reason": finish_reason,
            "text_preview": text[:500],
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Gemini finishReason={finish_reason} (incomplete judge JSON)",
            raw_response_ref=str(raw_path),
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    if not str(text).strip():
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {"error": "empty_text", "raw_response_ref": str(raw_path)})
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "Response contained no judge text",
            raw_response_ref=str(raw_path),
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    result = _extract_json_from_text(text)
    if result is None:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {
            "error": "json_extraction",
            "text_preview": text[:500],
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Failed to extract JSON from {provider_key} response",
            raw_response_ref=str(raw_path),
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    blocked = _validate_judge_parse_result(provider_key, input_hash, model_name, result, str(raw_path))
    if blocked is not None:
        return blocked

    parse_path = _artifact_path(provider_key, "provider_parse_result")
    _write_artifact(parse_path, {
        "result": result,
        "raw_response_ref": str(raw_path),
        "original_model": original_model,
        "fallback_model": fallback_model,
    })

    return _make_model_backed_output(
        provider_key,
        input_hash,
        model_name,
        result,
        raw_response_ref=str(raw_path),
        original_model=original_model,
        fallback_model=fallback_model,
    )


def _call_gemini(
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    provider_key: str,
    *,
    model_source: str = "unknown",
) -> JudgeOutput:
    """Call Gemini API with full artifact preservation."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": _gemini_generation_config(),
    }

    endpoint_version = "v1beta" if "preview" in model or model.startswith("gemini-2") or model.startswith("gemini-3") else "v1"
    url = f"https://generativelanguage.googleapis.com/{endpoint_version}/models/{model}:generateContent?key={api_key}"
    
    # Write request artifact
    req_path = _artifact_path(provider_key, "provider_request")
    _write_artifact(req_path, {
        "payload": payload,
        "url": url,
        "resolved_model": model,
        "resolved_model_source": model_source,
        "input_hash": input_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
    
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result")
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(e),
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", f"Gemini response envelope parse error: {e}",
            raw_response_ref=str(raw_path), model_name=model,
        )

    text, finish_reason = _extract_gemini_text(data)
    return _finish_judge_text_parse(
        provider_key=provider_key,
        input_hash=input_hash,
        model_name=model,
        raw_path=raw_path,
        text=text,
        finish_reason=finish_reason,
    )


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
    prompt = _build_judge_user_prompt(resume_display_text, claim_ledger)

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
        
        model_source = "unknown"
        if key == "gemini_pro":
            model, model_source = _resolve_gemini_model(meta)
        elif key == "anthropic_claude":
            model, model_source = _resolve_anthropic_model(meta)
        else:
            model_env = meta.get("model_env", meta["env"].replace("_API_KEY", "_MODEL"))
            model = os.environ.get(model_env, "").strip()
            model_source = model_env if model else "unknown"
            if not model:
                model = meta.get("default_model", "unknown")
                model_source = "default"

        try:
            if key == "openai_chatgpt":
                output = _call_openai(api_key, prompt, model, input_hash, key)
            elif key == "anthropic_claude":
                output = _call_anthropic(
                    api_key, prompt, model, input_hash, key, model_source=model_source
                )
            else:
                output = _call_gemini(
                    api_key, prompt, model, input_hash, key, model_source=model_source
                )
            outputs.append(output)
        except Exception as exc:  # noqa: BLE001
            # Catch any unexpected errors and mark as blocked
            outputs.append(_make_blocked_output(
                key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE", f"{meta['provider_name']} judge call failed: {type(exc).__name__}: {exc}",
                model_name=model
            ))
    
    return outputs
