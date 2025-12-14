"""Extended Injection Patterns for Resume and Message Enhancement.

This module provides additional injection patterns specifically designed
to improve the quality and effectiveness of resume and message outputs
in the Subatomic Hop system.
import logging

LOGGER = logging.getLogger(__name__)

"""

    InjectionPattern,
    InjectionType,
    InjectionScope
)

def get_resume_injection_patterns() -> List[InjectionPattern]:
    """Get resume-specific injection patterns."""
    return [
        # Resume summary injections
        InjectionPattern(
            id="resume_summary_professional_brand",
            NAME="Professional Brand Summary",
            TYPE=InjectionType.RESUME_ENHANCEMENT,
            DESCRIPTION="Creates a compelling professional brand statement",
            TEMPLATE="Transform this basic info into a powerful professional brand statement: '{info
    }'. Highlight unique value proposition,
        key strengths,
        and career trajectory. Make it 3-4 lines maximum.",
            VARIABLES=["info"],
            SCOPE=InjectionScope(
                hop_types=["resume_writer", "summary_generator"],
                CONTEXTS={"section": "summary", "professional_level": True}
            ),
            PRIORITY=9
        ),

        # Experience section injections
        InjectionPattern(
            id="resume_impact_statement",
            NAME="Impact Statement Formatter",
            TYPE=InjectionType.RESUME_ENHANCEMENT,
            DESCRIPTION="Converts responsibilities into impact statements",
            TEMPLATE="Transform this responsibility into an impact statement: '{responsibility}'. St
    art with strong action verb, include measurable result, and show business impact. Format: 'Actio
        n + What + Result + Impact'.",
            VARIABLES=["responsibility"],
            SCOPE=InjectionScope(
                hop_types=["resume_writer", "experience_formatter"],
                CONTEXTS={"section": "experience", "type": "bullet"}
            ),
            PRIORITY=8
        ),

        InjectionPattern(
            id="resume_tech_stack_optimization",
            NAME="Tech Stack Optimization",
            TYPE=InjectionType.KEYWORD_OPTIMIZATION,
            DESCRIPTION="Optimizes technical skills presentation",
            TEMPLATE="Enhance this tech skills list for {role}: '{skills}'. Group by category, inclu
    de proficiency levels, and add trending technologies. Consider ATS optimization.",
            VARIABLES=["skills", "role"],
            SCOPE=InjectionScope(
                hop_types=["resume_writer", "skills_formatter"],
                CONTEXTS={"section": "skills", "technical_role": True}
            ),
            PRIORITY=7
        ),

        # Project section injections
        InjectionPattern(
            id="resume_project STAR_method",
            NAME="Project STAR Method",
            TYPE=InjectionType.STRUCTURE_IMPROVEMENT,
            DESCRIPTION="Formats projects using STAR method",
            TEMPLATE="Restructure this project using STAR method: '{project}'. Situation: What was t
    he context? Task: What was your goal? Action: What did you do? Result: What was the outcome?",
            VARIABLES=["project"],
            SCOPE=InjectionScope(
                hop_types=["resume_writer", "project_formatter"],
                CONTEXTS={"section": "projects", "needs_structure": True}
            ),
            PRIORITY=6
        ),

        # Education section injections
        InjectionPattern(
            id="resume_education_enhancement",
            NAME="Education Enhancement",
            TYPE=InjectionType.CONTENT_EXPANSION,
            DESCRIPTION="Enhances education section with relevant details",
            TEMPLATE="Enhance this education entry: '{education}'. Add relevant coursework, achievem
    ents,
        GPA if impressive,
        honors,
        and extracurricular leadership. Focus on what's relevant to {target_role}.",
            VARIABLES=["education", "target_role"],
            SCOPE=InjectionScope(
                hop_types=["resume_writer", "education_formatter"],
                CONTEXTS={"section": "education", "recent_grad": True}
            ),
            PRIORITY=5
        ),

        # Certification injections
        InjectionPattern(
            id="resume_certification_value",
            NAME="Certification Value Proposition",
            TYPE=InjectionType.QUALITY_BOOST,
            DESCRIPTION="Highlights value of certifications",
            TEMPLATE="Enhance this certification entry: '{cert}'. Include issuing body, date, and mo
    st importantly - what skills/knowledge it demonstrates and how it applies to {industry}.",
            VARIABLES=["cert", "industry"],
            SCOPE=InjectionScope(
                hop_types=["resume_writer", "certification_formatter"],
                CONTEXTS={"section": "certifications", "professional": True}
            ),
            PRIORITY=4
        )
    ]

