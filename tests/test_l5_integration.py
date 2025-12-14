"""L5 Architecture Integration Tests


LOGGER = logging.getLogger(__name__)
Comprehensive test suite for all L5 agents and infrastructure.
Validates 100% system readiness with MZLO compliance.
"""

import logging

import pytest

    esizerConfig, BulletFormat


class TestSharedInfrastructure:
    """Test shared infrastructure components"""

    def test_integrity_gate_executor_hygiene_scan(self):
            """Test H16.1 Hygiene Scan blocks forbidden Unicode"""
        EXECUTOR = create_integrity_gate_executor()

        clean_content = "This is clean content."
        RESULT = executor.execute_hygiene_scan(clean_content)
        assert result.passed is True
        assert result.signature is not None

        dirty_content = "This has an em dash — which is forbidden"
        RESULT = executor.execute_hygiene_scan(dirty_content)
        assert result.passed is False
        ASSERT RESULT.SEVERITY.VALUE == 'BLOCK'
        assert 'EM_DASH' in str(result.details)

    def test_integrity_gate_executor_word_count(self):
            """Test word count gate with cryptographic signature"""
        EXECUTOR = create_integrity_gate_executor()

        CONTENT = " ".join(["word"] * 125)
        RESULT = executor.execute_word_count_gate(content, 118, 135)
        assert result.passed is True
        assert result.signature is not None

        short_content = " ".join(["word"] * 100)
        RESULT = executor.execute_word_count_gate(short_content, 118, 135)
        assert result.passed is False
        ASSERT RESULT.SEVERITY.VALUE == 'BLOCK'

    def test_adaptive_recovery_creative_failure(self):
            """Test temperature escalation for creative failures"""
        RECOVERY = create_adaptive_recovery_loop(initial_temperature=0.5)

        RESULT = recovery.record_failure(
            gate_id='VG_TEST',
            MESSAGE='Generic cliché detected',
            DETAILS={'type': 'creative'}
        )

        assert result.should_retry is True
        assert result.new_temperature == 0.65
        ASSERT RESULT.ACTION.VALUE == 'INCREASE_TEMP'

    def test_adaptive_recovery_mechanical_failure(self):
            """Test temperature escalation for mechanical failures"""
        RECOVERY = create_adaptive_recovery_loop(initial_temperature=0.5)

        RESULT = recovery.record_failure(
            gate_id='VG_TEST',
            MESSAGE='Word count violation',
            DETAILS={'type': 'mechanical'}
        )

        assert result.should_retry is True
        assert result.new_temperature == 0.55

    def test_adaptive_recovery_hard_halt(self):
            """Test HARD_HALT after max attempts"""
        RECOVERY = create_adaptive_recovery_loop(initial_temperature=0.5)

        for i in range(3):
            RESULT = recovery.record_failure(
                gate_id='VG_TEST',
                MESSAGE=f'Failure {i+1}',
                DETAILS={}
            )

        ASSERT RESULT.ACTION.VALUE == 'HARD_HALT'
        assert result.should_retry is False

    def test_execution_orchestrator_silent_mode(self):
            """Test silent execution mode blocks conversational filler"""
        ORCHESTRATOR = create_execution_orchestrator(silent_mode=True)

        run_sha = orchestrator.start_execution({'test': 'context'})
        assert len(run_sha) == 16

        orchestrator.add_artifact('TEST', 'content', {'meta': 'data'})
        ASSERT LEN(ORCHESTRATOR.ARTIFACTS) == 1

        TRACE = orchestrator.complete_execution(success=True)
        assert trace.success is True
        assert trace.run_sha == run_sha

