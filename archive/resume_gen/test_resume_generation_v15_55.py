import pytest
import os
from pathlib import Path
from datetime import datetime
import json
import re
import functools # Needed for consolidated failure test helpers
import copy # For deep copying master resume in mocks
from typing import Dict, Any, Set, List, Tuple # For type hinting

# --- START REFACTOR: Update imports for v15.55 ---
from Resume_Generation_v15_55 import (
    WorkflowOrchestrator, MASTER_RESUME_JSON, APP_TRACKER_SCHEMA_V4, ResumeSection,
    COVER_LETTER_SIGNATURE_TEMPLATE, GateDecision, HopExecutionError, HopStatus,
    PreFlightValidator, TextSanitizer, ArtistGenerator, ReasoningConfig,
    FileRenderer, ValidationResult, ValidationSeverity,
    reasoning_config_to_api_params, _build_reasoning_prompt_addendum, calculate_signal_score,
    ImmutableStagingBuffer,
    _count_sentences, EnhancedJobDescriptionAnalyzer, RAGConfig,
    count_words_ms_word_style, # <<< MODIFICATION: Use ms_word_style counter >>>
    BulletProvenance, ThematicAnalysis,
    ContentConstraintsConfig, SignalControlConfig, ValidationContext # Import new context class
)
# --- END REFACTOR ---

# --- Fixtures ---

@pytest.fixture(scope="module")
def job_description() -> str:
    """Loads the test job description from a file, creating a dummy if not found."""
    # Using a slightly different JD for better keyword diversity in tests
    jd_path = Path(__file__).parent / "test_data/datadog_jd.txt"
    if not jd_path.exists():
        print(f"\nWarning: Test JD file not found at {jd_path}. Creating dummy file.")
        jd_path.parent.mkdir(parents=True, exist_ok=True)
        # Add more keywords relevant to the master resume
        jd_path.write_text("""
Dummy Job Description for DataDog Director, Technology Alliances.
Keywords: Strategic partnerships, AWS, Google Cloud, Microsoft Azure, SaaS, cloud services, GTM strategy, revenue growth, team leadership, cross-functional collaboration, executive presentations, AI platforms, partner enablement. Seeking experienced alliance leader.
        """)
    return jd_path.read_text()

@pytest.fixture(scope="module")
def orchestrator_instance() -> WorkflowOrchestrator:
    """
    Initializes the WorkflowOrchestrator once per module.
    Skips tests requiring API if key is missing.
    """
    if "GEMINI_API_KEY" not in os.environ or not os.environ["GEMINI_API_KEY"]:
        pytest.skip("GEMINI_API_KEY environment variable not set, skipping tests requiring API.")
    # Use deepcopy to prevent tests from modifying the global MASTER_RESUME_JSON
    return WorkflowOrchestrator(copy.deepcopy(MASTER_RESUME_JSON), test_mode=True) # <<< MODIFICATION: Added test_mode=True

@pytest.fixture
def mock_thematic_analysis_base(mocker):
    """Provides a basic mock ThematicAnalysis object reflecting RAG output."""
    mock_analysis = mocker.MagicMock(spec=ThematicAnalysis)
    mock_analysis.competitive_intelligence = mocker.MagicMock()
    # Simulate get_top_differentiators returning ranked keywords
    mock_analysis.competitive_intelligence.get_top_differentiators.return_value = ["GenAI adoption", "SaaS delivery", "retention"]
    # Simulate differentiator_keywords_raw having the unranked list
    mock_analysis.competitive_intelligence.differentiator_keywords_raw = ['GenAI adoption', 'SaaS delivery', 'retention', 'cloud strategy', 'AWS partnerships']
    mock_analysis.primary_theme = {'name': 'Strategic Cloud Alliances', 'confidence': 0.9, 'keywords': ['aws', 'gcp', 'azure', 'partnerships']}
    mock_analysis.secondary_themes = [{'name': 'GTM Strategy', 'relevance': 0.8, 'keywords': ['gtm', 'revenue growth']}]
    mock_analysis.problem_solution_narratives = {"common_problems": ["Slow partner onboarding", "Low attach rate"], "solution_patterns": ["Automated enablement", "Joint solution bundles"]}
    mock_analysis.role_classification = {'seniority': 'executive', 'role_archetype': 'Pre-Sales_GTM', 'precise_role_title': 'Director, Tech Alliances'}
    mock_analysis.signal_quality_score = 0.85
    mock_analysis.retrieval_method = "MOCK_RAG"
    # Ensure authenticity patterns exist and have the expected 'patterns' sub-dict
    mock_analysis.authenticity_patterns = {
        'patterns': {
            'executive_summary_patterns': ["Led <X> achieving <Y>"],
            'achievement_verb_patterns': ["Drove", "Scaled", "Forged"], # Add some verbs
            'metric_presentation_patterns': ["$XM ARR"],
            'competency_phrasing': ["Strategic Alliances: <Context>"]
        },
         'confidence': {'overall': 0.75}, # Add confidence
         'status': 'STRONG'
    }
    return mock_analysis

@pytest.fixture
def artist_generator_instance(mocker, job_description, mock_thematic_analysis_base):
    """Provides an ArtistGenerator instance with basic mock dependencies for v12.80."""
    # Use a minimal, clean master resume
    mock_master_resume = {
        "schema_version": "test_v1",
        "owner": {"name": "Test User", "contact": {"email": "a@b.c", "phone":"1", "linkedin":"l"}},
        "professional_experience": [
             {"company": "Unify Consulting", "title": "T1", "location":"L1", "dates":{"start":"S","end":"E"}, "bullet_pool": ["B1"], "overview":"O1"},
        ],
        "education": [], "certifications_and_credentials": [], "strategic_and_technical_competencies": []
    }
    # Provide a minimal scaffold matching expected structure
    mock_enriched_scaffold = {
        "experience_sections": [{"company": "Unify Consulting", "bullets": [{"bullet_text": "B1", "provenance": "Verbatim"}]}]
    }
    generator = ArtistGenerator(
        master_resume=copy.deepcopy(mock_master_resume),
        enriched_scaffold=mock_enriched_scaffold,
        job_description=job_description,
        thematic_analysis=mock_thematic_analysis_base
    )
    # Mock the internal API call helper used by all generation methods
    mocker.patch.object(generator, '_call_gemini_api', return_value="Mocked LLM Response") # type: ignore
    return generator # type: ignore

@pytest.fixture
def mock_thematic_analysis_k1(mock_thematic_analysis_base):
    """Provides a more detailed mock ThematicAnalysis specifically for K.1 tests."""
    # Keep alliances focus
    mock_thematic_analysis_base.primary_theme = {'name': 'Strategic Technology Alliances', 'confidence': 0.95, 'keywords': ['partnerships', 'aws', 'gcp', 'azure']}
    mock_thematic_analysis_base.competitive_intelligence.get_top_differentiators.return_value = ["AWS Partnerships", "GTM Execution", "Revenue Growth", "Executive Leadership", "SaaS Delivery"] # Top 5 ranked
    mock_thematic_analysis_base.competitive_intelligence.differentiator_keywords_raw = ["AWS Partnerships", "GTM Execution", "Revenue Growth", "Executive Leadership", "SaaS Delivery", "Cloud Strategy", "Partner Enablement"] # Raw list
    mock_thematic_analysis_base.role_classification = {'seniority': 'executive', 'role_archetype': 'Pre-Sales_GTM', 'precise_role_title': 'Director, Tech Alliances'}
    # Ensure authenticity patterns exist
    if not mock_thematic_analysis_base.authenticity_patterns:
        mock_thematic_analysis_base.authenticity_patterns = {
            'patterns': {'achievement_verb_patterns': ["Drove", "Scaled"]},
            'confidence': {'overall': 0.7}
        }
    return mock_thematic_analysis_base

@pytest.fixture
def artist_generator_k1(mocker, job_description, mock_thematic_analysis_k1):
    """ArtistGenerator instance specifically for K.1 testing."""
    mock_master_resume = {
        "schema_version": "test_v1",
        "owner": {"name": "Test User", "contact": {"email": "a@b.c", "phone":"1", "linkedin":"l"}},
        "professional_experience": [
            {"company": "Unify Consulting", "title":"T1","location":"L1","dates":{"start":"S","end":"E"}, "bullet_pool": ["U Bullet 1 Achieved X%", "U Bullet 2 Led Y team", "U3 Secured $18M AWS partnership revenue", "U4 Generated $32M client value"], "overview":"O1"},
            {"company": "IBM", "title":"T2","location":"L2","dates":{"start":"S","end":"E"}, "bullet_pool": ["IBM Bullet 1 Drove $34M transformation", "IBM Bullet 2 Scaled Platform", "IBM3 Established strategic alliances generating $16M", "IBM4 Migrated risk models saving $4.2M"], "overview":"O2"}
        ],
         "education": [], "certifications_and_credentials": [], "strategic_and_technical_competencies": []
    }
    # Scaffold needs correct structure from HOP-2 for K.1 prompt context
    mock_enriched_scaffold = {
         "experience_sections": [
            {"company": "Unify Consulting", "overview":"O1", "bullets": [{"text": b, "provenance": "Verbatim"} for b in mock_master_resume["professional_experience"][0]["bullet_pool"]]},
            {"company": "IBM", "overview":"O2", "bullets": [{"text": b, "provenance": "Verbatim"} for b in mock_master_resume["professional_experience"][1]["bullet_pool"]]}
        ]
    }
    generator = ArtistGenerator(
        master_resume=copy.deepcopy(mock_master_resume),
        enriched_scaffold=mock_enriched_scaffold,
        job_description=job_description,
        thematic_analysis=mock_thematic_analysis_k1
    )
    # Mock the API call itself for unit testing the prompt/config
    mocker.patch.object(generator, '_call_gemini_api', return_value="Mocked LLM Summary - 7 sentences precisely.") # type: ignore # Simulate compliant output
    return generator

@pytest.fixture(scope="module") # Use module scope for efficiency
def master_resume_for_provenance() -> dict:
    """Provides a richer master resume fixture specifically for provenance tests."""
    # (Content is same as v9.98, structure matches MASTER_RESUME_JSON v12.80)
    return {
      "schema_version": "master_resume_v2.15", # Match v12.80
      "owner": { "name": "Test User", "headline": "H", "contact": { "phone": "1", "email": "a@b.c", "linkedin": "l" } },
      "professional_experience": [
        {
          "company": "Unify Consulting", "location": "FL", "title": "Chief AI Officer", "dates": { "start": "Feb 2023", "end": "Present" },
          "overview": "Led enterprise generative AI...", # ~25 words
          "bullet_pool": [ # ~15-20 words each, need enough for V+C+S=7
            "Designed context-engineering frameworks, improving generative AI accuracy by 33%.",
            "Architected LLM deployment pipelines, cutting latency by 38%.",
            "Deployed agentic API frameworks, reducing manual intervention by 28%.",
            "Built senior engineering teams, reducing fraud detection response times by 42%.",
            "Recruited and scaled LLM engineering practice from 5 to 18 members.",
            "Led strategic partnerships with AWS, securing $18M in partnership revenue.",
            "Partnered with C-suite executives, generating $32M in client value.",
            "Drove strategic alliances with AWS and Snowflake, launching 8 client-specific pilots." # Added 8th bullet
          ]
        },
        {
          "company": "IBM", "location": "NY", "title": "Lead Client Partner", "dates": { "start": "Apr 2017", "end": "Oct 2022" },
          "overview": "Directed global digital transformation...", # ~20 words
          "bullet_pool": [ # ~15-20 words each, need enough for V+C+S=6
            "Integrated AI decision engines into risk platforms, raising client renewal rates by 24%.",
            "Launched machine learning risk analytics platform, improving predictive accuracy by 17%.",
            "Led multi-region regulatory modernization projects, reducing false positives by 29%.",
            "Introduced AI-infused reporting and compliance automation, improving response times by 53%.",
            "Delivered $34M transformation by migrating legacy risk systems to AWS.",
            "Migrated large-scale Monte Carlo risk models to cloud HPC, accelerating execution by 43%.",
            "Oversaw global migrations saving $3.8M.", # Added 7th bullet
            "Established strategic alliances generating $16M." # Added 8th bullet
          ]
        },
        { # Added TraderSense section
            "company": "TraderSense (Early-Stage / Stealth)", "location": "New York, NY", "title": "Chief Technology Officer",
            "dates": {"start": "April 2014", "end": "March 2017"},
            "overview": "As co-founder and CTO...", # ~15 words
            "highlights": [
                "Architected the company's proprietary automated trading platform.",
                "Led the 6-person engineering team and launched beta product."
            ]
        },
        {
          "company": "Ernst & Young", "location": "NY", "title": "Principal", "dates": { "start": "Oct 2009", "end": "Mar 2014" },
          "overview": "Managed an 18-person enterprise risk team...", # ~18 words
          "highlights": [ # Need 2 for C=2
            "Directed $16M stress testing transformation for Tier 1 banks, reducing findings by 38%.",
            "Advised insurance boards on Solvency II implementation, reducing provisions by 19%."
          ]
        },
        {
          "company": "Early Career Roles", "location": "PA", "title": "Actuarial Consultant", "dates": { "start": "Oct 2002", "end": "Sep 2009" },
          "overview": "Advanced from actuarial analyst...", # ~20 words
          "highlights": [ # Need 1 for C=1
            "Designed stochastic pricing models for variable annuities."
          ]
        }
      ],
      "education": [ { "degree": "MS", "institution": "Columbia" }, { "degree": "BA", "institution": "Brown" } ],
      "certifications_and_credentials": [ "Cert1", "Cert2" ],
      "strategic_and_technical_competencies": [ # ~15-25 words each, need V+C+S=6
        "â€¢ **Enterprise AI Platform Architecture:** Designed multi-cloud AI platforms.",
        "â€¢ **AI Governance & Risk Management:** Established enterprise governance frameworks.",
        "â€¢ **Production System Scalability & Reliability:** Built scalable AI systems.",
        "â€¢ **Executive Leadership & Strategic Transformation:** Unified senior leaders.",
        "â€¢ **Strategic Partnership & Alliance Development:** Forged alliances with providers.",
        "â€¢ **AI-Driven Operational Excellence & Innovation:** Embedded automation.",
        "â€¢ **Cloud Expertise:** Deep knowledge of AWS, Azure, GCP." # Added 7th
      ]
    }

