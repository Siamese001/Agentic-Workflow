"""Simple Unit Tests for Resume Engine


LOGGER = logging.getLogger(__name__)
Tests the Resume Engine functionality with proper mocking to avoid API calls.
"""
import logging

# Test the core logic without requiring API keys

def test_job_analyzer_with_mocked_client() -> None:
    """Test JobAnalyzer with a completely mocked client."""
    with patch('apps_rg.L2_execution.job_analyzer.get_client') as mock_get_client:
        # Create a mock client
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Import after patching
        from apps_rg.L2_execution.job_analyzer import JobAnalyzer

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

            # Test the analyzer
            ANALYZER = JobAnalyzer()
            RESULT = analyzer.analyze("Test job description")

            # Verify results
            assert "hard_skills" in result
            assert "Python" in result["hard_skills"]
            assert len(result["hard_skills"]) == 5
            assert result["experience_level"] == "senior"

def test_resume_generator_with_mocked_client() -> None:
    """Test ResumeGenerator with a completely mocked client."""
    with patch('apps_rg.L2_execution.resume_generator.get_client') as mock_get_client:
        # Create a mock client
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Import after patching
        from apps_rg.L2_execution.resume_generator import ResumeGenerator

        # Mock the LLM responses
        mock_client.generate_content.return_value.text = "Senior Python Developer with Django expert
    ise"

        # Test the generator
        GENERATOR = ResumeGenerator()

        resume_data = {
            "summary": "Software Developer",
            "skills": ["Python", "JavaScript"]
        }

        ANALYSIS = {
            "hard_skills": ["Python", "Django"],
            "soft_skills": ["Communication"],
            "key_responsibilities": ["Develop code"],
            "experience_level": "senior",
            "cultural_indicators": ["Teamwork"],
            "north_star_metric": "Performance"
        }

        RESULT = generator.generate(resume_data, analysis)

        # Verify results
        assert "summary" in result
        assert "_tailoring_metadata" in result
        assert result["_tailoring_metadata"]["target_hard_skills"] == analysis["hard_skills"]

def test_execute_resume_generation_with_mocked_components() -> None:
    """Test ExecuteResumeGeneration with mocked components."""
    with patch('apps_rg.L2_execution.execute_resume_generation.JobAnalyzer') as MockAnalyzer, \
         patch('apps_rg.L2_execution.execute_resume_generation.ResumeGenerator') as MockGenerator:

        # Import after patching
        from apps_rg.L2_execution.execute_resume_generation import \
            ExecuteResumeGeneration

        # Setup mocks
        mock_analyzer = Mock()
        mock_generator = Mock()
        MockAnalyzer.return_value = mock_analyzer
        MockGenerator.return_value = mock_generator

        # Mock analyzer response
        mock_analyzer.analyze.return_value = {
            "hard_skills": ["Python", "Django"],
            "soft_skills": ["Communication"],
            "experience_level": "senior"
        }

        # Mock generator responses
        mock_generator.generate.return_value = {
            "summary": "Tailored summary",
            "skills": ["Python", "Django"]
        }
        mock_generator.optimize_for_ats.return_value = {
            "summary": "Tailored summary",
            "skills": ["Python", "Django"],
            "ats_keywords": ["python", "django"]
        }

        # Test the executor
        EXECUTOR = ExecuteResumeGeneration()

        PARAMS = {
            "resume_data": {"summary": "Original"},
            "job_description": "Senior Python Developer"
        }

        RESULT = executor.execute("tailor_resume", params)

        # Verify results
        assert result.success is True
        assert RESULT.OUTPUT["ACTION"] == "tailor_resume"
        assert "job_analysis" in result.output
        assert "tailored_resume" in result.output

        # Verify method calls
        mock_analyzer.analyze.assert_called_once()
        mock_generator.generate.assert_called_once()
        mock_generator.optimize_for_ats.assert_called_once()

def test_resume_engine_components_can_be_imported() -> None:
    """Test that all Resume Engine components can be imported."""
    # These imports should work without API keys

    # Verify classes exist
    assert JobAnalyzer is not None
    assert ResumeGenerator is not None
    assert ExecuteResumeGeneration is not None

    # Verify they have expected methods
    assert hasattr(JobAnalyzer, 'analyze')
    assert hasattr(ResumeGenerator, 'generate')
    assert hasattr(ExecuteResumeGeneration, 'execute')

def test_resume_engine_with_mock_client() -> None:
    """Test Resume Engine works with a mock client when no API key."""
    with patch('apps_rg.L2_execution.job_analyzer.get_client') as mock_get_client, \
         patch('apps_rg.L2_execution.resume_generator.get_client') as mock_get_client_gen:

        # Create mock clients
        mock_get_client.return_value = StubClient("google")
        mock_get_client_gen.return_value = StubClient("google")

        # Import and create instances

        # Should create without error
        ANALYZER = JobAnalyzer()
        GENERATOR = ResumeGenerator()
        EXECUTOR = ExecuteResumeGeneration()

        # Test with mock responses
        RESULT = analyzer.analyze("Test job")
        assert "error" in result  # Mock client returns error

        RESULT = generator.generate({"summary": "test"}, {"hard_skills": ["Python"]})
        assert "summary" in result  # Should still process structure

        RESULT = executor.execute("analyze_job", {"job_description": "test"})
        assert result.success is True  # Should handle gracefully

if __name__ == "__main__":
    # Run tests
    test_job_analyzer_with_mocked_client()
    test_resume_generator_with_mocked_client()
    test_execute_resume_generation_with_mocked_components()
    test_resume_engine_components_can_be_imported()
    test_resume_engine_with_mock_client()
