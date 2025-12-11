#!/usr/bin/env python3
"""
Outreach Engine Demo - Phase F LIC Capability Integration
Realistic end-to-end demo showcasing all 13 capability modules
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, object, List

from archives.legacy_resume_gen.Older Microservices Models.v2.engine import ValidationSeverity, RoutingEngine, RAGPipelineV75, InsightsEngine, ToneEngine, ConstraintEngine, TemplateEngine, KNodeAssemblyEngine, SeniorityEngine, FusionPlanner
    # Core models
    ValidationSeverity,
    
    # Main engines
    RoutingEngine, RAGPipelineV75, InsightsEngine,
    ToneEngine, ConstraintEngine,
    TemplateEngine, KNodeAssemblyEngine, SeniorityEngine,
    
    # Fusion planning
    FusionPlanner
)

def load_lic_capabilities() -> Dict[str, object]:
    """Load LIC capabilities from reconstructed_capabilities.py"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'LIC_capabilities'))
        from archives.LIC_capabilities.reconstructed_capabilities import LIC_CAPABILITIES

        return LIC_CAPABILITIES
    except ImportError as e:


        return get_demo_configuration()

def get_demo_configuration() -> Dict[str, object]:
    """Demo configuration for testing without real LIC data"""
    return {
        "routing_rules": {
            "routing_rules": {
                "CONNECTION_REQ": {
                    "conditions": {"connection_status": "not_connected"},
                    "constraints": {
                        "char_limit": 300,
                        "word_range": [50, 100],
                        "signature_format": "standard",
                        "subject_line_enabled": False,
                        "attachments_enabled": False,
                        "cta_format": "standard",
                        "cta_max_words": 15,
                        "greeting_format": "Hi {first_name},"
                    }
                },
                "INMAIL": {
                    "conditions": {"connection_status": "connected"},
                    "constraints": {
                        "char_limit": 500,
                        "word_range": [75, 150],
                        "signature_format": "professional",
                        "subject_line_enabled": True,
                        "attachments_enabled": False,
                        "cta_format": "professional",
                        "cta_max_words": 20,
                        "greeting_format": "Dear {first_name},"
                    }
                },
                "SHORT_NEW": {
                    "conditions": {"connection_status": "any"},
                    "constraints": {
                        "char_limit": 400,
                        "word_range": [60, 120],
                        "signature_format": "standard",
                        "subject_line_enabled": False,
                        "attachments_enabled": False,
                        "cta_format": "standard",
                        "cta_max_words": 15,
                        "greeting_format": "Hi {first_name},"
                    }
                }
            }
        },
        "parameter_presets": {
            "context_manager": {
                "max_tokens": 8000,
                "allocation": {
                    "sender_profile": 500,
                    "recipient_context": 1500,
                    "rag_results": 4000,
                    "reasoning_space": 2000
                },
                "overflow_strategy": {
                    "priority": "sender_profile > rag_results > recipient_context"
                }
            },
            "adaptive_temperature_controller": {
                "base_temperatures": {
                    "EXECUTIVE": 0.7,
                    "C_LEVEL": 0.6,
                    "SENIOR_TA": 0.8,
                    "RECRUITER": 0.7
                },
                "escalation_step": 0.15,
                "max_temperature": 0.95,
                "max_creative_retries": 3
            },
            "tool_call_budget": {
                "minimum": 0,
                "maximum": 20,
                "guidance": {
                    "CONNECTION_REQ": "6-10",
                    "INMAIL": "8-12",
                    "SHORT_NEW": "6-10"
                },
                "scaling": "Based on query complexity and job context"
            }
        },
        "scenario_rules": {
            "rag_pipeline_v75": {
                "stage_0_hyde": {
                    "enabled": True,
                    "trigger": {"recipient_profile.about": "< 50 chars"},
                    "constraints": {"max_length": 100},
                    "validation": {
                        "forbidden_patterns": ["\\d{4}", "\\$\\d+"],
                        "max_retries": 3
                    }
                },
                "stage_1_hybrid_recall": {
                    "web_search_calls": 6,
                    "internal_sources": ["linkedin", "company_website", "news"]
                },
                "stage_2_cross_encoder_reranking": {
                    "model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
                    "threshold": 0.75,
                    "weights": {
                        "relevance": 0.35,
                        "authority": 0.2,
                        "recency": 0.45
                    },
                    "anchor_temporal_window_days": 45
                },
                "stage_3_self_rag": {
                    "max_hops": 6,
                    "min_hops": 2,
                    "hop_trigger": "insufficient evidence, low relevance, outdated info, low authority"
                },
                "stage_4_episodic_memory": {
                    "enabled": True,
                    "trigger": "route == FOLLOW_UP",
                    "max_results": 5
                },
                "stage_5_knowledge_graph": {
                    "enabled": True,
                    "queries": ["shared_connections", "company_relationships", "industry_overlaps"]
                },
                "stage_6_few_shot_injection": {
                    "enabled": True,
                    "examples": "3-5"
                }
            }
        },
        "insight_patterns": {
            "signal_quality_scorer": {
                "source_weights": {
                    "web": 1.0,
                    "linkedin": 0.9,
                    "company_website": 0.8,
                    "news": 0.7
                },
                "minimum_signal_threshold": 0.7
            },
            "claim_confidence_scorer": {
                "per_claim_minimum": 0.8,
                "aggregate_minimum": 0.95,
                "scoring_methodology": {
                    "claim_extraction": {
                        "splitters": [".", "and", "while", "by"]
                    },
                    "per_claim_scoring": {
                        "base_score": 1.0,
                        "deductions": [
                            {"condition": "No RAG source found", "penalty": -0.3},
                            {"condition": "Metric has no source mapping", "penalty": -0.2},
                            {"condition": "Company not in whitelist", "penalty": -0.1}
                        ]
                    }
                }
            }
        },
        "cta_patterns": {
            "archetype_specific": {
                "EXECUTIVE": {
                    "example": "Would you be open to discussing how we could collaborate on strategic initiatives?",
                    "style": "professional",
                    "focus": "strategic_value",
                    "formality": "medium",
                    "verbs": ["discuss", "collaborate", "explore"]
                },
                "C_LEVEL": {
                    "example": "Would you be interested in a brief conversation about potential partnership opportunities?",
                    "style": "peer_to_peer",
                    "focus": "business_outcomes",
                    "formality": "high",
                    "verbs": ["connect", "partner", "align"]
                },
                "SENIOR_TA": {
                    "example": "Would you be open to a technical discussion about scalable architecture patterns?",
                    "style": "consultative",
                    "focus": "technical_peer",
                    "formality": "medium",
                    "verbs": ["discuss", "share", "explore"]
                },
                "RECRUITER": {
                    "example": "Would you be available for a quick call to discuss potential opportunities?",
                    "style": "warm_professional",
                    "focus": "skill_alignment",
                    "formality": "medium",
                    "verbs": ["connect", "discuss", "explore"]
                }
            },
            "date_window_engine": {
                "business_day_rules": {
                    "skip_weekends": True,
                    "skip_holidays": True,
                    "window_size_days": 2
                },
                "business_day_buffer_map": {
                    "Monday": {"min_buffer_days": 2, "suggested_pattern": "Wed-Thu"},
                    "Tuesday": {"min_buffer_days": 2, "suggested_pattern": "Thu-Fri"},
                    "Wednesday": {"min_buffer_days": 2, "suggested_pattern": "Fri-Mon"},
                    "Thursday": {"min_buffer_days": 3, "suggested_pattern": "Mon-Tue"},
                    "Friday": {"min_buffer_days": 4, "suggested_pattern": "Tue-Wed"}
                },
                "output_format": {
                    "date_format": "MM/DD",
                    "natural_language": "on {date1}, {date2}, or {date3}"
                }
            }
        },
        "tone_rules": {
            "archetype_tone_mappings": {
                "EXECUTIVE": {
                    "message_tone": "professional",
                    "verb_preference": ["collaborate", "discuss", "connect"],
                    "jargon_level": "business",
                    "formality": "medium",
                    "focus": "value"
                },
                "C_LEVEL": {
                    "message_tone": "executive",
                    "verb_preference": ["partner", "align", "strategic"],
                    "jargon_level": "business",
                    "formality": "high",
                    "focus": "strategic"
                },
                "SENIOR_TA": {
                    "message_tone": "technical",
                    "verb_preference": ["discuss", "share", "explore"],
                    "jargon_level": "technical",
                    "formality": "medium",
                    "focus": "technical"
                },
                "RECRUITER": {
                    "message_tone": "warm",
                    "verb_preference": ["connect", "discuss", "opportunity"],
                    "jargon_level": "business",
                    "formality": "medium",
                    "focus": "opportunity"
                }
            },
            "language_matcher": {
                "adaptation_matrix": {
                    "C_LEVEL": {
                        "any technical_level": "STRATEGIC_VALUE"
                    },
                    "EXECUTIVE": {
                        "high_technical": "BUSINESS_OUTCOMES",
                        "medium_technical": "BUSINESS_OUTCOMES",
                        "low_technical": "STRATEGIC_VALUE"
                    },
                    "SENIOR_TA": {
                        "high_technical": "TECHNICAL_DETAIL",
                        "medium_technical": "TECHNICAL_DETAIL",
                        "low_technical": "BUSINESS_OUTCOMES"
                    },
                    "RECRUITER": {
                        "any technical_level": "BUSINESS_IMPACT_ONLY"
                    }
                },
                "transformation_rules": {
                    "TECHNICAL_DETAIL": "Use sender technical terms as-is",
                    "BUSINESS_OUTCOMES": "Transform technical → business metrics",
                    "STRATEGIC_VALUE": "Transform technical → strategic impact",
                    "LAYMAN_WITH_METRICS": "Simplify jargon, keep metrics",
                    "BUSINESS_IMPACT_ONLY": "Strip technical, keep dollars/percentages"
                }
            }
        },
        "constraints": {
            "content_cleanliness": {
                "forbidden_verbs": ["spearheaded", "synergize", "leverage", "optimize"],
                "filler_phrases": ["I think", "maybe", "perhaps", "I feel"],
                "placeholder_patterns": ["\\[.*?\\]", "<.*?>", "\\{.*?\\}"],
                "max_violations": 2,
                "severity": "MEDIUM"
            },
            "ascii_hygiene": {
                "replacements": {
                    "\\u2019": "'",
                    "\\u2018": "'",
                    "\\u201C": '"',
                    "\\u201D": '"',
                    "\\u2013": "-",
                    "\\u2014": "--",
                    "\\u2026": "..."
                },
                "max_non_ascii": 5,
                "severity": "LOW"
            },
            "structural_validation": {
                "word_count_tolerance": 0.1,
                "char_limit_hard": 600,
                "subject_line_max_chars": 100,
                "cta_max_questions": 1,
                "severity": "HIGH"
            }
        },
        "message_templates": {
            "greeting_templates": {
                "CONNECTION_REQ": {
                    "template": "Hi {first_name},",
                    "examples": ["Hi John,", "Hi Sarah,"]
                },
                "INMAIL": {
                    "template": "Dear {first_name},",
                    "examples": ["Dear Michael,", "Dear Jennifer,"]
                },
                "SHORT_NEW": {
                    "template": "Hi {first_name},",
                    "examples": ["Hi David,", "Hi Lisa,"]
                }
            },
            "cta_templates": {
                "CONNECTION_REQ": {
                    "template": "Would you be open to a brief chat about {topic}?",
                    "word_limit": 15,
                    "examples": ["Would you be open to a brief chat?", "Would you be interested in connecting?"]
                },
                "INMAIL": {
                    "template": "Would you be available for a call on {date_window} to discuss {topic}?",
                    "word_limit": 20,
                    "examples": ["Would you be available for a call next week?", "Would you be open to a discussion?"]
                },
                "SHORT_NEW": {
                    "template": "Would you be open to discussing {topic}?",
                    "word_limit": 15,
                    "examples": ["Would you be open to discussing opportunities?", "Would you be interested in a conversation?"]
                }
            },
            "signature_templates": {
                "standard": {
                    "template": "Best regards,\n{name}\n{title}\n{company}",
                    "examples": ["Best regards,\nJane Doe\nSenior Engineer\nTech Corp"]
                },
                "professional": {
                    "template": "Sincerely,\n{name}\n{title}\n{company}\n{email}",
                    "examples": ["Sincerely,\nJohn Smith\nDirector\nInnovation Inc\njohn@innovation.com"]
                }
            }
        },
        "seniority_rules": {
            "recipient_classifier_taxonomy": {
                "types": ["EXECUTIVE", "C_LEVEL", "SENIOR_TA", "RECRUITER"],
                "type_definitions": {
                    "EXECUTIVE": {
                        "message_tone": "professional",
                        "formality_level": "medium",
                        "preferred_verbs": ["collaborate", "discuss"],
                        "focus_areas": ["operational_impact", "team_metrics"],
                        "communication_style": "professional_collaborative",
                        "expected_response_time": "standard",
                        "optimal_send_times": ["Tue-Thu", "10am-2pm"]
                    },
                    "C_LEVEL": {
                        "message_tone": "executive",
                        "formality_level": "high",
                        "preferred_verbs": ["partner", "strategic"],
                        "focus_areas": ["strategic_value", "business_metrics_only"],
                        "communication_style": "peer_to_peer_executive",
                        "expected_response_time": "longer",
                        "optimal_send_times": ["Tue-Wed", "9am-11am"]
                    },
                    "SENIOR_TA": {
                        "message_tone": "technical",
                        "formality_level": "medium",
                        "preferred_verbs": ["discuss", "technical"],
                        "focus_areas": ["technical_peer", "technical_details"],
                        "communication_style": "consultative_expert",
                        "expected_response_time": "standard",
                        "optimal_send_times": ["Mon-Thu", "10am-4pm"]
                    },
                    "RECRUITER": {
                        "message_tone": "warm",
                        "formality_level": "medium",
                        "preferred_verbs": ["connect", "opportunity"],
                        "focus_areas": ["skill_alignment", "skills_experience"],
                        "communication_style": "warm_professional",
                        "expected_response_time": "fast",
                        "optimal_send_times": ["Tue-Fri", "9am-3pm"]
                    }
                }
            }
        }
    }