@pytest.fixture
def enriched_scaffold_for_provenance(master_resume_for_provenance):
    """Provides the enriched scaffold corresponding to the provenance master resume."""
    # Based on v9.98, structure matches v12.80
    scaffold = {"experience_sections": []}
    for i, exp in enumerate(master_resume_for_provenance["professional_experience"]):
        bullets_key = "bullet_pool" if "bullet_pool" in exp else "highlights"
        scaffold["experience_sections"].append({
            "company": exp["company"],
            "bullets": [{"bullet_text": b, "provenance": BulletProvenance.Verbatim.value, "canonical_verbs": [], "quantified_metrics":[]} for b in exp.get(bullets_key, [])]
        })
    # Add other top-level keys if needed by the code being tested
    scaffold["header"] = {}
    scaffold["education"] = []
    scaffold["certifications"] = master_resume_for_provenance["certifications_and_credentials"] # Use correct key
    return scaffold

@pytest.fixture
def artist_generator_provenance(mocker, job_description, master_resume_for_provenance, enriched_scaffold_for_provenance, mock_thematic_analysis_base):
    """Provides an ArtistGenerator instance with mocks for provenance testing."""
    generator = ArtistGenerator(
        master_resume=copy.deepcopy(master_resume_for_provenance),
        enriched_scaffold=enriched_scaffold_for_provenance,
        job_description=job_description,
        thematic_analysis=mock_thematic_analysis_base # Use the base mock
    )
    # Mock the internal API call helper
    mocker.patch.object(generator, '_call_gemini_api', return_value="Mocked LLM Response") # type: ignore
    # No need to mock _rewrite_bullet_for_word_count as it's internal to _validate_and_potentially_rewrite_bullets, which is mocked in the test
    return generator

@pytest.fixture
def preflight_validator_instance(mocker):
    """Fixture for PreFlightValidator with a minimal master resume."""
    minimal_master_resume = {
        "schema_version": "test_v1",
        "owner": { "name": "Test User", "contact": { "email": "test@example.com", "phone": "123-456-7890", "linkedin": "linkedin.com/in/test" } },
        "professional_experience": [], "education": [], "certifications_and_credentials": [], "strategic_and_technical_competencies": []
    }
    validator = PreFlightValidator(master_resume=minimal_master_resume)
    # Mock the duplicate detector's similarity calculation if needed
    # The dup_detector is now on the ValidationContext, so we don't mock it here.
    return validator

@pytest.fixture
def mock_staging_buffer_fixture(mocker):
    """Fixture providing a mock ImmutableStagingBuffer and its underlying data dict."""
    buffer = mocker.MagicMock(spec=ImmutableStagingBuffer)
    buffer_data = {}
    is_locked_state = False # Track lock state

    # Define side effects using closures
    def get_side_effect(key, default=None): return buffer_data.get(key, default)
    def set_side_effect(key, value):
        if is_locked_state: raise StagingBufferError("Buffer locked") # Simulate error if locked
        buffer_data[key] = value
    def data_property(): return copy.deepcopy(buffer_data) # Return a copy
    def lock_side_effect(): nonlocal is_locked_state; is_locked_state = True
    def is_locked_side_effect(): return is_locked_state

    buffer.get.side_effect = get_side_effect
    buffer.set.side_effect = set_side_effect
    type(buffer).data = mocker.PropertyMock(side_effect=data_property)
    buffer.lock.side_effect = lock_side_effect
    buffer.is_locked.side_effect = is_locked_side_effect
    return buffer, buffer_data


# --- Test Functions ---

# Use the instance fixture directly
def test_golden_e2e_workflow(orchestrator_instance: WorkflowOrchestrator, job_description: str):
    """
    "Golden" E2E test: Validates workflow success and output artifact integrity for v12.80.
    Checks new QA structure. Uses updated word counter. Checks stateful retry metadata.
    """
    # Use a unique name for test artifacts
    run_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    COMPANY_NAME = f"DataDog_Golden_{run_timestamp}"
    JOB_TITLE = "Director_Tech_Alliances" # Use title from JD fixture

    # Execute the workflow
    result = orchestrator_instance.execute_workflow(job_description=job_description, company_name=COMPANY_NAME, job_title=JOB_TITLE)

    # 1. Validate Workflow Success & File Paths
    assert result.get('status') == 'SUCCESS', f"Workflow failed with status: {result.get('status')}, Reason: {result.get('reason', result.get('error', 'N/A'))}" # type: ignore
    assert result.get('gate_decision') == GateDecision.PROCEED.value
    file_paths = result.get('file_paths', {})
    assert isinstance(file_paths, dict)
    assert len(file_paths) == 5, f"Expected 5 file paths, but found {len(file_paths)}: {list(file_paths.keys())}"
    expected_keys = ["resume_md", "skills", "cover_letter", "qa_report", "app_tracker"]
    assert all(key in file_paths for key in expected_keys), f"File paths dict missing one of {expected_keys}"
    assert all(COMPANY_NAME in path for path in file_paths.values()), "Company name missing from artifact paths."

    # 2. Validate Resume Content (Formatting remains mostly the same as v9.98)
    resume_content = result.get('resume_md_content', '')
    assert resume_content, "Resume content is empty."
    assert "Amit Ayer" in resume_content, "Candidate name missing from resume."

    # --- Formatting Assertions (Largely unchanged, verify key points) ---
    assert re.search(r"^## Amit Ayer\n\n", resume_content), "Name not H2 or not separated by double newline."
    headline_match = re.search(r"## Amit Ayer\n\n(.*?)\n\n", resume_content, re.DOTALL)
    assert headline_match, "Could not extract headline or spacing issue."
    headline = headline_match.group(1).strip()
    assert "\n" not in headline, "Headline contains unexpected newline."
    contact_match = re.search(re.escape(headline) + r"\n\n(.*?)\n\n## EXECUTIVE SUMMARY", resume_content, re.DOTALL)
    assert contact_match, "Contact info section/spacing incorrect."
    assert "\n## EXECUTIVE SUMMARY\n\n" in resume_content
    assert "\n## PROFESSIONAL EXPERIENCE\n\n" in resume_content
    assert "\n## EDUCATION\n\n" in resume_content
    assert "\n## CERTIFICATIONS & CREDENTIALS\n\n" in resume_content
    assert "\n## STRATEGIC & TECHNICAL COMPETENCIES\n\n" in resume_content
    unify_header_match = re.search(r"(\*\*Unify Consulting.*?Boca Raton, FL\*\*)\n\n(\*\*Chief AI Officer.*?Present\*\*)", resume_content, re.DOTALL)
    assert unify_header_match, "Unify experience header bolding or line break failed."
    ibm_section_start = resume_content.find("\n**IBM | New York, NY**")
    unify_section_text = resume_content[unify_header_match.end():ibm_section_start]
    assert re.search(r"\n\* .*?\n\* ", unify_section_text, re.DOTALL), "Unify bullets (* ) or spacing failed."
    assert not re.search(r"\n\n\* ", unify_section_text), "Double newline before Unify bullet."
    assert re.search(r"\n\* [^\n]+\n\n\*\*IBM", resume_content, re.DOTALL), "Missing double newline after Unify bullets."
    edu_section_match = re.search(r"## EDUCATION\n\n(.*?)\n\n## CERTIFICATIONS", resume_content, re.DOTALL)
    assert edu_section_match and "*" not in edu_section_match.group(1).strip() and "\n\n" not in edu_section_match.group(1).strip()
    cert_section_match = re.search(r"## CERTIFICATIONS & CREDENTIALS\n\n(.*?)\n\n## STRATEGIC", resume_content, re.DOTALL)
    assert cert_section_match and "*" not in cert_section_match.group(1).strip() and "\n\n" not in cert_section_match.group(1).strip()
    comp_section_match = re.search(r"## STRATEGIC & TECHNICAL COMPETENCIES\n\n(.*?)(?:\Z)", resume_content, re.DOTALL)
    assert comp_section_match and comp_section_match.group(1).strip().startswith("* ") and "\n* " in comp_section_match.group(1)
    # --- End Formatting Assertions ---

    # <<< MODIFICATION: Use constraints and ms_word_style counter >>>
    constraints = ContentConstraintsConfig()
    word_count = count_words_ms_word_style(resume_content) # Use correct counter
    assert constraints.TOTAL_WORD_COUNT_MIN <= word_count <= constraints.TOTAL_WORD_COUNT_MAX, \
        f"Resume word count ({word_count}) out of config range {constraints.TOTAL_WORD_COUNT_MIN}-{constraints.TOTAL_WORD_COUNT_MAX}."

    # Re-check headline extraction and validation using constraints
    assert headline, "Headline extraction failed."
    assert "Alliances" in headline or "Partnerships" in headline or "GTM" in headline, "Headline lacks target keywords."
    assert not any(title in headline.lower() for title in ['vp ', 'director', 'chief', 'manager']), "Headline contains forbidden titles."
    assert "," not in headline, "Headline contains commas."
    headline_word_count = count_words_ms_word_style(headline) # Use correct counter
    assert constraints.HEADLINE_WORD_COUNT_MIN <= headline_word_count <= constraints.HEADLINE_WORD_COUNT_MAX, \
        f"Headline word count ({headline_word_count}) out of config range {constraints.HEADLINE_WORD_COUNT_MIN}-{constraints.HEADLINE_WORD_COUNT_MAX}."


    # 3. Validate Skills List
    skills_content = result.get('skills_content', '')
    assert skills_content, "Skills list is empty."
    skills = [s.replace("â€¢", "").strip() for s in skills_content.split('\n\n') if s.strip()]
    assert len(skills) == 12, f"Expected exactly 12 skills, found {len(skills)}: {skills}" # v12.x enforces exactly 12
    assert not any("[Warning:" in s for s in skills_content.split('\n\n')), "Malformed skills found."
    for skill in skills:
        assert 1 <= count_words_ms_word_style(skill) <= 3, f"Skill '{skill}' is not 1-3 words."

    # 4. Validate Cover Letter
    cover_letter_content = result.get('cover_letter_content', '')
    assert cover_letter_content, "Cover letter is empty."
    assert "Alliances" in cover_letter_content or "Partnerships" in cover_letter_content or "GTM" in cover_letter_content, "Cover letter lacks target keywords."
    owner_info = MASTER_RESUME_JSON['owner']
    expected_signature_multiline = COVER_LETTER_SIGNATURE_TEMPLATE.format(
        name=owner_info.get('name', ''),
        email=owner_info.get('contact', {}).get('email', ''),
        phone=owner_info.get('contact', {}).get('phone', ''),
        linkedin=owner_info.get('contact', {}).get('linkedin', '')
    ).strip()
    assert cover_letter_content.strip().endswith(expected_signature_multiline), "Cover letter signature block mismatch or missing."
    sincerely_pos = cover_letter_content.rfind("Sincerely,")
    assert sincerely_pos != -1, "Could not find 'Sincerely,' in cover letter."
    signature_part_rendered = cover_letter_content[sincerely_pos:]
    assert '\n' in signature_part_rendered[len("Sincerely,"):].strip(), "Cover letter signature is not rendering multi-line."

    # 5. Validate QA Report Structure (Updated for v12.80 - removed sections 7, 8)
    qa_report_text = result.get('qa_report_content', '') # Use content key
    assert qa_report_text, "QA report is empty."
    assert f"RESUME QA REPORT (v{orchestrator_instance.__class__.__module__}.__version__)" not in qa_report_text, f"QA report version mismatch. Expected v{__version__}."
    assert "1. SIGNAL QUALITY" in qa_report_text
    assert "2. HOP-0 RAG SIGNAL FLOW MAP" in qa_report_text
    assert "3. HOP-BY-HOP EXECUTION SUMMARY" in qa_report_text
    assert "4. WORD COUNT & DISTRIBUTION COMPLIANCE" in qa_report_text
    assert "5. BULLET PROVENANCE & WORD COUNT" in qa_report_text # Still exists, but logic removed average check
    assert "6. CONTENT AUTHENTICITY" in qa_report_text
    # --- START REFACTOR: Update QA section numbering ---
    assert "7. EXECUTIVE SUMMARY VS. SECTION CONTENT SIMILARITY" in qa_report_text
    assert "8. PAIRWISE BULLET SIMILARITY (Deduplication)" in qa_report_text
    assert "9. PIPELINE HEALTH" in qa_report_text
    assert "10. STRUCTURAL VALIDATION" in qa_report_text
    assert "11. PRODUCTION READINESS" in qa_report_text
    assert "12. COVER LETTER QA" in qa_report_text
    assert "13. JD ENFORCEMENT VALIDATION" in qa_report_text
    assert "14. FORMATTING OF OUTPUTS" in qa_report_text
    # --- END REFACTOR ---

    assert "â–ˆ" in qa_report_text, "QA Section 1 missing ASCII bar chart."
    # Check table 12 (was 14) uses fenced pre-formatted text
    final_format_section_match = re.search(r"12\. FORMATTING OF OUTPUTS\n```markdown(.*?)```", qa_report_text, re.DOTALL)
    assert final_format_section_match, "Cannot find fenced Formatting section (Table 12)."
    final_format_table = final_format_section_match.group(1)
    # Check for pre-formatted style (spaces, not pipes) and specific checks
    assert "Artifact      " in final_format_table, "Table 12 doesn't look like pre-formatted text."
    assert "| " not in final_format_table, "QA Table 12 should not use Markdown '|' syntax."
    assert "VG_RESUME_HEADER_H2         PASS" in final_format_table, "Table 12 missing header H2 check or failed unexpectedly." # Check PASS status
    assert "VG_COMPETENCIES_FORMATTING  PASS" in final_format_table, "Table 14 missing competencies format check or failed unexpectedly."

    # Check HOP-3 metadata in Hop Summary (Table 3)
    hop_summary_match = re.search(r"3\. HOP-BY-HOP EXECUTION SUMMARY\n```markdown(.*?)```", qa_report_text, re.DOTALL)
    assert hop_summary_match, "Cannot find fenced Hop Summary section (Table 3)."
    hop_summary_table = hop_summary_match.group(1)
    assert "HOP-3   Artist Generation (final attempt" in hop_summary_table, "HOP-3 entry missing or format changed."

    # 6. Validate App Tracker (No changes needed)
    app_tracker_content = result.get('app_tracker_content', '{}')
    assert app_tracker_content and app_tracker_content != '{}', "App tracker content is empty."
    try:
        app_tracker_data = json.loads(app_tracker_content)
    except json.JSONDecodeError:
        pytest.fail("App tracker content is not valid JSON.")
    assert app_tracker_data.get("Company") == COMPANY_NAME, "App tracker company name mismatch."
    assert app_tracker_data.get("Job Title") == JOB_TITLE, "App tracker job title mismatch."
    assert app_tracker_data.get("Pipeline Status") == "Applied", "App tracker initial status incorrect."
    assert len(app_tracker_data) == 54, f"App tracker has {len(app_tracker_data)} fields, expected 54."
    date_str = app_tracker_data.get("Application Date")
    assert date_str, "App tracker missing application date."
    try:
        datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        pytest.fail(f"App tracker application date '{date_str}' is not in MM/DD/YYYY format.")

    # 7. Check HOP-3 metadata for stateful retry
    hop3_checkpoint = next((c for c in result.get('hop_checkpoints', []) if c['hop_id'] == 'HOP-3'), None)
    assert hop3_checkpoint is not None, "HOP-3 checkpoint missing."
    assert 'metadata' in hop3_checkpoint, "HOP-3 metadata missing."
    assert 'attempts_made' in hop3_checkpoint['metadata'], "HOP-3 metadata missing 'attempts_made'."
    assert hop3_checkpoint['metadata']['attempts_made'] >= 1, "HOP-3 attempts should be >= 1."
    assert 'final_temperatures' in hop3_checkpoint['metadata'], "HOP-3 metadata missing 'final_temperatures'."
    # Check if final_temperatures is a dictionary (could be empty if only 1 attempt)
    assert isinstance(hop3_checkpoint['metadata']['final_temperatures'], dict), "'final_temperatures' is not a dictionary."

    print(f"\nâœ“ E2E Workflow Test Passed (v13.10): All assertions met.")


