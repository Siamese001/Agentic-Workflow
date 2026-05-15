"""W2: fact_vectors foundation tests.

Plan: 04_apps-rg-c0-architecture-analysis-f3d8b2 W2

Goals:
- fact_vectors and process_docs are separate collections
- Only candidate_profile and project_evidence source classes accepted
- app=apps_rg metadata is required on every chunk
- Sample resume can produce 10+ ingestable chunks
- No process_docs write/query path is used for fact_vectors ingest

Non-goals:
- Briefing bypass, section retrieval, metadata filtering, claim verification, L6 spans
- Changing retrieval behavior beyond W2 requirements
- L4/UWG durable writes
- Company-research retrieval inside apps_rg C0
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from apps_rg.tools.fact_vector_ingest import (
    FactVectorChunk,
    FactVectorSchema,
    ingest_candidate_profile,
    ingest_project_evidence,
)


# Sample resume content for testing (sufficiently detailed to produce 10+ chunks)
SAMPLE_RESUME_CONTENT = """
JOHN DOE
Senior Software Engineer
San Francisco, CA | john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 15 years building scalable distributed systems, 
cloud infrastructure, and AI-powered applications. Led teams of 5-20 engineers across 
multiple successful product launches. Deep expertise in Python, AWS, Kubernetes, and 
machine learning pipelines. Passionate about clean code, system reliability, and 
mentoring junior engineers.

TECHNICAL SKILLS
Languages: Python, Go, JavaScript/TypeScript, Java, SQL
Cloud & Infrastructure: AWS (EC2, S3, Lambda, ECS, EKS), GCP, Terraform, CloudFormation
Containers & Orchestration: Docker, Kubernetes, Helm, service mesh
Databases: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, Cassandra
ML/Data: TensorFlow, PyTorch, scikit-learn, Pandas, NumPy, Apache Spark
Tools: Git, GitHub Actions, Jenkins, CircleCI, Datadog, PagerDuty

PROFESSIONAL EXPERIENCE

SENIOR PRINCIPAL ENGINEER | TechCorp Inc. | San Francisco, CA | 2018 - Present
- Architected and built core platform processing 10M+ daily transactions with 99.99% uptime
- Led migration from monolith to microservices, reducing deployment time from days to minutes
- Built real-time ML inference pipeline handling 50K predictions/second using Kubernetes
- Mentored team of 15 engineers; established code review practices and incident response
- Technologies: Python, Go, AWS, Kubernetes, Kafka, PostgreSQL, Redis, TensorFlow
- Reduced infrastructure costs by 40% through auto-scaling and spot instance optimization
- Implemented distributed tracing and monitoring across 200+ microservices