def create_demo_sender_profile() -> Dict[str, object]:
    """Create realistic sender profile for demo"""
    return {
        "name": "Jane Doe",
        "title": "Senior Software Engineer",
        "company": "TechStart Inc",
        "current_company": "TechStart Inc",
        "domain": "software engineering",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "TechStart Inc",
                "start_date": "2022-01-15",
                "current": True,
                "description": "Leading microservices architecture development"
            },
            {
                "title": "Software Engineer",
                "company": "DataCorp",
                "start_date": "2019-06-01",
                "end_date": "2021-12-31",
                "description": "Built scalable data processing pipelines"
            }
        ],
        "skills": ["Python", "React", "AWS", "Docker", "Kubernetes", "Microservices"],
        "education": [
            {
                "degree": "BS Computer Science",
                "school": "Tech University",
                "year": "2019"
            }
        ],
        "linkedin_url": "https://linkedin.com/in/janedoe",
        "email": "jane.doe@techstart.com",
        "location": "San Francisco, CA",
        "summary": "Senior software engineer specializing in scalable systems and cloud architecture"
    }

def create_demo_recipient_profiles() -> List[Dict[str, object]]:
    """Create diverse recipient profiles for demo"""
    return [
        {
            "name": "Michael Chen",
            "title": "VP of Engineering",
            "company": "EnterpriseTech Corp",
            "department": "Engineering",
            "connection_status": "not_connected",
            "about": "VP of Engineering at EnterpriseTech, leading 200+ engineering team focused on cloud transformation and digital innovation",
            "experience": [
                {
                    "title": "VP of Engineering",
                    "company": "EnterpriseTech Corp",
                    "start_date": "2020-03-01",
                    "current": True
                }
            ],
            "skills": ["Leadership", "Cloud Strategy", "Team Building", "DevOps"],
            "location": "New York, NY",
            "industry": "Enterprise Software",
            "domain": "engineering leadership"
        },
        {
            "name": "Sarah Johnson",
            "title": "Senior Staff Engineer",
            "company": "CloudScale Inc",
            "department": "Platform Engineering",
            "connection_status": "connected",
            "about": "Senior Staff Engineer specializing in distributed systems, microservices, and high-performance computing",
            "experience": [
                {
                    "title": "Senior Staff Engineer",
                    "company": "CloudScale Inc",
                    "start_date": "2018-09-15",
                    "current": True
                }
            ],
            "skills": ["Go", "Kubernetes", "Distributed Systems", "Performance Optimization"],
            "location": "Seattle, WA",
            "industry": "Cloud Infrastructure",
            "domain": "software engineering"
        },
        {
            "name": "David Kim",
            "title": "Technical Recruiter",
            "company": "TalentHub",
            "department": "Recruiting",
            "connection_status": "not_connected",
            "about": "Technical recruiter specializing in software engineering and leadership roles at tech companies",
            "experience": [
                {
                    "title": "Technical Recruiter",
                    "company": "TalentHub",
                    "start_date": "2021-02-01",
                    "current": True
                }
            ],
            "skills": ["Technical Recruiting", "Talent Sourcing", "Interview Coordination"],
            "location": "Austin, TX",
            "industry": "Recruiting",
            "domain": "talent acquisition"
        }
    ]

