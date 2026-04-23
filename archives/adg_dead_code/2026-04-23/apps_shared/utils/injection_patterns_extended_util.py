"""Extended Injection Patterns for Resume and Message Enhancement.

This module provides additional injection patterns specifically designed
to improve the quality and effectiveness of resume and message outputs
in the Subatomic Hop system.
"""

from __future__ import annotations


def get_resume_injection_patterns() -> list[InjectionPattern]:
    """Get resume-specific injection patterns."""
    return [
        # Resume summary injections
        InjectionPattern(
            id="resume_summary_professional_brand",
            name="Professional Brand Summary",
            type=InjectionType.RESUME_ENHANCEMENT,
            description="Creates a compelling professional brand statement",
            template="Transform this basic info into a powerful professional brand statement: '{info}'. Highlight unique value proposition, key strengths, and career trajectory. Make it 3-4 lines maximum.",
            variables=["info"],
            scope=InjectionScope(
                hop_types=["resume_writer", "summary_generator"],
                contexts={"section": "summary", "professional_level": True},
            ),
            priority=9,
        ),
        # Experience section injections
        InjectionPattern(
            id="resume_impact_statement",
            name="Impact Statement Formatter",
            type=InjectionType.RESUME_ENHANCEMENT,
            description="Converts responsibilities into impact statements",
            template="Transform this responsibility into an impact statement: '{responsibility}'. Start with strong action verb, include measurable result, and show business impact. Format: 'Action + What + Result + Impact'.",
            variables=["responsibility"],
            scope=InjectionScope(
                hop_types=["resume_writer", "experience_formatter"],
                contexts={"section": "experience", "type": "bullet"},
            ),
            priority=8,
        ),
        InjectionPattern(
            id="resume_tech_stack_optimization",
            name="Tech Stack Optimization",
            type=InjectionType.KEYWORD_OPTIMIZATION,
            description="Optimizes technical skills presentation",
            template="Enhance this tech skills list for {role}: '{skills}'. Group by category, include proficiency levels, and add trending technologies. Consider ATS optimization.",
            variables=["skills", "role"],
            scope=InjectionScope(
                hop_types=["resume_writer", "skills_formatter"],
                contexts={"section": "skills", "technical_role": True},
            ),
            priority=7,
        ),
        # Project section injections
        InjectionPattern(
            id="resume_project STAR_method",
            name="Project STAR Method",
            type=InjectionType.STRUCTURE_IMPROVEMENT,
            description="Formats projects using STAR method",
            template="Restructure this project using STAR method: '{project}'. Situation: What was the context? Task: What was your goal? Action: What did you do? Result: What was the outcome?",
            variables=["project"],
            scope=InjectionScope(
                hop_types=["resume_writer", "project_formatter"],
                contexts={"section": "projects", "needs_structure": True},
            ),
            priority=6,
        ),
        # Education section injections
        InjectionPattern(
            id="resume_education_enhancement",
            name="Education Enhancement",
            type=InjectionType.CONTENT_EXPANSION,
            description="Enhances education section with relevant details",
            template="Enhance this education entry: '{education}'. Add relevant coursework, achievements, GPA if impressive, honors, and extracurricular leadership. Focus on what's relevant to {target_role}.",
            variables=["education", "target_role"],
            scope=InjectionScope(
                hop_types=["resume_writer", "education_formatter"],
                contexts={"section": "education", "recent_grad": True},
            ),
            priority=5,
        ),
        # Certification injections
        InjectionPattern(
            id="resume_certification_value",
            name="Certification Value Proposition",
            type=InjectionType.QUALITY_BOOST,
            description="Highlights value of certifications",
            template="Enhance this certification entry: '{cert}'. Include issuing body, date, and most importantly - what skills/knowledge it demonstrates and how it applies to {industry}.",
            variables=["cert", "industry"],
            scope=InjectionScope(
                hop_types=["resume_writer", "certification_formatter"],
                contexts={"section": "certifications", "professional": True},
            ),
            priority=4,
        ),
    ]