STAFF SOFTWARE ENGINEER | StartupXYZ | San Francisco, CA | 2014 - 2018
- Early engineer (employee #15) at B2B SaaS startup; grew to 500+ employees
- Built foundational data pipeline processing 1TB+ daily from 1000+ enterprise customers
- Designed and implemented REST API serving 100K+ requests/day with 99.9% availability
- Created Python SDK used by 500+ developers; maintained open-source documentation
- Led security audit achieving SOC2 Type II compliance
- Technologies: Python, Django, PostgreSQL, AWS, Docker, Elasticsearch

SENIOR SOFTWARE DEVELOPER | BigTech Company | Seattle, WA | 2010 - 2014
- Developed distributed caching layer serving 1M+ requests/second
- Built internal tool adopted by 50+ teams, reducing deployment friction
- Contributed to open-source projects (Apache Kafka, Redis) with patches merged upstream
- Won company-wide hackathon for innovative monitoring dashboard
- Technologies: Java, Python, MySQL, Memcached, RabbitMQ

SOFTWARE ENGINEER | MidSize Corp | Seattle, WA | 2008 - 2010
- Full-stack development for customer-facing web application (2M+ users)
- Implemented payment processing integration with Stripe and PayPal
- Optimized database queries reducing page load time by 60%
- Technologies: Python, Django, JavaScript, PostgreSQL, jQuery

EDUCATION

MASTER OF SCIENCE IN COMPUTER SCIENCE | Stanford University | 2008
- GPA: 3.9/4.0
- Focus: Distributed Systems and Machine Learning
- Teaching Assistant for CS 140 (Operating Systems)

BACHELOR OF SCIENCE IN COMPUTER ENGINEERING | University of Washington | 2006
- Magna Cum Laude
- Senior Project: Built autonomous robot navigation system (1st place in competition)

PROJECTS & OPEN SOURCE

distributed-task-queue (GitHub: 2.5K stars)
- Python library for reliable background job processing with Redis
- Used by 100+ companies in production
- Published PyPI package with 1M+ downloads

ml-pipeline-framework (GitHub: 1.2K stars)
- Framework for production ML model deployment and monitoring
- Supports TensorFlow, PyTorch, and scikit-learn models
- Presented at PyCon 2022 and AWS re:Invent 2021

CERTIFICATIONS
- AWS Solutions Architect Professional
- Kubernetes Administrator (CKA)
- Certified Scrum Master
"""

# Sample project evidence content
SAMPLE_PROJECT_EVIDENCE = """
PROJECT: Enterprise Data Platform Migration

OVERVIEW
Led 18-month initiative to migrate on-premise data warehouse to cloud-native 
platform serving 50+ business units and 500+ analysts.

CHALLENGES
- Legacy Oracle database with 100TB data and 10,000+ stored procedures
- Zero downtime requirement for critical reporting during migration
- Complex data dependencies across 200+ downstream systems
- Compliance requirements: SOC2, HIPAA, GDPR

SOLUTION
- Designed phased migration using CDC (Change Data Capture) with Debezium
- Built Apache Kafka streaming pipeline for real-time data sync
- Implemented Apache Spark jobs for historical data backfill
- Created automated testing framework for data quality validation

OUTCOMES
- 99.99% data accuracy maintained throughout migration
- Query performance improved 10x (average query time: 5min → 30sec)
- Infrastructure costs reduced 60% ($2M/year → $800K/year)
- Zero unplanned downtime during 18-month migration
- 50+ business units migrated with no data loss incidents

TECHNOLOGIES
Python, Apache Kafka, Apache Spark, PostgreSQL, AWS (S3, EMR, RDS), Terraform, Docker

TIMELINE
Start: January 2020 | Completion: June 2021 | Team size: 12 engineers
"""


class TestFactVectorsSchema:
    """Test 1: fact_vectors_schema.yaml exists and is valid."""
    
    def test_schema_file_exists(self):
        """PROOF: fact_vectors_schema.yaml exists at canonical path."""
        # Resolve relative to test file location
        test_file_dir = Path(__file__).parent.parent.parent
        schema_path = test_file_dir / "apps_rg" / "config" / "domain_contract" / "fact_vectors_schema.yaml"
        assert schema_path.exists(), f"Schema file not found at {schema_path}"
    
    def test_schema_loads_successfully(self):
        """PROOF: Schema can be loaded by FactVectorSchema class."""
        schema = FactVectorSchema()
        assert schema._schema, "Schema should load successfully"
        assert schema.collection_name == "fact_vectors"
    
    def test_collection_name_is_fact_vectors(self):
        """PROOF: Collection name is 'fact_vectors', not 'process_docs'."""
        schema = FactVectorSchema()
        assert schema.collection_name == "fact_vectors"
        assert schema.collection_name != "process_docs"
    
    def test_allowed_source_classes_are_candidate_owned(self):
        """PROOF: Only candidate_profile and project_evidence are allowed."""
        schema = FactVectorSchema()
        allowed = schema.allowed_source_classes
        
        assert "candidate_profile" in allowed
        assert "project_evidence" in allowed
        assert len(allowed) == 2, f"Expected exactly 2 allowed classes, got {allowed}"
    
    def test_process_docs_classes_are_rejected(self):
        """PROOF: process_docs source classes (rubrics, governance_docs, etc.) are rejected."""
        schema = FactVectorSchema()
        rejected = schema.rejected_source_classes
        
        assert "rubrics" in rejected
        assert "governance_docs" in rejected
        assert "approved_examples" in rejected
        assert "receipts" in rejected


class TestFactVectorsIngest:
    """Test 2: fact_vector_ingest.py works correctly."""
    
    def test_ingest_candidate_profile_returns_chunks(self):
        """PROOF: Candidate profile ingestion produces FactVectorChunk objects."""
        chunks = ingest_candidate_profile(
            content=SAMPLE_RESUME_CONTENT,
            candidate_name="John Doe",
            source_document_id="resume_001",
        )
        
        assert len(chunks) > 0, "Should produce at least 1 chunk"
        assert all(isinstance(c, FactVectorChunk) for c in chunks)
    
    def test_ingest_candidate_profile_produces_10_plus_chunks(self):
        """PROOF: Detailed resume produces at least 10 chunks."""
        chunks = ingest_candidate_profile(
            content=SAMPLE_RESUME_CONTENT,
            candidate_name="John Doe",
            source_document_id="resume_001",
        )
        
        assert len(chunks) >= 10, (
            f"Detailed resume should produce 10+ chunks, got {len(chunks)}"
        )
    
    def test_ingest_project_evidence_returns_chunks(self):
        """PROOF: Project evidence ingestion produces FactVectorChunk objects."""
        chunks = ingest_project_evidence(
            content=SAMPLE_PROJECT_EVIDENCE,
            project_name="Enterprise Data Platform Migration",
            candidate_name="John Doe",
            source_document_id="project_001",
            employer_or_client="TechCorp Inc.",
            role_or_title="Senior Principal Engineer",
        )
        
        assert len(chunks) > 0, "Should produce at least 1 chunk"
        assert all(isinstance(c, FactVectorChunk) for c in chunks)
    
    def test_all_chunks_have_required_app_metadata(self):
        """PROOF: Every chunk has app='apps_rg' metadata."""
        chunks = ingest_candidate_profile(
            content=SAMPLE_RESUME_CONTENT,
            candidate_name="John Doe",
            source_document_id="resume_001",
        )
        
        for chunk in chunks:
            assert chunk.app == "apps_rg", f"Chunk {chunk.chunk_id} missing app='apps_rg'"
    
    def test_all_chunks_have_source_class_candidate_profile(self):
        """PROOF: Candidate profile chunks have correct source_class."""
        chunks = ingest_candidate_profile(
            content=SAMPLE_RESUME_CONTENT,
            candidate_name="John Doe",
            source_document_id="resume_001",
        )
        
        for chunk in chunks:
            assert chunk.source_class == "candidate_profile"
    
    def test_all_chunks_have_source_class_project_evidence(self):
        """PROOF: Project evidence chunks have correct source_class."""
        chunks = ingest_project_evidence(
            content=SAMPLE_PROJECT_EVIDENCE,
            project_name="Data Platform Migration",
            candidate_name="John Doe",
            source_document_id="project_001",
        )
        
        for chunk in chunks:
            assert chunk.source_class == "project_evidence"
    
    def test_all_chunks_have_required_metadata_fields(self):
        """PROOF: Every chunk has all required metadata fields."""
        chunks = ingest_candidate_profile(
            content=SAMPLE_RESUME_CONTENT,
            candidate_name="John Doe",
            source_document_id="resume_001",
        )
        
        for chunk in chunks:
            assert chunk.chunk_id, "Missing chunk_id"
            assert chunk.ingestion_timestamp, "Missing ingestion_timestamp"
            assert chunk.source_document_id, "Missing source_document_id"
            assert chunk.source_version_hash, "Missing source_version_hash"
    
    def test_chunks_extract_skills_from_content(self):
        """PROOF: Chunks extract skills from content."""
        chunks = ingest_candidate_profile(
            content=SAMPLE_RESUME_CONTENT,
            candidate_name="John Doe",
            source_document_id="resume_001",
        )
        
        # At least some chunks should have skills extracted
        chunks_with_skills = [c for c in chunks if c.skills_mentioned]
        assert len(chunks_with_skills) > 0, "Should extract skills from resume"
        
        # Python should be detected
        all_skills = set()
        for c in chunks:
            all_skills.update(c.skills_mentioned)
        
        assert "Python" in all_skills or "python" in [s.lower() for s in all_skills]
    
    def test_chunks_detect_section_types(self):
        """PROOF: Chunks are tagged with appropriate section types."""
        chunks = ingest_candidate_profile(
            content=SAMPLE_RESUME_CONTENT,
            candidate_name="John Doe",
            source_document_id="resume_001",
        )
        
        section_types = {c.section_type for c in chunks}
        
        # Should have detected various section types
        assert "experience" in section_types or "skills" in section_types or "summary" in section_types


class TestFactVectorsValidation:
    """Test 3: Schema validation works correctly."""
    
    def test_schema_rejects_missing_app(self):
        """PROOF: Chunks without app metadata are rejected."""
        schema = FactVectorSchema()
        
        chunk = FactVectorChunk(
            chunk_id="test-001",
            content="Some resume content here",
            app="",  # Missing
            source_class="candidate_profile",
            ingestion_timestamp="2026-01-01T00:00:00+00:00",
            source_document_id="doc_001",
            source_version_hash="abc123",
        )
        
        is_valid, errors = schema.validate_chunk(chunk)
        assert not is_valid
        assert any("app" in e.lower() for e in errors)
    
    def test_schema_rejects_wrong_app_value(self):
        """PROOF: Chunks with app != 'apps_rg' are rejected."""
        schema = FactVectorSchema()
        
        chunk = FactVectorChunk(
            chunk_id="test-001",
            content="Some resume content here",
            app="wrong_app",  # Wrong value
            source_class="candidate_profile",
            ingestion_timestamp="2026-01-01T00:00:00+00:00",
            source_document_id="doc_001",
            source_version_hash="abc123",
        )
        
        is_valid, errors = schema.validate_chunk(chunk)
        assert not is_valid
        assert any("apps_rg" in e for e in errors)
    
    def test_schema_rejects_disallowed_source_class(self):
        """PROOF: Chunks with rubrics/governance_docs source_class are rejected."""
        schema = FactVectorSchema()
        
        chunk = FactVectorChunk(
            chunk_id="test-001",
            content="Some governance policy content",
            app="apps_rg",
            source_class="governance_docs",  # Disallowed - belongs in process_docs
            ingestion_timestamp="2026-01-01T00:00:00+00:00",
            source_document_id="doc_001",
            source_version_hash="abc123",
        )
        
        is_valid, errors = schema.validate_chunk(chunk)
        assert not is_valid
        assert any("process_docs" in e for e in errors)
    
    def test_schema_accepts_valid_candidate_profile(self):
        """PROOF: Valid candidate_profile chunks pass validation."""
        schema = FactVectorSchema()
        
        chunk = FactVectorChunk(
            chunk_id="test-001",
            content="Senior software engineer with 10 years experience in Python and AWS.",
            app="apps_rg",
            source_class="candidate_profile",
            ingestion_timestamp="2026-01-01T00:00:00+00:00",
            source_document_id="resume_001",
            source_version_hash="abc123",
        )
        
        is_valid, errors = schema.validate_chunk(chunk)
        assert is_valid, f"Expected valid but got errors: {errors}"
    
    def test_schema_accepts_valid_project_evidence(self):
        """PROOF: Valid project_evidence chunks pass validation."""
        schema = FactVectorSchema()
        
        chunk = FactVectorChunk(
            chunk_id="test-001",
            content="Led migration of 100TB data warehouse to cloud platform.",
            app="apps_rg",
            source_class="project_evidence",
            ingestion_timestamp="2026-01-01T00:00:00+00:00",
            source_document_id="project_001",
            source_version_hash="abc123",
        )
        
        is_valid, errors = schema.validate_chunk(chunk)
        assert is_valid, f"Expected valid but got errors: {errors}"


class TestFactVectorsSeparation:
    """Test 4: fact_vectors is physically separate from process_docs."""
    
    def test_collection_names_are_different(self):
        """PROOF: fact_vectors and process_docs are different collection names."""
        schema = FactVectorSchema()
        
        assert schema.collection_name == "fact_vectors"
        assert schema.collection_name != "process_docs"
    
    def test_no_process_docs_collection_usage_in_ingest_module(self):
        """PROOF: fact_vector_ingest.py does not use process_docs collection.
        
        Note: Error messages may mention process_docs to explain rejection,
        but there's no actual code path that reads/writes process_docs.
        """
        import inspect
        from apps_rg.tools import fact_vector_ingest
        
        source = inspect.getsource(fact_vector_ingest)
        
        # Check that we don't import or use process_docs as a collection
        # Allow mentioning it in error messages/strings, but not as code paths
        import_patterns = [
            "from process_docs",
            "import process_docs",
            "get_collection(\"process_docs\"",
            "get_collection('process_docs'",
            "chroma_client.get_collection",
        ]
        
        for pattern in import_patterns:
            assert pattern not in source, (
                f"fact_vector_ingest should not use process_docs collection: {pattern}"
            )
        
        # Verify the module only targets fact_vectors collection
        # The schema itself defines the separation
        schema = FactVectorSchema()
        assert schema.collection_name == "fact_vectors"
    
    def test_chroma_document_format_is_correct(self):
        """PROOF: to_chroma_document produces correct Chroma format."""
        chunk = FactVectorChunk(
            chunk_id="test-001",
            content="Test content",
            app="apps_rg",
            source_class="candidate_profile",
            ingestion_timestamp="2026-01-01T00:00:00+00:00",
            source_document_id="doc_001",
            source_version_hash="abc123",
        )
        
        doc = chunk.to_chroma_document()
        
        # Chroma ingest pipeline format: {id: str, text: str, metadata: dict}
        assert "id" in doc
        assert "text" in doc
        assert "metadata" in doc
        assert doc["metadata"]["app"] == "apps_rg"
        assert doc["metadata"]["source_class"] == "candidate_profile"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
