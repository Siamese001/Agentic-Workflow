#!/usr/bin/env python3
"""Comprehensive RAG pipeline document ingestion validation test."""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List


class RAGIngestionValidator:
    """Validator for RAG pipeline document ingestion."""

    def __init__(self):
        self.test_docs = []
        self.ingestion_results = []
        self.retrieval_results = []

    def create_test_documents(self) -> List[Path]:
        """Create various test documents for ingestion."""
        test_dir = Path("test_rag_documents")
        test_dir.mkdir(exist_ok=True)

        documents = []

        # 1. Text document
        txt_doc = test_dir / "claims_analysis.txt"
        txt_content = """
        Claims Analysis Report - Q4 2025

        Executive Summary:
        - Total claims processed: 15,432
        - Approval rate: 68.5%
        - Denial rate: 31.5%
        - Average processing time: 4.2 days

        Key Findings:
        1. Prior authorization denials increased by 23%
        2. Coding errors remain the primary denial reason (42%)
        3. Missing documentation accounts for 28% of denials
        4. Timely filing issues: 15% of denials
        5. Medical necessity: 12% of denials

        Recommendations:
        - Implement automated coding validation
        - Enhance documentation requirements
        - Streamline prior authorization process
        - Improve timely filing monitoring
        """
        txt_doc.write_text(txt_content.strip())
        documents.append(txt_doc)

        # 2. Markdown document
        md_doc = test_dir / "policy_guidelines.md"
        md_content = """
        # Medical Policy Guidelines

        ## Coverage Criteria

        ### Inpatient Hospital Stay
        1. **Medical Necessity**: Patient requires acute inpatient care
        2. **Intensity of Services**: Daily physician intervention required
        3. **Complexity**: Multiple comorbidities or complications

        ### Outpatient Services
        1. **Preventive Care**: Annual wellness visits covered
        2. **Diagnostic Tests**: Medically necessary testing covered
        3. **Therapeutic Services**: Evidence-based treatments covered

        ## Documentation Requirements

        ### Required Elements
        - Chief complaint
        - History of present illness
        - Physical examination findings
        - Diagnostic test results
        - Treatment plan
        - Progress notes

        ## Billing Codes
        - **CPT Codes**: Procedure codes for services rendered
        - **ICD-10 Codes**: Diagnosis codes
        - **HCPCS Codes**: Supplies and equipment
        """
        md_doc.write_text(md_content.strip())
        documents.append(md_doc)

        # 3. CSV document
        csv_doc = test_dir / "denial_codes.csv"
        csv_content = """Denial Code,Description,Frequency,Percentage
CO-16,Claim/service information missing,1245,8.1%
CO-97,Benefit determination for this service is pending,987,6.4%
CO-24,Services are not billed correctly,876,5.7%
CO-151,Payment adjusted because the claim is controlled by a liability plan,765,5.0%
PR-1,Deductible amount,654,4.2%
CO-226,This service may be billed only when performed,543,3.5%
CO-96,Non-covered charge(s),432,2.8%
PR-27,It has been determined that you are not enrolled in the plan,321,2.1%
CO-242,Services provided by an out-of-network provider,298,1.9%
PR-204,This claim/service is being held for review,276,1.8%
"""
        csv_doc.write_text(csv_content.strip())
        documents.append(csv_doc)

        # 4. HTML document
        html_doc = test_dir / "provider_manual.html"
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Provider Manual</title></head>
        <body>
            <h1>Provider Billing Manual</h1>

            <h2>Section 1: Claim Submission</h2>
            <p>All claims must be submitted within 365 days of service date.</p>
            <ul>
                <li>Electronic claims: 48-hour processing</li>
                <li>Paper claims: 14-day processing</li>
                <li>Faxed claims: Not accepted</li>
            </ul>

            <h2>Section 2: Modifiers</h2>
            <table>
                <tr><th>Modifier</th><th>Description</th><th>Usage</th></tr>
                <tr><td>-25</td><td>Significant Separately Identifiable E/M Service</td><td>Same day as procedure</td></tr>
                <tr><td>-59</td><td>Distinct Procedural Service</td><td>Separate procedure</td></tr>
                <tr><td>-91</td><td>Repeat Clinical Diagnostic Laboratory Test</td><td>Same test, different result</td></tr>
            </table>

            <h2>Section 3: Appeal Process</h2>
            <p>Providers have 180 days to appeal denied claims.</p>
            <ol>
                <li>Level 1: Internal review</li>
                <li>Level 2: External review</li>
                <li>Level 3: Independent review organization</li>
            </ol>
        </body>
        </html>
        """
        html_doc.write_text(html_content.strip())
        documents.append(html_doc)

        self.test_docs = documents
        return documents

    async def test_ingestion(self, orchestrator) -> Dict[str, Any]:
        """Test document ingestion for all formats."""
        print("\n[INGESTION TEST] Testing document ingestion...")

        ingestion_results = {}
        total_docs = len(self.test_docs)
        successful = 0

        for doc_path in self.test_docs:
            try:
                print(f"  Ingesting: {doc_path.name} ({doc_path.suffix})")

                # Time the ingestion
                import time
                start_time = time.time()

                # Ingest document
                result = orchestrator.ingest(doc_path)

                elapsed = time.time() - start_time

                # Validate result
                if result and len(result) > 0:
                    successful += 1
                    ingestion_results[doc_path.name] = {
                        "success": True,
                        "content_length": len(result),
                        "ingestion_time": elapsed,
                        "format": doc_path.suffix
                    }
                    print(f"    ✓ Success: {len(result)} chars in {elapsed:.3f}s")
                else:
                    ingestion_results[doc_path.name] = {
                        "success": False,
                        "error": "Empty result",
                        "format": doc_path.suffix
                    }
                    print(f"    ✗ Failed: Empty result")

            except Exception as e:
                ingestion_results[doc_path.name] = {
                    "success": False,
                    "error": str(e),
                    "format": doc_path.suffix
                }
                print(f"    ✗ Failed: {e}")

        self.ingestion_results = ingestion_results

        print(f"\n[INGESTION TEST] Results: {successful}/{total_docs} successful")
        return {
            "total": total_docs,
            "successful": successful,
            "success_rate": successful / total_docs,
            "details": ingestion_results
        }

    async def test_retrieval(self, orchestrator) -> Dict[str, Any]:
        """Test document retrieval with various queries."""
        print("\n[RETRIEVAL TEST] Testing document retrieval...")

        test_queries = [
            "What is the claims denial rate?",
            "What are the most common denial codes?",
            "How do I submit a claim appeal?",
            "What modifiers should I use for billing?",
            "What are the coverage criteria for inpatient stays?",
            "How long do I have to submit a claim?",
            "What documentation is required?",
            "What is the average processing time?"
        ]

        retrieval_results = {}
        successful_retrievals = 0

        for query in test_queries:
            try:
                print(f"  Query: {query[:50]}...")

                # Retrieve documents
                results = await orchestrator.retrieve(query, top_k=5)

                if results and len(results) > 0:
                    successful_retrievals += 1
                    retrieval_results[query] = {
                        "success": True,
                        "result_count": len(results),
                        "top_score": results[0].get('score', 0) if results else 0,
                        "results": results[:3]  # Keep top 3 for validation
                    }
                    print(f"    ✓ Found {len(results)} results")

                    # Show top result snippet
                    if results:
                        content = results[0].get('content', '')
                        snippet = content[:100].replace('\n', ' ')
                        print(f"      Top: {snippet}...")
                else:
                    retrieval_results[query] = {
                        "success": False,
                        "error": "No results",
                        "result_count": 0
                    }
                    print(f"    ✗ No results found")

            except Exception as e:
                retrieval_results[query] = {
                    "success": False,
                    "error": str(e),
                    "result_count": 0
                }
                print(f"    ✗ Error: {e}")

        self.retrieval_results = retrieval_results

        print(f"\n[RETRIEVAL TEST] Results: {successful_retrievals}/{len(test_queries)} successful")
        return {
            "total": len(test_queries),
            "successful": successful_retrievals,
            "success_rate": successful_retrievals / len(test_queries),
            "details": retrieval_results
        }

    def validate_content_quality(self) -> Dict[str, Any]:
        """Validate the quality of ingested content."""
        print("\n[QUALITY TEST] Validating content quality...")

        quality_metrics = {
            "total_docs": len(self.ingestion_results),
            "avg_content_length": 0,
            "format_coverage": {},
            "error_analysis": {}
        }

        total_length = 0
        format_counts = {}
        error_counts = {}

        for doc_name, result in self.ingestion_results.items():
            if result["success"]:
                total_length += result["content_length"]
                fmt = result["format"]
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
            else:
                error = result.get("error", "Unknown error")
                error_counts[error] = error_counts.get(error, 0) + 1

        quality_metrics["avg_content_length"] = total_length / max(len(self.ingestion_results), 1)
        quality_metrics["format_coverage"] = format_counts
        quality_metrics["error_analysis"] = error_counts

        print(f"  Average content length: {quality_metrics['avg_content_length']:.0f} chars")
        print(f"  Format coverage: {format_counts}")
        if error_counts:
            print(f"  Errors: {error_counts}")

        return quality_metrics

    def cleanup(self):
        """Clean up test documents."""
        test_dir = Path("test_rag_documents")
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
            print("\n[CLEANUP] Test documents removed")


async def test_rag_ingestion_e2e():
    """End-to-end validation of RAG pipeline document ingestion."""
    print("[RAG E2E] Starting RAG pipeline ingestion validation...")

    try:
        # Import RAG orchestrator
        from agentic_core.knowledge.engine.rag_orchestrator import SovereignRagOrchestrator

        # Initialize validator
        validator = RAGIngestionValidator()

        # Create test documents
        print("\n[RAG E2E] Creating test documents...")
        documents = validator.create_test_documents()
        print(f"  ✓ Created {len(documents)} test documents")

        # Initialize RAG orchestrator
        project_root = Path.cwd()
        orchestrator = SovereignRagOrchestrator(project_root)

        # Test 1: Document ingestion
        ingestion_result = await validator.test_ingestion(orchestrator)

        # Test 2: Document retrieval
        retrieval_result = await validator.test_retrieval(orchestrator)

        # Test 3: Content quality validation
        quality_result = validator.validate_content_quality()

        # Summary
        print("\n[RAG E2E] ✅ RAG pipeline ingestion validation completed!")
        print(f"[RAG E2E] Summary:")
        print(f"  - Ingestion: {ingestion_result['successful']}/{ingestion_result['total']} "
              f"({ingestion_result['success_rate']:.1%})")
        print(f"  - Retrieval: {retrieval_result['successful']}/{retrieval_result['total']} "
              f"({retrieval_result['success_rate']:.1%})")
        print(f"  - Avg content length: {quality_result['avg_content_length']:.0f} chars")
        print(f"  - Formats supported: {list(quality_result['format_coverage'].keys())}")

        # Success criteria
        success = (
            ingestion_result['success_rate'] >= 0.75 and  # 75% ingestion success
            retrieval_result['success_rate'] >= 0.50 and  # 50% retrieval success
            quality_result['avg_content_length'] > 100     # Meaningful content
        )

        if success:
            print(f"[RAG E2E] ✅ All validation criteria met!")
        else:
            print(f"[RAG E2E] ⚠ Some validation criteria not met")

        return success

    except ImportError as e:
        print(f"[RAG E2E] RAG pipeline not available: {e}")
        return False
    except Exception as e:
        print(f"[RAG E2E] ❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if 'validator' in locals():
            validator.cleanup()


if __name__ == "__main__":
    success = asyncio.run(test_rag_ingestion_e2e())
    exit(0 if success else 1)