# --- Unit Tests for Individual Hops/Components ---

# <<< REMOVED test_generate_artist_output_data_driven as it tested obsolete internals >>>

@pytest.mark.parametrize("hop_config", [
    {
        "name": "HOP-0", "method_name": "_execute_hop_0_jd_analysis",
        "mock_target": "Resume_Generation_v14_53.EnhancedJobDescriptionAnalyzer",
        "mock_method": "analyze",
        "mock_return": (mocker.MagicMock(spec=ThematicAnalysis, signal_quality_score=0.88), 5), # Return tuple
        "expected_output_data": {"signal_score": 0.88},
        "expected_metadata": {"gemini_api_calls": 5},
        "method_args": ["job_description"],
        "allow_warnings": False
    },
    {
        "name": "HOP-1", "method_name": "_execute_hop_1_clerk_extraction",
        "mock_target": "Resume_Generation_v14_53.ClerkExtractor",
        "mock_method": "extract",
        "mock_return": ({"experience_sections": [{"bullets": [{}, {}]}]}, [mocker.MagicMock(spec=ValidationResult)]),
        "expected_output_data": {"bullets_extracted": 2},
        "expected_metadata": {},
        "method_args": [],
        "allow_warnings": True
    },
    {
        "name": "HOP-2", "method_name": "_execute_hop_2_enrichment",
        "mock_target": "Resume_Generation_v14_53.DataEnricher",
        "mock_method": "enrich",
        "mock_return": ({"key": "enriched"}, [mocker.MagicMock(spec=ValidationResult)]),
        "expected_output_data": {"key": "enriched"},
        "expected_metadata": {},
        "method_args": [{"key": "extracted"}, "mock_thematic_analysis_base"],
        "allow_warnings": True
    },
    {
        "name": "HOP-5", "method_name": "_execute_hop_5_validation",
        "mock_target": "Resume_Generation_v14_53.PreFlightValidator",
        "mock_method": "validate",
        "mock_return": ([mocker.MagicMock(spec=ValidationResult, passed=True)], True, set()),
        "expected_output_data": {"all_rules_checked": 3, "all_passed": True}, # Mocked rule count
        "expected_metadata": {},
        "method_args": ["mock_staging_buffer", "mock_thematic_analysis_base", "job_description"],
        "allow_warnings": True
    }
])
def test_orchestrator_hops(orchestrator_instance, mocker, job_description, mock_thematic_analysis_base, hop_config):
    """Consolidated unit test for individual, non-retry workflow hops."""
    # 1. Setup Mocks
    mock_component_instance = mocker.MagicMock()
    getattr(mock_component_instance, hop_config["mock_method"]).return_value = hop_config["mock_return"]
    mock_component_class = mocker.patch(hop_config["mock_target"], return_value=mock_component_instance)

    # Mock checkpointing
    mock_checkpoint = mocker.MagicMock(spec=HopCheckpoint, metadata={}, timestamp_start="")
    mock_create_checkpoint = mocker.patch.object(orchestrator_instance, '_create_checkpoint', return_value=mock_checkpoint)
    mock_check_hop_status = mocker.patch.object(orchestrator_instance, '_check_hop_status')
    orchestrator_instance.hop_checkpoints = []

    # Special setup for HOP-5 validator mock
    if hop_config["name"] == "HOP-5":
        mock_component_instance.engine = mocker.MagicMock()
        mock_component_instance.engine.rules = [1, 2, 3] # Simulate 3 rules for metadata check

    # 2. Prepare Arguments
    arg_map = {
        "job_description": job_description,
        "mock_thematic_analysis_base": mock_thematic_analysis_base,
        "mock_staging_buffer": mocker.MagicMock(spec=ImmutableStagingBuffer)
    }
    method_to_call = getattr(orchestrator_instance, hop_config["method_name"])
    call_args = [arg_map.get(arg, arg) for arg in hop_config["method_args"]]

    # 3. Execute
    result = method_to_call(*call_args)

    # 4. Assertions
    # Assert component was called
    getattr(mock_component_instance, hop_config["mock_method"]).assert_called_once()
    
    # Assert checkpoint was created correctly
    mock_create_checkpoint.assert_called_once()
    cp_args, cp_kwargs = mock_create_checkpoint.call_args
    assert cp_args[0] == hop_config["name"]
    assert cp_args[3] == hop_config["expected_output_data"]
    assert cp_kwargs.get("metadata", {}) == hop_config["expected_metadata"]
    assert orchestrator_instance.hop_checkpoints == [mock_checkpoint]

    # Assert status check was called
    mock_check_hop_status.assert_called_once()
    status_kwargs = mock_check_hop_status.call_args.kwargs
    assert status_kwargs.get('allow_warnings') == hop_config['allow_warnings']

    print(f"\nâœ“ Parameterized test passed for: {hop_config['name']}")

# --- HOP-3 Stateful Retry Logic Tests (REWORKED for v12.80) ---

@pytest.fixture
def mock_artist_for_retry(mocker) -> Tuple[ArtistGenerator, Any]:
    """Provides a mocked ArtistGenerator for retry tests."""
    mock_artist = mocker.MagicMock(spec=ArtistGenerator) # type: ignore
    mock_artist_class = mocker.patch('Resume_Generation_v14_53.ArtistGenerator', return_value=mock_artist)
    return mock_artist, mock_artist_class

@pytest.fixture
def mock_validator_for_retry(mocker) -> Tuple[PreFlightValidator, Any]:
    """Provides a mocked PreFlightValidator for retry tests."""
    mock_validator = mocker.MagicMock(spec=PreFlightValidator) # type: ignore
    mock_validator_class = mocker.patch('Resume_Generation_v14_53.PreFlightValidator', return_value=mock_validator)
    # Mock the engine rule count needed by HOP-5 check
    mock_validator.engine = mocker.MagicMock()
    mock_validator.engine.rules = [1, 2, 3] # Simulate having 3 rules
    return mock_validator, mock_validator_class

def test_hop_3_stateful_retry_succeeds_on_third_attempt(
    orchestrator_instance: WorkflowOrchestrator, job_description: str,
    mock_thematic_analysis_base, mocker,
    mock_artist_for_retry: Tuple[ArtistGenerator, Any],
    mock_validator_for_retry: Tuple[PreFlightValidator, Any]
):
    """Tests HOP-3 stateful retry: Should succeed on the 3rd attempt."""
    mock_artist, _ = mock_artist_for_retry
    mock_validator, _ = mock_validator_for_retry
    mock_enriched_scaffold = {"key": "value", "experience_sections": []}


    # Sections needing generation
    section_k1 = ResumeSection.K1_EXECUTIVE_SUMMARY
    section_k5b = ResumeSection.K5_UNIFY_BULLETS

    # Define side effects for generate:
    # Attempt 1 (T=1.0): Returns content for K1, K5B. Validation will fail K1.
    # Attempt 2 (T=0.8): Returns new content for K1. Validation will fail K1 again.
    # Attempt 3 (T=0.6): Returns new content for K1. Validation will pass K1.
    mock_artist.generate.side_effect = [
        # Attempt 1: Generate K1, K5B. Returns (content, results, calls)
        ({section_k1.value: "k1_fail_1", section_k5b.value: "k5b_pass"}, [ValidationResult("Gen1", True, ValidationSeverity.INFO, "")], 2),
        # Attempt 2: Generate only K1.
        ({section_k1.value: "k1_fail_2"}, [ValidationResult("Gen2", True, ValidationSeverity.INFO, "")], 1),
        # Attempt 3: Generate only K1.
        ({section_k1.value: "k1_pass"}, [ValidationResult("Gen3", True, ValidationSeverity.INFO, "")], 1)
    ]

    # Define side effects for validate:
    # Attempt 1: K5B passes, K1 fails (returns failed_sections={section_k1})
    # Attempt 2: K1 fails again (returns failed_sections={section_k1})
    # Attempt 3: K1 passes (returns failed_sections=set())
    fail_k1_result = ValidationResult("VG_SENTENCE_COUNT_K1", False, ValidationSeverity.CRITICAL, "K1 Fail")
    pass_k5b_result = ValidationResult("VG_PROVENANCE_SPLIT_CHECK", True, ValidationSeverity.INFO, "K5B Pass")
    pass_k1_result = ValidationResult("VG_SENTENCE_COUNT_K1", True, ValidationSeverity.INFO, "K1 Pass")

    mock_validator.validate.side_effect = [
        # Attempt 1 Validation Result: K1 fails
        ([fail_k1_result, pass_k5b_result], False, {section_k1}),
        # Attempt 2 Validation Result: K1 fails
        ([fail_k1_result, pass_k5b_result], False, {section_k1}),
        # Attempt 3 Validation Result: All pass
        ([pass_k1_result, pass_k5b_result], True, set())
    ]

    # Mock checkpointing and status check
    mock_checkpoint = mocker.MagicMock(spec=HopCheckpoint, metadata={}, timestamp_start="", status=HopStatus.PASS) # Assume success
    mocker.patch.object(orchestrator_instance, '_create_checkpoint', return_value=mock_checkpoint)
    mocker.patch.object(orchestrator_instance, '_check_hop_status')
    orchestrator_instance.hop_checkpoints = []

    # Execute the hop
    final_output = orchestrator_instance._execute_hop_3_artist_generation(
        enriched_scaffold=mock_enriched_scaffold,
        job_description=job_description,
        thematic_analysis=mock_thematic_analysis_base
    )

    # Assertions
    assert mock_artist.generate.call_count == 3, "Artist.generate should be called 3 times."
    assert mock_validator.validate.call_count == 3, "Validator.validate should be called 3 times."

    # Check calls to artist.generate
    # Call 1: sections={K1, K5B}, temp=1.0
    call1_args, call1_kwargs = mock_artist.generate.call_args_list[0]
    assert call1_kwargs['sections_to_generate'] == {section_k1, section_k5b}
    assert call1_kwargs['temperature_overrides'] == {section_k1: 1.0, section_k5b: 1.0}
    # Call 2: sections={K1}, temp=0.8
    call2_args, call2_kwargs = mock_artist.generate.call_args_list[1]
    assert call2_kwargs['sections_to_generate'] == {section_k1}
    assert call2_kwargs['temperature_overrides'] == {section_k1: 0.8}
    # Call 3: sections={K1}, temp=0.6
    call3_args, call3_kwargs = mock_artist.generate.call_args_list[2]
    assert call3_kwargs['sections_to_generate'] == {section_k1}
    assert call3_kwargs['temperature_overrides'] == {section_k1: 0.6}

    # Check final output contains the correct versions
    assert final_output.get(section_k1.value) == "k1_pass" # From attempt 3
    assert final_output.get(section_k5b.value) == "k5b_pass" # From attempt 1

    orchestrator_instance._create_checkpoint.assert_called_once() # Called on final success
    # Check metadata in checkpoint
    _, cp_kwargs = orchestrator_instance._create_checkpoint.call_args
    assert cp_kwargs['metadata']['attempts_made'] == 3
    assert cp_kwargs['metadata']['gemini_api_calls'] == 4 # 2 (attempt 1) + 1 (attempt 2) + 1 (attempt 3)
    # Check final locked temps (no change here)
    assert cp_kwargs['metadata']['final_temperatures'] == {section_k1.name: 0.6, section_k5b.name: 1.0}

    orchestrator_instance._check_hop_status.assert_called_once_with(mock_checkpoint)
    # Check stored validation results are from the last successful run
    assert orchestrator_instance.validation_results == [pass_k1_result, pass_k5b_result]

    print("\nâœ“ HOP-3 Stateful Retry Logic Test Passed: Correctly retried and succeeded on attempt 3.")


