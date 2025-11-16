from prompt_taxonomy import (
    DEFAULT_INJECTION_PATTERNS,
    INSTRUCTIONAL_INJECTION_ALL,
    InjectionType,
    InstructionalInjection,
    PromptSection,
    SECTION_ORDER,
)


def test_prompt_section_taxonomy_count():
    assert len(PromptSection) == 6


def test_injection_type_count():
    assert len(InjectionType) == 4
    assert DEFAULT_INJECTION_PATTERNS == [
        InjectionType.OVERRIDE_SYSTEM.value,
        InjectionType.IGNORE_PREVIOUS.value,
        InjectionType.DISABLE_SAFETY.value,
        InjectionType.RUN_ARBITRARY_CODE.value,
    ]


def test_instructional_injection_count():
    assert len(InstructionalInjection) == 30


EXPECTED_SECTION_ORDER = [
    PromptSection.FRAMING,
    PromptSection.CONTEXT,
    PromptSection.REASONING,
    PromptSection.INSTRUCTIONS,
    PromptSection.SAFETY,
    PromptSection.OUTPUT_SCHEMA,
]


def test_section_order_matches_expected():
    assert SECTION_ORDER == EXPECTED_SECTION_ORDER


def test_instructional_injection_all_contains_all_values():
    assert len(INSTRUCTIONAL_INJECTION_ALL) == 30
    assert set(INSTRUCTIONAL_INJECTION_ALL) == {member.value for member in InstructionalInjection}
