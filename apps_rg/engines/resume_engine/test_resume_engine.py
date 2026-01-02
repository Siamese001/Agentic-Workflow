from __future__ import annotations
#!/usr/bin/env python3
"""
Test script for the generate_personalized_cover_letter function.
This demonstrates the Resume Engine's Hyper-Personalized Cover Letter use case.
"""

import json

from resume_engine import generate_personalized_cover_letter


# Mock MCP Tools for testing
class MockMCPTools:
    def fetch(self, url, max_length):
        if url == "https://careers.example.com/senior-dev":
            return """# Senior Software Engineer at TechCorp

We are looking for a Senior Software Engineer to join our growing team.

## Requirements
- 5+ years of experience in software development
- Strong proficiency in Python and JavaScript
- Experience with cloud platforms (AWS/Azure)
- Excellent communication skills

## Responsibilities
- Design and implement scalable software solutions
- Mentor junior developers
- Collaborate with cross-functional teams
- Drive technical excellence

## Benefits
- Competitive salary and equity
- Flexible work arrangements
- Professional development budget"""
        raise ValueError(f"Invalid URL: {url}")

    def search_nodes(self, query):
        if "John Doe" in query:
            return json.dumps({
                "entity": "John Doe",
                "preferences": {
                    "industry": "software engineering",
                    "communication_style": "professional yet friendly"
                },
                "career_goals": [
                    "lead a development team",
                    "work on scalable systems",
                    "mentor junior engineers"
                ],
                "relationships": [
                    "knows Jane Smith at TechCorp",
                    "worked with Mike Johnson at previous company"
                ],
                "skills": [
                    "Python", "JavaScript", "AWS", "Team Leadership"
                ]
            })
        return json.dumps({"entity": "Not found"})

    def search_records(self, query, index, top_k, namespace):
        # Simulating Pinecone finding the best cover letter template
        return json.dumps([{
            "id": "template-001",
            "text": """Dear Hiring Manager,

I am writing to express my strong interest in the Senior Software Engineer position at TechCorp. With my extensive background in software engineering and passion for building scalable solutions, I am confident I would be a valuable addition to your team.

Throughout my career, I have consistently demonstrated the ability to lead technical projects and mentor team members while maintaining high standards of code quality. My experience with cloud platforms and modern development practices aligns perfectly with the requirements outlined in your job description.

I am particularly excited about this opportunity because it combines my technical expertise with my desire to make a meaningful impact. The chance to work with cross-functional teams and drive technical excellence resonates deeply with my career aspirations.

I look forward to discussing how my skills and experience can benefit TechCorp's engineering team.

Sincerely,""",
            "metadata": {
                "template_type": "cover_letter",
                "success_rate": "0.85"
            }
        }])

    def write_file(self, path, content):
        # print(f"[FILESYSTEM MOCK] Writing to {path} ({len(content)} chars)")  # [Security Fix]
        return f"Successfully wrote {len(content)} characters to {path}"

    def add_observations(self, observations):
        # print(f"[MEMORY MOCK] Adding observations: {observations}")  # [Security Fix]
        return "Memory updated successfully"

# Mock Logger


class MockLogger:
    # def info(self, msg): print(f"[INFO] {msg}")  # [Security Fix]
    # def warning(self, msg): print(f"[WARN] {msg}")  # [Security Fix]
    # def error(self, msg): print(f"[ERROR] {msg}")  # [Security Fix]
    pass


def test_cover_letter_generation():
    """Test the generate_personalized_cover_letter function with mock data."""

    # print("=" * 60)  # [Security Fix]
    # print("🧪 Testing Resume Engine - Personalized Cover Letter")  # [Security Fix]
    # print("=" * 60)  # [Security Fix]

    # Initialize mock tools and Logger
    mock_tools = MockMCPTools()
    Logger = MockLogger()

    # Pass tools as dictionary
    tools = {
        'fetch': mock_tools.fetch,
        'search_nodes': mock_tools.search_nodes,
        'search_records': mock_tools.search_records,
        'write_file': mock_tools.write_file,
        'add_observations': mock_tools.add_observations
    }

    # Test Case 1: Successful cover letter generation
    # print("\n--- Test Case 1: Successful Cover Letter Generation ---")  # [Security Fix]
    result = generate_personalized_cover_letter(
        job_url="https://careers.example.com/senior-dev",
        user_name="John Doe",
        file_path_out="output/cover_letter_john_doe.md",
        tools=tools,
        Logger=Logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # Test Case 2: Invalid URL
    # print("\n" + "=" * 60)  # [Security Fix]
    # print("\n--- Test Case 2: Invalid Job URL ---")  # [Security Fix]
    result = generate_personalized_cover_letter(
        job_url="https://invalid.url",
        user_name="John Doe",
        file_path_out="output/cover_letter_error.md",
        tools=tools,
        Logger=Logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # Test Case 3: User not found in memory
    # print("\n" + "=" * 60)  # [Security Fix]
    # print("\n--- Test Case 3: User Not Found in Memory ---")  # [Security Fix]
    result = generate_personalized_cover_letter(
        job_url="https://careers.example.com/senior-dev",
        user_name="Unknown User",
        file_path_out="output/cover_letter_unknown.md",
        tools=tools,
        Logger=Logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # print("\n" + "=" * 60)  # [Security Fix]
    # print("✅ Test completed!")  # [Security Fix]


if __name__ == "__main__":
    test_cover_letter_generation()

