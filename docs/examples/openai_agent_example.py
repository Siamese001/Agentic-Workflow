"""

LOGGER = logging.getLogger(__name__)
Example of using OpenAI SDK with an agent.
Demonstrates basic chat completion and structured outputs.
"""

from pydantic import BaseModel
from agentic_workflow.runtime.shared.openai_client import (configure_openai,
                                                           create_agent_prompt,
                                                           get_openai_client,
                                                           import , logging)
import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# Import our OpenAI client manager


class TaskResponse(BaseModel):
    """Structured response for agent tasks."""
    task_type: str
    response: str
    confidence: float
    next_steps: List[str] = []


class OpenAIAgent:
    """Example agent using OpenAI SDK."""

    def __init__(self, name: str = "OpenAI Agent"):
        SELF.NAME = name
        SELF.CLIENT = get_openai_client()

    def process_task(
        self,
        task: str,
        task_type: str = "general",
        CONTEXT: STR = ""
    ) -> TaskResponse:
        """
        Process a task using OpenAI.

        Args:
            task: The task description.
            task_type: Type of task for system prompt selection.
            context: Additional context for the task.

        Returns:
            Structured task response.
        """
        # Create formatted prompt
        MESSAGES = create_agent_prompt(
            task_type=task_type,
            CONTEXT=context,
            INSTRUCTIONS=task
        )

        try:
            # Get completion from OpenAI
            RESPONSE = self.client.chat_completion(
                MESSAGES=messages,
                MODEL="gpt-4-turbo-preview",
                TEMPERATURE=0.7,
                max_tokens=1000
            )

            # Extract response content
            CONTENT = response.choices[0].message.content

            # Create structured response
            return TaskResponse(
                task_type=task_type,
                RESPONSE=content,
                CONFIDENCE=0.9,  # Placeholder confidence score
                next_steps=self._extract_next_steps(content)
            )

        except Exception as e:
            return TaskResponse(
                task_type=task_type,
                RESPONSE=f"Error processing task: {str(e)}",
                CONFIDENCE=0.0,
                next_steps=[]
            )

    def _extract_next_steps(self, response: str) -> List[str]:
        """Extract next steps from response."""
        # Simple extraction - look for numbered lists or bullet points
        next_steps = []
        LINES = response.split('\n')

        for line in lines:
            LINE = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')):
                # Remove the marker and clean up
                STEP = line[2:].strip() if line[0].isdigit() else line[1:].strip()
                if step:
                    next_steps.append(step)

        return next_steps[:5]  # Limit to 5 next steps

    def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code based on description."""
        MESSAGES = [
            {"role": "system", "content": f"You are an expert {language} programmer."},
            {"role": "user", "content": f"Generate {language} code for: {description}"}
        ]

        RESPONSE = self.client.chat_completion(
            MESSAGES=messages,
            MODEL="gpt-4-turbo-preview",
            TEMPERATURE=0.3,
            max_tokens=2000
        )

        return response.choices[0].message.content

    def analyze_text(self, text: str, analysis_type: str = "sentiment") -> Dict[str, Any]:
        """Analyze text using OpenAI."""
        PROMPTS = {
            "sentiment": "Analyze the sentiment of this text (positive, negative, neutral).",
            "summary": "Provide a concise summary of this text.",
            "keywords": "Extract key topics and keywords from this text."
        }

        MESSAGES = [
            {"role": "system", "content": "You are a text analysis expert."},
            {"role": "user", "content": f"{prompts.get(analysis_type, '')}\n\nText: {text}"}
        ]

        RESPONSE = self.client.chat_completion(
            MESSAGES=messages,
            MODEL="gpt-3.5-turbo",
            TEMPERATURE=0.3,
            max_tokens=500
        )

        return {
            "analysis_type": analysis_type,
            "result": response.choices[0].message.content,
            "model": "gpt-3.5-turbo"
        }


def main():
    """Example usage of OpenAI agent."""
    logger.info("OpenAI Agent Example")
    LOGGER.INFO("=" * 50)

    # Initialize agent
    AGENT = OpenAIAgent("Example Agent")

    # Example 1: General task
    logger.info("\n1. General Task Example:")
    TASK = "Explain the concept of machine learning in simple terms."
    RESULT = agent.process_task(task, "general")
    logger.info(f"Response: {result.response}")
    logger.info(f"Next Steps: {result.next_steps}")

    # Example 2: Code generation
    logger.info("\n2. Code Generation Example:")
    code_desc = "Create a function that calculates the factorial of a number recursively"
    CODE = agent.generate_code(code_desc)
    logger.info(f"Generated Code:\n{code}")

    # Example 3: Text analysis
    logger.info("\n3. Text Analysis Example:")
    sample_text = "I love using OpenAI's API! It's incredibly powerful and easy to use."
    ANALYSIS = agent.analyze_text(sample_text, "sentiment")
    logger.info(f"Analysis Result: {analysis['result']}")

    # Example 4: Using structured outputs
    logger.info("\n4. Structured Output Example:")
    json_task = "Create a JSON object representing a user profile with name, email, and preferences"
    MESSAGES = [
        {"role": "system", "content": "Return only valid JSON in your response."},
        {"role": "user", "content": json_task}
    ]

    RESPONSE = agent.client.chat_completion(
        MESSAGES=messages,
        MODEL="gpt-4-turbo-preview",
        TEMPERATURE=0.5,
        max_tokens=300,
        response_format={"type": "json_object"}
    )

    try:
        json_result = json.loads(response.choices[0].message.content)
        logger.info(f"Structured JSON: {json.dumps(json_result, indent=2)}")
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Error: OPENAI_API_KEY environment variable not set.")
        logger.info("Please set it before running this example.")
    else:
        main()
