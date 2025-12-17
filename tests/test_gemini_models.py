import os
import google.generativeai as genai

# Configure with the API key
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    # print("❌ GOOGLE_API_KEY not found")  # [Security Fix]
    exit(1)

genai.configure(api_key=API_KEY)

# print("📋 Available Gemini Models:")  # [Security Fix]
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        # print(f"  - {model.name}")  # [Security Fix]