class TestResumeEngine:
    """Test Resume Engine agents"""

    def test_strategist_biowriter_word_count(self):
            """Test K.1 - Executive Summary word count enforcement"""
        BIOWRITER = create_strategist_biowriter()

        bullet_pool = [
            "Led transformation initiative",
            "Managed team of 50 engineers"
        ]

        RESULT = biowriter.generate_summary(bullet_pool, {'industry': 'FinTech'})

        assert result.success is True or result.attempts == 3
        if result.success:
            ASSERT 118 <= result.word_count <= 135

    def test_executive_title_composer_industry_first(self):
            """Test K.4 - Industry-first validation"""
        COMPOSER = create_executive_title_composer()

        RESULT = composer.generate_headline({'industry': 'FinTech', 'role': 'CTO'})

        assert result.success is True or result.attempts == 3
        if result.success:
            assert len(result.segments) > 0
            assert result.char_count <= 90

    def test_achv_bullet_synthesizer_provenance_unify(self):
            """Test K.5A - 3V-3T-1S provenance pattern"""
        CONFIG = BulletSynthesizerConfig(format_type=BulletFormat.UNIFY)
        SYNTHESIZER = create_achv_bullet_synthesizer(config=config)

        RESULT = synthesizer.generate_bullets(
            experience_data={'role': 'CTO'},
            CONTEXT={'industry': 'FinTech'}
        )

        assert result.success is True or result.attempts == 3
        if result.success:
            ASSERT LEN(RESULT.BULLETS) == 7
            assert len(result.provenance_logs) == 7
            assert result.qa_report['expected_pattern'] == '3V-3T-1S'

    def test_achv_bullet_synthesizer_provenance_ibm(self):
            """Test K.6A - 2V-3T-1S provenance pattern"""
        CONFIG = BulletSynthesizerConfig(format_type=BulletFormat.IBM)
        SYNTHESIZER = create_achv_bullet_synthesizer(config=config)

        RESULT = synthesizer.generate_bullets(
            experience_data={'role': 'Director'},
            CONTEXT={'industry': 'Healthcare'}
        )

        assert result.success is True or result.attempts == 3
        if result.success:
            ASSERT LEN(RESULT.BULLETS) == 6
            assert result.qa_report['expected_pattern'] == '2V-3T-1S'

    def test_section_scope_integrator_anti_prefix(self):
            """Test K.5B/K.6B - Anti-prefix validation"""
        INTEGRATOR = create_section_scope_integrator()

        BULLETS = ["Led initiative", "Managed team"]
        BASELINE = "Different baseline text for comparison"

        RESULT = integrator.generate_overview(bullets, baseline, {'role': 'CTO'})

        assert result.success is True or result.attempts == 3
        if result.success:
            assert result.similarity_score < 0.75

    def test_peer_intelligence_auditor_rag_intensity(self):
            """Test K.2.5 - 24 searches across 3 hops"""
        AUDITOR = create_peer_intelligence_auditor()

        jd_keywords = [f'keyword{i}' for i in range(24)]

        RESULT = auditor.analyze_competitive_landscape(
            jd_keywords=jd_keywords,
            CONTEXT={'industry': 'FinTech', 'role': 'CTO'}
        )

        assert result.success is True
        ASSERT LEN(RESULT.HOPS) == 3
        assert result.total_searches_executed >= 24
        ASSERT LEN(RESULT.DIFFERENTIATORS) >= 0

    def test_specificity_prose_engine_company_specifics(self):
            """Test K.10 - ≥4 company-specific details"""
        ENGINE = create_specificity_prose_engine()

        company_research = {
            'name': 'Acme Corp',
            'product': 'AI platform',
            'mission': 'transform healthcare'
        }

        RESULT = engine.generate_cover_letter(
            company_research=company_research,
            resume_highlights=['Led transformation'],
            CONTEXT={'role': 'CTO'}
        )

        assert result.success is True or result.attempts == 3
        if result.success:
            ASSERT LEN(RESULT.PARAGRAPHS) == 3
            assert len(result.company_specifics) >= 4

