"""Shared Test Factories."""

class JobInputFactory:
    """Factory for creating JobInput test objects."""
    
    @staticmethod
    def create(title="Software Engineer", requirements=None):
        """Create a JobInput dict."""
        return {
            "title": title,
            "requirements": requirements or ["Python", "AWS"],
        }

class ResumeInputFactory:
    """Factory for creating ResumeInput test objects."""
    
    @staticmethod
    def create(summary="Experienced developer", skills=None):
        """Create a ResumeInput dict."""
        return {
            "summary": summary,
            "skills": skills or ["Python", "JavaScript"],
            "experience_sections": [],
            "projects": [],
        }

def test_job_input_factory():
    """Test JobInputFactory."""
    job = JobInputFactory.create()
    assert job["title"] == "Software Engineer"

def test_resume_input_factory():
    """Test ResumeInputFactory."""
    resume = ResumeInputFactory.create()
    assert resume["summary"] == "Experienced developer"
