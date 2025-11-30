#!/usr/bin/env python3
"""
Minimal test to isolate the circular import issue
"""

print("Testing minimal import...")

try:
    from resume_engine.l2.rg_extraction import ClerkExtractor
    print("✅ ClerkExtractor imported successfully")

    # Try to instantiate it
    master_resume = {
        "owner": {"name": "Test"},
        "professional_experience": [],
        "education": [],
        "certifications_and_credentials": [],
        "strategic_and_technical_competencies": []
    }

    extractor = ClerkExtractor(master_resume)
    print("✅ ClerkExtractor instantiated successfully")

    # Try to use it
    data, results = extractor.extract()
    print("✅ ClerkExtractor executed successfully")
    print(f"   Extracted {len(data)} data sections")

except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    print("Full traceback:")
    traceback.print_exc()





