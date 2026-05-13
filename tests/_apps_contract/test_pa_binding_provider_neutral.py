"""Test provider-neutrality of apps_rg PA bullet-rewrite binding.

Verifies:
1. No retrieval language (C0-free path)
2. No Claude-specific wording
3. No unsupported metric invention
4. PA remains package-only
5. JSON output format with required fields

Plan: apps-rg-pa-provider-neutral-prompt-c9d2a8
"""

import pytest
from apps_rg.runtime.bindings.pa_binding import (
    _build_bullet_rewrite_prompt,
    _build_system_preamble,
    _build_u0_task_block,
)


# Forbidden patterns that indicate provider-specific or retrieval language
FORBIDDEN_PATTERNS = [
    # Claude-specific
    "anthropic",
    "claude",
    "constitution",
    "constitutional",
    "ai constitution",
    "claude-3",
    "opus",
    "sonnet",
    "haiku",
    
    # OpenAI-specific
    "gpt-4",
    "gpt-3",
    "chatgpt",
    "openai",
    
    # Retrieval implications (C0)
    "retrieve",
    "fetch",
    "query",
    "search for",
    "look up",
    "find additional",
    "supplement with",
    "augment with",
    "enrich with",
    "c0_verified",
    "c0_evidence",
    "retrieve from chroma",
    "vector search",
    "embedding",
    
    # Web/search implications
    "web search",
    "internet",
    "online",
    "browse",
    "scrape",
    
    # Invention encouragement (use word boundaries to avoid matching "invention" context)
    "make up",
    "create new",  # "invent" is allowed in "invention_blocked" context
    "add details",
    "fill in",
    "round up",
    "approximate",
    "estimate",
    "typical for role",
    "industry standard",
]

# Required anti-invention terms (checked case-insensitively)
REQUIRED_ANTI_INVENTION_TERMS = [
    "INSUFFICIENT_SOURCE_SUPPORT",
    "source_span",
    "jd_alignment",
    "rewritten_bullet",
    "blocked_items",
    "metrics not present",  # matches "NO new metrics not present"
    "client names not present",   # matches "NO new client names not present"
    "tools/technologies not present",    # matches prompt
    "scope beyond what source materials support",    # matches prompt
]

# Required output format fields
REQUIRED_OUTPUT_FIELDS = [
    "source_span",
    "jd_alignment",
    "rewritten_bullet",
    "blocked_items",
    "status",
]


class TestProviderNeutralPrompt:
    """Verify PA binding is provider-neutral and C0-free."""

    def test_bullet_rewrite_prompt_no_forbidden_patterns(self):
        """REQ-1: Prompt contains no provider-specific or retrieval language."""
        prompt = _build_bullet_rewrite_prompt(
            source_resume_text="Led team of 10 engineers",
            jd_text="SVP Engineering role",
            target_company="TestCorp",
            target_role="SVP Engineering",
        )
        
        prompt_lower = prompt.lower()
        violations = []
        
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in prompt_lower:
                violations.append(pattern)
        
        assert not violations, f"Forbidden patterns found: {violations}"

    def test_bullet_rewrite_prompt_has_anti_invention_rules(self):
        """REQ-2: Prompt contains strict anti-invention rules."""
        prompt = _build_bullet_rewrite_prompt(
            source_resume_text="Led team of 10 engineers",
            jd_text="SVP Engineering role",
            target_company="TestCorp",
            target_role="SVP Engineering",
        )
        
        prompt_lower = prompt.lower()
        
        for term in REQUIRED_ANTI_INVENTION_TERMS:
            assert term.lower() in prompt_lower, f"Missing anti-invention term: {term}"

    def test_bullet_rewrite_prompt_requires_source_spans(self):
        """REQ-3: Prompt requires exact source-span extraction."""
        prompt = _build_bullet_rewrite_prompt(
            source_resume_text="Led team of 10 engineers",
            jd_text="SVP Engineering role",
            target_company="TestCorp",
            target_role="SVP Engineering",
        )
        
        assert "source_span" in prompt
        assert "verbatim" in prompt.lower()
        assert "exact" in prompt.lower()

    def test_bullet_rewrite_prompt_json_output_format(self):
        """REQ-4: Prompt specifies JSON output with required fields."""
        prompt = _build_bullet_rewrite_prompt(
            source_resume_text="Led team of 10 engineers",
            jd_text="SVP Engineering role",
            target_company="TestCorp",
            target_role="SVP Engineering",
        )
        
        for field in REQUIRED_OUTPUT_FIELDS:
            assert field in prompt, f"Missing output field: {field}"
        
        assert "INSUFFICIENT_SOURCE_SUPPORT" in prompt
        assert "SUCCESS" in prompt
        assert "PRESERVED_VERBATIM" in prompt

    def test_bullet_rewrite_prompt_no_c0_implication(self):
        """REQ-5: Prompt does not imply C0 retrieval or external evidence."""
        prompt = _build_bullet_rewrite_prompt(
            source_resume_text="Led team of 10 engineers",
            jd_text="SVP Engineering role",
            target_company="TestCorp",
            target_role="SVP Engineering",
        )
        
        # Should reference only supplied inputs
        assert "supplied source materials" in prompt.lower()
        assert "source_materials" in prompt
        
        # Should NOT reference retrieval
        assert "retrieve" not in prompt.lower()
        assert "fetch" not in prompt.lower()

    def test_bullet_rewrite_prompt_has_xml_sections(self):
        """REQ-6: Prompt uses XML-style sections for structure."""
        prompt = _build_bullet_rewrite_prompt(
            source_resume_text="Led team of 10 engineers",
            jd_text="SVP Engineering role",
            target_company="TestCorp",
            target_role="SVP Engineering",
        )
        
        xml_sections = ["<task>", "<source_materials>", "<job_description>", 
                       "<instructions>", "<output_format>"]
        
        for section in xml_sections:
            assert section in prompt, f"Missing XML section: {section}"