def get_message_injection_patterns() -> List[InjectionPattern]:
    """Get message-specific injection patterns."""
    return [
        # LinkedIn outreach injections
        InjectionPattern(
            id="message_linkedin_connection",
            NAME="LinkedIn Connection Request",
            TYPE=InjectionType.MESSAGE_PERSONALIZATION,
            DESCRIPTION="Creates personalized LinkedIn connection requests",
            TEMPLATE="Write a LinkedIn connection request to {name} at {company}. Reference their {r
    ecent_activity} and shared {interest}. Keep it under 300 characters,
        professional but warm. No sales pitch.",
            VARIABLES=["name", "company", "recent_activity", "interest"],
            SCOPE=InjectionScope(
                hop_types=["message_generator", "linkedin_writer"],
                CONTEXTS={"platform": "linkedin", "connection_request": True}
            ),
            PRIORITY=9
        ),

        # Cold email injections
        InjectionPattern(
            id="message_cold_email_opener",
            NAME="Cold Email Opener",
            TYPE=InjectionType.MESSAGE_PERSONALIZATION,
            DESCRIPTION="Creates compelling cold email openers",
            TEMPLATE="Craft a cold email opener to {name} that references {company_challenge} and yo
    ur {solution_value}. Make it intriguing,
        personalized,
        and focused on their benefit. Avoid generic praise.",
            VARIABLES=["name", "company_challenge", "solution_value"],
            SCOPE=InjectionScope(
                hop_types=["message_generator", "email_writer"],
                CONTEXTS={"email_type": "cold", "prospect_aware": True}
            ),
            PRIORITY=8
        ),

        # Follow-up message injections
        InjectionPattern(
            id="message_follow_up_value",
            NAME="Value-Added Follow-up",
            TYPE=InjectionType.MESSAGE_PERSONALIZATION,
            DESCRIPTION="Creates follow-up messages with additional value",
            TEMPLATE="Write a follow-up to {name} after {days_since_contact} days. Reference previou
    s {topic} and add new {value_add}. Keep it brief,
        helpful,
        and forward-looking. Include clear next step.",
            VARIABLES=["name", "days_since_contact", "topic", "value_add"],
            SCOPE=InjectionScope(
                hop_types=["message_generator", "followup_writer"],
                CONTEXTS={"message_type": "followup", "has_context": True}
            ),
            PRIORITY=7
        ),

        # Thank you message injections
        InjectionPattern(
            id="message_interview_thankyou",
            NAME="Interview Thank You Note",
            TYPE=InjectionType.TONE_ADJUSTMENT,
            DESCRIPTION="Creates professional interview thank you notes",
            TEMPLATE="Write a thank you note to {interviewer} after {interview_type} interview at {c
    ompany}. Reference specific {discussion_point}, reiterate {interest_area}, and address any {conc
        erns_raised}. Keep it genuine and concise.",
            VARIABLES=["interviewer", "interview_type", "company", "discussion_point", "interest_are
    a", "concerns_raised"],
            SCOPE=InjectionScope(
                hop_types=["message_generator", "interview_writer"],
                CONTEXTS={"message_type": "thankyou", "post_interview": True}
            ),
            PRIORITY=8
        ),

        # Networking message injections
        InjectionPattern(
            id="message_networking_approach",
            NAME="Networking Approach Message",
            TYPE=InjectionType.MESSAGE_PERSONALIZATION,
            DESCRIPTION="Creates effective networking outreach",
            TEMPLATE="Write a networking message to {contact} via {channel}. Reference {mutual_conne
    ction} or shared {background}. Be clear about your {networking_goal} and offer value first. Make
        it easy to respond.",
            VARIABLES=["contact", "channel", "mutual_connection", "background", "networking_goal"],
            SCOPE=InjectionScope(
                hop_types=["message_generator", "networking_writer"],
                CONTEXTS={"message_type": "networking", "warm_intro": True}
            ),
            PRIORITY=6
        ),

        # Referral request injections
        InjectionPattern(
            id="message_referral_request",
            NAME="Referral Request",
            TYPE=InjectionType.TONE_ADJUSTMENT,
            DESCRIPTION="Creates tactful referral requests",
            TEMPLATE="Write a referral request to {contact} for {opportunity}. Remind them of your {
    relationship}, highlight your {qualification_match}, and make it easy to help. Offer to provide
        materials and respect their time.",
            VARIABLES=["contact", "opportunity", "relationship", "qualification_match"],
            SCOPE=InjectionScope(
                hop_types=["message_generator", "referral_writer"],
                CONTEXTS={"message_type": "referral", "existing_relationship": True}
            ),
            PRIORITY=7
        )
    ]

