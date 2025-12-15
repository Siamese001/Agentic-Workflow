# Create a simple test resume
test_resume = """
JOHN DOE
Software Engineer
==================

SUMMARY
Experienced software engineer with 5 years in full-stack development.

EXPERIENCE
Senior Developer - Tech Corp (2020-Present)
• Led development of microservices architecture
• Improved system performance by 40%

Software Engineer - StartupXYZ (2018-2020)
• Built REST APIs and web applications
• Implemented CI/CD pipelines

SKILLS
Python, JavaScript, React, Docker, AWS
"""

# Save test resume
with open("test_resume.txt", "w") as f:
    f.write(test_resume)

print("✅ Test resume created: test_resume.txt")
