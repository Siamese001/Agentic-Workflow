# Resume parsing tool
from .base import BaseTool

class ResumeParser(BaseTool):
    def execute(self, resume_text):
        return {"parsed": True, "data": {}}