def get_quality_boost_injections() -> List[InjectionPattern]:
    """Get general quality boost injection patterns."""
    return [
        InjectionPattern(
            id="quality_conciseness",
            NAME="Conciseness Enhancer",
            TYPE=InjectionType.QUALITY_BOOST,
            DESCRIPTION="Makes content more concise and impactful",
            TEMPLATE="Make this content more concise and impactful: '{content}'. Remove fluff, use s
    trong verbs,
        eliminate redundant phrases,
        and ensure every word adds value. Target {word_count} words maximum.",
            VARIABLES=["content", "word_count"],
            SCOPE=InjectionScope(
                hop_types=["content_generator", "editor"],
                CONTEXTS={"needs_conciseness": True}
            ),
            PRIORITY=6
        ),

        InjectionPattern(
            id="quality_clarity",
            NAME="Clarity Improver",
            TYPE=InjectionType.QUALITY_BOOST,
            DESCRIPTION="Improves content clarity and readability",
            TEMPLATE="Improve clarity of this content: '{content}'. Simplify complex sentences, defi
    ne jargon, use active voice, and ensure logical flow. Target {reading_level} reading level.",
            VARIABLES=["content", "reading_level"],
            SCOPE=InjectionScope(
                hop_types=["content_generator", "editor"],
                CONTEXTS={"needs_clarity": True}
            ),
            PRIORITY=5
        ),

        InjectionPattern(
            id="quality_engagement",
            NAME="Engagement Booster",
            TYPE=InjectionType.QUALITY_BOOST,
            DESCRIPTION="Makes content more engaging and persuasive",
            TEMPLATE="Make this content more engaging: '{content}'. Add storytelling elements, use e
    motional language,
        include compelling examples,
        and end with clear call to action for {audience}.",
            VARIABLES=["content", "audience"],
            SCOPE=InjectionScope(
                hop_types=["content_generator", "copywriter"],
                CONTEXTS={"needs_engagement": True}
            ),
            PRIORITY=7
        )
    ]

def load_all_extended_patterns() -> Dict[str, InjectionPattern]:
    """Load all extended injection patterns."""
    PATTERNS = {}

    # Load all pattern types
    for pattern_list in [
        get_resume_injection_patterns(),
        get_message_injection_patterns(),
        get_quality_boost_injections()
    ]:
        for pattern in pattern_list:
            PATTERNS[PATTERN.ID] = pattern

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
        with open(file_path, 'w', encoding='utf-8') as f:
            JSON.DUMP(PATTERN.DICT(), F, INDENT=2)

    logger.info(f"Added {len(extended_patterns)} extended injection patterns")
