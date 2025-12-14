import yaml
from pydantic import BaseModel
import instructor
from openai import AsyncOpenAI
import logging


logger = logging.getLogger(__name__)
class ViolationCheck(BaseModel):
    is_violation: bool
    reason: str

class ConstitutionalOverseer:
    def __init__(self, client: AsyncOpenAI, config_path: str = "config/constitution.yaml"):
        self.client = instructor.patch(client)
        with open(config_path, 'r') as f:
            self.rules = yaml.safe_load(f).get('safety_rules', [])

    async def verify(self, content: str) -> None:
        """Raises ValueError if content violates the constitution."""
        rule_text = "\n".join(self.rules)
        resp = await self.client.chat.completions.create(
            model="gpt-3.5-turbo", # Use cheap model for policing
            response_model=ViolationCheck,
            messages=[
                {"role": "system", "content": f"You are a safety filter. Rules:\n{rule_text}"},
                {"role": "user", "content": f"Assess this output:\n{content}"}
            ]
        )

        if resp.is_violation:
            raise ValueError(f"Constitutional Violation: {resp.reason}")