def create_demo_job_context() -> Dict[str, object]:
    """Create realistic job context for demo"""
    return {
        "title": "Principal Software Engineer, Cloud Infrastructure",
        "company": "EnterpriseTech Corp",
        "location": "New York, NY",
        "description": "We're looking for a Principal Software Engineer to lead our cloud infrastructure transformation initiatives. You'll work on cutting-edge distributed systems, scale our platform to millions of users, and mentor senior engineers.",
        "requirements": [
            "10+ years of software engineering experience",
            "Expertise in cloud platforms (AWS, Azure, or GCP)",
            "Strong background in distributed systems",
            "Experience with Kubernetes and container orchestration",
            "Leadership experience and mentoring skills"
        ],
        "responsibilities": [
            "Design and implement scalable cloud infrastructure",
            "Lead technical architecture decisions",
            "Mentor senior engineers",
            "Drive engineering best practices",
            "Collaborate with product and business teams"
        ],
        "skills_required": ["Cloud Computing", "Distributed Systems", "Kubernetes", "Leadership"],
        "experience_level": "Senior",
        "job_type": "full-time",
        "remote_policy": "hybrid",
        "department": "Engineering",
        "industry": "Enterprise Software"
    }

def print_section_header(title: str):
    """Print formatted section header"""



def print_subsection(title: str):
    """Print formatted subsection header"""

