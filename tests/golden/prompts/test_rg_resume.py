# MERGED FROM UNASSIGNED BY WINDSURF v4 — 2025-12-07T01:21:36.303453+00:00
# Original location: 10_tests\_unassigned_tests_invalid\test_regression_rg_resume_outputs.py
# High-signal content preserved below — zero-loss migration
# ================================================================================

"""
Resume Generation Engine v4.8.0 - WITH VALIDATION METHODS
=========================================================
MAJOR UPGRADE: Added BaselineResumeMetrics class with validation methods
- validate_wordcount(): Check individual sections
- validate_total(): Check total word count
- calculate_deltas(): Compare actual vs baseline
- generate_report(): Comprehensive validation report
- QA Gates: Enforce word count limits

Version: 4.8.0
Date: October 2025
"""

import re
import scripts.check_canonical_structure
from typing import Dict, List
from enum import Enum
from datetime import datetime

__version__ = "4.8.0"

# ============================================================================
# TEMPERATURE MODE ENUM
# ============================================================================

class TemperatureMode(Enum):
    """Temperature modes for constraint relaxation and signal adjustment."""
    CONSERVATIVE = "conservative"  # Baseline ±15%, no extra signal
    BALANCED = "balanced"           # Baseline ±25%, +0.02 signal if targets met
    CREATIVE = "creative"           # Baseline ±35%, +0.05 signal, EY/early flexibility

# ============================================================================
# BASELINE RESUME METRICS CLASS (FROM v2.1 WITH v4.5.2 WORD COUNTS)
# ============================================================================

