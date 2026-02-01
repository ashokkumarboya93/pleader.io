
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"c:\Users\Master\Desktop\Pleader IO\pleader.io\backend\.env")

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

with open("models_found.txt", "w") as f:
    f.write("Searching for Flash/Pro/2.0 models...\n")
    try:
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower() or '2.0' in m.name or 'pro' in m.name.lower():
                    f.write(f"FOUND: {m.name}\n")
                    found = True
        if not found:
            f.write("No models found matching criteria.\n")
            # List all just in case
            f.write("All models:\n")
            for m in genai.list_models():
                 if 'generateContent' in m.supported_generation_methods:
                    f.write(f"ALL: {m.name}\n")
                    
    except Exception as e:
        f.write(f"Error: {e}\n")
