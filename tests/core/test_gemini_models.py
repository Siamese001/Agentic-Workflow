import os
from typing import Any
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import google.generativeai as genai
api_key: Any = os.environ.get('GOOGLE_API_KEY')
if not api_key:
    pass
genai.configure(api_key=api_key)
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        pass