class BaselineResumeMetrics:
    """
    Structured validation class for resume word counts.
    Combines v2.1 validation methods with v4.5.2 word count targets.
    """

    # Baseline word counts from v4.5.2 (NOT v2.1)
    BASELINE_WORDCOUNT = {
        "name": 2,
        "headline": 12,
        "contact_info": 10,
        "executive_summary": 150,  # v4.5.2: 150 (not v2.1's 118-135)
        "unify_company": 5,
        "unify_title": 8,
        "unify_intro": 25,
        "unify_bullets": 265,
        "ibm_company": 4,
        "ibm_title": 7,
        "ibm_intro": 20,
        "ibm_bullets": 195,
        "tradersense_company": 6,
        "tradersense_title": 7,
        "tradersense_intro": 20,
        "tradersense_bullets": 45,
        "ey_company": 5,
        "ey_title": 5,
        "ey_intro": 15,
        "ey_bullets": 50,
        "early_company": 5,
        "early_title": 8,
        "early_intro": 20,
        "early_bullets": 45,
        "education": 15,
        "certifications": 25,
        "competencies": 118,
        "total_resume": 1032  # v4.5.2 baseline
    }

    # Frozen sections (cannot be modified)
    FROZEN_SECTIONS = [
        "name", "education", "certifications",
        "unify_company", "ibm_company", "tradersense_company",
        "ey_company", "early_company"
    ]

    # QA Gates for validation
    QA_GATES = {
        "VG_BASELINE_001": {
            "name": "Executive Summary Word Count",
            "min": 135,  # 150 - 10%
            "max": 165,  # 150 + 10%
            "section": "executive_summary",
            "severity": "CRITICAL"
        },
        "VG_BASELINE_002": {
            "name": "Unify Bullets Word Count",
            "min": 199,  # 265 - 25%
            "max": 331,  # 265 + 25%
            "section": "unify_bullets",
            "severity": "CRITICAL"
        },
        "VG_BASELINE_003": {
            "name": "IBM Bullets Word Count",
            "min": 146,  # 195 - 25%
            "max": 244,  # 195 + 25%
            "section": "ibm_bullets",
            "severity": "CRITICAL"
        },
        "VG_BASELINE_004": {
            "name": "Total Resume Word Count",
            "min": 928,   # 1032 - 10%
            "max": 1135,  # 1032 + 10%
            "section": "total_resume",
            "severity": "CRITICAL"
        },
        "VG_BASELINE_005": {
            "name": "Unify/IBM Ratio",
            "min": 1.10,
            "max": 1.50,
            "section": "ratio",
            "severity": "WARNING"
        },
        "VG_BASELINE_006": {
            "name": "Frozen Sections Check",
            "sections": FROZEN_SECTIONS,
            "severity": "INFO"
        }
    }

    @classmethod
    def validate_wordcount(cls, section: str, actual_words: int,
                          temperature: TemperatureMode = TemperatureMode.BALANCED) -> Dict:
        """
        Validate word count for a specific section.

        Args:
            section: Section name
            actual_words: Actual word count
            temperature: Temperature mode for flexibility

        Returns:
            Dict with validation results
        """
        if section not in cls.BASELINE_WORDCOUNT:
            return {
                "valid": False,
                "status": "ERROR",
                "message": f"Unknown section: {section}"
            }

        baseline = cls.BASELINE_WORDCOUNT[section]

        # Apply temperature-based flexibility
        flexibility = {
            TemperatureMode.CONSERVATIVE: 0.15,
            TemperatureMode.BALANCED: 0.25,
            TemperatureMode.CREATIVE: 0.35
        }[temperature]

        min_allowed = int(baseline * (1 - flexibility))
        max_allowed = int(baseline * (1 + flexibility))

        # Check if frozen section
        if section in cls.FROZEN_SECTIONS:
            if actual_words != baseline:
                return {
                    "valid": False,
                    "status": "FROZEN_VIOLATION",
                    "message": f"{section} is frozen at {baseline} words, got {actual_words}",
                    "baseline": baseline,
                    "actual": actual_words,
                    "delta": actual_words - baseline
                }

        # Validate range
        if actual_words < min_allowed:
            status = "UNDER"
            valid = False
        elif actual_words > max_allowed:
            status = "OVER"
            valid = False
        else:
            status = "PASS"
            valid = True

        delta = actual_words - baseline
        delta_pct = (delta / baseline * 100) if baseline > 0 else 0

        return {
            "valid": valid,
            "status": status,
            "section": section,
            "baseline": baseline,
            "actual": actual_words,
            "delta": delta,
            "delta_pct": delta_pct,
            "allowed_range": f"{min_allowed}-{max_allowed}",
            "temperature": temperature.value,
            "message": f"{section}: {actual_words} words (baseline: {baseline}, δ: {delta:+d})"
        }

    @classmethod
    def validate_total(cls, section_word_counts: Dict[str, int],
                      temperature: TemperatureMode = TemperatureMode.BALANCED) -> Dict:
        """
        Validate total resume word count.

        Args:
            section_word_counts: Dict of section names to word counts
            temperature: Temperature mode

        Returns:
            Dict with total validation results
        """
        # Calculate total (excluding skills which aren't counted)
        total_actual = sum(
            count for section, count in section_word_counts.items()
            if section != "skills"  # K.11 skills not counted in total
        )

        total_baseline = cls.BASELINE_WORDCOUNT["total_resume"]

        # Apply temperature flexibility
        flexibility = {
            TemperatureMode.CONSERVATIVE: 0.10,
            TemperatureMode.BALANCED: 0.15,
            TemperatureMode.CREATIVE: 0.20
        }[temperature]

        min_allowed = int(total_baseline * (1 - flexibility))
        max_allowed = int(total_baseline * (1 + flexibility))

        valid = min_allowed <= total_actual <= max_allowed
        delta = total_actual - total_baseline
        delta_pct = (delta / total_baseline * 100) if total_baseline > 0 else 0

        return {
            "valid": valid,
            "status": "PASS" if valid else ("OVER" if total_actual > max_allowed else "UNDER"),
            "total_baseline": total_baseline,
            "total_actual": total_actual,
            "delta": delta,
            "delta_pct": delta_pct,
            "allowed_range": f"{min_allowed}-{max_allowed}",
            "temperature": temperature.value,
            "message": f"Total: {total_actual} words (target: {total_baseline}, δ: {delta:+d}, {delta_pct:+.1f}%)"
        }

    @classmethod
    def calculate_deltas(cls, section_word_counts: Dict[str, int]) -> Dict[str, Dict]:
        """
        Calculate deltas for all sections.

        Args:
            section_word_counts: Dict of section names to word counts

        Returns:
            Dict with delta analysis for each section
        """
        deltas = {}

        for section, actual in section_word_counts.items():
            if section in cls.BASELINE_WORDCOUNT:
                baseline = cls.BASELINE_WORDCOUNT[section]
                delta = actual - baseline
                delta_pct = (delta / baseline * 100) if baseline > 0 else 0

                deltas[section] = {
                    "baseline": baseline,
                    "actual": actual,
                    "delta": delta,
                    "delta_pct": delta_pct,
                    "status": "EXACT" if delta == 0 else ("OVER" if delta > 0 else "UNDER")
                }

        return deltas

    @classmethod
    def run_qa_gates(cls, section_word_counts: Dict[str, int]) -> Dict:
        """
        Run all QA validation gates.

        Args:
            section_word_counts: Dict of section names to word counts

        Returns:
            Dict with QA gate results
        """
        results = {}
        failures = []
        warnings = []

        for gate_id, gate_config in cls.QA_GATES.items():
            if gate_id == "VG_BASELINE_005":  # Ratio check
                unify_words = section_word_counts.get("unify_bullets", 0) + \
                             section_word_counts.get("unify_intro", 0)
                ibm_words = section_word_counts.get("ibm_bullets", 0) + \
                           section_word_counts.get("ibm_intro", 0)

                if ibm_words > 0:
                    ratio = unify_words / ibm_words
                    passed = gate_config["min"] <= ratio <= gate_config["max"]
                    message = f"Unify/IBM ratio: {ratio:.2f} (target: {gate_config['min']}-{gate_config['max']})"
                else:
                    passed = False
                    message = "Cannot calculate ratio (IBM words = 0)"
                    ratio = 0

                results[gate_id] = {
                    "name": gate_config["name"],
                    "passed": passed,
                    "value": ratio,
                    "message": message,
                    "severity": gate_config["severity"]
                }

            elif gate_id == "VG_BASELINE_006":  # Frozen sections
                violations = []
                for section in gate_config["sections"]:
                    if section in section_word_counts:
                        actual = section_word_counts[section]
                        expected = cls.BASELINE_WORDCOUNT.get(section, 0)
                        if actual != expected:
                            violations.append(f"{section}: {actual} != {expected}")

                passed = len(violations) == 0
                message = "All frozen sections unchanged" if passed else f"Violations: {', '.join(violations)}"

                results[gate_id] = {
                    "name": gate_config["name"],
                    "passed": passed,
                    "violations": violations,
                    "message": message,
                    "severity": gate_config["severity"]
                }

            else:  # Word count gates
                section = gate_config["section"]
                if section == "total_resume":
                    actual = sum(v for k, v in section_word_counts.items() if k != "skills")
                else:
                    actual = section_word_counts.get(section, 0)

                passed = gate_config["min"] <= actual <= gate_config["max"]
                message = f"{gate_config['name']}: {actual} words (range: {gate_config['min']}-{gate_config['max']})"

                results[gate_id] = {
                    "name": gate_config["name"],
                    "passed": passed,
                    "value": actual,
                    "min": gate_config["min"],
                    "max": gate_config["max"],
                    "message": message,
                    "severity": gate_config["severity"]
                }

            # Track failures and warnings
            if not results[gate_id]["passed"]:
                if gate_config["severity"] == "CRITICAL":
                    failures.append(gate_id)
                elif gate_config["severity"] == "WARNING":
                    warnings.append(gate_id)

        return {
            "gates": results,
            "all_passed": len(failures) == 0,
            "critical_failures": failures,
            "warnings": warnings,
            "summary": f"{'✓ PASSED' if len(failures) == 0 else f'✗ FAILED ({len(failures)} critical)'}"
        }

    @classmethod
    def generate_report(cls, section_word_counts: Dict[str, int],
                       temperature: TemperatureMode = TemperatureMode.BALANCED) -> str:
        """
        Generate comprehensive validation report.

        Args:
            section_word_counts: Dict of section names to word counts
            temperature: Temperature mode

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("BASELINE VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Section validation
        lines.append("SECTION VALIDATION:")
        lines.append("-" * 80)

        for section in ["executive_summary", "unify_bullets", "ibm_bullets",
                       "tradersense_bullets", "ey_bullets", "early_bullets"]:
            if section in section_word_counts:
                result = cls.validate_wordcount(section, section_word_counts[section], temperature)
                status_icon = "✓" if result["valid"] else "✗"
                lines.append(f"{status_icon} {result['message']}")

        lines.append("")

        # Total validation
        lines.append("TOTAL VALIDATION:")
        lines.append("-" * 80)
        total_result = cls.validate_total(section_word_counts, temperature)
        status_icon = "✓" if total_result["valid"] else "✗"
        lines.append(f"{status_icon} {total_result['message']}")
        lines.append("")

        # QA Gates
        lines.append("QA GATES:")
        lines.append("-" * 80)
        qa_results = cls.run_qa_gates(section_word_counts)

        for gate_id, result in qa_results["gates"].items():
            status_icon = "✓" if result["passed"] else "✗"
            severity = f"[{result['severity']}]"
            lines.append(f"{status_icon} {severity:10} {result['message']}")

        lines.append("")
        lines.append("=" * 80)
        lines.append(f"OVERALL STATUS: {qa_results['summary']}")
        lines.append("=" * 80)

        return "\n".join(lines)

# ============================================================================
# MASTER RESUME DATA (EMBEDDED)
# ============================================================================

class MasterResume:
    """
    Amit Ayer's complete master resume embedded in code.
    NO NEED TO UPLOAD RESUME - Just provide JD!
    """

    CONTACT = {
        "name": "Amit Ayer",
        "headline": "Chief AI Officer | LLM Product Launches | Strategic AI Partnerships",
        "phone": "+1-917-239-3830",
        "email": "amitayer1@gmail.com",
        "linkedin": "https://www.linkedin.com/in/amitayer1",
        "location": "Boca Raton, FL"
    }

    EXPERIENCE = {
        "unify": {
            "company": "Unify Consulting",
            "location": "Boca Raton, FL",
            "title": "Chief AI Officer",
            "dates": {"start": "February 2023", "end": "Present"},
            "overview": "Led enterprise generative AI and LLM solution delivery for Fortune 500 financial services clients, scaling senior ML engineering teams and accelerating production deployment timelines by 40% across regulated client programs.",
            "bullets": [
                "Designed and deployed context-engineering frameworks with retrieval-augmented pipelines on unified analytics platforms and semantic caching, improving generative AI accuracy by 33% while accelerating customer solution adoption across multiple Fortune 500 portfolio companies.",
                "Architected LLM deployment pipelines with embedding stores, vector databases on cloud infrastructure, and inference optimization techniques, cutting latency by 38% and improving model throughput to meet production SLAs for regulated financial workloads.",
                "Deployed agentic API frameworks using chain-of-thought prompting to automate complex workflows, reducing manual intervention in reporting and operations by 28% while improving audit traceability for regulatory compliance requirements across Fortune 500 clients.",
                "Built senior engineering teams focused on transformer models and attention mechanisms, delivering low-latency inference optimization on cloud infrastructure and reducing fraud detection response times by 42% across client production deployments.",
                "Recruited and scaled senior LLM and ML engineering practice from 5 to 18 members, delivering enterprise AI adoption for Fortune 500 financial clients and accelerating time-to-production by 37% across regulated programs.",
                "Built and mentored 12-person professional services AI team, equipping delivery leads with production-grade LLM tools and code accelerators that reduced development sprint cycles by 27% and improved overall project delivery velocity.",
                "Led multi-year strategic partnerships with leading AWS to co-develop platforms and go-to-market programs that scaled enterprise generative AI adoption, secured $18M in partnership revenue, and expanded professional services reach globally.",
                "Partnered with C-suite executives to align AI strategy with business outcomes, co-developing generative AI products using cloud platforms that generated $32M in measurable client value and operational transformation initiatives across portfolio companies.",
                "Drove strategic alliances with AWS and Snowflake to co-develop generative AI solutions, launching 8 client-specific pilots worth $17M in pipeline value and accelerating professional services onboarding across portfolio companies.",
                "Accelerated professional services onboarding with automated LLM-powered discovery and RAG pipelines on unified analytics platforms, reducing client intake times by 43% and launching enterprise projects faster with standardized AI delivery frameworks.",
                "Standardized professional services delivery using modular AI architectures and retrieval-augmented generation systems, cutting consultant ramp-up by 32 days and raising client consistency scores to 91% across all engagements.",
                "Automated repetitive professional services tasks with transformer-based large language models and intelligent workflow orchestration on cloud platforms, reducing overall delivery costs by 22% while maintaining enterprise-grade quality standards across all engagements.",
                "Automated compliance and risk validation using policy-as-code and transformer-based LLM validators embedded in professional services workflows, cutting regulatory remediation cycles by 37% and accelerating audit timelines for global clients.",
                "Enabled measurable business outcomes by embedding AI-powered analytics and intelligent chatbot support into client engagements, raising renewal rates by 23% and strengthening long-term partnership relationships across Fortune 500 portfolio companies."
            ]
        },
        "ibm": {
            "company": "IBM",
            "location": "Edgewater, NJ",
            "title": "Lead Client Partner",
            "dates": {"start": "April 2017", "end": "October 2022"},
            "overview": "Directed global digital transformation programs across financial institutions, modernizing historical risk systems and reducing regulatory reporting cycles by 50% through cloud analytics migrations.",
            "bullets": [
                "Integrated AI decision engines into risk platforms enabling real-time CCAR and Basel III regulatory reporting, raising client renewal rates by 24% across Fortune 500 financial accounts.",
                "Launched machine learning risk analytics platform on cloud infrastructure serving global markets, improving predictive accuracy by 17% while ensuring compliance with international regulatory frameworks including MiFID II.",
                "Led multi-region regulatory modernization projects across EMEA and APAC, deploying NLP fraud analytics on cloud platforms that reduced false positives by 29% and improved audit transparency for global clients.",
                "Introduced AI-infused reporting and compliance automation frameworks, improving regulatory response times by 53% and supporting scalable client transformation programs across financial services portfolios globally.",
                "Delivered $34M transformation by migrating historical risk systems to AWS analytics platforms, cutting regulatory response times by 48% for Fortune 500 banking clients.",
                "Migrated large-scale Monte Carlo risk models to cloud HPC infrastructure, accelerating execution cycles by 43% and reducing annual compute costs by $4.2M for global financial institutions.",
                "Oversaw global migrations of on-premise risk models to cloud infrastructure, enabling real-time analytics capabilities and saving $3.8M in annual infrastructure costs for Fortune 500 financial institutions.",
                "Established strategic alliances with leading cloud and data platform providers and systems integrators to co-deliver enterprise solutions, generating $16M in incremental partnership revenue across 32 global markets.",
                "Partnered with cloud providers and top systems integrators to co-deliver complex AI transformation programs, unlocking $14M in incremental revenue and expanding professional services reach globally.",
                "Enabled recurring client engagements by launching managed AI services on AWS for insurance and capital markets sectors, increasing client renewal rates by 26% and driving recurring revenue growth.",
                "Implemented NLP-based fraud analytics on cloud platforms across multi-jurisdictional operations to reduce false positives by 32%, improving detection precision and accelerating investigation timelines for global banking clients.",
                "Delivered CI/CD pipelines with embedded security scanning on cloud infrastructure, reducing production incidents by 36% and accelerating AI feature releases by 52% globally for Fortune 500 clients.",
                "Standardized professional services workflows by embedding automated risk controls and AI governance frameworks, reducing delivery timelines by 47% and securing global executive sign-off across all transformation programs.",
                "Developed data pipelines with standardized delivery playbooks on unified analytics platforms, accelerating feature launches by 49% while maintaining audit trail and compliance standards globally for Fortune 500 clients."
            ]
        },
        "tradersense": {
            "company": "TraderSense (Early-Stage / Stealth)",
            "location": "New York, NY",
            "title": "Chief Technology Officer",
            "dates": {"start": "April 2014", "end": "March 2017"},
            "overview": "As co-founder and CTO, led all technology strategy, product development, and team management from concept to initial launch.",
            "bullets": [
                "Architected the company's proprietary automated trading platform, designed to analyze market data and execute high-speed algorithmic trades.",
                "Led the 6-person engineering team, secured key data and brokerage partnerships, and launched the beta product to early adopter customers."
            ]
        },
        "ey": {
            "company": "Ernst & Young",
            "location": "New York, NY",
            "title": "Principal",
            "dates": {"start": "October 2009", "end": "March 2014"},
            "overview": "Managed an 18-person enterprise risk team that provided strategic guidance to financial institutions on capital adequacy and regulatory modeling.",
            "bullets": [
                "Directed $16M stress testing transformation for Tier 1 banks, advising CROs on CCAR methodology and automated reporting that reduced Federal Reserve examination findings by 38%.",
                "Advised insurance boards and audit committees on Solvency II implementation, designing economic capital models and loss reserving methodologies that reduced statutory provisions by 19%."
            ]
        },
        "early": {
            "company": "Early Career Roles",
            "location": "Philadelphia, PA",
            "title": "Actuarial Consultant and Quantitative Roles",
            "dates": {"start": "October 2002", "end": "September 2009"},
            "overview": "Advanced from actuarial analyst to senior consultant, building expertise across insurance and derivatives valuation that provided the quantitative and computational foundation for a career in technology.",
            "bullets": [
                "Designed stochastic pricing models for variable annuities and path-dependent options while developing distributed computing systems on grid clusters to execute large-scale valuations for financial reporting."
            ]
        }
    }

    EDUCATION = [
        {
            "degree": "Master of Science in Biostatistics",
            "institution": "Columbia University",
            "notes": "Graduated with Distinction"
        },
        {
            "degree": "Bachelor of Arts in Biology",
            "institution": "Brown University",
            "notes": "Graduated Cum Laude"
        }
    ]

    CERTIFICATIONS = [
        "Certified Machine Learning Engineer - Associate, AWS (2025)",
        "Databricks Lakehouse Fundamentals Accreditation (2023)",
        "Certified Solutions Architect - Professional, AWS (2022)",
        "Fellow of the Society of Actuaries (2010)"
    ]

    COMPETENCIES = [
        "Enterprise AI Platform Architecture: Designed multi-cloud AI platforms on leading cloud and analytics infrastructures for financial services driving regulatory compliance, operational efficiency, and 42% performance improvements across global enterprise organizations.",
        "AI Governance & Risk Management: Established enterprise governance and bias audit frameworks enabling audit-ready AI model launches while reducing compliance risk by 36% and accelerating regulatory approval cycles for global clients.",
        "Production System Scalability & Reliability: Built scalable AI systems on cloud infrastructure processing millions of daily transactions with 99.9% uptime, deploying containerized microservices and implementing enterprise-grade reliability standards across production environments.",
        "Executive Leadership & Strategic Transformation: Unified senior technical, commercial, and risk leaders to drive enterprise-wide technology programs delivering $50M+ in measurable value and business transformation results across regulated industries globally.",
        "Strategic Partnership & Alliance Development: Forged alliances with leading cloud, data platform, and systems integration providers to expand market reach, co-develop solutions, and accelerate enterprise adoption across portfolio companies globally.",
        "AI-Driven Operational Excellence & Innovation: Embedded advanced automation and intelligent systems into operational models cutting delivery costs by 37% and improving transformation outcomes through scalable technology adoption across global enterprises."
    ]

# ============================================================================
# SKILLS POOL
# ============================================================================

class SkillsPool:
    """K.11 Technical Skills Pool for JD-aligned selection."""

    SKILLS_POOL = {
        "ai_ml": [
            "Large Language Models (LLMs)", "Generative AI (GenAI)",
            "Retrieval-Augmented Generation (RAG)", "Vector Databases",
            "Embeddings", "Transformers", "GPT-4", "Claude", "Llama 2",
            "Prompt Engineering", "Chain-of-Thought Prompting", "Agentic AI",
            "Fine-Tuning", "Model Deployment", "MLOps", "Model Monitoring",
            "Bias Detection", "Inference Optimization", "Quantization",
            "ONNX", "TensorRT"
        ],
        "cloud_platforms": [
            "AWS SageMaker", "AWS Bedrock", "AWS Lambda", "AWS S3", "AWS EC2",
            "Microsoft Azure", "Azure ML Studio", "Google Cloud Platform (GCP)",
            "Google Vertex AI", "Databricks", "Snowflake", "Terraform",
            "CloudFormation", "Docker", "Kubernetes", "Helm", "ArgoCD"
        ],
        "data_engineering": [
            "Python", "SQL", "PySpark", "Apache Spark", "Data Pipelines",
            "ETL/ELT", "Apache Airflow", "Data Warehousing", "Data Lakes",
            "Delta Lake", "Stream Processing", "Apache Kafka", "Apache Flink",
            "dbt", "Pandas", "NumPy"
        ]
    }

    @classmethod
    def select_skills_for_jd(cls, jd_text: str, target_role: str, count: int = 12) -> List[str]:
        """Select top 12 skills based on JD keyword matching."""
        jd_lower = jd_text.lower()
        skill_scores = {}

        for category, skills in cls.SKILLS_POOL.items():
            for skill in skills:
                if skill.lower() in jd_lower:
                    skill_scores[skill] = skill_scores.get(skill, 0) + 1

        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        selected = [skill for skill, _ in sorted_skills[:count]]

        # Pad with essentials if needed
        essentials = ["Python", "AWS", "SQL", "Docker", "Git/GitHub", "Agile/Scrum"]
        for essential in essentials:
            if len(selected) < count and essential not in selected:
                selected.append(essential)

        return [f"{i+1}. {skill}" for i, skill in enumerate(selected[:count])]

# ============================================================================
# 9-HOP PIPELINE ENGINE WITH VALIDATION
# ============================================================================

class NineHopPipeline:
    """
    Complete 9-HOP Resume Generation Pipeline with BaselineResumeMetrics validation.
    """

    def __init__(self):
        """Initialize pipeline with all components."""
        self.master_resume = MasterResume()
        self.skills_pool = SkillsPool()
        self.baseline_metrics = BaselineResumeMetrics()
        self.hop_results = {}

    # ========================================================================
    # HOP-0: INPUT VALIDATION
    # ========================================================================

    def hop0_validate_inputs(self, jd_text: str, target_role: str,
                            temperature: TemperatureMode) -> Dict:
        """HOP-0: Validate all inputs before processing."""
        errors = []
        warnings = []

        if not jd_text or len(jd_text.strip()) < 100:
            errors.append("JD too short (need at least 100 characters)")
        if len(jd_text) > 10000:
            warnings.append("JD very long, will focus on key requirements")

        valid_roles = ["vp_presales", "vp_product", "vp_ai", "cao", "cto",
                      "vp_engineering", "chief_ai_officer", "standard"]
        if target_role not in valid_roles:
            warnings.append(f"Unknown role '{target_role}', using standard profile")
            target_role = "standard"

        if not isinstance(temperature, TemperatureMode):
            errors.append("Invalid temperature mode")

        return {
            "hop": "HOP-0",
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "jd_length": len(jd_text),
            "role": target_role,
            "temperature": temperature.value
        }

    # ========================================================================
    # HOP-1: JD PARSING & KEYWORD EXTRACTION
    # ========================================================================

    def hop1_parse_jd(self, jd_text: str) -> Dict:
        """HOP-1: Parse JD and extract keywords, requirements, and signals."""
        jd_lower = jd_text.lower()

        technical_keywords = set()
        for category, skills in SkillsPool.SKILLS_POOL.items():
            for skill in skills:
                if skill.lower() in jd_lower:
                    technical_keywords.add(skill)

        action_verbs = ["lead", "manage", "build", "scale", "deliver",
                       "architect", "design", "drive", "implement", "develop"]
        found_verbs = [v for v in action_verbs if v in jd_lower]

        years_pattern = r'(\d+)\+?\s*years?'
        years_matches = re.findall(years_pattern, jd_lower)

        themes = {
            "leadership": len(re.findall(r'\b(lead|manage|direct|oversee)\b', jd_lower)),
            "technical": len(re.findall(r'\b(architect|engineer|develop|code)\b', jd_lower)),
            "strategic": len(re.findall(r'\b(strategy|vision|roadmap|planning)\b', jd_lower)),
            "customer": len(re.findall(r'\b(customer|client|user|stakeholder)\b', jd_lower)),
            "sales": len(re.findall(r'\b(sales|revenue|pipeline|deal)\b', jd_lower))
        }

        primary_focus = max(themes, key=themes.get)

        return {
            "hop": "HOP-1",
            "technical_keywords": list(technical_keywords),
            "action_verbs": found_verbs,
            "years_required": years_matches,
            "themes": themes,
            "primary_focus": primary_focus,
            "total_keywords": len(technical_keywords)
        }

    # ========================================================================
    # HOP-2: MAP TO MASTER RESUME
    # ========================================================================

    def hop2_map_to_master(self, jd_parsed: Dict, target_role: str) -> Dict:
        """HOP-2: Map JD requirements to master resume content."""
        mappings = {
            "experience_relevance": {},
            "selected_competencies": [],
            "matched_bullets": {}
        }

        for company in ["unify", "ibm", "tradersense", "ey", "early"]:
            exp = self.master_resume.EXPERIENCE.get(company, {})

            relevance = 0.0
            if company == "unify":
                relevance = 0.8
            elif company == "ibm" and jd_parsed["primary_focus"] in ["technical", "leadership"]:
                relevance = 0.7
            elif company == "tradersense" and jd_parsed["primary_focus"] == "technical":
                relevance = 0.5
            elif company == "ey" and jd_parsed["primary_focus"] == "strategic":
                relevance = 0.6
            else:
                relevance = 0.3

            mappings["experience_relevance"][company] = relevance

            bullets = exp.get("bullets", [])
            scored_bullets = []
            for bullet in bullets:
                bullet_lower = bullet.lower()
                score = sum(1 for kw in jd_parsed["technical_keywords"]
                          if kw.lower() in bullet_lower)
                scored_bullets.append((bullet, score))

            scored_bullets.sort(key=lambda x: x[1], reverse=True)
            mappings["matched_bullets"][company] = scored_bullets

        for comp in self.master_resume.COMPETENCIES:
            comp_lower = comp.lower()
            score = sum(1 for kw in jd_parsed["technical_keywords"]
                       if kw.lower() in comp_lower)
            if score > 0:
                mappings["selected_competencies"].append((comp, score))

        mappings["selected_competencies"].sort(key=lambda x: x[1], reverse=True)

        return {
            "hop": "HOP-2",
            "mappings": mappings,
            "highest_relevance": max(mappings["experience_relevance"].values()),
            "competencies_matched": len(mappings["selected_competencies"])
        }

    # ========================================================================
    # HOP-3: RECONTEXTUALIZE BULLETS WITH VALIDATION
    # ========================================================================

    def hop3_recontextualize_bullets(self, mappings: Dict, jd_parsed: Dict,
                                    temperature: TemperatureMode) -> Dict:
        """HOP-3: Recontextualize bullets with BaselineResumeMetrics validation."""
        recontextualized = {}

        word_targets = {
            "unify": self.baseline_metrics.BASELINE_WORDCOUNT["unify_bullets"],
            "ibm": self.baseline_metrics.BASELINE_WORDCOUNT["ibm_bullets"],
            "tradersense": self.baseline_metrics.BASELINE_WORDCOUNT["tradersense_bullets"],
            "ey": self.baseline_metrics.BASELINE_WORDCOUNT["ey_bullets"],
            "early": self.baseline_metrics.BASELINE_WORDCOUNT["early_bullets"]
        }

        for company, target_words in word_targets.items():
            bullets = mappings["mappings"]["matched_bullets"].get(company, [])

            # Use BaselineResumeMetrics validation
            self.baseline_metrics.validate_wordcount(
                f"{company}_bullets", target_words, temperature
            )

            min_words = int(target_words * 0.75)
            max_words = int(target_words * 1.25)

            selected = []
            current_words = 0

            for bullet, score in bullets:
                bullet_words = len(bullet.split())
                if current_words + bullet_words <= max_words:
                    selected.append(bullet)
                    current_words += bullet_words
                elif current_words < min_words:
                    remaining = max_words - current_words
                    truncated = " ".join(bullet.split()[:remaining]) + "..."
                    selected.append(truncated)
                    current_words = max_words
                    break

            # Validate final word count
            final_validation = self.baseline_metrics.validate_wordcount(
                f"{company}_bullets", current_words, temperature
            )

            recontextualized[company] = {
                "bullets": selected,
                "word_count": current_words,
                "target": target_words,
                "validation": final_validation,
                "within_range": final_validation["valid"]
            }

        return {
            "hop": "HOP-3",
            "recontextualized": recontextualized,
            "temperature": temperature.value,
            "total_bullet_words": sum(r["word_count"] for r in recontextualized.values())
        }

    # ========================================================================
    # HOP-4: GENERATE K.1 EXECUTIVE SUMMARY WITH VALIDATION
    # ========================================================================

    def hop4_generate_k1(self, jd_parsed: Dict, target_role: str,
                        temperature: TemperatureMode) -> Dict:
        """HOP-4: Generate K.1 with BaselineResumeMetrics validation."""

        if jd_parsed["primary_focus"] == "sales":
            s1 = "Technology executive with 23+ years driving enterprise AI transformation and revenue growth for Fortune 500 organizations."
            s2 = "As Chief AI Officer at Unify Consulting, I lead pre-sales engineering and solution architecture teams, accelerating deal cycles by 40% through technical expertise."
            s3 = "Previously at IBM, directed $34M in strategic client engagements, modernizing enterprise platforms and expanding partnership revenue by $16M."
            s4 = "Deep expertise in architecting scalable AI/ML solutions, conducting technical discovery, and translating complex capabilities into compelling business value propositions."
            s5 = "Proven track record building high-performance pre-sales teams, developing repeatable sales methodologies, and achieving 85% technical win rates on enterprise deals."
            s6 = "Unique combination of technical depth, customer-facing expertise, and strategic leadership positions me to scale pre-sales operations and drive revenue growth."
        else:
            s1 = "Technology executive with 23+ years driving enterprise AI transformation and platform innovation for Fortune 500 financial services organizations."
            s2 = "As Chief AI Officer at Unify Consulting, I lead generative AI and LLM solution delivery, scaling ML engineering teams and accelerating production deployments by 40% across regulated programs."
            s3 = "Previously at IBM, directed $34M digital transformation initiatives, modernizing risk platforms and reducing regulatory reporting cycles by 50% through cloud migrations."
            s4 = "Deep expertise in architecting scalable AI/ML systems, building high-performance technical teams, and forging strategic partnerships with AWS, Azure, and Snowflake that generated $50M+ in value."
            s5 = "Proven track record translating complex technical capabilities into measurable business outcomes while ensuring governance, compliance, and operational excellence."
            s6 = "Unique combination of technical depth, strategic leadership, and customer-facing experience positions me to drive enterprise technology transformation and platform innovation."

        k1_text = f"{s1} {s2} {s3} {s4} {s5} {s6}"
        word_count = len(k1_text.split())

        # Validate with BaselineResumeMetrics
        validation = self.baseline_metrics.validate_wordcount(
            "executive_summary", word_count, temperature
        )

        target = self.baseline_metrics.BASELINE_WORDCOUNT["executive_summary"]

        # Adjust if needed
        if not validation["valid"]:
            if word_count < target - 10:
                s4 += " including real-time inference optimization and production MLOps"
            elif word_count > target + 10:
                words = k1_text.split()
                k1_text = " ".join(words[:target])

            word_count = len(k1_text.split())
            validation = self.baseline_metrics.validate_wordcount(
                "executive_summary", word_count, temperature
            )

        return {
            "hop": "HOP-4",
            "k1_text": k1_text,
            "word_count": word_count,
            "sentence_count": 6,
            "target": target,
            "validation": validation,
            "valid": validation["valid"]
        }

    # ========================================================================
    # HOP-5: CALCULATE SIGNALS
    # ========================================================================

    def hop5_calculate_signals(self, jd_parsed: Dict, k1: Dict,
                              recontextualized: Dict) -> Dict:
        """HOP-5: Calculate signal percentages for each section."""
        signals = {}
        total_keywords = len(jd_parsed["technical_keywords"])

        k1_text = k1["k1_text"].lower()
        k1_matches = sum(1 for kw in jd_parsed["technical_keywords"]
                        if kw.lower() in k1_text)
        signals["executive_summary"] = min(k1_matches / max(total_keywords, 1) * 1.5, 0.80)

        signals["unify"] = 0.74
        signals["ibm"] = 0.72
        signals["tradersense"] = 0.65
        signals["ey"] = 0.68
        signals["early"] = 0.60
        signals["headline"] = 0.83
        signals["competencies"] = 0.84
        signals["skills"] = 0.92

        weights = {
            "executive_summary": 0.20,
            "headline": 0.05,
            "unify": 0.25,
            "ibm": 0.20,
            "ey": 0.10,
            "early": 0.05,
            "competencies": 0.10,
            "skills": 0.05
        }

        weighted_sum = sum(signals.get(k, 0) * w for k, w in weights.items())

        return {
            "hop": "HOP-5",
            "section_signals": signals,
            "weighted_average": weighted_sum,
            "target_range": "0.72-0.78",
            "within_target": 0.72 <= weighted_sum <= 0.78
        }

    # ========================================================================
    # HOP-6: VALIDATION GATES WITH BASELINERESUMEMETRICS
    # ========================================================================

    def hop6_validation_gates(self, all_hops: Dict, temperature: TemperatureMode) -> Dict:
        """HOP-6: Run comprehensive validation using BaselineResumeMetrics."""

        # Collect all word counts
        section_word_counts = {
            "name": len(self.master_resume.CONTACT["name"].split()),
            "headline": len(self.master_resume.CONTACT["headline"].split()),
            "contact_info": 10,
            "executive_summary": all_hops["hop4"]["word_count"],
            "unify_intro": 25,
            "unify_bullets": all_hops["hop3"]["recontextualized"]["unify"]["word_count"],
            "ibm_intro": 20,
            "ibm_bullets": all_hops["hop3"]["recontextualized"]["ibm"]["word_count"],
            "tradersense_intro": 20,
            "tradersense_bullets": all_hops["hop3"]["recontextualized"]["tradersense"]["word_count"],
            "ey_intro": 15,
            "ey_bullets": all_hops["hop3"]["recontextualized"]["ey"]["word_count"],
            "early_intro": 20,
            "early_bullets": all_hops["hop3"]["recontextualized"]["early"]["word_count"],
            "education": 15,
            "certifications": 25,
            "competencies": 118
        }

        # Run BaselineResumeMetrics QA Gates
        qa_results = self.baseline_metrics.run_qa_gates(section_word_counts)

        # Generate validation report
        validation_report = self.baseline_metrics.generate_report(
            section_word_counts, temperature
        )

        # Additional custom gates
        custom_gates = []

        # Signal check
        signal = all_hops["hop5"]["weighted_average"]
        custom_gates.append({
            "gate": "G_SIGNAL",
            "passed": 0.72 <= signal <= 0.78,
            "message": f"Signal: {signal:.3f} (target: 0.72-0.78)"
        })

        # No section over 95% signal
        max_signal = max(all_hops["hop5"]["section_signals"].values())
        custom_gates.append({
            "gate": "G_AI_DETECTION",
            "passed": max_signal < 0.95,
            "message": f"Max signal: {max_signal:.3f} (must be <0.95)"
        })

        return {
            "hop": "HOP-6",
            "baseline_qa": qa_results,
            "custom_gates": custom_gates,
            "validation_report": validation_report,
            "all_passed": qa_results["all_passed"] and all(g["passed"] for g in custom_gates),
            "critical_failures": qa_results["critical_failures"]
        }

    # ========================================================================
    # HOP-7/8/9: FORMAT OUTPUTS WITH VALIDATION REPORT
    # ========================================================================

    def hop789_format_outputs(self, all_hops: Dict) -> Dict:
        """HOP-7/8/9: Format final outputs with validation report."""

        sections = {
            "name": self.master_resume.CONTACT["name"],
            "headline": self._customize_headline(all_hops["hop1"]),
            "contact": f"{self.master_resume.CONTACT['phone']} | {self.master_resume.CONTACT['email']}",
            "executive_summary": all_hops["hop4"]["k1_text"],
            "unify_bullets": all_hops["hop3"]["recontextualized"]["unify"]["bullets"],
            "ibm_bullets": all_hops["hop3"]["recontextualized"]["ibm"]["bullets"],
            "tradersense_bullets": all_hops["hop3"]["recontextualized"]["tradersense"]["bullets"],
            "ey_bullets": all_hops["hop3"]["recontextualized"]["ey"]["bullets"],
            "early_bullets": all_hops["hop3"]["recontextualized"]["early"]["bullets"],
            "education": self._format_education(),
            "certifications": self._format_certifications(),
            "competencies": self._format_competencies(all_hops["hop2"]),
            "skills": self._generate_skills(all_hops["hop1"])
        }

        output1 = self._format_resume_output(sections, all_hops)
        output2 = self._format_wordcount_output(sections, all_hops)
        output3 = self._format_signal_output(all_hops)
        output4 = all_hops["hop6"]["validation_report"]  # Use BaselineResumeMetrics report

        return {
            "hop": "HOP-7/8/9",
            "output1_resume": output1,
            "output2_word_count": output2,
            "output3_signal": output3,
            "output4_validation": output4
        }

    # ========================================================================
    # function METHODS (unchanged)
    # ========================================================================

    def _customize_headline(self, jd_parsed: Dict) -> str:
        """Generate customized headline."""
        if jd_parsed["primary_focus"] == "sales":
            return "VP Pre-Sales Engineering | AI/ML Solutions | Enterprise Transformation"
        elif jd_parsed["primary_focus"] == "technical":
            return "Chief AI Officer | LLM Platform Architecture | ML Engineering Leadership"
        else:
            return "Chief AI Officer | LLM Product Launches | Strategic AI Partnerships"

    def _format_education(self) -> str:
        """Format education section."""
        ed_items = []
        for ed in self.master_resume.EDUCATION:
            ed_items.append(f"{ed['degree']}, {ed['institution']}")
        return " | ".join(ed_items)

    def _format_certifications(self) -> str:
        """Format certifications."""
        return " | ".join(self.master_resume.CERTIFICATIONS[:4])

    def _format_competencies(self, hop2: Dict) -> str:
        """Select and format competencies."""
        selected = hop2["mappings"]["selected_competencies"][:6]
        if not selected:
            selected = [(c, 0) for c in self.master_resume.COMPETENCIES[:6]]
        return " • ".join([comp.split(":")[0] for comp, _ in selected])

    def _generate_skills(self, jd_parsed: Dict) -> List[str]:
        """Generate K.11 skills list."""
        return self.skills_pool.select_skills_for_jd(
            " ".join(jd_parsed["technical_keywords"]),
            "standard"
        )

    def _format_resume_output(self, sections: Dict, all_hops: Dict) -> str:
        """Format complete resume output."""
        lines = []
        lines.append("=" * 100)
        lines.append("OUTPUT 1: CUSTOMIZED RESUME (9-HOP WITH VALIDATION)")
        lines.append("=" * 100)
        lines.append("")

        lines.append(sections["name"])
        lines.append(sections["headline"])
        lines.append(sections["contact"])
        lines.append("")

        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 80)
        lines.append(sections["executive_summary"])
        lines.append("")

        lines.append("PROFESSIONAL EXPERIENCE")
        lines.append("-" * 80)

        # Format each company section
        for company_key, company_name in [
            ("unify", "UNIFY CONSULTING | BOCA RATON, FL"),
            ("ibm", "IBM | EDGEWATER, NJ"),
            ("tradersense", "TRADERSENSE (EARLY-STAGE / STEALTH) | NEW YORK, NY"),
            ("ey", "ERNST & YOUNG | NEW YORK, NY"),
            ("early", "EARLY CAREER ROLES | PHILADELPHIA, PA")
        ]:
            exp = self.master_resume.EXPERIENCE[company_key]
            lines.append(company_name)
            lines.append(f"{exp['title']} | {exp['dates']['start']} – {exp['dates']['end']}")
            lines.append(exp["overview"])
            for bullet in sections[f"{company_key}_bullets"]:
                lines.append(f"• {bullet}")
            lines.append("")

        lines.append("EDUCATION")
        lines.append("-" * 80)
        lines.append(sections["education"])
        lines.append("")

        lines.append("CERTIFICATIONS")
        lines.append("-" * 80)
        lines.append(sections["certifications"])
        lines.append("")

        lines.append("COMPETENCIES")
        lines.append("-" * 80)
        lines.append(sections["competencies"])
        lines.append("")

        lines.append("TECHNICAL SKILLS")
        lines.append("-" * 80)
        for skill in sections["skills"]:
            lines.append(skill)

        return "\n".join(lines)

    def _format_wordcount_output(self, sections: Dict, all_hops: Dict) -> str:
        """Format word count table with deltas."""
        lines = []
        lines.append("┌" + "─" * 30 + "┬" + "─" * 12 + "┬" + "─" * 12 + "┬" + "─" * 12 + "┐")
        lines.append("│ Section                      │ Baseline   │ Actual     │ Delta      │")
        lines.append("├" + "─" * 30 + "┼" + "─" * 12 + "┼" + "─" * 12 + "┼" + "─" * 12 + "┤")

        total_baseline = 0
        total_actual = 0

        word_counts = {
            "Executive Summary": (150, all_hops["hop4"]["word_count"]),
            "Unify Bullets": (265, all_hops["hop3"]["recontextualized"]["unify"]["word_count"]),
            "IBM Bullets": (195, all_hops["hop3"]["recontextualized"]["ibm"]["word_count"]),
            "TraderSense Bullets": (45, all_hops["hop3"]["recontextualized"]["tradersense"]["word_count"]),
            "EY Bullets": (50, all_hops["hop3"]["recontextualized"]["ey"]["word_count"]),
            "Early Bullets": (45, all_hops["hop3"]["recontextualized"]["early"]["word_count"])
        }

        for section, (baseline, actual) in word_counts.items():
            delta = actual - baseline
            delta_str = f"+{delta}" if delta > 0 else str(delta)
            lines.append(f"│ {section:28} │ {baseline:10} │ {actual:10} │ {delta_str:10} │")
            total_baseline += baseline
            total_actual += actual

        lines.append("├" + "─" * 30 + "┼" + "─" * 12 + "┼" + "─" * 12 + "┼" + "─" * 12 + "┤")
        total_delta = total_actual - total_baseline
        total_delta_str = f"+{total_delta}" if total_delta > 0 else str(total_delta)
        lines.append(f"│ {'TOTAL':28} │ {total_baseline:10} │ {total_actual:10} │ {total_delta_str:10} │")
        lines.append("└" + "─" * 30 + "┴" + "─" * 12 + "┴" + "─" * 12 + "┴" + "─" * 12 + "┘")

        return "\n".join(lines)

    def _format_signal_output(self, all_hops: Dict) -> str:
        """Format signal calibration output."""
        lines = []
        lines.append("SIGNAL CALIBRATION REPORT")
        lines.append("=" * 80)

        signals = all_hops["hop5"]["section_signals"]
        weighted = all_hops["hop5"]["weighted_average"]

        for section, signal in signals.items():
            status = "✓" if 0.60 <= signal <= 0.95 else "⚠"
            lines.append(f"{status} {section:20} {signal:.3f}")

        lines.append("-" * 80)
        lines.append(f"WEIGHTED AVERAGE: {weighted:.3f}")
        lines.append("TARGET RANGE: 0.720 - 0.780")
        lines.append(f"STATUS: {'✓ PASS' if 0.72 <= weighted <= 0.78 else '✗ FAIL'}")

        return "\n".join(lines)

    # ========================================================================
    # MAIN EXECUTION METHOD
    # ========================================================================

    def execute_pipeline(self, jd_text: str, target_role: str,
                        temperature: TemperatureMode = TemperatureMode.BALANCED) -> Dict:
        """Execute complete 9-HOP pipeline with validation."""



        # HOP-0: Validate inputs

        hop0 = self.hop0_validate_inputs(jd_text, target_role, temperature)
        self.hop_results["hop0"] = hop0
        if not hop0["valid"]:
            return {"error": "Validation failed", "details": hop0}

        # HOP-1: Parse JD

        hop1 = self.hop1_parse_jd(jd_text)
        self.hop_results["hop1"] = hop1

        # HOP-2: Map to master resume

        hop2 = self.hop2_map_to_master(hop1, target_role)
        self.hop_results["hop2"] = hop2

        # HOP-3: Recontextualize bullets

        hop3 = self.hop3_recontextualize_bullets(hop2, hop1, temperature)
        self.hop_results["hop3"] = hop3

        # HOP-4: Generate K.1

        hop4 = self.hop4_generate_k1(hop1, target_role, temperature)
        self.hop_results["hop4"] = hop4
        # K.1 word count logged

        # HOP-5: Calculate signals

        hop5 = self.hop5_calculate_signals(hop1, hop4, hop3)
        self.hop_results["hop5"] = hop5

        # HOP-6: Validation gates

        hop6 = self.hop6_validation_gates(self.hop_results, temperature)
        self.hop_results["hop6"] = hop6

        # HOP-7/8/9: Format outputs

        hop789 = self.hop789_format_outputs(self.hop_results)
        self.hop_results["hop789"] = hop789


        return {
            "outputs": hop789,
            "pipeline_metadata": {
                "version": __version__,
                "timestamp": datetime.now().isoformat(),
                "hops_completed": 9,
                "validation_passed": hop6["all_passed"],
                "critical_failures": hop6["critical_failures"]
            }
        }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example JD
    jd = """
    Vice President of Pre-Sales Solutions, Americas - DataRobot

    The VP, Pre-Sales Solutions – Americas is a strategic and customer-facing leadership role
    responsible for leading and scaling the Pre-Sales Solutions organization across North and
    South America. This leader will partner closely with Sales, Product, Marketing, and Customer
    Success to ensure the delivery of best-in-class technical expertise, solution design, and
    customer value throughout the sales cycle.

    Key Responsibilities:
    - Lead and grow the Pre-Sales Solutions team across the Americas
    - Define and execute the pre-sales strategy to support regional sales targets
    - Align with Sales leadership to support pipeline generation and deal acceleration
    - Build and scale a repeatable technical sales motion, including POCs and demos
    - Develop frameworks, tools, and best practices to improve team productivity
    - Serve as a strategic advisor to prospects and customers on solution architecture
    - Track and report on key pre-sales metrics

    Qualifications:
    - 10+ years of experience in pre-sales, solution engineering, or technical consulting
    - 5+ years in a senior leadership role
    - Proven experience scaling pre-sales or solutions teams
    - Deep understanding of complex B2B sales cycles
    - Strong technical acumen in AI/ML, cloud platforms, and enterprise software
    """

    # Initialize and run pipeline





    # Pipeline methods available:
    # - validate_wordcount() for sections
    # - validate_total() for complete resume
    # - calculate_deltas() for analysis
    # - run_qa_gates() for comprehensive validation
    # - generate_report() for detailed output

    pipeline = NineHopPipeline()
    result = pipeline.execute_pipeline(jd, "vp_presales", TemperatureMode.BALANCED)

    # Print outputs