def test_hop_3_stateful_retry_fails_after_all_attempts(
    orchestrator_instance: WorkflowOrchestrator, job_description: str,
    mock_thematic_analysis_base, mocker,
    mock_artist_for_retry: Tuple[ArtistGenerator, Any],
    mock_validator_for_retry: Tuple[PreFlightValidator, Any]
):
    """Tests HOP-3: Should raise HopExecutionError after 5 failed validation attempts."""
    mock_artist, _ = mock_artist_for_retry
    mock_validator, _ = mock_validator_for_retry
    mock_enriched_scaffold = {"key": "value", "experience_sections": []}
    max_attempts = 5 # Matches temperature schedule length

    section_k1 = ResumeSection.K1_EXECUTIVE_SUMMARY

    # Simulate generate always returning content for K1 (assume it tries each time)
    mock_artist.generate.side_effect = [
        # Return (content, results, calls)
        ({section_k1.value: f"k1_fail_{i}"}, [ValidationResult(f"Gen{i}", True, ValidationSeverity.INFO, "")], 1) for i in range(1, max_attempts + 1)
    ]

    # Simulate validate always failing K1
    fail_k1_result = ValidationResult("VG_SENTENCE_COUNT_K1", False, ValidationSeverity.CRITICAL, "K1 Persistent Fail")
    fail_validation_return = ([fail_k1_result], False, {section_k1}) # Always fail K1
    mock_validator.validate.side_effect = [fail_validation_return] * max_attempts

    # Mock checkpointing (should be called once at the end with failure status)
    mock_checkpoint = mocker.MagicMock(spec=HopCheckpoint, metadata={}, timestamp_start="", status=HopStatus.FAIL, error_message="Validation failed") # Simulate failure checkpoint
    mocker.patch.object(orchestrator_instance, '_create_checkpoint', return_value=mock_checkpoint)
    mocker.patch.object(orchestrator_instance, '_check_hop_status') # Don't check status during the test itself
    orchestrator_instance.validation_results = [] # Reset

    # Execute the hop and expect an exception
    expected_error_msg = f"HOP-3 failed: Content validation failed after {max_attempts} attempts."
    with pytest.raises(HopExecutionError, match=re.escape(expected_error_msg)):
        orchestrator_instance._execute_hop_3_artist_generation(
            enriched_scaffold=mock_enriched_scaffold,
            job_description=job_description,
            thematic_analysis=mock_thematic_analysis_base
        )

    # Assertions
    assert mock_artist.generate.call_count == max_attempts, f"Artist.generate should be called {max_attempts} times."
    assert mock_validator.validate.call_count == max_attempts, f"Validator.validate should be called {max_attempts} times."
    # Check sections_to_generate passed to generate (should always be {section_k1} after first attempt)
    assert mock_artist.generate.call_args_list[0].kwargs['sections_to_generate'] == {section_k1} # Initial depends on config, assume K1 is only LLM section for simplicity mock
    for i in range(1, max_attempts):
        assert mock_artist.generate.call_args_list[i].kwargs['sections_to_generate'] == {section_k1}

    # Check checkpoint was created once at the end, capturing the failure
    orchestrator_instance._create_checkpoint.assert_called_once()
    _, cp_kwargs = orchestrator_instance._create_checkpoint.call_args
    assert cp_kwargs['metadata']['attempts_made'] == max_attempts
    assert cp_kwargs['metadata']['gemini_api_calls'] == max_attempts # 1 call per attempt
    assert cp_kwargs['metadata']['final_temperatures'] == {} # No sections locked
    # Check stored validation results are from the *last* failed run
    assert orchestrator_instance.validation_results == [fail_k1_result]

    print(f"\nâœ“ HOP-3 Stateful Retry Failure Test Passed: Correctly raised HopExecutionError after {max_attempts} failed attempts.")


@pytest.mark.parametrize("gate_decision, gate_reason, should_raise", [
    (GateDecision.PROCEED, "All validations passed", False),
    (GateDecision.HALT, "HALT: Critical failure detected: RULE_X", True),
    (GateDecision.HALT, "HALT: High severity failure detected: RULE_Y", True),
])
def test_execute_hop_6_gate_decision(orchestrator_instance: WorkflowOrchestrator, mocker, gate_decision, gate_reason, should_raise):
    """Unit test for _execute_hop_6_gate_decision."""
    mock_hop5_results = [mocker.MagicMock(spec=ValidationResult)] # Input results
    mock_gate_engine_instance = mocker.MagicMock()
    mock_gate_engine_instance.decide.return_value = (gate_decision, gate_reason)
    mock_gate_engine_class = mocker.patch('Resume_Generation_v14_53.GateDecisionEngine', return_value=mock_gate_engine_instance)

    mock_checkpoint = mocker.MagicMock(spec=HopCheckpoint, metadata={}, timestamp_start="")
    mock_create_checkpoint = mocker.patch.object(orchestrator_instance, '_create_checkpoint', return_value=mock_checkpoint)
    orchestrator_instance.hop_checkpoints = []

    if should_raise:
        # Expect HopExecutionError on HALT, check message includes reason
        with pytest.raises(HopExecutionError, match=f"HALT decision at HOP-6: {re.escape(gate_reason)}"):
             orchestrator_instance._execute_hop_6_gate_decision(mock_hop5_results)
    else:
        result_decision = orchestrator_instance._execute_hop_6_gate_decision(mock_hop5_results)
        assert result_decision == gate_decision

    mock_gate_engine_class.assert_called_once()
    mock_gate_engine_instance.decide.assert_called_once_with(mock_hop5_results)
    mock_create_checkpoint.assert_called_once()
    args, kwargs = mock_create_checkpoint.call_args
    assert args[0] == "HOP-6"
    assert args[3] == {"decision": gate_decision.value, "reason": gate_reason}

    print(f"\nâœ“ HOP-6 Gate Decision unit test passed for {gate_decision.name} scenario.")


# --- Reasoning Config and Helper Tests --- (Minor Updates)

@pytest.mark.parametrize("params, expected_substrings", [
    # Test HIGH intensity
    ({"cot": 5, "tot_b": 5, "tot_d": 5, "reflexion": True, "max_loops": 3, "reasoning_level": "VERY_HIGH", "intensity_score": 35.0, "sc":8}, # sc clamped to 8
     ["MANDATORY: Explore at least 5", "MANDATORY: evaluate 5", "MANDATORY: depth must be 5+", "MANDATORY: Review your answer 3 times"]),
    # Test MODERATE intensity
    ({"cot": 4, "tot_b": 4, "tot_d": 4, "reflexion": True, "max_loops": 2, "reasoning_level": "HIGH", "intensity_score": 28.0, "sc":8}, # sc clamped to 8
     ["Explore 4 different", "Explore 4 decision", "Provide 4-level deep", "Review your answer 2 times"]),
    # Test LOW intensity, no reflexion (updated for v13.10 where reflexion is always True for this config)
    ({"cot": 2, "tot_b": 2, "tot_d": 2, "reflexion": False, "max_loops": 1, "reasoning_level": "LOW", "intensity_score": 14.0, "sc":5},
     ["Consider multiple reasoning", "Consider multiple decision", "Structure reasoning with clear"]), # Reflexion directive should be absent
])
def test_build_reasoning_prompt_addendum(params, expected_substrings):
    """Unit test: _build_reasoning_prompt_addendum generates correct directives."""
    # <<< MODIFICATION: Updated module path >>>
    result = _build_reasoning_prompt_addendum(params) # Use directly from imported module
    assert f"(Configuration Level: {params['reasoning_level']}" in result
    assert f"Intensity: {params['intensity_score']:.1f}" in result
    for substring in expected_substrings:
        assert substring in result, f"Expected substring '{substring}' not found in addendum."
    if not params["reflexion"]:
        assert "Review your answer" not in result, "Reflexion directive included when reflexion=False."
    print(f"\nâœ“ _build_reasoning_prompt_addendum passed for level: {params['reasoning_level']}")


def test_reasoning_config_to_api_params_integration(mocker):
    """Integration test: reasoning_config_to_api_params calls helpers correctly (v12.80)."""
    # Mock helper functions
    mock_normalized_params = {"cot": 4, "tot_b": 3, "tot_d": 3, "sc": 8, "reflexion": True, "max_loops": 2} # sc clamped to 8
    mocker.patch('Resume_Generation_v14_53._get_normalized_reasoning_params', return_value=mock_normalized_params)
    mocker.patch('Resume_Generation_v14_53._calculate_reasoning_intensity', return_value=(26.4, "HIGH"))
    mocker.patch('Resume_Generation_v14_53._get_generation_temperature', return_value=0.9) # Expect high temp
    mocker.patch('Resume_Generation_v14_53._build_reasoning_prompt_addendum', return_value="Mock Addendum Text")
    # Mock RAGConfig max_tokens directly
    mocker.patch('Resume_Generation_v14_53.RAGConfig.max_tokens', 30000, create=True) # Mock the class attribute
    # Mock the genai GenerationConfig class
    mock_gen_config_instance = mocker.MagicMock()
    mock_gen_config_class = mocker.patch('Resume_Generation_v14_53.genai.GenerationConfig', return_value=mock_gen_config_instance)

    sample_config = ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG # Example config
    result = reasoning_config_to_api_params(sample_config)

    # Assertions
    _get_normalized_reasoning_params.assert_called_once_with(sample_config)
    _calculate_reasoning_intensity.assert_called_once_with(mock_normalized_params)
    _get_generation_temperature.assert_called_once()
    expected_params_for_addendum = {**mock_normalized_params, 'intensity_score': 26.4, 'reasoning_level': "HIGH"}
    _build_reasoning_prompt_addendum.assert_called_once_with(expected_params_for_addendum)

    # Verify GenerationConfig instantiation uses mocked RAGConfig.max_tokens
    mock_gen_config_class.assert_called_once_with(temperature=0.9, max_output_tokens=30000)

    assert 'generation_config' in result
    assert result['generation_config'] == mock_gen_config_instance
    assert result['system_prompt_addendum'] == "Mock Addendum Text"
    assert result['intensity_score'] == 26.4
    assert result['sc'] == mock_normalized_params['sc'] # Should be clamped value (8)
    print("\nâœ“ reasoning_config_to_api_params integration test passed (v13.10).")


# <<< REMOVED test_allocate_tokens_from_depth as it's no longer used >>>


# --- CONSOLIDATED WORKFLOW FAILURE/HALT TESTS ---

# Mock Failure Setup Functions (Update paths to v12.80)
# Ensure these functions align with the new stateful retry logic in HOP-3

