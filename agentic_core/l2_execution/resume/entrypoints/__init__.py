"""
Resume Engine Entry Points

Entry point implementations for resume processing workflows.
"""

class ResumeEntryPoint:
    """Base class for resume engine entry points."""

    def __init__(self):
        self.initialized = True

    def process_resume(self, resume_data: dict) -> dict:
        """Process resume data and return structured output."""
        return {
            "status": "completed",
            "skills_extracted": [],
            "experience_parsed": {},
            "education_parsed": {}
        }

class ResumeAPIEntryPoint(ResumeEntryPoint):
    """API-based resume processing entry point."""

    def __init__(self):
        super().__init__()
        self.api_endpoint = "/api/resume/process"

    def process_resume(self, resume_data: dict) -> dict:
        """Process resume via API endpoint."""
        result = super().process_resume(resume_data)
        result["processing_method"] = "api"
        return result

__all__ = ['ResumeEntryPoint', 'ResumeAPIEntryPoint']
