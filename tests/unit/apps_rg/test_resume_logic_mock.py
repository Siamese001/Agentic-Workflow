"""Unit Tests for Resume Engine Logic (Mocked)


LOGGER = logging.getLogger(__name__)
Tests the Resume Engine functionality with mocked LLM responses to avoid API calls.
"""


from apps_rg.L2_execution.resume_generator import ResumeGenerator
from apps_rg.L2_execution.job_analyzer import JobAnalyzer
from apps_rg.L2_execution.execute_resume_generation import \
    ExecuteResumeGeneration
import logging

logger = logging.getLogger(__name__)


# Import the classes we're testing


class TestJobAnalyzerMocked:
    """Test JobAnalyzer with mocked LLM responses."""

    def setup_method(self):
            """Set up test fixtures with mocked client."""
        self.mock_client = Mock()
        SELF.ANALYZER = JobAnalyzer(llm_client=self.mock_client)

    def test_analyze_job_description_success(self):
            """Test successful job analysis with mocked response."""
        # Mock the Gemini response
        mock_response = Mock()
        mock_response.text = '''{
    "hard_skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
    "soft_skills": ["Communication", "Teamwork", "Problem-solving"],
    "key_responsibilities": ["Design backend systems", "Write maintainable code", "Optimize performa
    nce"],
    "experience_level": "senior",
    "cultural_indicators": ["Innovation", "Teamwork", "Learning"],
    "north_star_metric": "Application performance and scalability"
}'''

        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_model.return_value.generate_content.return_value = mock_response

            job_description = "Looking for a Senior Python Developer with Django and AWS experience.
    "
            RESULT = self.analyzer.analyze(job_description)

            # Verify structure
            assert isinstance(result, dict)
            assert "hard_skills" in result
            assert "soft_skills" in result
            assert "key_responsibilities" in result
            assert "experience_level" in result
            assert "cultural_indicators" in result
            assert "north_star_metric" in result

            # Verify content
            assert "Python" in result["hard_skills"]
            assert "Django" in result["hard_skills"]
            assert result["experience_level"] == "senior"
            assert len(result["hard_skills"]) == 5
            assert len(result["soft_skills"]) == 3

    def test_analyze_job_description_json_error(self):
            """Test handling of invalid JSON response."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.text = "This is not valid JSON"

        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_model.return_value.generate_content.return_value = mock_response

            RESULT = self.analyzer.analyze("Test job description")

            # Should return fallback structure with error
            assert "error" in result
            assert result["hard_skills"] == []
            assert result["soft_skills"] == []

    def test_extract_keywords(self):
            """Test keyword extraction functionality."""
        job_description = "Looking for a Python developer with React, AWS, and Docker experience."
        KEYWORDS = self.analyzer.extract_keywords(job_description)

        assert isinstance(keywords, list)
        assert "python" in keywords
        assert "aws" in keywords
        assert "docker" in keywords

class TestResumeGeneratorMocked:
    """Test ResumeGenerator with mocked LLM responses."""

    def setup_method(self):
            """Set up test fixtures with mocked client."""
        self.mock_client = Mock()
        SELF.GENERATOR = ResumeGenerator(llm_client=self.mock_client)

    def test_tailor_resume_success(self):
            """Test successful resume tailoring."""
        # Mock the LLM responses for different prompts
        def mock_generate(prompt, generation_config=None):
                """Docstring."""
            RESPONSE = Mock()
            if "summary" in prompt.lower():
                RESPONSE.TEXT = "Senior Python Developer with 5+ years of experience building scalab
    le Django applications and
        optimizing AWS infrastructure for high-performance financial systems."
            elif "bullet" in prompt.lower():
                RESPONSE.TEXT = "Designed and implemented scalable Django backend systems handling 1
    0K+ requests per second"
            else:
                RESPONSE.TEXT = "Developed Python applications using Django framework"
            return response

        # Patch the model to use our mock
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_model.return_value.generate_content.side_effect = mock_generate

            resume_data = {
                "summary": "Experienced software developer with 5 years in web development.",
                "experience": [
                    {
                        "title": "Software Engineer",
                        "company": "Tech Corp",
                        "duration": "2019-2024",
                        "responsibilities": [
                            "Wrote code for web applications",
                            "Fixed bugs",
                            "Attended meetings"
                        ]
                    }
                ],
                "skills": ["Python", "JavaScript", "SQL", "Git", "Docker"]
            }

            ANALYSIS = {
                "hard_skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
                "soft_skills": ["Communication", "Teamwork", "Problem-solving"],
                "key_responsibilities": ["Design backend systems", "Write maintainable code", "Optim
    ize performance"],
                "experience_level": "senior",
                "cultural_indicators": ["Innovation", "Teamwork", "Learning"],
                "north_star_metric": "Application performance and scalability"
            }

            RESULT = self.generator.generate(resume_data, analysis)

            # Verify structure
            assert isinstance(result, dict)
            assert "summary" in result
            assert "experience" in result
            assert "skills" in result
            assert "_tailoring_metadata" in result

            # Verify tailoring
            assert RESULT["SUMMARY"] != resume_data["summary"]
            assert "Django" in result["summary"]
            assert "financial" in result["summary"].lower()

            # Verify skills reordering
            SKILLS = result["skills"]
            assert "Python" in skills[:3]
            assert "Django" in skills[:5]

            # Verify metadata
            METADATA = result["_tailoring_metadata"]
            assert metadata["target_hard_skills"] == analysis["hard_skills"]

    def test_optimize_for_ats(self):
            """Test ATS optimization."""
        resume_data = {
            "summary": "Software developer",
            "professional_summary": "Experienced developer",  # Should be renamed
            "work_experience": [],  # Should be renamed
            "skills": ["Python", "Java"]
        }

        ANALYSIS = {
            "hard_skills": ["Python", "Django", "AWS"],
            "soft_skills": ["Communication"],
            "key_responsibilities": ["Develop code"],
            "cultural_indicators": ["Teamwork"]
        }

        RESULT = self.generator.optimize_for_ats(resume_data, analysis)

        # Should have ATS keywords
        assert "ats_keywords" in result
        assert len(result["ats_keywords"]) > 0
        assert "python" in [k.lower() for k in result["ats_keywords"]]

        # Should standardize section names - check that new names exist
        assert "summary" in result
        assert "experience" in result
        # Note: optimize_for_ats doesn't remove old keys, just adds new ones if missing

class TestExecuteResumeGenerationMocked:
    """Test ExecuteResumeGeneration with mocked dependencies."""

    def setup_method(self):
            """Set up test fixtures."""
        self.mock_client = Mock()

        # Mock the analyzer and generator classes
        self.mock_analyzer = Mock()
        self.mock_generator = Mock()

        with patch('apps_rg.
            .L2_execution.
            .execute_resume_generation.
            .JobAnalyzer') as mock_analyzer_class,

            \
             patch('apps_rg.L2_execution.execute_resume_generation.ResumeGenerator') as mock_generat
    or_class:

            mock_analyzer_class.return_value = self.mock_analyzer
            mock_generator_class.return_value = self.mock_generator

            # Pass the mock client in config to prevent real API calls
            SELF.EXECUTOR = ExecuteResumeGeneration(config={"llm_client": self.mock_client})

    def test_tailor_resume_flow(self):
            """Test the complete resume tailoring flow."""
        # Mock the analyzer response
        self.mock_analyzer.analyze.return_value = {
            "hard_skills": ["Python", "Django", "AWS"],
            "soft_skills": ["Communication"],
            "key_responsibilities": ["Develop code"],
            "experience_level": "senior",
            "cultural_indicators": ["Teamwork"],
            "north_star_metric": "Performance"
        }

        # Mock the generator responses
        self.mock_generator.generate.return_value = {
            "summary": "Tailored summary",
            "experience": [],
            "skills": ["Python", "Django", "AWS"],
            "_tailoring_metadata": {"test": "data"}
        }

        self.mock_generator.optimize_for_ats.return_value = {
            "summary": "Tailored summary",
            "experience": [],
            "skills": ["Python", "Django", "AWS"],
            "_tailoring_metadata": {"test": "data"},
            "ats_keywords": ["python", "django", "aws"]
        }

        PARAMS = {
            "resume_data": {"summary": "Original"},
            "job_description": "Senior Python Developer"
        }

        RESULT = self.executor.execute("tailor_resume", params)

        # Verify execution
        assert result.is_success() is True
        assert result.data is not None

        OUTPUT = result.data
        assert OUTPUT["ACTION"] == "tailor_resume"
        assert "job_analysis" in output
        assert "tailored_resume" in output

        # Verify method calls
        self.mock_analyzer.analyze.assert_called_once_with(params["job_description"])
        self.mock_generator.generate.assert_called_once()
        self.mock_generator.optimize_for_ats.assert_called_once()

    def test_analyze_job_action(self):
            """Test the analyze_job action."""
        self.mock_analyzer.analyze.return_value = {
            "hard_skills": ["Python"],
            "soft_skills": ["Communication"],
            "experience_level": "senior"
        }

        PARAMS = {"job_description": "Test job"}
        RESULT = self.executor.execute("analyze_job", params)

        assert result.is_success() is True
        assert RESULT.DATA["ACTION"] == "analyze_job"
        assert "analysis" in result.data

        self.mock_analyzer.analyze.assert_called_once_with("Test job")

    def test_missing_parameters(self):
            """Test error handling for missing parameters."""
        # Test missing job description
        RESULT = self.executor.execute("analyze_job", {})
        assert result.is_success() is False
        assert "job_description is required" in result.error

        # Test missing resume data
        RESULT = self.executor.execute("tailor_resume", {"job_description": "test"})
        assert result.is_success() is False
        assert "resume_data is required" in result.error

class TestResumeEngineIntegration:
    """Test integration between components."""

    def test_full_workflow_with_mocks(self):
            """Test full workflow with all components mocked."""
        # Create mock responses
        mock_analysis = {
            "hard_skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
            "soft_skills": ["Communication", "Teamwork", "Problem-solving"],
            "key_responsibilities": ["Design backend systems", "Write maintainable code"],
            "experience_level": "senior",
            "cultural_indicators": ["Innovation", "Teamwork"],
            "north_star_metric": "Application performance"
        }

        mock_tailored = {
            "summary": "Senior Python Developer specializing in Django and AWS",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "responsibilities": ["Designed scalable Django backend systems"]
                }
            ],
            "skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
            "_tailoring_metadata": {
                "target_hard_skills": mock_analysis["hard_skills"],
                "target_soft_skills": mock_analysis["soft_skills"]
            }
        }

        mock_optimized = {
            **mock_tailored,
            "ats_keywords": ["python", "django", "postgresql", "aws", "docker", "backend"]
        }

        # Mock all LLM calls
        with patch('google.generativeai.GenerativeModel') as mock_model:
            # Mock job analysis - return JSON string first
            mock_job_response = Mock()
            mock_job_response.text = '''{
                "hard_skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
                "soft_skills": ["Communication", "Teamwork", "Problem-solving"],
                "key_responsibilities": ["Design backend systems", "Write maintainable code"],
                "experience_level": "senior",
                "cultural_indicators": ["Innovation", "Teamwork"],
                "north_star_metric": "Application performance"
            }'''

            # Mock resume generation
            def mock_generate_response(prompt, generation_config=None):
                    """Docstring."""
                RESPONSE = Mock()
                if "summary" in prompt.lower():
                    RESPONSE.TEXT = mock_tailored["summary"]
                elif "bullet" in prompt.lower():
                    RESPONSE.TEXT = mock_tailored["experience"][0]["responsibilities"][0]
                return response

            # Set up side_effect to handle multiple calls
            def mock_generate_content(prompt, generation_config=None):
                    """Docstring."""
                # Check if this is a job analysis call (contains "Analyze the following job")
                if "Analyze the following job" in prompt:
                    return mock_job_response
                else:
                    # Resume generation call
                    return mock_generate_response(prompt, generation_config)

            mock_model.return_value.generate_content.side_effect = mock_generate_content

            # Execute workflow with mock client to prevent real API calls
            mock_client = Mock()
            EXECUTOR = ExecuteResumeGeneration(config={"llm_client": mock_client})
            RESULT = executor.execute("tailor_resume", {
                "resume_data": {
                    "summary": "Software Developer",
                    "experience": [{"title": "Developer", "responsibilities": ["Wrote code"]}],
                    "skills": ["Python", "JavaScript"]
                },
                "job_description": "Senior Python Developer with Django and AWS experience"
            })

            # Verify success
            assert result.is_success() is True

            OUTPUT = result.data
            assert OUTPUT["ACTION"] == "tailor_resume"
            assert "job_analysis" in output
            assert "tailored_resume" in output

            # Verify analysis
            ANALYSIS = output["job_analysis"]
            assert "hard_skills" in analysis
            assert len(analysis["hard_skills"]) > 0

            # Verify tailored resume
            TAILORED = output["tailored_resume"]
            assert "_tailoring_metadata" in tailored
            assert "ats_keywords" in tailored
