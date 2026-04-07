"""Industry-Specific VLLM Prompt Templates.

This module provides specialized prompt templates for different industries
and use cases to ensure domain-appropriate vLLM responses.
"""

from typing import Any


class IndustryPromptTemplates:
    """Industry-specific prompt templates for vLLM generation."""

    @staticmethod
    def healthcare_analysis(content: str, analysis_type: str = "clinical") -> str:
        """Healthcare industry analysis prompt.

        Args:
            content: Medical content to analyze
            analysis_type: Type of healthcare analysis

        Returns:
            Healthcare-specific prompt
        """
        prompt = f"""HEALTHCARE ANALYSIS REQUEST

ANALYSIS TYPE: {analysis_type}

MEDICAL CONTENT:
{content}

INSTRUCTIONS:
Please provide a comprehensive healthcare analysis that includes:
1. Clinical Assessment
2. Risk Factors Identification
3. Treatment Considerations
4. Patient Safety Implications
5. Regulatory Compliance (HIPAA, FDA, etc.)
6. Evidence-Based Recommendations

IMPORTANT: This analysis is for informational purposes only and does not constitute medical advice.
Always consult qualified healthcare professionals for medical decisions.

Ensure compliance with healthcare privacy regulations and maintain professional medical terminology.
"""

        return prompt

    @staticmethod
    def finance_proposal(
        opportunity: str,
        requirements: list[str],
        risk_factors: list[str],
        financial_constraints: dict[str, Any],
    ) -> str:
        """Financial services proposal prompt.

        Args:
            opportunity: Business opportunity description
            requirements: List of financial requirements
            risk_factors: List of risk factors
            financial_constraints: Financial constraints and limits

        Returns:
        Finance-specific prompt
        """
        requirements_text = "\n".join(f"- {req}" for req in requirements)
        risks_text = "\n".join(f"- {risk}" for risk in risk_factors)
        constraints_text = "\n".join(f"{k}: {v}" for k, v in financial_constraints.items())

        prompt = f"""FINANCIAL SERVICES PROPOSAL REQUEST

BUSINESS OPPORTUNITY:
{opportunity}

REQUIREMENTS:
{requirements_text}

RISK FACTORS:
{risks_text}

FINANCIAL CONSTRAINTS:
{constraints_text}

INSTRUCTIONS:
Please generate a comprehensive financial services proposal that includes:
1. Executive Summary with ROI projections
2. Service Offering Details
3. Pricing Structure and Fee Schedule
4. Risk Management Framework
5. Compliance and Regulatory Considerations
6. Implementation Timeline
7. Success Metrics and KPIs
8. Terms and Conditions

Ensure adherence to financial regulations (SEC, FINRA, etc.) and include appropriate disclaimers.
Focus on value proposition, risk mitigation, and measurable financial outcomes.
"""

        return prompt

    @staticmethod
    def technical_documentation(
        system_description: str, technical_requirements: list[str], audience: str = "technical",
    ) -> str:
        """Technical documentation prompt.

        Args:
            system_description: Description of the system or technology
            technical_requirements: List of technical requirements
            audience: Target audience (technical, business, mixed)

        Returns:
        Technical documentation prompt
        """
        requirements_text = "\n".join(f"- {req}" for req in technical_requirements)

        audience_instructions = {
            "technical": "Use detailed technical terminology and include implementation details.",
            "business": "Focus on business value, outcomes, and high-level technical concepts.",
            "mixed": "Balance technical details with business implications and benefits.",
        }

        instruction = audience_instructions.get(audience, audience_instructions["mixed"])

        prompt = f"""TECHNICAL DOCUMENTATION REQUEST

SYSTEM DESCRIPTION:
{system_description}

TECHNICAL REQUIREMENTS:
{requirements_text}

TARGET AUDIENCE: {audience}

INSTRUCTIONS:
{instruction}

Please generate comprehensive technical documentation that includes:
1. System Overview and Architecture
2. Technical Specifications
3. API Documentation (if applicable)
4. Integration Guidelines
5. Performance Requirements
6. Security Considerations
7. Troubleshooting Guide
8. Maintenance Procedures

Ensure accuracy, clarity, and completeness. Include diagrams and examples where appropriate.
Follow industry standards and best practices for technical documentation.
"""

        return prompt

    @staticmethod
    def legal_compliance_check(content: str, jurisdiction: str, compliance_type: str = "general") -> str:
        """Legal compliance analysis prompt.

        Args:
            content: Content to check for compliance
            jurisdiction: Legal jurisdiction
            compliance_type: Type of compliance check

        Returns:
        Legal compliance prompt
        """
        prompt = f"""LEGAL COMPLIANCE ANALYSIS REQUEST

JURISDICTION: {jurisdiction}
COMPLIANCE TYPE: {compliance_type}

CONTENT TO ANALYZE:
{content}

INSTRUCTIONS:
Please provide a thorough legal compliance analysis that includes:
1. Compliance Assessment
2. Risk Identification
3. Regulatory Requirements
4. Recommended Changes
5. Documentation Requirements
6. Monitoring and Reporting

DISCLAIMER: This analysis is for informational purposes only and does not constitute legal advice.
Consult qualified legal counsel for specific legal matters.

Ensure consideration of relevant laws, regulations, and industry standards for the specified jurisdiction.
"""

        return prompt

    @staticmethod
    def marketing_content(
        product: str, target_audience: str, value_proposition: str, content_type: str = "general",
    ) -> str:
        """Marketing content generation prompt.

        Args:
            product: Product or service description
            target_audience: Target audience description
            value_proposition: Key value proposition
            content_type: Type of marketing content

        Returns:
        Marketing content prompt
        """
        content_instructions = {
            "email": "Create compelling email marketing copy with subject line and call-to-action.",
            "social": "Generate engaging social media content with hashtags and engagement prompts.",
            "website": "Create website copy that is SEO-friendly and conversion-focused.",
            "brochure": "Develop brochure content with clear sections and visual appeal.",
            "video": "Write video script content with scenes and timing.",
            "general": "Create versatile marketing content adaptable to multiple channels.",
        }

        instruction = content_instructions.get(content_type, content_instructions["general"])

        prompt = f"""MARKETING CONTENT GENERATION REQUEST

PRODUCT/SERVICE:
{product}

TARGET AUDIENCE:
{target_audience}

VALUE PROPOSITION:
{value_proposition}

CONTENT TYPE: {content_type}

INSTRUCTIONS:
{instruction}

Please generate marketing content that includes:
1. Compelling Headline/Subject
2. Key Benefits and Features
3. Emotional Appeal
4. Clear Call-to-Action
5. Brand Voice Consistency
6. Audience-Specific Language
7. Measurable Objectives

Ensure the content is persuasive, authentic, and aligned with marketing best practices.
Include appropriate disclaimers and compliance considerations where applicable.
"""

        return prompt

    @staticmethod
    def research_synthesis(
        research_topic: str, sources: list[dict[str, Any]], synthesis_type: str = "comprehensive",
    ) -> str:
        """Research synthesis prompt for academic/scientific content.

        Args:
            research_topic: Main research topic
            sources: List of research sources
            synthesis_type: Type of synthesis required

        Returns:
        Research synthesis prompt
        """
        sources_text = ""
        for i, source in enumerate(sources[:8], 1):
            sources_text += f"\nSOURCE {i}:\n"
            sources_text += f"Title: {source.get('title', 'Untitled')}\n"
            sources_text += f"Authors: {source.get('authors', 'Unknown')}\n"
            sources_text += f"Year: {source.get('year', 'Unknown')}\n"
            sources_text += f"Key Findings: {source.get('findings', 'No findings available')[:300]}...\n"
            sources_text += f"Methodology: {source.get('methodology', 'Not specified')[:200]}...\n"
            sources_text += "---\n"

        synthesis_instructions = {
            "literature_review": "Provide a comprehensive literature review with thematic analysis.",
            "meta_analysis": "Conduct a meta-analysis with statistical synthesis of findings.",
            "systematic_review": "Generate a systematic review following PRISMA guidelines.",
            "comprehensive": "Provide a comprehensive synthesis integrating all sources.",
        }

        instruction = synthesis_instructions.get(synthesis_type, synthesis_instructions["comprehensive"])

        prompt = f"""RESEARCH SYNTHESIS REQUEST

RESEARCH TOPIC: {research_topic}
SYNTHESIS TYPE: {synthesis_type}

SOURCES:
{sources_text}

INSTRUCTIONS:
{instruction}

Please provide a rigorous academic synthesis that includes:
1. Abstract/Executive Summary
2. Introduction and Research Context
3. Methodology of Synthesis
4. Thematic Analysis
5. Key Findings and Patterns
6. Critical Evaluation
7. Research Gaps and Limitations
8. Future Research Directions
9. Conclusions
10. References

Ensure academic rigor, proper citation practices, and scholarly tone.
Maintain objectivity and acknowledge methodological limitations.
"""

        return prompt


