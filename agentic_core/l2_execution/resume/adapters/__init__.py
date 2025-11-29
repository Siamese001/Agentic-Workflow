"""
Resume Engine Adapters

Adapter implementations for different resume formats and sources.
"""

class ResumeAdapter:
    """Base class for resume adapters."""

    def __init__(self):
        self.initialized = True

    def adapt(self, raw_data: dict) -> dict:
        """Adapt raw data to standardized resume format."""
        return {
            "personal_info": {},
            "experience": [],
            "education": [],
            "skills": []
        }

class PDFResumeAdapter(ResumeAdapter):
    """Adapter for PDF resume files."""

    def __init__(self):
        super().__init__()
        self.supported_formats = [".pdf"]

    def adapt(self, raw_data: dict) -> dict:
        """Adapt PDF resume data."""
        result = super().adapt(raw_data)
        result["source_format"] = "pdf"
        return result

class JSONResumeAdapter(ResumeAdapter):
    """Adapter for JSON resume data."""

    def __init__(self):
        super().__init__()
        self.supported_formats = [".json"]

    def adapt(self, raw_data: dict) -> dict:
        """Adapt JSON resume data."""
        result = super().adapt(raw_data)
        result["source_format"] = "json"
        return result

__all__ = ['ResumeAdapter', 'PDFResumeAdapter', 'JSONResumeAdapter']
