"""
Resume Engine Configuration

Configuration settings and parameters for resume processing.
"""

class ResumeConfig:
    """Configuration for resume processing engine."""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.supported_formats = [".pdf", ".docx", ".txt", ".json"]
        self.extraction_timeout = 30  # seconds
        self.enable_skill_extraction = True
        self.enable_experience_parsing = True
        self.enable_contact_extraction = True
    
    def get_config(self) -> dict:
        """Get configuration as dictionary."""
        return {
            "max_file_size": self.max_file_size,
            "supported_formats": self.supported_formats,
            "extraction_timeout": self.extraction_timeout,
            "enable_skill_extraction": self.enable_skill_extraction,
            "enable_experience_parsing": self.enable_experience_parsing,
            "enable_contact_extraction": self.enable_contact_extraction
        }

# Default configuration instance
default_config = ResumeConfig()

__all__ = ['ResumeConfig', 'default_config']
