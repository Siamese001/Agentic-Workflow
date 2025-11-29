"""
Outreach Engine Adapters

Adapter implementations for different outreach platforms and formats.
"""

class OutreachAdapter:
    """Base class for outreach adapters."""
    
    def __init__(self):
        self.initialized = True
    
    def adapt(self, outreach_data: dict) -> dict:
        """Adapt outreach data to platform-specific format."""
        return {
            "message": "",
            "subject": "",
            "platform": "generic",
            "metadata": {}
        }

class EmailOutreachAdapter(OutreachAdapter):
    """Adapter for email outreach."""
    
    def __init__(self):
        super().__init__()
        self.platform = "email"
    
    def adapt(self, outreach_data: dict) -> dict:
        """Adapt outreach data for email format."""
        result = super().adapt(outreach_data)
        result["platform"] = "email"
        result["subject"] = outreach_data.get("subject", "Professional Connection")
        result["message"] = outreach_data.get("message", "")
        return result

class LinkedInOutreachAdapter(OutreachAdapter):
    """Adapter for LinkedIn outreach."""
    
    def __init__(self):
        super().__init__()
        self.platform = "linkedin"
    
    def adapt(self, outreach_data: dict) -> dict:
        """Adapt outreach data for LinkedIn format."""
        result = super().adapt(outreach_data)
        result["platform"] = "linkedin"
        result["message"] = outreach_data.get("message", "")
        result["connection_request"] = outreach_data.get("connection_request", True)
        return result

__all__ = ['OutreachAdapter', 'EmailOutreachAdapter', 'LinkedInOutreachAdapter']