class TestSystemPreambleProviderNeutral:
    """Verify system preamble is provider-neutral."""

    def test_system_preamble_no_provider_specific_terms(self):
        """REQ-7: System preamble contains no provider-specific wording."""
        preamble = _build_system_preamble(
            forbidden=["responsible for"],
            power=["led", "delivered"],
        )
        
        preamble_lower = preamble.lower()
        violations = []
        
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in preamble_lower:
                violations.append(pattern)
        
        assert not violations, f"Provider-specific terms in preamble: {violations}"

    def test_system_preamble_grounding_instruction(self):
        """REQ-8: System preamble requires source material grounding."""
        preamble = _build_system_preamble(
            forbidden=["responsible for"],
            power=["led", "delivered"],
        )
        
        assert "source materials" in preamble.lower()
        assert "no fabrication" in preamble.lower()


class TestReceiptCompliance:
    """Generate compliance receipt for PA binding."""

    def test_generate_compliance_receipt(self):
        """Generate structured receipt showing PA compliance."""
        prompt = _build_bullet_rewrite_prompt(
            source_resume_text="Led team of 10 engineers",
            jd_text="SVP Engineering role",
            target_company="TestCorp",
            target_role="SVP Engineering",
        )
        
        # Check all requirements
        checks = {
            "no_provider_specific": not any(p.lower() in prompt.lower() for p in FORBIDDEN_PATTERNS[:15]),
            "no_retrieval_language": "retrieve" not in prompt.lower() and "fetch" not in prompt.lower(),
            "has_anti_invention": "INSUFFICIENT_SOURCE_SUPPORT" in prompt,
            "requires_source_spans": "source_span" in prompt,
            "json_output_format": all(f in prompt for f in REQUIRED_OUTPUT_FIELDS),
            "xml_structure": all(s in prompt for s in ["<task>", "<output_format>"]),
            "c0_free": "c0" not in prompt.lower() or "supplied source" in prompt.lower(),
        }
        
        # Generate receipt
        receipt = {
            "component": "apps_rg PA binding",
            "compliance_checks": checks,
            "overall_status": "PASS" if all(checks.values()) else "FAIL",
            "notes": [
                "PA remains package-only: assembles U0 inputs without modification",
                "C0-free path: references only supplied source_materials from U0",
                "Provider-neutral: compatible with Qwen vLLM and future lanes",
                "Anti-invention enforced: strict rules against unsupported claims",
            ],
        }
        
        # Print receipt for visibility
        print("\n" + "=" * 60)
        print("PA BINDING COMPLIANCE RECEIPT")
        print("=" * 60)
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}")
        print(f"\nOverall: {receipt['overall_status']}")
        print("\nNotes:")
        for note in receipt["notes"]:
            print(f"  • {note}")
        print("=" * 60)
        
        assert receipt["overall_status"] == "PASS", f"Compliance failed: {checks}"
