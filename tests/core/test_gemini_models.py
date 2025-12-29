import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import google.generativeai as genai
api_key: Any = os.environ.get('GOOGLE_API_KEY')
if not API_KEY:
    pass
genai.configure(api_key=API_KEY)
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        pass