def setup_mock_word_count_failure(mocker, orchestrator_instance, mock_thematic_analysis_base):
    """Mocks Artist output causing total word count failure (v12.80)."""
    very_long_string = "word " * 1500
    mock_output = {section.value: "minimal" for section in ResumeSection}
    mock_output[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = very_long_string
    mock_output[ResumeSection.K0_HEADLINE.value] = "Word word word word word word word word" # Pass headline
    mock_output[ResumeSection.K13_COVER_LETTER.value] = "word "*150 + COVER_LETTER_SIGNATURE_TEMPLATE.format(name='N',email='E',phone='P',linkedin='L')

    # Simulate Artist.generate succeeding but returning bad content. Returns (content, results, calls)
    mocker.patch('Resume_Generation_v14_53.ArtistGenerator.generate', return_value=(mock_output, [ValidationResult("Gen", True, ValidationSeverity.INFO, "")], 1)) # type: ignore
    # Let sanitization pass # type: ignore
    mocker.patch('Resume_Generation_v14_53.TextSanitizer.sanitize_buffer', side_effect=lambda buffer: ([], buffer.data)) # type: ignore
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', return_value=mock_thematic_analysis_base)

def setup_mock_low_relevance_failure(mocker, orchestrator_instance, mock_thematic_analysis_base):
    """Mocks Artist output with low relevance cover letter (v12.80)."""
    mock_output = {section.value: "word "*20 for section in ResumeSection}
    mock_output[ResumeSection.K13_COVER_LETTER.value] = "Completely irrelevant text."
    mock_output[ResumeSection.K0_HEADLINE.value] = "Word word word word word word word word"
    mock_output[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = "word "*130
    # Add passing signature
    owner_info = MASTER_RESUME_JSON['owner']
    signature = COVER_LETTER_SIGNATURE_TEMPLATE.format(
        name=owner_info.get('name', ''), email=owner_info.get('contact', {}).get('email', ''),
        phone=owner_info.get('contact', {}).get('phone', ''), linkedin=owner_info.get('contact', {}).get('linkedin', '')
    ).strip()
    mock_output[ResumeSection.K13_COVER_LETTER.value] += f"\n\nSincerely,\n\n{signature}" # Add closing

    mocker.patch('Resume_Generation_v14_53.ArtistGenerator.generate', return_value=(mock_output, [ValidationResult("Gen", True, ValidationSeverity.INFO, "")], 1)) # type: ignore
    mocker.patch('Resume_Generation_v14_53.TextSanitizer.sanitize_buffer', side_effect=lambda buffer: ([], buffer.data)) # type: ignore
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', return_value=mock_thematic_analysis_base)
    # Mock similarity calculation on the context's detector
    mocker.patch('Resume_Generation_v14_53.ValidationContext.cover_letter_jd_similarity', new_callable=mocker.PropertyMock, return_value=0.1)


def setup_mock_placeholder_failure(mocker, orchestrator_instance, mock_thematic_analysis_base):
    """Mocks Artist output containing placeholder text (v12.80)."""
    placeholder_text = "[Placeholder for K.1]"
    mock_output = {section.value: "word "*20 for section in ResumeSection}
    mock_output[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = placeholder_text
    mock_output[ResumeSection.K0_HEADLINE.value] = "Word word word word word word word word"
    mock_output[ResumeSection.K13_COVER_LETTER.value] = "word "*150 + COVER_LETTER_SIGNATURE_TEMPLATE.format(name='N',email='E',phone='P',linkedin='L')

    mocker.patch('Resume_Generation_v14_53.ArtistGenerator.generate', return_value=(mock_output, [ValidationResult("Gen", True, ValidationSeverity.INFO, "")], 1)) # type: ignore
    mocker.patch('Resume_Generation_v14_53.TextSanitizer.sanitize_buffer', side_effect=lambda buffer: ([], buffer.data)) # type: ignore
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', return_value=mock_thematic_analysis_base) # type: ignore

def setup_mock_rag_hop0_failure(mocker, orchestrator_instance):
    """Mocks HOP-0 to raise HopExecutionError."""
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', side_effect=HopExecutionError("Simulated RAG Failure in HOP-0"))

def setup_mock_artist_hop3_failure(mocker, orchestrator_instance, mock_thematic_analysis_base):
    """Mocks HOP-3 ArtistGenerator.generate to raise HopExecutionError immediately."""
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', return_value=mock_thematic_analysis_base)
    # Simulate generate itself failing (e.g., internal API call fails permanently) # type: ignore
    mocker.patch('Resume_Generation_v14_53.ArtistGenerator.generate', side_effect=HopExecutionError("Simulated LLM Failure in HOP-3"))

def setup_mock_no_api_key(mocker):
    """Simulates missing API key (v12.80)."""
    mocker.patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True)
    # Re-initialize orchestrator *after* removing key
    orchestrator_no_key = WorkflowOrchestrator(copy.deepcopy(MASTER_RESUME_JSON), test_mode=False) # Turn off test mode to trigger check
    # Mock the API call helpers to raise errors if somehow reached # type: ignore
    mocker.patch('Resume_Generation_v14_53.ArtistGenerator._call_gemini_api', side_effect=HopExecutionError("GEMINI_API_KEY not set")) # type: ignore
    mocker.patch('Resume_Generation_v14_53.EnhancedJobDescriptionAnalyzer._execute_pre_rag_analysis', side_effect=HopExecutionError("GEMINI_API_KEY not set")) # Mock pre-rag # type: ignore
    mocker.patch('Resume_Generation_v14_53.GeminiWebSearchClient.search_and_analyze', side_effect=HopExecutionError("GEMINI_API_KEY not set")) # Mock RAG # type: ignore
    return orchestrator_no_key

def setup_mock_missing_narrative(mocker, orchestrator_instance, mock_thematic_analysis_base):
    """Modifies mock ThematicAnalysis to lack narrative data (v12.80)."""
    mock_thematic_analysis_base.problem_solution_narratives = None
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', return_value=mock_thematic_analysis_base)
    # Ensure generate returns enough data to pass other checks
    mock_output = {section.value: "word "*20 for section in ResumeSection}
    mock_output[ResumeSection.K0_HEADLINE.value] = "Word word word word word word word word"
    mock_output[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = "word "*130
    mock_output[ResumeSection.K13_COVER_LETTER.value] = "word "*150 + COVER_LETTER_SIGNATURE_TEMPLATE.format(name='N',email='E',phone='P',linkedin='L')

    mocker.patch('Resume_Generation_v14_53.ArtistGenerator.generate', return_value=(mock_output, [ValidationResult("Gen", True, ValidationSeverity.INFO, "")], 1)) # type: ignore
    mocker.patch('Resume_Generation_v14_53.TextSanitizer.sanitize_buffer', side_effect=lambda buffer: ([], buffer.data)) # type: ignore

def setup_mock_hop0_malformed_json_failure(mocker, orchestrator_instance):
    """Mocks RAG in HOP-0 to return malformed JSON (v12.80)."""
    # Simulate the RAG client failing during JSON parsing (caught by HOP-0 executor)
    mocker.patch('Resume_Generation_v14_53.GeminiWebSearchClient.search_and_analyze', side_effect=ValueError("Simulated bad JSON")) # type: ignore
    # Patch the HOP-0 method to raise the correct error type
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', side_effect=HopExecutionError("HOP-0 failed: Simulated bad JSON"))

def setup_mock_hop3_missing_company_failure(mocker, orchestrator_instance, mock_thematic_analysis_base):
    """Creates orchestrator with corrupted master_resume missing 'Unify' (v12.80)."""
    corrupted_resume = copy.deepcopy(MASTER_RESUME_JSON)
    corrupted_resume['professional_experience'] = [
        exp for exp in corrupted_resume['professional_experience'] if 'Unify' not in exp['company']
    ]
    orchestrator_corrupted = WorkflowOrchestrator(corrupted_resume, test_mode=True)
    mocker.patch.object(orchestrator_corrupted, '_execute_hop_0_jd_analysis', return_value=mock_thematic_analysis_base)
    # The actual ArtistGenerator method called *inside* the stateful retry loop will fail
    return orchestrator_corrupted

def setup_mock_persistent_k1_failure(mocker, orchestrator_instance, mock_thematic_analysis_base):
    """Mocks Artist.generate to always return content failing K.1 validation (v12.80)."""
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', return_value=mock_thematic_analysis_base)

    def mock_generate_always_fail_k1(*args, **kwargs):
        sections_to_gen = kwargs.get('sections_to_generate', set())
        output = {}
        # Only generate output for requested sections
        if ResumeSection.K1_EXECUTIVE_SUMMARY in sections_to_gen:
             output[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = "Too short." # Always fail K.1 sentence count
        # Add *passing* content for other potential sections IF requested, to avoid unrelated failures
        if ResumeSection.K0_HEADLINE in sections_to_gen:
            output[ResumeSection.K0_HEADLINE.value] = "Headline has enough words now eight"
        if ResumeSection.K5_UNIFY_BULLETS in sections_to_gen:
            output[ResumeSection.K5_UNIFY_BULLETS.value] = [{"text":"word "*25, "provenance": "Verbatim"}] * 7
        # ... add other sections similarly if needed ...
        if ResumeSection.K13_COVER_LETTER in sections_to_gen:
            output[ResumeSection.K13_COVER_LETTER.value] = "word "*150 + COVER_LETTER_SIGNATURE_TEMPLATE.format(name='N',email='E',phone='P',linkedin='L')

        # Simulate generate itself succeeding, returning 1 call
        return output, [ValidationResult("Gen", True, ValidationSeverity.INFO, "")], 1

    mocker.patch('Resume_Generation_v12_80.ArtistGenerator.generate', side_effect=mock_generate_always_fail_k1)
    mocker.patch('Resume_Generation_v12_80.TextSanitizer.sanitize_buffer', side_effect=lambda buffer: ([], buffer.data))


def setup_mock_cl_signature_fail(mocker, orchestrator_instance, mock_thematic_analysis_base):
    """Mocks Artist output with CL failing multi-line signature check (v12.80)."""
    mocker.patch.object(orchestrator_instance, '_execute_hop_0_jd_analysis', return_value=mock_thematic_analysis_base)

    def mock_generate_with_bad_sig(*args, **kwargs):
        sections_to_gen = kwargs.get('sections_to_generate', set())
        output = {}
        # Always generate passing content for critical sections if requested
        if ResumeSection.K1_EXECUTIVE_SUMMARY in sections_to_gen:
            output[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = "word " * 130 + ". Sentence. Sentence. Sentence. Sentence. Sentence. Sentence." # Pass counts
        if ResumeSection.K0_HEADLINE in sections_to_gen:
            output[ResumeSection.K0_HEADLINE.value] = "Headline has enough words now eight"
        # ... Add minimal passing content for other sections if needed to prevent unrelated failures ...
        if ResumeSection.K5_UNIFY_BULLETS in sections_to_gen: # Add enough for total word count
             output[ResumeSection.K5_UNIFY_BULLETS.value] = [{"text":"word "*25, "provenance":"V"}]*7
        if ResumeSection.K6_IBM_BULLETS in sections_to_gen:
             output[ResumeSection.K6_IBM_BULLETS.value] = [{"text":"word "*25, "provenance":"V"}]*6
        if ResumeSection.K10_COMPETENCIES in sections_to_gen:
             output[ResumeSection.K10_COMPETENCIES.value] = [{"text":"word "*28, "provenance":"V"}]*6

        # Generate the bad signature CL if requested
        if ResumeSection.K13_COVER_LETTER in sections_to_gen:
            owner_info = MASTER_RESUME_JSON['owner']
            name = owner_info.get('name', 'N')
            email = owner_info.get('contact', {}).get('email', 'E')
            phone = owner_info.get('contact', {}).get('phone', 'P')
            linkedin = owner_info.get('contact', {}).get('linkedin', 'L')
            single_line_sig_no_spaces = f"Sincerely,\n\n{name}\n{email}\n{phone}\n{linkedin}"
            # Add date, recipient, salutation to pass full structure check
            date = datetime.now().strftime("%B %d, %Y")
            recipient = "Hiring Manager\n[Company Name]"
            salutation = "Dear Hiring Manager,"
            body = "\n\nParagraph 2.\n\nParagraph 3." # Ensure 3 body paras
            output[ResumeSection.K13_COVER_LETTER.value] = f"{date}\n\n{recipient}\n\n{salutation}\n\nParagraph 1 " + "word "*150 + body + "\n\n" + single_line_sig_no_spaces

        return output, [ValidationResult("Gen", True, ValidationSeverity.INFO, "")], 1 # type: ignore

    mocker.patch('Resume_Generation_v14_53.ArtistGenerator.generate', side_effect=mock_generate_with_bad_sig) # type: ignore
    mocker.patch('Resume_Generation_v14_53.TextSanitizer.sanitize_buffer', side_effect=lambda buffer: ([], buffer.data)) # type: ignore


# Consolidated Parameterized Failure Test (Updated for v12.80)
@pytest.mark.parametrize("scenario_name, setup_func, job_desc_override, expected_status, reason_substring", [
    ("Critical Word Count", setup_mock_word_count_failure, None, 'HALTED', "VG_TOTAL_WORD_COUNT"),
    ("Low Cover Letter Relevance", setup_mock_low_relevance_failure, None, 'HALTED', "VG_COVER_LETTER_RELEVANCE_RANGE"),
    ("Placeholder Text", setup_mock_placeholder_failure, None, 'HALTED', "CONTENT_NO_PLACEHOLDERS"),
    ("Empty Job Description", None, "", 'HALTED', "GATE-0: JD too short"),
    ("RAG Phase Failure (HOP-0)", setup_mock_rag_hop0_failure, None, 'FAILED', "Simulated RAG Failure in HOP-0"),
    ("Artist Generation Failure (HOP-3)", setup_mock_artist_hop3_failure, None, 'FAILED', "HOP-3 failed: Simulated LLM Failure in HOP-3"), # Updated expected message
    ("No API Key", setup_mock_no_api_key, None, 'FAILED', "HOP-0 failed: GEMINI_API_KEY not set"), # Expect failure at HOP-0 now
    ("Missing Narrative Data", setup_mock_missing_narrative, None, 'HALTED', "NARRATIVE_MINING_PRESENCE"),
    ("Malformed RAG JSON (HOP-0)", setup_mock_hop0_malformed_json_failure, None, 'FAILED', "HOP-0 failed: Simulated bad JSON in HOP-0"),
    ("Missing Company in Master Resume (HOP-3)", setup_mock_hop3_missing_company_failure, None, 'FAILED', "HOP-3 failed: Master experience data not found for company 'Unify Consulting'"), # Updated expected message
    ("Very Short Job Description", None, "Short JD.", 'HALTED', "GATE-0: JD too short"),
    ("Persistent K.1 Failure (HOP-3 Retry Fail)", setup_mock_persistent_k1_failure, None, 'HALTED', "Content validation failed after 5 attempts"),
    ("Cover Letter Signature Single Line", setup_mock_cl_signature_fail, None, 'HALTED', "VG_COVER_LETTER_SIGNATURE_VALID"),
])
def test_workflow_failure_scenarios(orchestrator_instance: WorkflowOrchestrator, job_description: str, mocker: MockerFixture, mock_thematic_analysis_base: MagicMock,
                                   scenario_name, setup_func, job_desc_override, expected_status, reason_substring):
    """Consolidated test for various workflow failure and halt scenarios (v12.80)."""
    current_orchestrator = orchestrator_instance
    if setup_func: # type: ignore
        maybe_new_orchestrator = setup_func(mocker, orchestrator_instance, mock_thematic_analysis_base)
        if maybe_new_orchestrator:
            current_orchestrator = maybe_new_orchestrator

    jd_to_use = job_desc_override if job_desc_override is not None else job_description

    result = current_orchestrator.execute_workflow(jd_to_use, f"{scenario_name}_Test", "TestRole")
    
    assert result.get('status') == expected_status, f"Scenario '{scenario_name}': Expected status '{expected_status}', got '{result.get('status')}'."
    reason_or_error = result.get('reason', result.get('error', ''))
    assert reason_substring in reason_or_error, f"Scenario '{scenario_name}': Expected reason/error substring '{reason_substring}' not found in '{reason_or_error}'."
    assert 'hop_checkpoints' in result, f"Scenario '{scenario_name}': Missing hop_checkpoints."
    if expected_status != 'FAILED' or "HOP-0 failed" not in reason_substring:
         assert len(result['hop_checkpoints']) > 0, f"Scenario '{scenario_name}': No hop checkpoints recorded."

    print(f"\nâœ“ test_workflow_failure_scenarios passed for: {scenario_name}")


# --- CONSOLIDATED HEADLINE VALIDATION ---
@pytest.mark.parametrize("headline_text, rule_id_to_check, expected_pass", [
    ("word " * 7, "VG_HEADLINE_WORD_COUNT", False),
    ("word " * 8, "VG_HEADLINE_WORD_COUNT", True),
    ("word " * 11, "VG_HEADLINE_WORD_COUNT", True),
    ("word " * 12, "VG_HEADLINE_WORD_COUNT", False),
    ("Cloud Alliances | GTM Strategy | Revenue Growth", "VG_HEADLINE_NO_TITLES", True),
    ("VP Cloud Alliances | GTM Strategy | Revenue Growth", "VG_HEADLINE_NO_TITLES", False),
    ("Senior Partner Manager | GTM Strategy | Revenue Growth", "VG_HEADLINE_NO_TITLES", False),
    ("Cloud Alliances | GTM Strategy | Revenue Growth", "VG_HEADLINE_NO_COMMAS", True),
    ("Cloud Alliances, GTM Strategy | Revenue Growth", "VG_HEADLINE_NO_COMMAS", False),
])
def test_headline_validation_rules(preflight_validator_instance, mock_thematic_analysis_base, mock_staging_buffer_fixture, job_description,
                                   mocker, headline_text, rule_id_to_check, expected_pass):
    """Consolidated test for K.0 Headline validation rules (VG_HEADLINE_*)."""
    buffer, buffer_data = mock_staging_buffer_fixture
    buffer_data[ResumeSection.K0_HEADLINE.value] = headline_text
    # Add minimal valid data for other critical checks
    constraints = ContentConstraintsConfig() # <<< Use constraints
    buffer_data[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = ". ".join(["Sentence"] * constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN) + "."
    buffer_data[ResumeSection.K13_COVER_LETTER.value] = "word "*150 + COVER_LETTER_SIGNATURE_TEMPLATE.format(name='N',email='E',phone='P',linkedin='L')

    # Run validation
    # --- START REFACTOR: Mock ValidationContext properties ---
    mock_context = mocker.MagicMock(spec=ValidationContext)
    type(mock_context).staging_buffer = mocker.PropertyMock(return_value=buffer)
    # Mock other properties used by rules under test
    type(mock_context).total_words = mocker.PropertyMock(return_value=1000) # Example value
    type(mock_context).unify_ibm_percent = mocker.PropertyMock(return_value=40.0)
    type(mock_context).unify_ibm_ratio = mocker.PropertyMock(return_value=1.2)
    type(mock_context).expected_signature = mocker.PropertyMock(return_value="sig")
    type(mock_context).cover_letter_jd_similarity = mocker.PropertyMock(return_value=0.5)
    type(mock_context).jd_keywords_found = mocker.PropertyMock(return_value=["kw"]*10)
    mock_context._cache = {} # Ensure cache exists

    # Patch the constructor to return our mock context
    mocker.patch('Resume_Generation_v14_53.ValidationContext', return_value=mock_context)
    # --- END REFACTOR ---

    validation_results, _, _ = preflight_validator_instance.validate(buffer, mock_thematic_analysis_base, job_description)

    result = next((r for r in validation_results if r.rule_id == rule_id_to_check), None)

    assert result is not None, f"Rule {rule_id_to_check} not found in validation results."

    # Check the result
    assert result.passed == expected_pass, f"Rule {rule_id_to_check} failed for headline '{headline_text}'. Expected pass={expected_pass}, but got pass={result.passed}. Message: {result.message}"


# --- CONSOLIDATED K.1 VALIDATION ---
# <<< MODIFICATION: Updated target ranges based on ContentConstraintsConfig v12.80 >>>
# EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 7
# EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 9
# K1_MIN_DIFFERENTIATORS: int = 4
# SignalControlConfig: K1_MAX_DIFFERENTIATORS: int = 4
@pytest.mark.parametrize("summary_text, required_kws_from_rag, rule_id_to_check, expected_pass", [
    # Sentence Count (Target: 7-9)
    (". ".join(["Sentence"] * 7) + ".", ["kw1","kw2","kw3","kw4"], "VG_SENTENCE_COUNT_K1", True),
    (". ".join(["Sentence"] * 9) + ".", ["kw1","kw2","kw3","kw4"], "VG_SENTENCE_COUNT_K1", True),
    (". ".join(["Sentence"] * 6) + ".", ["kw1","kw2","kw3","kw4"], "VG_SENTENCE_COUNT_K1", False),
    (". ".join(["Sentence"] * 10) + ".", ["kw1","kw2","kw3","kw4"], "VG_SENTENCE_COUNT_K1", False),
    # Differentiator Keywords (Target 4-4) - Using VG_K1_DIFFERENTIATOR_RANGE
    ("word "*130 + " kw1 kw2 kw3 kw4.", ["kw1", "kw2", "kw3", "kw4", "kw5"], "VG_K1_DIFFERENTIATOR_RANGE", True), # Found 4 -> Pass (exactly 4)
    ("word "*130 + " kw1 kw2 kw3.", ["kw1", "kw2", "kw3", "kw4", "kw5"], "VG_K1_DIFFERENTIATOR_RANGE", False), # Found 3 -> Fail (min 4)
    ("word "*130 + " kw1 kw2 kw3 kw4 kw5.", ["kw1", "kw2", "kw3", "kw4", "kw5"], "VG_K1_DIFFERENTIATOR_RANGE", False), # Found 5 -> Fail (max 4)
])
def test_k1_validation_rules(preflight_validator_instance, mocker, mock_staging_buffer_fixture, job_description,
                              mock_thematic_analysis_base, summary_text, required_kws_from_rag, rule_id_to_check, expected_pass):
    """Consolidated test for K.1 Executive Summary validation rules (v12.80)."""
    buffer, buffer_data = mock_staging_buffer_fixture
    buffer_data[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = summary_text
    # Add minimal valid data for other critical checks
    buffer_data[ResumeSection.K0_HEADLINE.value] = "Word word word word word word word word"
    buffer_data[ResumeSection.K13_COVER_LETTER.value] = "word "*150 + COVER_LETTER_SIGNATURE_TEMPLATE.format(name='N',email='E',phone='P',linkedin='L')

    # --- START REFACTOR: Mock ValidationContext properties for K.1 ---
    mock_context = mocker.MagicMock(spec=ValidationContext)
    type(mock_context).staging_buffer = mocker.PropertyMock(return_value=buffer)
    # Mock properties needed by other rules to prevent them from failing
    type(mock_context).total_words = mocker.PropertyMock(return_value=1000)
    type(mock_context).unify_ibm_percent = mocker.PropertyMock(return_value=40.0)
    type(mock_context).unify_ibm_ratio = mocker.PropertyMock(return_value=1.2)
    type(mock_context).expected_signature = mocker.PropertyMock(return_value="sig")
    type(mock_context).cover_letter_jd_similarity = mocker.PropertyMock(return_value=0.5)
    type(mock_context).jd_keywords_found = mocker.PropertyMock(return_value=["kw"]*10)
    # Mock the specific property for the differentiator rule
    type(mock_context).top_differentiators = mocker.PropertyMock(return_value=required_kws_from_rag[:SignalControlConfig().K1_MAX_DIFFERENTIATORS])
    mock_context._cache = {} # Ensure cache exists

    mocker.patch('Resume_Generation_v14_53.ValidationContext', return_value=mock_context)
    # --- END REFACTOR ---

    # Run validation
    validation_results, _, _ = preflight_validator_instance.validate(buffer, mock_thematic_analysis_base, job_description)

    result = next((r for r in validation_results if r.rule_id == rule_id_to_check), None)

    assert result is not None, f"Rule {rule_id_to_check} not found in validation results."

    # Check the result
    assert result.passed == expected_pass, f"Rule {rule_id_to_check} failed for summary '{summary_text[:30]}...'. Expected pass={expected_pass}, but got pass={result.passed}. Message: {result.message}"


# --- Test new critical formatting rules registration ---
def test_critical_formatting_rules_exist_v1280(preflight_validator_instance):
    """Check registered critical formatting/structure rules for v12.80."""
    rule_ids = {r.rule_id for r in preflight_validator_instance.engine.rules}
    expected_critical_rules = [
        # Structure/Format
        "VG_RESUME_HEADER_H2",
        "VG_EDU_CERTS_FORMAT",
        "VG_EXPERIENCE_BULLET_STYLE",
    "VG_COVER_LETTER_SIGNATURE_VALID",
        "VG_COMPETENCIES_FORMATTING",
        "VG_EXPERIENCE_RENDER_FORMAT",
        # Headline Format
        "VG_HEADLINE_NO_TITLES",
        "VG_HEADLINE_NO_COMMAS",
        # Content/Counts
        "VG_TOTAL_WORD_COUNT",
        "VG_SENTENCE_COUNT_K1",
        "VG_HEADLINE_WORD_COUNT",
        "VG_K1_DIFFERENTIATOR_RANGE",
        "VG_PROVENANCE_SPLIT_CHECK",
        # Workflow
        "BUFFER_LOCK_STATUS",
        # Dynamically added structure presence rules (check a few key ones)
        "STRUCTURE_K0_HEADLINE_PRESENT",
        "STRUCTURE_K1_EXECUTIVE_SUMMARY_PRESENT",
        "STRUCTURE_K5_UNIFY_BULLETS_PRESENT",
        "STRUCTURE_K10_COMPETENCIES_PRESENT",
        "STRUCTURE_K13_COVER_LETTER_PRESENT",
    ]
    assert "VG_BULLET_WORD_COUNT_TOLERANCE" not in rule_ids, "VG_BULLET_WORD_COUNT_TOLERANCE should be removed." # type: ignore

    missing_rules = [rule for rule in expected_critical_rules if rule not in rule_ids]
    assert not missing_rules, f"Missing critical rules: {missing_rules}"
    print(f"\nâœ“ Critical formatting/structure/provenance rules checked for v12.80.")


# --- Helper Function Tests ---
@pytest.mark.parametrize("text, expected_count", [
    ("Test one. Test two.", 2),
    ("Test e.g. one sentence.", 1),
    ("Dr. Smith went to Washington D.C. It was fun.", 2),
    ("Earned $1.5M. Success! Another sentence?", 3),
    ("One... Two? Three!", 3),
    ("", 0),
    ("Sentence ending with vs. like this.", 1),
    ("Sentence ending with i.e. like this.", 1),
    ("Mr. Jones said 'Hello.'", 1),
])
def test_count_sentences_regex_robustness(text, expected_count):
    """Tests the _count_sentences regex."""
    count = _count_sentences(text)
    assert count == expected_count, f"For '{text}', expected {expected_count} sentences, got {count}."
    print(f"\nâœ“ _count_sentences passed for: '{text}' (Expected: {expected_count}, Got: {count})")


# <<< REMOVED test_count_words_clean_robustness as function is gone >>>

# <<< ADDED test for count_words_ms_word_style >>>
@pytest.mark.parametrize("text, expected_count", [
    ("Simple test.", 2),
    ("Test -- good.", 2), # Treats '--' as separator
    ("Testâ€”good.", 1), # Em-dash treated as part of word if attached
    ("state-of-the-art", 1), # Hyphenated counts as one
    ("Hello, world!", 2),
    ("", 0),
    ("Word.", 1),
    (" Multi space test ", 3),
    (" leading/trailing ", 2),
    ("test@example.com", 1), # Email
    ("$1.5M", 1), # Metric
    ("word-", 1), # Trailing hyphen
    ("-word", 1), # Leading hyphen
    ("A B C D E F G H I J K L", 12), # Skills test case
])
def test_count_words_ms_word_style_robustness(text, expected_count):
    """Tests the count_words_ms_word_style function."""
    count = count_words_ms_word_style(text)
    assert count == expected_count, f"For '{text}', expected {expected_count} words (MS style), got {count}."
    print(f"\nâœ“ count_words_ms_word_style passed for: '{text}' (Expected: {expected_count}, Got: {count})")


# --- Word Distribution Test (Updated for v12.80 constraints) ---
@pytest.mark.parametrize("unify_words, ibm_words, other_words, expected_pass", [
    # UNIFY_IBM_COMBINED_PERCENT_MIN: 35.0, MAX: 45.0
    # UNIFY_IBM_RATIO_MIN: 1.1, MAX: 1.3
    (400, 350, 1250, True),  # (750/2000 = 37.5%, Ratio 1.14) -> PASS
    (350, 300, 1350, False), # (650/2000 = 32.5%) -> FAIL %
    (450, 400, 1150, True),  # (850/2000 = 42.5%, Ratio 1.125) -> PASS
    (300, 300, 1400, False), # (600/2000 = 30%, Ratio 1.0) -> FAIL % and Ratio
    (500, 400, 1100, True), # (900/2000 = 45%, Ratio 1.25) -> PASS
    (400, 200, 1400, False), # (600/2000 = 30%, Ratio 2.0) -> FAIL % and Ratio
    (450, 320, 1230, False), # (770/2000 = 38.5%, Ratio 1.41) -> PASS %, FAIL Ratio
])
def test_hop5_validates_unify_ibm_distribution_and_ratio_v1280(
    preflight_validator_instance: PreFlightValidator, mock_thematic_analysis_base: MagicMock, mocker: MockerFixture, job_description: str,
    unify_words, ibm_words, other_words, expected_pass
):
    """Test HOP-5 validation for Unify/IBM distribution and ratio (v12.80 constraints)."""
    # --- START REFACTOR: Mock ValidationContext properties for distribution test ---
    mock_context = mocker.MagicMock(spec=ValidationContext)
    total_words = unify_words + ibm_words + other_words
    type(mock_context).total_words = mocker.PropertyMock(return_value=total_words)
    type(mock_context).unify_words = mocker.PropertyMock(return_value=unify_words)
    type(mock_context).ibm_words = mocker.PropertyMock(return_value=ibm_words)
    type(mock_context).unify_ibm_percent = mocker.PropertyMock(return_value=(unify_words + ibm_words) / total_words * 100 if total_words > 0 else 0)
    type(mock_context).unify_ibm_ratio = mocker.PropertyMock(return_value=unify_words / ibm_words if ibm_words > 0 else float('inf'))
    # Mock other properties to ensure other rules pass
    type(mock_context).staging_buffer = mocker.PropertyMock(return_value=mocker.MagicMock(spec=ImmutableStagingBuffer, get=lambda k,d=None: "dummy"))
    type(mock_context).expected_signature = mocker.PropertyMock(return_value="dummy")
    type(mock_context).cover_letter_jd_similarity = mocker.PropertyMock(return_value=0.5)
    type(mock_context).jd_keywords_found = mocker.PropertyMock(return_value=["kw"]*10)
    mock_context._cache = {}
    
    mocker.patch('Resume_Generation_v14_53.ValidationContext', return_value=mock_context)
    # --- END REFACTOR ---

    # Calculate expected outcomes based on v12.80 rules
    constraints = ContentConstraintsConfig() # Use config object
    percent = (unify_words + ibm_words) / total_words * 100 if total_words > 0 else 0
    ratio = unify_words / ibm_words if ibm_words > 0 else float('inf')
    expected_percent_pass = constraints.UNIFY_IBM_COMBINED_PERCENT_MIN <= percent <= constraints.UNIFY_IBM_COMBINED_PERCENT_MAX
    expected_ratio_pass = constraints.UNIFY_IBM_RATIO_MIN <= ratio <= constraints.UNIFY_IBM_RATIO_MAX
    combined_expected_pass = expected_percent_pass and expected_ratio_pass

    validation_results, _, _ = preflight_validator_instance.validate(mocker.MagicMock(spec=ImmutableStagingBuffer), mock_thematic_analysis_base, job_description)

    dist_result = next((r for r in validation_results if r.rule_id == "WORD_DISTRIBUTION_UNIFY_IBM"), None)
    ratio_result = next((r for r in validation_results if r.rule_id == "UNIFY_IBM_RATIO"), None)

    assert dist_result is not None, "Distribution rule result missing."
    assert ratio_result is not None, "Ratio rule result missing."
    assert dist_result.passed == expected_percent_pass, f"Dist % check fail. Got {percent:.1f}%, Exp pass={expected_percent_pass}"
    assert ratio_result.passed == expected_ratio_pass, f"Ratio check fail. Got {ratio:.2f}, Exp pass={expected_ratio_pass}"
    if not expected_percent_pass: assert dist_result.severity == ValidationSeverity.HIGH
    if not expected_ratio_pass: assert ratio_result.severity == ValidationSeverity.HIGH
    assert (dist_result.passed and ratio_result.passed) == combined_expected_pass, f"Combined expectation mismatch. Expected: {combined_expected_pass}"

    print(f"\nâœ“ test_hop5_validates_unify_ibm_v1280 (Percent: {percent:.1f}%, Ratio: {ratio:.2f}) passed for combined_expected_pass={combined_expected_pass}.")


# --- Provenance Tests (Updated for v12.80 - Removed avg length check) ---

def test_clerk_extraction_initial_provenance_v1280(mocker):
    """Verify ClerkExtractor assigns 'Verbatim' provenance (v12.80)."""
    from Resume_Generation_v15_54 import ClerkExtractor # Import locally
    mock_master_resume = { # Needs all keys required by ClerkExtractor's internal validation
        "schema_version": "test_v1", "owner": {"name": "Test"},
        "professional_experience": [{"company": "TestCo", "title": "Dev", "location":"L","dates":{"start":"S","end":"E"}, "bullet_pool": ["B1", "B2"], "overview": "O"}],
        "education": [], "certifications_and_credentials": [], "strategic_and_technical_competencies": []
    }
    mocker.patch('Resume_Generation_v12_80.HallucinationDetector.detect', return_value=[])
    clerk = ClerkExtractor(mock_master_resume)
    extracted_data, _ = clerk.extract()

    assert 'experience_sections' in extracted_data and len(extracted_data['experience_sections']) == 1
    bullets = extracted_data['experience_sections'][0].get('bullets', [])
    assert len(bullets) == 2 and all(isinstance(b, dict) for b in bullets)
    assert all(b.get('provenance') == BulletProvenance.Verbatim.value for b in bullets), "Initial provenance fail."
    assert all('bullet_text' in b for b in bullets), "Missing 'bullet_text'."
    print("\nâœ“ ClerkExtractor assigns 'Verbatim' provenance correctly (v12.80).")


def test_artist_provenance_assignment_v1280(artist_generator_provenance, mocker):
    """
    Integration test: Checks _generate_tailored_bullets_for_experience assigns
    V/C/S provenance and reorders (v12.80 - mocks word count validation).
    """
    section_id_enum = ResumeSection.K5_UNIFY_BULLETS
    targets = artist_generator_provenance.PROVENANCE_SPLIT_TARGETS[section_id_enum]
    master_bullets_unify = artist_generator_provenance.enriched_scaffold['experience_sections'][0]['bullets']

    # Mock LLM calls (same as v9.98 test)
    select_v_response = "\n".join([b['bullet_text'] for b in master_bullets_unify[:targets['Verbatim']]])
    customize_response_raw = []
    custom_sources = []
    start_custom = targets['Verbatim']
    end_custom = start_custom + targets['Customized']
    for i in range(start_custom, end_custom):
        customize_response_raw.append(f"â€¢ Customized: {master_bullets_unify[i]['bullet_text']}")
        custom_sources.append(master_bullets_unify[i]['bullet_text'])
    customize_response = "\n".join(customize_response_raw)
    synthesize_response_raw = [f"* Synthetic bullet {i+1}." for i in range(targets['Synthetic'])]
    synthesize_response = "\n".join(synthesize_response_raw)
    expected_final_texts_ordered = (
        [b.replace("* ", "") for b in synthesize_response_raw] +
        [b.replace("â€¢ Customized: ", "") for b in customize_response_raw] +
        [b['bullet_text'] for b in master_bullets_unify[:targets['Verbatim']]]
    )[::-1] # Reverse order
    reorder_response = "\n".join(expected_final_texts_ordered)

    def api_side_effect(prompt, config, section_id_call, system_prompt, temperature_override=None): # Added temp override arg
        if section_id_call.endswith("_SelectV"): return select_v_response
        if section_id_call.endswith("_CustomC"): return customize_response
        if section_id_call.endswith("_SynthS"): return synthesize_response
        if section_id_call.endswith("_Reorder"): return reorder_response
        return "Unexpected API call"

    artist_generator_provenance._call_gemini_api.side_effect = api_side_effect # type: ignore
    mocker.patch.object(artist_generator_provenance, '_validate_llm_bullet_selection', side_effect=lambda sel, master, exp, sec: [b for b in master if b['bullet_text'] in sel][:exp])

    # Mock the word count validation helper to just return input
    mocker.patch.object(artist_generator_provenance, '_validate_and_potentially_rewrite_bullets', side_effect=lambda selected_bullets_structured, *args, **kwargs: selected_bullets_structured)

    # --- Execute the function under test ---
    result_bullets = artist_generator_provenance._generate_k5_unify_bullets(temperature_override=0.7) # Pass required temp

    # --- Assertions ---
    total_expected = sum(targets.values())
    assert len(result_bullets) == total_expected, f"Expected {total_expected} bullets, got {len(result_bullets)}"

    counts = {BulletProvenance.Verbatim.value: 0, BulletProvenance.Customized.value: 0, BulletProvenance.Synthetic.value: 0}
    for bullet in result_bullets:
        prov = bullet.get('provenance')
        if prov in counts: counts[prov] += 1
        else: pytest.fail(f"Unexpected provenance type: {prov}")

    assert counts[BulletProvenance.Verbatim.value] == targets['Verbatim'], f"Verbatim count mismatch."
    assert counts[BulletProvenance.Customized.value] == targets['Customized'], f"Customized count mismatch."
    assert counts[BulletProvenance.Synthetic.value] == targets['Synthetic'], f"Synthetic count mismatch."

    # Check that the final order matches the reorder mock response (using 'text' key now)
    result_texts_ordered = [b.get('text', b.get('bullet_text','')) for b in result_bullets] # Prefer 'text' key
    assert result_texts_ordered == expected_final_texts_ordered, "Final bullet order does not match reorder mock."

    # Check that word counts were added
    assert all('word_count' in b for b in result_bullets), "Missing 'word_count' in result bullets."

    # Verify the mocked word count validator was called
    artist_generator_provenance._validate_and_potentially_rewrite_bullets.assert_called_once() # type: ignore

    print("\nâœ“ Artist provenance assignment integration test passed (v12.80).")


# --- Headline Prompt Test (Updated for v12.80) ---
@pytest.fixture
def artist_generator_k0(mocker, job_description, mock_thematic_analysis_k1):
    """ArtistGenerator instance specifically for K.0 testing (v12.80)."""
    mock_master_resume = { # Minimal master resume
        "schema_version": "test_v1",
        "owner": {"name": "Test User", "contact": {"email": "a@b.c", "phone":"1", "linkedin":"l"}},
        "professional_experience": [], "education": [], "certifications_and_credentials": [], "strategic_and_technical_competencies": []
    }
    mock_enriched_scaffold = {"experience_sections": [] } # Minimal scaffold
    generator = ArtistGenerator(
        master_resume=copy.deepcopy(mock_master_resume),
        enriched_scaffold=mock_enriched_scaffold,
        job_description=job_description,
        thematic_analysis=mock_thematic_analysis_k1 # Uses the K1 fixture for detailed analysis
    )
    mocker.patch.object(generator, '_call_gemini_api', return_value="Mocked LLM Headline") # type: ignore
    return generator

def test_k0_headline_prompt_construction_v1280(artist_generator_k0, mock_thematic_analysis_k1):
    """Verify K.0 Headline prompt includes v12.80 constraints."""
    # Execute the method to trigger the API call mock
    artist_generator_k0._generate_k0_headline(temperature_override=0.7) # type: ignore # Pass required temp

    artist_generator_k0._call_gemini_api.assert_called_once()
    call_args, call_kwargs = artist_generator_k0._call_gemini_api.call_args
    prompt = call_args[0]
    config_used = call_args[1]
    section_id_called = call_args[2]

    # Check basic prompt content & constraints
    assert "Generate a compelling resume headline" in prompt
    # Check differentiator keywords from mock_thematic_analysis_k1 fixture
    assert "AWS Partnerships, GTM Execution, Revenue Growth, Executive Leadership, SaaS Delivery" in prompt
    assert "3 distinct components separated by pipes (|)" in prompt
    constraints = ContentConstraintsConfig() # Use config object
    assert f"{constraints.HEADLINE_WORD_COUNT_MIN} and {constraints.HEADLINE_WORD_COUNT_MAX} words" in prompt
    assert f"{constraints.HEADLINE_COMPONENT_WORDS_MIN} and {constraints.HEADLINE_COMPONENT_WORDS_MAX} words" in prompt
    assert "DO NOT include job titles" in prompt
    assert "DO NOT use commas." in prompt
    assert "Output ONLY the headline text." in prompt
    # <<< MODIFICATION: Archetype instruction removed from K0 prompt in v12.x >>>
    assert "CRITICAL INSTRUCTION FOR THIS JOB:" not in prompt
    assert "POST-SALES customer-facing role" not in prompt

    assert config_used == ReasoningConfig.K0_HEADLINE_CONFIG
    assert section_id_called == ResumeSection.K0_HEADLINE.value

    print("\nâœ“ K.0 Headline prompt construction test passed (v12.80).")


# --- Synthesis and QA Report Tests (Updated for v12.80) ---

def test_synthesize_thematic_analysis_weighted_scoring_v1280(mocker, master_resume_for_provenance):
    """Unit test: Weighted scoring in _synthesize_thematic_analysis (v12.80)."""
    analyzer = EnhancedJobDescriptionAnalyzer(master_resume=copy.deepcopy(master_resume_for_provenance), enable_web_search=False) # type: ignore
    test_weights = {"SOURCE_COMPANY_BLOG": 2.0, "SOURCE_PEER_JD": 1.0, "SOURCE_TARGET_EMPLOYEE": 1.5, "SOURCE_GENERIC_PROFILE": 0.5, "SOURCE_GARTNER_MQ": 1.2, "LOCAL_NLP": 0.1, "SOURCE_NARRATIVE_MINING": 0.0} # Added Narrative source
    analyzer.config.source_weights = test_weights
    analyzer.rag_mission = mocker.MagicMock(spec=RAGMission, precise_role_title="Mock Role")

    # Define mock phase outputs (dictionaries now, as per v11.60 fixes)
    phase1 = {"thematic_analysis": {"primary_theme": {"keywords": ["kw1", "kw2"], "name": "T1", "confidence": 0.9}, "secondary_themes": [{"keywords": ["kw2", "kw3"], "name": "T2", "relevance": 0.8}], "trending_keywords": ["kw4"]}, "role_classification": {}, "search_summary": {"searches_performed": 1}}
    phase2 = {"authenticity_patterns": {"competency_phrasing": ["kw1", "kw5"], "other_patterns": ["kw3", "kw6"]}, "pattern_confidence": {"overall": 0.8}, "search_summary": {"profiles_analyzed": 1}}
    phase3 = {"competitive_analysis": {"differentiator_keywords": [{"keyword": "kw1", "uniqueness_score": 0.9}], "table_stakes_keywords": [{"keyword": "kw4"}]}, "search_summary": {"peer_jds_analyzed": 1}, "positioning_insight": ""}
    phase4 = {"problem_solution_narratives": {"common_problems":["p1"], "solution_patterns":["s1"]}, "search_summary": {"searches_performed": 1}}

    analysis_result = analyzer._synthesize_thematic_analysis(phase1, phase2, phase3, phase4, "job description text")

    # Expected scores (same as v9.98 test as inputs didn't change narrative weight)
    expected_scores = {"kw1": 4.58, "kw2": 3.0, "kw3": 1.5, "kw4": 2.0, "kw5": 1.5, "kw6": 0.5}

    assert hasattr(analysis_result, 'competitive_intelligence')
    assert hasattr(analysis_result.competitive_intelligence, 'differentiator_keywords_weighted')
    result_scores = {item['keyword']: round(item['weight'], 2) for item in analysis_result.competitive_intelligence.differentiator_keywords_weighted}

    assert result_scores == expected_scores, f"Weighted scores mismatch. Got: {result_scores}, Expected: {expected_scores}"
    assert analysis_result.competitive_intelligence.differentiator_keywords[:3] == ["kw1", "kw2", "kw4"]

    print("\nâœ“ _synthesize_thematic_analysis weighted scoring test passed (v12.80).")


# QA Report Table Formatting tests (Updated for v12.80 - Removed sections 7, 8)
def test_qa_report_table_formatting_v1280(orchestrator_instance: WorkflowOrchestrator, mocker, mock_thematic_analysis_base):
    """Tests QA report uses bar chart (Sec 1) and pre-formatted tables (Sec 2-12)."""
    mock_buffer = mocker.MagicMock(spec=ImmutableStagingBuffer)
    # Simulate content for sections needed by builders
    mock_buffer_data = {section_config[1][0].value: "content" for section_config in orchestrator_instance.SECTION_SIGNAL_TARGETS_CONFIG.items()}
    mock_buffer_data[ResumeSection.K1_EXECUTIVE_SUMMARY.value] = "Exec Summary content"
    # Add dummy provenance data for section 5
    mock_buffer_data[ResumeSection.K5_UNIFY_BULLETS.value] = [{"text":"bullet", "provenance":BulletProvenance.Verbatim.value, "word_count":10}]
    mock_buffer.get.side_effect = lambda key, default=None: mock_buffer_data.get(key, default)
    type(mock_buffer).data = mocker.PropertyMock(return_value=mock_buffer_data)
    mock_reasoning_params = {"generation_config": mocker.MagicMock(temperature=0.9), "sc": 1} # type: ignore
    mocker.patch('Resume_Generation_v14_53.reasoning_config_to_api_params', return_value=mock_reasoning_params)
    mocker.patch('Resume_Generation_v14_53.calculate_signal_score', return_value=0.8) # Mock score calc

    # Mock all individual section builder methods to ensure they are called
    original_methods = {}
    for cfg in orchestrator_instance.QA_REPORT_SECTIONS: # type: ignore # Use the instance's config
        method_name = cfg["method"]
        if hasattr(orchestrator_instance, method_name):
             original_methods[method_name] = getattr(orchestrator_instance, method_name)
             # Use specific mocks for sections we want to check format of
             if "signal_quality" in method_name:
                 mocker.patch.object(orchestrator_instance, method_name, return_value=["1. Title", "```markdown", "[â–ˆ] 80% (Tgt:X-Y) PASS (T:0.9)"])
             elif "hop_summary" in method_name:
                  mocker.patch.object(orchestrator_instance, method_name, return_value=["3. Title", "```markdown", "Hop ID   Hop Name", "------   --------"])
             elif "exec_summary_similarity" in method_name: mocker.patch.object(orchestrator_instance, method_name, return_value=["7. Title", "```markdown", "Section   Similarity", "-------   ----------"])
             elif "pairwise_similarity" in method_name: mocker.patch.object(orchestrator_instance, method_name, return_value=["8. Title", "```markdown", "Bullet 1   Bullet 2", "--------   --------"])
             elif "final_format" in method_name: # Check section 14
                 mocker.patch.object(orchestrator_instance, method_name, return_value=["12. Title", "```markdown", "Artifact      Check", "--------      -----"])
             else: # Default mock for others
                  mocker.patch.object(orchestrator_instance, method_name, return_value=["", f"Mock Content for {method_name}", "```markdown", "Mock Table", "```"])
        else:
             print(f"Warning: Method {method_name} not found on orchestrator instance.")

    # --- Execute ---
    validation_results, qa_report_text, _ = orchestrator_instance._generate_qa_report( # type: ignore
        mock_buffer, mock_thematic_analysis_base, [] # Pass empty initial validation results
    )

    # --- Assertions ---
    format_check_result = next((r for r in validation_results if r.rule_id == "QA_TABLE_FORMAT_INVALID"), None)
    assert format_check_result and format_check_result.passed is True, "Internal QA table format check failed."

    # Check Section 1 format
    assert "1. Title" in qa_report_text and "```markdown" in qa_report_text and "[â–ˆ]" in qa_report_text and "(T:" in qa_report_text
    assert "| " not in qa_report_text # Ensure no markdown tables anywhere

    # Check Sections format (spot check Sec 3, 7, 8, 14)
    assert "3. Title" in qa_report_text and "Hop ID   Hop Name" in qa_report_text
    assert "7. Title" in qa_report_text and "Section   Similarity" in qa_report_text
    assert "8. Title" in qa_report_text and "Bullet 1   Bullet 2" in qa_report_text
    assert "12. Title" in qa_report_text and "Artifact      Check" in qa_report_text

    print("\nâœ“ QA Report Formatting Test (v12.80) Passed.")


# Self-Consistency test (No change needed from v9.98 logic, just path update)
def test_refactored_self_consistency_logic_v1280(artist_generator_instance, mocker):
    """Unit test: _call_gemini_api handles self-consistency logic correctly (v12.80)."""
    mock_model_instance = mocker.MagicMock()
    mock_candidate_response = mocker.MagicMock()
    candidate_texts = ["Sample Response 1", "Sample Response 2", "Sample Response 3"]
    mock_candidates = []
    for text in candidate_texts:
        mock_part = mocker.MagicMock(text=text)
        mock_content = mocker.MagicMock(parts=[mock_part])
        # Simulate finish_reason = 1 (STOP)
        mock_candidate = mocker.MagicMock(content=mock_content, finish_reason=1)
        mock_candidates.append(mock_candidate)
    type(mock_candidate_response).candidates = mocker.PropertyMock(return_value=mock_candidates)
    # Simulate synthesis response with finish_reason = 1
    mock_synthesis_response = mocker.MagicMock(text="Final Synthesized Result")
    mock_synthesis_candidate = mocker.MagicMock(finish_reason=1)
    type(mock_synthesis_response).candidates = mocker.PropertyMock(return_value=[mock_synthesis_candidate])

    mock_model_instance.generate_content.side_effect = [mock_candidate_response, mock_synthesis_response]
    mocker.patch('Resume_Generation_v14_53.genai.GenerativeModel', return_value=mock_model_instance)
    mocker.patch('Resume_Generation_v14_53.os.environ.get', return_value="mock_api_key")
    mocker.patch('Resume_Generation_v14_53.genai.configure')

    sc_count = 3
    reasoning_config = ReasoningConfig(self_consistency=sc_count)

    final_result = artist_generator_instance._call_gemini_api(
        prompt="Test prompt for SC",
        reasoning_config=reasoning_config,
        section_id="TEST_SC",
        system_prompt="Base system prompt",
        temperature_override=None # Test default SC temp logic
    )

    assert final_result == "Final Synthesized Result", "Final result mismatch."
    assert mock_model_instance.generate_content.call_count == 2

    # Check candidate call config
    candidate_call_args, candidate_call_kwargs = mock_model_instance.generate_content.call_args_list[0]
    gen_config_candidates = candidate_call_kwargs.get('generation_config')
    assert gen_config_candidates and gen_config_candidates.candidate_count == sc_count
    assert gen_config_candidates.temperature == 0.9, "Expected high temperature for SC candidates."

    # Check synthesis call config
    synthesis_call_args, synthesis_call_kwargs = mock_model_instance.generate_content.call_args_list[1]
    gen_config_synthesis = synthesis_call_kwargs.get('generation_config')
    assert gen_config_synthesis and gen_config_synthesis.temperature == 0.5, "Expected 0.5 temperature for synthesis."

    print("\nâœ“ Refactored Self-Consistency Logic Test Passed (v12.80).")

# <<< MODIFICATION: Added test for removed markdown fences >>>
def test_call_gemini_api_removes_markdown_fences(artist_generator_instance, mocker):
    """Unit test: _call_gemini_api removes markdown fences."""
    mock_model_instance = mocker.MagicMock()
    # Simulate single response with fences
    mock_response_with_fence = mocker.MagicMock(text="```json\n{\"key\": \"value\"}\n```")
    mock_candidate_fence = mocker.MagicMock(finish_reason=1) # STOP
    type(mock_response_with_fence).candidates = mocker.PropertyMock(return_value=[mock_candidate_fence])

    mock_model_instance.generate_content.return_value = mock_response_with_fence
    mocker.patch('Resume_Generation_v14_53.genai.GenerativeModel', return_value=mock_model_instance)
    mocker.patch('Resume_Generation_v14_53.os.environ.get', return_value="mock_api_key")
    mocker.patch('Resume_Generation_v14_53.genai.configure')

    # Use default reasoning (no self-consistency)
    reasoning_config = ReasoningConfig()

    final_result = artist_generator_instance._call_gemini_api(
        prompt="Test prompt",
        reasoning_config=reasoning_config,
        section_id="TEST_FENCE",
        system_prompt="Base system prompt",
        temperature_override=0.7
    )

    expected_result = "{\"key\": \"value\"}" # Fences removed
    assert final_result == expected_result, f"Markdown fences not removed. Got: '{final_result}'"
    mock_model_instance.generate_content.assert_called_once()
    print("\nâœ“ _call_gemini_api removes markdown fences test passed.")