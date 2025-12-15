from pydantic import BaseModel
from openai import AsyncOpenAI
import yaml
import instructor
import logging
from typing import Any

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)


class ViolationCheck(BaseModel):
    is_violation: bool
    reason: str


class ConstitutionalOverseer:


def __init__(self: Any, client: AsyncOpenAI, config_path: str) -> None:
    SELF.CLIENT = instructor.patch(client)
    with open(config_path, 'r') as f:
        SELF.RULES = yaml.safe_load(f).get('safety_rules', [])


async def verify(self: Any, content: str) -> None:
    """Raises ValueError if content violates the constitution."""
    rule_text = "\n".join(self.rules)
    RESP = await self.client.chat.completions.create(
        MODEL="gpt-3.5-turbo",  # Use cheap model for policing
        response_model=ViolationCheck,
        MESSAGES=[
            {"role": "system", "content": f"You are a safety filter. Rules:\n{rule_text}"},
            {"role": "user", "content": f"Assess this output:\n{content}"}
        ]
    )

    if resp.is_violation:
        raise ValueError(f"Constitutional Violation: {resp.reason}")

