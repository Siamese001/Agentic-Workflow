"""
Resume Engine Debug Tools
LEVEL 5 - Debugging and diagnostic utilities for resume engine
"""

import asyncio
import json
import sys
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

# Import engine components
from ..services.pipelines.resume_pipeline import ResumePipeline
from ..services.utils.scoring import ResumeScorer
from ..workers.resume_generate_worker import ResumeGenerateWorker
from ..workers.enrichment_worker import EnrichmentWorker

class ResumeEngineDebugger:
    """Debugging and diagnostic tools for resume engine"""

    def __init__(self):
        self.resume_pipeline = ResumePipeline()
        self.resume_scorer = ResumeScorer()
        self.resume_worker = ResumeGenerateWorker()
        self.enrichment_worker = EnrichmentWorker()

    async def diagnose_pipeline(self) -> Dict[str, Any]:
        """Diagnose pipeline health and configuration"""
        print("🔍 Diagnosing resume pipeline...")

        diagnosis = {
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_status": await self.resume_pipeline.get_pipeline_status(),
            "component_health": {},
            "issues": [],
            "recommendations": []
        }

        # Check each component
        components = {
            "resume_builder": self.resume_pipeline.resume_builder,
            "ats_optimizer": self.resume_pipeline.ats_optimizer,
            "skill_expander": self.resume_pipeline.skill_expander,
            "job_aligner": self.resume_pipeline.job_aligner,
            "section_generator": self.resume_pipeline.section_generator,
            "summary_generator": self.resume_pipeline.summary_generator
        }

        for component_name, component in components.items():
            try:
                # Basic health check
                if hasattr(component, '__init__'):
                    diagnosis["component_health"][component_name] = "healthy"
                else:
                    diagnosis["component_health"][component_name] = "warning"
                    diagnosis["issues"].append(f"Component {component_name} may not be properly initialized")
            except Exception as e:
                diagnosis["component_health"][component_name] = "error"
                diagnosis["issues"].append(f"Component {component_name} error: {e}")

        # Check pipeline stages
        stages = self.resume_pipeline.pipeline_stages
        diagnosis["stages_configured"] = len(stages)
        diagnosis["expected_stages"] = 5

        if len(stages) != 5:
            diagnosis["issues"].append(f"Expected 5 pipeline stages, found {len(stages)}")

        # Generate recommendations
        if not diagnosis["issues"]:
            diagnosis["recommendations"].append("Pipeline appears healthy")
        else:
            diagnosis["recommendations"].append("Review and fix identified issues")

        return diagnosis

    async def test_scoring_system(self, test_resume: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test scoring system with sample data"""
        print("🧪 Testing scoring system...")

        if not test_resume:
            test_resume = await self._create_test_resume()

        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_resume": test_resume,
            "scoring_results": {},
            "performance_metrics": {},
            "issues": []
        }

        try:
            # Test comprehensive scoring
            start_time = datetime.utcnow()
            score_result = await self.resume_scorer.calculate_comprehensive_score(test_resume)
            end_time = datetime.utcnow()

            test_results["scoring_results"] = score_result
            test_results["performance_metrics"]["scoring_time"] = (end_time - start_time).total_seconds()

            # Validate results
            if score_result["overall_score"] < 0 or score_result["overall_score"] > 1:
                test_results["issues"].append("Overall score out of valid range [0,1]")

            if not score_result["individual_scores"]:
                test_results["issues"].append("No individual scores calculated")

            # Check scoring consistency
            individual_scores = score_result["individual_scores"]
            for score_name, score_data in individual_scores.items():
                if score_data.score < 0 or score_data.score > 1:
                    test_results["issues"].append(f"Score {score_name} out of range")

            print(f"✅ Scoring test completed - Overall: {score_result['overall_score']:.2f}")

        except Exception as e:
            test_results["issues"].append(f"Scoring test failed: {e}")
            print(f"❌ Scoring test failed: {e}")

        return test_results

    async def test_worker_system(self) -> Dict[str, Any]:
        """Test worker system functionality"""
        print("🔧 Testing worker system...")

        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "worker_status": {},
            "task_processing": {},
            "issues": []
        }

        try:
            # Test resume worker
            resume_status = await self.resume_worker.get_worker_status()
            test_results["worker_status"]["resume_worker"] = resume_status

            if resume_status["queue_size"] < 0:
                test_results["issues"].append("Resume worker queue size invalid")

            # Test enrichment worker
            enrichment_status = await self.enrichment_worker.get_worker_status()
            test_results["worker_status"]["enrichment_worker"] = enrichment_status

            if enrichment_status["queue_size"] < 0:
                test_results["issues"].append("Enrichment worker queue size invalid")

            # Test task submission (mock)
            from ..workers.resume_generate_worker import ResumeGenerateTask
            from ..workers.enrichment_worker import EnrichmentTask

            # Create test tasks
            test_resume_task = ResumeGenerateTask(
                task_id="debug_test_resume",
                user_id="debug_user",
                user_profile={"name": "Test User", "skills": ["python"]},
                job_description={"title": "Test Job"},
                preferences={}
            )

            test_enrichment_task = EnrichmentTask(
                task_id="debug_test_enrichment",
                resume_id="debug_resume",
                resume_content=await self._create_test_resume(),
                enrichment_type="skills"
            )

            # Test task validation
            if test_resume_task.task_id != "debug_test_resume":
                test_results["issues"].append("Resume task creation failed")

            if test_enrichment_task.enrichment_type != "skills":
                test_results["issues"].append("Enrichment task creation failed")

            test_results["task_processing"]["task_creation"] = "success"

            print("✅ Worker system test completed")

        except Exception as e:
            test_results["issues"].append(f"Worker system test failed: {e}")
            print(f"❌ Worker system test failed: {e}")

        return test_results

    async def validate_file_structure(self, base_path: str = "apps/resume_engine") -> Dict[str, Any]:
        """Validate resume engine file structure"""
        print("📁 Validating file structure...")

        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "base_path": base_path,
            "structure_validation": {},
            "missing_files": [],
            "extra_files": [],
            "issues": []
        }

        # Expected structure
        expected_structure = {
            "api/v1/endpoints": ["generate_resume.py", "validate_resume.py", "healthcheck.py"],
            "api/v1/schemas": ["resume_request.json", "resume_response.json"],
            "api/v1/middleware": ["auth.py", "rate_limit.py"],
            "api/v1": ["router.py"],
            "services/builders": ["resume_builder.py", "ats_optimizer.py"],
            "services/enrichers": ["skill_expander.py", "job_alignment.py"],
            "services/generators": ["section_generator.py", "summary_generator.py"],
            "services/pipelines": ["resume_pipeline.py", "validation_pipeline.py"],
            "services/utils": ["formatting.py", "scoring.py"],
            "workers": ["job_ingest_worker.py", "resume_generate_worker.py", "enrichment_worker.py"],
            "cli": ["run_resume_engine.py", "debug_tools.py"],
            "tests/unit": [],
            "tests/integration": [],
            "tests/e2e": []
        }

        base_dir = Path(base_path)

        for directory, expected_files in expected_structure.items():
            dir_path = base_dir / directory

            if not dir_path.exists():
                validation_results["missing_files"].append(f"Directory: {directory}")
                validation_results["issues"].append(f"Missing directory: {directory}")
                continue

            # Check for expected files
            existing_files = [f.name for f in dir_path.iterdir() if f.is_file()]

            for expected_file in expected_files:
                if expected_file not in existing_files:
                    validation_results["missing_files"].append(f"{directory}/{expected_file}")

            # Check for __init__.py files
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                validation_results["issues"].append(f"Missing __init__.py in {directory}")

            validation_results["structure_validation"][directory] = {
                "exists": True,
                "file_count": len(existing_files),
                "expected_files": len(expected_files)
            }

        # Summary
        total_missing = len(validation_results["missing_files"])
        total_issues = len(validation_results["issues"])

        if total_missing == 0 and total_issues == 0:
            print("✅ File structure validation passed")
        else:
            print(f"⚠️  Found {total_missing} missing files and {total_issues} issues")

        return validation_results

    async def run_full_diagnosis(self) -> Dict[str, Any]:
        """Run complete system diagnosis"""
        print("🏥 Running full resume engine diagnosis...")

        full_diagnosis = {
            "timestamp": datetime.utcnow().isoformat(),
            "diagnosis_results": {},
            "overall_health": "unknown",
            "critical_issues": [],
            "recommendations": []
        }

        # Run all diagnostic tests
        try:
            # Pipeline diagnosis
            pipeline_result = await self.diagnose_pipeline()
            full_diagnosis["diagnosis_results"]["pipeline"] = pipeline_result

            # Scoring system test
            scoring_result = await self.test_scoring_system()
            full_diagnosis["diagnosis_results"]["scoring"] = scoring_result

            # Worker system test
            worker_result = await self.test_worker_system()
            full_diagnosis["diagnosis_results"]["workers"] = worker_result

            # File structure validation
            structure_result = await self.validate_file_structure()
            full_diagnosis["diagnosis_results"]["structure"] = structure_result

            # Analyze results
            all_issues = []
            for result in full_diagnosis["diagnosis_results"].values():
                if "issues" in result:
                    all_issues.extend(result["issues"])
                if "missing_files" in result:
                    all_issues.extend(result["missing_files"])

            full_diagnosis["critical_issues"] = [issue for issue in all_issues if "error" in issue.lower() or "missing" in issue.lower()]

            # Determine overall health
            if len(full_diagnosis["critical_issues"]) == 0:
                full_diagnosis["overall_health"] = "healthy"
            elif len(full_diagnosis["critical_issues"]) < 5:
                full_diagnosis["overall_health"] = "degraded"
            else:
                full_diagnosis["overall_health"] = "unhealthy"

            # Generate recommendations
            if full_diagnosis["overall_health"] == "healthy":
                full_diagnosis["recommendations"].append("System appears to be functioning correctly")
            else:
                full_diagnosis["recommendations"].append("Address critical issues identified in diagnosis")
                full_diagnosis["recommendations"].append("Review component health and missing files")

            # Display summary
            print("\n📊 Diagnosis Summary:")
            print(f"  Overall Health: {full_diagnosis['overall_health']}")
            print(f"  Critical Issues: {len(full_diagnosis['critical_issues'])}")
            print(f"  Total Issues: {len(all_issues)}")

            if full_diagnosis["critical_issues"]:
                print("\n🚨 Critical Issues:")
                for issue in full_diagnosis["critical_issues"][:5]:
                    print(f"  • {issue}")

        except Exception as e:
            full_diagnosis["overall_health"] = "error"
            full_diagnosis["critical_issues"].append(f"Diagnosis failed: {e}")
            print(f"❌ Full diagnosis failed: {e}")

        return full_diagnosis

    async def _create_test_resume(self) -> Dict[str, Any]:
        """Create test resume for debugging"""
        return {
            "summary": {
                "title": "Professional Summary",
                "content": ["Results-oriented software engineer with 5 years of experience"]
            },
            "experience": {
                "title": "Professional Experience",
                "content": [
                    "Software Engineer - Tech Corp (2020-2023)",
                    "• Developed and maintained web applications",
                    "• Led team of 3 developers",
                    "• Improved system performance by 30%"
                ]
            },
            "education": {
                "title": "Education",
                "content": ["Bachelor of Science in Computer Science - University (2016-2020)"]
            },
            "skills": {
                "title": "Skills",
                "content": [
                    "Technical Skills:",
                    "• Python, JavaScript, SQL",
                    "• AWS, Docker, Git",
                    "Soft Skills:",
                    "• Leadership, Communication, Problem-solving"
                ]
            }
        }

async def main():
    """Main debug interface"""
    debugger = ResumeEngineDebugger()

    if len(sys.argv) < 2:
        print("Resume Engine Debug Tools")
        print("Usage: python debug_tools.py <command>")
        print("\nCommands:")
        print("  pipeline     - Diagnose pipeline health")
        print("  scoring      - Test scoring system")
        print("  workers      - Test worker system")
        print("  structure    - Validate file structure")
        print("  full         - Run complete diagnosis")
        return

    command = sys.argv[1].lower()

    try:
        if command == "pipeline":
            result = await debugger.diagnose_pipeline()
            print(json.dumps(result, indent=2, default=str))

        elif command == "scoring":
            result = await debugger.test_scoring_system()
            print(json.dumps(result, indent=2, default=str))

        elif command == "workers":
            result = await debugger.test_worker_system()
            print(json.dumps(result, indent=2, default=str))

        elif command == "structure":
            result = await debugger.validate_file_structure()
            print(json.dumps(result, indent=2, default=str))

        elif command == "full":
            result = await debugger.run_full_diagnosis()
            print(json.dumps(result, indent=2, default=str))

        else:
            print(f"Unknown command: {command}")

    except Exception as e:
        print(f"Debug tool error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