def print_validation_summary(validations: list, title: str):
    """Print validation results summary"""
    if not validations:

        return
    
    failed = [v for v in validations if not v.passed]
    passed = len(validations) - len(failed)

    if failed:

        for validation in failed[:3]:  # Show first 3 failures

        if len(failed) > 3:

def demo_complete_workflow():
    """Demo complete end-to-end workflow"""
    print_section_header("OUTREACH ENGINE DEMO - PHASE F LIC CAPABILITY INTEGRATION")
    
    # Load configuration
    print_subsection("Loading Configuration")
    lic_capabilities = load_lic_capabilities()
    
    # Initialize all engines
    print_subsection("Initializing Engines")
    routing_engine = RoutingEngine(lic_capabilities.get("routing_rules", {}))
    rag_engine = RAGPipelineV75(lic_capabilities)
    insights_engine = InsightsEngine(lic_capabilities)
    fusion_planner = FusionPlanner()
    tone_engine = ToneEngine(lic_capabilities)
    constraint_engine = ConstraintEngine(lic_capabilities)
    template_engine = TemplateEngine(lic_capabilities)
    assembly_engine = KNodeAssemblyEngine(lic_capabilities)
    seniority_engine = SeniorityEngine(lic_capabilities)

    # Create demo data
    print_subsection("Creating Demo Profiles")
    sender_profile = create_demo_sender_profile()
    recipient_profiles = create_demo_recipient_profiles()
    job_context = create_demo_job_context()


    # Process each recipient
    for i, recipient_profile in enumerate(recipient_profiles, 1):
        print_section_header(f"PROCESSING RECIPIENT {i}: {recipient_profile['name']}")
        
        # Step 1: Seniority Classification
        print_subsection("1. Seniority Classification")
        classification, analysis, seniority_validations = seniority_engine.analyze_recipient_seniority(recipient_profile)


        print_validation_summary(seniority_validations, "Seniority Validations")
        
        # Step 2: Route Determination
        print_subsection("2. Route Determination")
        route = routing_engine.determine_route(recipient_profile, [])
        context = routing_engine.create_message_context(sender_profile, recipient_profile)


        # Step 3: RAG Pipeline Execution
        print_subsection("3. RAG Pipeline v75 Execution")
        rag_result, rag_validations = rag_engine.execute_rag_pipeline(
            recipient_profile=recipient_profile,
            sender_profile=sender_profile,
            job_context=job_context,
            route=route.value
        )



        if rag_result.hyde_profile:

        print_validation_summary(rag_validations, "RAG Validations")
        
        # Step 4: Insights Analysis
        print_subsection("4. Insights Quality Analysis")
        # Create mock RAG evidence for insights
        from archives.legacy_resume_gen.Agentic_Workflow-10_10.tests.dag.test_dag_models import RAGEvidence
        mock_evidence = [
            RAGEvidence(
                source_type=ev.source_type,
                content=ev.content,
                relevance_score=ev.relevance_score,
                authority_score=ev.authority_score,
                recency_score=ev.recency_score
            ) for ev in rag_result.evidence[:3]
        ]
        
        insights_results = insights_engine.analyze_message_quality(
            message_body="Sample message body for analysis",
            rag_evidence=mock_evidence,
            rag_sources=[{"content": ev.content} for ev in mock_evidence]
        )



        # Step 4.5: Fusion Planning (NEW)
        print_subsection("4.5. Fusion Planning")
        fusion_plan = fusion_planner.plan(
            role_title=job_context["title"],
            company_name=job_context["company"],
            archetype=context.archetype.value,
            resume_features=sender_profile,
            research_signals={
                "company_info": f"Company: {job_context['company']}",
                "market_context": f"Industry: {job_context.get('industry', 'Technology')}",
                "product_info": f"Role: {job_context['title']}"
            },
            rag_evidence=rag_result.evidence
        )
        fusion_summary = fusion_planner.get_fusion_summary(fusion_plan)



        # Step 5: Template Generation
        print_subsection("5. Template Component Generation")
        components = template_engine.assemble_template_components(
            route=route,
            archetype=context.archetype,
            sender_profile=sender_profile,
            recipient_profile=recipient_profile,
            context={"topic": "engineering opportunities", "company": job_context["company"]}
        )

        if components.get('subject_line'):



        # Step 6: Message Assembly
        print_subsection("6. K-Node Message Assembly")
        assembly, assembly_validations = assembly_engine.execute_k_node_assembly(
            route=route,
            archetype=context.archetype,
            components=components,
            sender_profile=sender_profile,
            recipient_profile=recipient_profile
        )
        
        formatted_message = assembly_engine.message_assembler.format_assembled_message(assembly, route)


        print_validation_summary(assembly_validations, "Assembly Validations")
        
        # Step 7: Final Validation
        print_subsection("7. Comprehensive Validation")
        
        # Constraint validation
        constraint_validations = constraint_engine.validate_message(formatted_message, context.constraints)
        print_validation_summary(constraint_validations, "Constraint Validations")
        
        # Tone validation
        tone_profile = tone_engine.get_tone_profile(context.archetype)
        tone_validations = tone_engine.validate_tone_compliance(formatted_message, tone_profile)
        print_validation_summary(tone_validations, "Tone Validations")
        
        # Entity grounding validation (skipped for demo)
        grounding_validations = []
        print_validation_summary(grounding_validations, "Entity Validations")
        
        # Display final message
        print_subsection("8. Final Generated Message")




        # Overall assessment
        all_validations = assembly_validations + constraint_validations + tone_validations + grounding_validations
        critical_failures = [v for v in all_validations if not v.passed and v.severity == ValidationSeverity.CRITICAL]
        
        if not critical_failures:

        else:






        if i < len(recipient_profiles):
            input("\n🔄 Press Enter to continue to next recipient...")

def main():
    """Main demo function"""
    try:
        demo_complete_workflow()
        
        print_section_header("DEMO COMPLETION SUMMARY")

















    except Exception as e:

        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