def get_message_injection_patterns() -> list[InjectionPattern]:
    """Get message-specific injection patterns."""
    return [
        # LinkedIn outreach injections
        InjectionPattern(
            id="message_linkedin_connection",
            name="LinkedIn Connection Request",
            type=InjectionType.MESSAGE_PERSONALIZATION,
            description="Creates personalized LinkedIn connection requests",
            template="Write a LinkedIn connection request to {name} at {company}. Reference their {recent_activity} and shared {interest}. Keep it under 300 characters, professional but warm. No sales pitch.",
            variables=["name", "company", "recent_activity", "interest"],
            scope=InjectionScope(
                hop_types=["message_generator", "linkedin_writer"],
                contexts={"platform": "linkedin", "connection_request": True},
            ),
            priority=9,
        ),
        # Cold email injections
        InjectionPattern(
            id="message_cold_email_opener",
            name="Cold Email Opener",
            type=InjectionType.MESSAGE_PERSONALIZATION,
            description="Creates compelling cold email openers",
            template="Craft a cold email opener to {name} that references {company_challenge} and your {solution_value}. Make it intriguing, personalized, and focused on their benefit. Avoid generic praise.",
            variables=["name", "company_challenge", "solution_value"],
            scope=InjectionScope(
                hop_types=["message_generator", "email_writer"],
                contexts={"email_type": "cold", "prospect_aware": True},
            ),
            priority=8,
        ),
        # Follow-up message injections
        InjectionPattern(
            id="message_follow_up_value",
            name="Value-Added Follow-up",
            type=InjectionType.MESSAGE_PERSONALIZATION,
            description="Creates follow-up messages with additional value",
            template="Write a follow-up to {name} after {days_since_contact} days. Reference previous {topic} and add new {value_add}. Keep it brief, helpful, and forward-looking. Include clear next step.",
            variables=["name", "days_since_contact", "topic", "value_add"],
            scope=InjectionScope(
                hop_types=["message_generator", "followup_writer"],
                contexts={"message_type": "followup", "has_context": True},
            ),
            priority=7,
        ),
        # Thank you message injections
        InjectionPattern(
            id="message_interview_thankyou",
            name="Interview Thank You Note",
            type=InjectionType.TONE_ADJUSTMENT,
            description="Creates professional interview thank you notes",
            template="Write a thank you note to {interviewer} after {interview_type} interview at {company}. Reference specific {discussion_point}, reiterate {interest_area}, and address any {concerns_raised}. Keep it genuine and concise.",
            variables=[
                "interviewer",
                "interview_type",
                "company",
                "discussion_point",
                "interest_area",
                "concerns_raised",
            ],
            scope=InjectionScope(
                hop_types=["message_generator", "interview_writer"],
                contexts={"message_type": "thankyou", "post_interview": True},
            ),
            priority=8,
        ),
        # Networking message injections
        InjectionPattern(
            id="message_networking_approach",
            name="Networking Approach Message",
            type=InjectionType.MESSAGE_PERSONALIZATION,
            description="Creates effective networking outreach",
            template="Write a networking message to {contact} via {channel}. Reference {mutual_connection} or shared {background}. Be clear about your {networking_goal} and offer value first. Make it easy to respond.",
            variables=["contact", "channel", "mutual_connection", "background", "networking_goal"],
            scope=InjectionScope(
                hop_types=["message_generator", "networking_writer"],
                contexts={"message_type": "networking", "warm_intro": True},
            ),
            priority=6,
        ),
        # Referral request injections
        InjectionPattern(
            id="message_referral_request",
            name="Referral Request",
            type=InjectionType.TONE_ADJUSTMENT,
            description="Creates tactful referral requests",
            template="Write a referral request to {contact} for {opportunity}. Remind them of your {relationship}, highlight your {qualification_match}, and make it easy to help. Offer to provide materials and respect their time.",
            variables=["contact", "opportunity", "relationship", "qualification_match"],
            scope=InjectionScope(
                hop_types=["message_generator", "referral_writer"],
                contexts={"message_type": "referral", "existing_relationship": True},
            ),
            priority=7,
        ),
    ]


def get_quality_boost_injections() -> list[InjectionPattern]:
    """Get general quality boost injection patterns."""
    return [
        InjectionPattern(
            id="quality_conciseness",
            name="Conciseness Enhancer",
            type=InjectionType.QUALITY_BOOST,
            description="Makes content more concise and impactful",
            template="Make this content more concise and impactful: '{content}'. Remove fluff, use strong verbs, eliminate redundant phrases, and ensure every word adds value. Target {word_count} words maximum.",
            variables=["content", "word_count"],
            scope=InjectionScope(
                hop_types=["content_generator", "editor"],
                contexts={"needs_conciseness": True},
            ),
            priority=6,
        ),
        InjectionPattern(
            id="quality_clarity",
            name="Clarity Improver",
            type=InjectionType.QUALITY_BOOST,
            description="Improves content clarity and readability",
            template="Improve clarity of this content: '{content}'. Simplify complex sentences, define jargon, use active voice, and ensure logical flow. Target {reading_level} reading level.",
            variables=["content", "reading_level"],
            scope=InjectionScope(
                hop_types=["content_generator", "editor"],
                contexts={"needs_clarity": True},
            ),
            priority=5,
        ),
        InjectionPattern(
            id="quality_engagement",
            name="Engagement Booster",
            type=InjectionType.QUALITY_BOOST,
            description="Makes content more engaging and persuasive",
            template="Make this content more engaging: '{content}'. Add storytelling elements, use emotional language, include compelling examples, and end with clear call to action for {audience}.",
            variables=["content", "audience"],
            scope=InjectionScope(
                hop_types=["content_generator", "copywriter"],
                contexts={"needs_engagement": True},
            ),
            priority=7,
        ),
    ]


def load_all_extended_patterns() -> dict[str, InjectionPattern]:
    """Load all extended injection patterns."""
    patterns = {}

    # Load all pattern types
    for pattern_list in [
        get_resume_injection_patterns(),
        get_message_injection_patterns(),
        get_quality_boost_injections(),
    ]:
        for pattern in pattern_list:
            patterns[pattern.id] = pattern

    return patterns


# Usage example for integration with PromptInjectionLoader
def extend_injection_loader(loader):
    """Extend an existing PromptInjectionLoader with additional patterns."""
    extended_patterns = load_all_extended_patterns()

    # Add to loader
    for pattern_id, pattern in extended_patterns.items():
        loader.injections[pattern_id] = pattern

    # Save to files
    for pattern in extended_patterns.values():
        file_path = loader.config.injection_dir / f"{pattern.id}.json"
        import json

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(pattern.dict(), f, indent=2)

    print(f"Added {len(extended_patterns)} extended injection patterns")