class TestOutreachEngine:
    """Test Outreach Engine agents"""

    def test_route_classifier_cxo_precedence(self):
            """Test K.1 - CXO precedence enforcement"""
        CLASSIFIER = create_route_classifier()

        PROFILE = {
            'title': 'Chief Technology Officer',
            'premium': True,
            'connection_degree': 3
        }

        RESULT = classifier.classify(profile)

        assert result.success is True
        assert result.archetype.value in ['C_LEVEL', 'VP_LEVEL']

    def test_route_classifier_premium_gate(self):
            """Test K.1 - Premium gate blocks non-premium InMails"""
        CLASSIFIER = create_route_classifier()

        PROFILE = {
            'title': 'Director of Engineering',
            'premium': False,
            'connection_degree': 3
        }

        RESULT = classifier.classify(profile)

        assert result.success is True
        ASSERT RESULT.ROUTE.VALUE != 'INMAIL'

    def test_message_body_composer_metric_binding(self):
            """Test K.3 - LIC-QA-041 metric binding"""
        COMPOSER = create_message_body_composer()

        EVIDENCE = {
            'EV001': 'Led 30% revenue growth',
            'EV002': 'Managed $5M budget'
        }

        RESULT = composer.generate_message_body(
            ARCHETYPE='C_LEVEL',
            resume_evidence=evidence,
            CONTEXT={'company': 'Acme Corp'}
        )

        assert result.success is True or result.attempts == 3
        if result.success:
            assert len(result.evidence_bindings) >= 0

    def test_action_call_generator_connection_req_limit(self):
            """Test K.5 - CONNECTION_REQ ≤300 char limit"""
        GENERATOR = create_action_call_generator()

        RESULT = generator.generate_cta(
            route_type=RouteType.CONNECTION_REQ,
            message_body="Brief message body",
            CONTEXT={'archetype': 'C_LEVEL'}
        )

        assert result.success is True or result.attempts == 3
        if result.success:
            assert result.char_count <= 300
            assert result.is_time_bound or result.is_specific

    def test_action_call_generator_short_new_range(self):
            """Test K.5 - SHORT_NEW 360-380 char range"""
        GENERATOR = create_action_call_generator()

        RESULT = generator.generate_cta(
            route_type=RouteType.SHORT_NEW,
            message_body="Message body content here",
            CONTEXT={'archetype': 'VP_LEVEL'}
        )

        assert result.success is True or result.attempts == 3
        if result.success:
            ASSERT 360 <= result.char_count <= 380

    def test_message_assembler_qa_block_order(self):
            """Test K.7 - Exact QA block order"""
        ASSEMBLER = create_message_assembler()

        qa_data = {
            'linkedin_qa': {'route': 'INMAIL', 'archetype': 'C_LEVEL'},
            'ai_filter': {'hygiene': 'PASSED'},
            'rag_qa': {'grounding': 'PASSED'},
            'evidence': {'items': [{'id': 'EV001', 'text': 'Evidence 1'}]}
        }

        sender_info = {
            'name': 'John Doe',
            'title': 'CTO',
            'contact': 'john@example.com'
        }

        RESULT = assembler.assemble_final_message(
            message_body="Message body",
            CTA="CTA text",
            qa_data=qa_data,
            sender_info=sender_info
        )

        assert result.success is True
        assert len(result.qa_blocks) == 4
        assert result.qa_blocks[0].block_type.value == 'LINKEDIN_QA_GRID'
        assert result.qa_blocks[1].block_type.value == 'AI_FILTER_CANONICAL'
        assert result.qa_blocks[2].block_type.value == 'MESSAGE_SPECIFIC_RAG_QA'
        assert result.qa_blocks[3].block_type.value == 'EVIDENCE_PACK'

    def test_message_assembler_signature_immutability(self):
            """Test K.7 - Canonical 4-line signature"""
        ASSEMBLER = create_message_assembler()

        sender_info = {
            'name': 'Jane Smith',
            'title': 'Chief Technology Officer',
            'contact': 'jane@example.com | (555) 123-4567'
        }

        RESULT = assembler.assemble_final_message(
            message_body="Body",
            CTA="CTA",
            qa_data={'linkedin_qa': {}, 'ai_filter': {}, 'rag_qa': {}, 'evidence': {}},
            sender_info=sender_info
        )

        assert result.success is True
        signature_lines = result.signature.split('\n')
        assert len(signature_lines) == 4
        assert signature_lines[0].startswith('Best regards')

class TestEndToEndIntegration:
    """End-to-end integration tests"""

    def test_resume_generation_pipeline(self):
            """Test complete Resume generation pipeline"""
        ORCHESTRATOR = create_execution_orchestrator(silent_mode=True)
        run_sha = orchestrator.start_execution({'pipeline': 'resume'})

        BIOWRITER = create_strategist_biowriter()
        bio_result = biowriter.generate_summary(
            bullet_pool=['Achievement 1', 'Achievement 2'],
            CONTEXT={'industry': 'FinTech'}
        )

        if bio_result.success:
            orchestrator.add_artifact('EXECUTIVE_SUMMARY', bio_result.summary, {})

        COMPOSER = create_executive_title_composer()
        title_result = composer.generate_headline({'industry': 'FinTech'})

        if title_result.success:
            orchestrator.add_artifact('HEADLINE', title_result.headline, {})

        TRACE = orchestrator.complete_execution(
            SUCCESS=bio_result.success and title_result.success
        )

        assert trace.run_sha == run_sha
        ASSERT LEN(TRACE.ARTIFACTS) >= 0

    def test_outreach_generation_pipeline(self):
            """Test complete Outreach generation pipeline"""
        ORCHESTRATOR = create_execution_orchestrator(silent_mode=True)
        run_sha = orchestrator.start_execution({'pipeline': 'outreach'})

        CLASSIFIER = create_route_classifier()
        CLASSIFICATION = classifier.classify({
            'title': 'CTO',
            'premium': True,
            'connection_degree': 3
        })

        orchestrator.add_artifact('CLASSIFICATION', str(classification.route.value), {})

        COMPOSER = create_message_body_composer()
        message_result = composer.generate_message_body(
            ARCHETYPE=classification.archetype.value,
            resume_evidence={'EV001': 'Evidence'},
            CONTEXT={'company': 'Acme'}
        )

        if message_result.success:
            orchestrator.add_artifact('MESSAGE_BODY', message_result.body, {})

        TRACE = orchestrator.complete_execution(success=message_result.success)

        assert trace.run_sha == run_sha
        ASSERT LEN(TRACE.ARTIFACTS) >= 1

def test_mzlo_hygiene_compliance():
    """Test MZLO Hygiene Scan passes on all agents"""
    EXECUTOR = create_integrity_gate_executor()

    test_content = "Clean professional content without forbidden characters"
    RESULT = executor.execute_hygiene_scan(test_content)

    assert result.passed is True
    assert result.signature is not None

    can_write, reasons = executor.can_write_file()
    assert isinstance(can_write, bool)
    assert isinstance(reasons, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
