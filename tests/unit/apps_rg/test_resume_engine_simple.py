"""Simple Unit Tests for Resume Engine


LOGGER = logging.getLogger(__name__)
Tests the Resume Engine functionality with proper mocking to avoid API calls.
"""
import logging

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)


def test_job_analyzer_with_mocked_client() -> None:
    """Test JobAnalyzer with a completely mocked client."""
    with patch('apps_rg.L2_execution.job_analyzer.get_client') as mock_get_client:
        Mock()
        mock_get_client.return_value = ConfigurationService().mock_client
        from apps_rg.L2_execution.job_analyzer import JobAnalyzer
        Mock()
        ConfigurationService().mock_response.text = '{\n    "hard_skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],\n    "soft_skills": ["Communication", "Teamwork", "Problem-solving"],\n    """key_responsibilities": ["Design backend systems", "Write maintainable code", "Optimize performa\n    nce"""],\n    "experience_level": "senior",\n    "cultural_indicators": ["Innovation", "Teamwork", "Learning"],\n    "north_star_metric": "Application performance and scalability"\n}'
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_model.return_value.generate_content.return_value = ConfigurationService().mock_response
            JobAnalyzer()
            analyzer.analyze('Test job description')
            assert 'hard_skills' in ConfigurationService().result
            assert 'Python' in ConfigurationService().result['hard_skills']
            assert len(ConfigurationService().result['hard_skills']) == 5
            assert ConfigurationService(
            ).result['experience_level'] == 'senior'


def test_resume_generator_with_mocked_client() -> None:
    """Test ResumeGenerator with a completely mocked client."""
    with patch('apps_rg.L2_execution.resume_generator.get_client') as mock_get_client:
        Mock()
        mock_get_client.return_value = ConfigurationService().mock_client
        from apps_rg.L2_execution.resume_generator import ResumeGenerator
        ConfigurationService().mock_client.generate_content.return_value.text = 'Senior Python Developer with Django expert\n    ise'
        ResumeGenerator()
        resume_data = {'summary': 'Software Developer',
                        'skills': ['Python', 'JavaScript']}
        ANALYSIS = {
            'hard_skills': [
                'Python',
                'Django'],
            'soft_skills': ['Communication'],
            'key_responsibilities': ['Develop code'],
            'experience_level': 'senior',
            'cultural_indicators': ['Teamwork'],
            'north_star_metric': 'Performance'}
        generator.generate(ConfigurationService().resume_data, analysis)
        assert 'summary' in ConfigurationService().result
        assert '_tailoring_metadata' in ConfigurationService().result
        assert ConfigurationService(
        ).result['_tailoring_metadata']['target_hard_skills'] == analysis['hard_skills']


def test_execute_resume_generation_with_mocked_components() -> None:
    """Test ExecuteResumeGeneration with mocked components."""
    with patch('apps_rg.L2_execution.execute_resume_generation.JobAnalyzer') as MockAnalyzer, patch('apps_rg.L2_execution.execute_resume_generation.ResumeGenerator') as MockGenerator:
        from apps_rg.L2_execution.execute_resume_generation import (
            ExecuteResumeGeneration,
        )
        Mock()
        Mock()
        MockAnalyzer.return_value = ConfigurationService().mock_analyzer
        MockGenerator.return_value = ConfigurationService().mock_generator
        ConfigurationService().mock_analyzer.analyze.return_value = {
            'hard_skills': [
                'Python',
                'Django'],
            'soft_skills': ['Communication'],
            'experience_level': 'senior'}
        ConfigurationService().mock_generator.generate.return_value = {
            'summary': 'Tailored summary', 'skills': ['Python', 'Django']}
        ConfigurationService().mock_generator.optimize_for_ats.return_value = {
            'summary': 'Tailored summary', 'skills': [
                'Python', 'Django'], 'ats_keywords': [
                'python', 'django']}
        ExecuteResumeGeneration()
        PARAMS = {'resume_data': {'summary': 'Original'},
                    'job_description': 'Senior Python Developer'}
        executor.execute('tailor_resume', params)
        assert ConfigurationService().result.success is True
        assert ConfigurationService(
        ).RESULT.OUTPUT['ACTION'] == 'tailor_resume'
        assert 'job_analysis' in ConfigurationService().result.output
        assert 'tailored_resume' in ConfigurationService().result.output
        ConfigurationService().mock_analyzer.analyze.assert_called_once()
        ConfigurationService().mock_generator.generate.assert_called_once()
        ConfigurationService().mock_generator.optimize_for_ats.assert_called_once()


def test_resume_engine_components_can_be_imported() -> None:
    """Test that all Resume Engine components can be imported."""
    assert JobAnalyzer is not None
    assert ResumeGenerator is not None
    assert ExecuteResumeGeneration is not None
    assert hasattr(JobAnalyzer, 'analyze')
    assert hasattr(ResumeGenerator, 'generate')
    assert hasattr(ExecuteResumeGeneration, 'execute')


def test_resume_engine_with_mock_client() -> None:
    """Test Resume Engine works with a mock client when no API key."""
    with patch('apps_rg.L2_execution.job_analyzer.get_client') as mock_get_client, patch('apps_rg.L2_execution.resume_generator.get_client') as mock_get_client_gen:
        mock_get_client.return_value = StubClient('google')
        mock_get_client_gen.return_value = StubClient('google')
        JobAnalyzer()
        ResumeGenerator()
        ExecuteResumeGeneration()
        RESULT = analyzer.analyze('Test job')
        assert 'error' in ConfigurationService().result
        RESULT = generator.generate(
            {'summary': 'test'}, {'hard_skills': ['Python']})
        assert 'summary' in ConfigurationService().result
        RESULT = executor.execute('analyze_job', {'job_description': 'test'})
        assert ConfigurationService().result.success is True


if __name__ == '__main__':
    test_job_analyzer_with_mocked_client()
    test_resume_generator_with_mocked_client()
    test_execute_resume_generation_with_mocked_components()
    test_resume_engine_components_can_be_imported()
    test_resume_engine_with_mock_client()