class UseCasePromptTemplates:
    """Use-case specific prompt templates."""

    @staticmethod
    def risk_assessment(scenario: str, risk_categories: list[str], context: dict[str, Any]) -> str:
        """Risk assessment prompt template.

        Args:
            scenario: Scenario to assess
            risk_categories: List of risk categories to consider
            context: Additional context information

        Returns:
        Risk assessment prompt
        """
        categories_text = "\n".join(f"- {category}" for category in risk_categories)
        context_text = "\n".join(f"{k}: {v}" for k, v in context.items())

        prompt = f"""RISK ASSESSMENT REQUEST

SCENARIO:
{scenario}

RISK CATEGORIES:
{categories_text}

CONTEXT:
{context_text}

INSTRUCTIONS:
Please provide a comprehensive risk assessment that includes:
1. Risk Identification and Categorization
2. Likelihood Assessment (High/Medium/Low)
3. Impact Analysis (Financial, Operational, Reputational)
4. Risk Interdependencies
5. Mitigation Strategies
6. Risk Monitoring Plan
7. Contingency Plans
8. Risk Appetite Alignment

Use standard risk assessment methodologies and provide actionable recommendations.
"""

        return prompt

    @staticmethod
    def process_optimization(current_process: str, objectives: list[str], constraints: list[str]) -> str:
        """Process optimization prompt template.

        Args:
            current_process: Description of current process
            objectives: Optimization objectives
            constraints: Process constraints

        Returns:
        Process optimization prompt
        """
        objectives_text = "\n".join(f"- {obj}" for obj in objectives)
        constraints_text = "\n".join(f"- {constraint}" for constraint in constraints)

        prompt = f"""PROCESS OPTIMIZATION REQUEST

CURRENT PROCESS:
{current_process}

OPTIMIZATION OBJECTIVES:
{objectives_text}

CONSTRAINTS:
{constraints_text}

INSTRUCTIONS:
Please provide a detailed process optimization analysis that includes:
1. Current Process Analysis
2. Bottleneck Identification
3. Efficiency Improvement Opportunities
4. Cost Reduction Strategies
5. Quality Enhancement Measures
6. Technology Integration Options
7. Implementation Roadmap
8. Success Metrics and KPIs
9. Change Management Considerations

Focus on practical, implementable solutions with measurable improvements.
"""

        return prompt

    @staticmethod
    def decision_support(decision_context: str, options: list[dict[str, Any]], criteria: list[str]) -> str:
        """Decision support prompt template.

        Args:
            decision_context: Context for the decision
            options: List of decision options
            criteria: Decision criteria

        Returns:
        Decision support prompt
        """
        options_text = ""
        for i, option in enumerate(options, 1):
            options_text += f"\nOPTION {i}:\n"
            for key, value in option.items():
                options_text += f"{key.title()}: {value}\n"
            options_text += "---\n"

        criteria_text = "\n".join(f"- {criterion}" for criterion in criteria)

        prompt = f"""DECISION SUPPORT ANALYSIS REQUEST

DECISION CONTEXT:
{decision_context}

DECISION OPTIONS:
{options_text}

EVALUATION CRITERIA:
{criteria_text}

INSTRUCTIONS:
Please provide a comprehensive decision analysis that includes:
1. Options Overview
2. Criteria-Based Evaluation
3. Pros and Cons Analysis
4. Risk Assessment for Each Option
5. Cost-Benefit Analysis
6. Stakeholder Impact Assessment
7. Recommendation with Rationale
8. Implementation Considerations
9. Contingency Planning

Ensure objective analysis and clear recommendation based on the provided criteria.
"""

        return prompt
