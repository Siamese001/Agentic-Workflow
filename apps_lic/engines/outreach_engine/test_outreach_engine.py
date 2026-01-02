from __future__ import annotations
#!/usr/bin/env python3
"""
Test script for the automated_lead_vetting function.
This demonstrates the Outreach Engine's Automated Lead Vetting & Contact use case.
"""

import json

from outreach_engine import automated_lead_vetting


# Mock MCP Tools for testing
class MockMCPTools:
    def fetch(self, url, max_length):
        if url == "https://techcorp.example.com/news":
            return """# TechCorp Announces Series C Funding Round

TechCorp today announced the successful completion of its Series C funding round, raising $50 million to accelerate product development and expand market presence.

## Key Highlights
- $50 million raised from leading venture capital firms
- Plans to hire 100+ engineers in the next 12 months
- Launch of new AI-powered platform scheduled for Q1 2024
- Recent award for "Most Innovative Enterprise Solution"

## Leadership Comments
"We're excited about this milestone and the opportunity to scale our impact," said CEO Jane Smith.

## Contact
For media inquiries: press@techcorp.com
 careers@techcorp.com"""
        raise ValueError(f"Invalid URL: {url}")

    def search_nodes(self, query):
        if "Alice Johnson" in query:
            return json.dumps({
                "entities": [
                    {
                        "name": "Jane Smith",
                        "title": "CEO",
                        "company": "TechCorp",
                        "email": "jane.smith@techcorp.com",
                        "relationship": "met at conference 2023"
                    },
                    {
                        "name": "Mike Chen",
                        "title": "Engineering Manager",
                        "company": "TechCorp",
                        "email": "mike.chen@techcorp.com",
                        "relationship": "former colleague"
                    }
                ]
            })
        return json.dumps({"entities": []})

    def search_records(self, query, index, top_k, namespace):
        # Simulating Pinecone finding the best outreach template
        return json.dumps([{
            "id": "outreach-001",
            "text": """I hope this message finds you well. I wanted to reach out regarding the exciting developments at your company. Your recent achievements demonstrate impressive vision and execution, and I believe my experience could contribute to your continued success.""",
            "metadata": {
                "template_type": "funding_round_outreach",
                "success_rate": "0.78"
            }
        }])

    def send_email(self, recipient, subject, body):
        # print(f"[EMAIL MOCK] Sending to: {recipient}")  # [Security Fix]
        # print(f"[EMAIL MOCK] Subject: {subject}")  # [Security Fix]
        # print(f"[EMAIL MOCK] Body preview: {body[:100]}...")  # [Security Fix]
        return "Email sent successfully"

    def add_observations(self, observations):
        # print(f"[MEMORY MOCK] Adding observations: {observations}")  # [Security Fix]
        return "Memory updated successfully"

# Mock Logger


class MockLogger:
    pass
    # def info(self, msg): print(f"[INFO] {msg}")  # [Security Fix]
    # def warning(self, msg): print(f"[WARN] {msg}")  # [Security Fix]
    # def error(self, msg): print(f"[ERROR] {msg}")  # [Security Fix]


def test_lead_vetting():
    """Test the automated_lead_vetting function with mock data."""

    # print("=" * 60)  # [Security Fix]
    # print("🧪 Testing Outreach Engine - Automated Lead Vetting")  # [Security Fix]
    # print("=" * 60)  # [Security Fix]

    # Initialize mock tools and Logger
    mock_tools = MockMCPTools()
    Logger = MockLogger()

    # Pass tools as dictionary
    tools = {
        'fetch': mock_tools.fetch,
        'search_nodes': mock_tools.search_nodes,
        'search_records': mock_tools.search_records,
        'send_email': mock_tools.send_email,
        'add_observations': mock_tools.add_observations
    }

    # Test Case 1: Successful lead vetting and outreach
    # print("\n--- Test Case 1: Successful Lead Vetting ---")  # [Security Fix]
    result = automated_lead_vetting(
        company_url="https://techcorp.example.com/news",
        user_name="Alice Johnson",
        tools=tools,
        Logger=Logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # Test Case 2: Invalid company URL
    # print("\n" + "=" * 60)  # [Security Fix]
    # print("\n--- Test Case 2: Invalid Company URL ---")  # [Security Fix]
    result = automated_lead_vetting(
        company_url="https://invalid.url",
        user_name="Alice Johnson",
        tools=tools,
        Logger=Logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # Test Case 3: User with no contacts
    # print("\n" + "=" * 60)  # [Security Fix]
    # print("\n--- Test Case 3: User with No Contacts ---")  # [Security Fix]
    result = automated_lead_vetting(
        company_url="https://techcorp.example.com/news",
        user_name="Unknown User",
        tools=tools,
        Logger=Logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # print("\n" + "=" * 60)  # [Security Fix]
    # print("✅ Test completed!")  # [Security Fix]


if __name__ == "__main__":
    test_lead_vetting()

