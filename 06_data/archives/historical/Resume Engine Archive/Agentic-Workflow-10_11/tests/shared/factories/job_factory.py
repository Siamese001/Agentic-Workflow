"""Job Factory for Testing."""

class JobFactory:
    """Factory for creating Job test objects."""
    
    @staticmethod
    def create(
        title="Software Engineer",
        company="Tech Corp",
        requirements=None,
        experience_years=3
    ):
        """Create a Job dict."""
        return {
            "title": title,
            "company": company,
            "requirements": requirements or ["Python", "AWS"],
            "experience_years": experience_years,
        }

class ResumeFactory:
    """Factory for creating Resume test objects."""
    
    @staticmethod
    def create(
        name="John Doe",
        summary="Experienced developer",
        skills=None,
        experience_years=5
    ):
        """Create a Resume dict."""
        return {
            "name": name,
            "summary": summary,
            "skills": skills or ["Python", "JavaScript", "AWS"],
            "experience_years": experience_years,
        }

def test_job_factory():
    """Test JobFactory."""
    job = JobFactory.create(title="ML Engineer")
    assert job["title"] == "ML Engineer"

def test_resume_factory():
    """Test ResumeFactory."""
    resume = ResumeFactory.create(name="Jane Doe")
    assert resume["name"] == "Jane Doe"
