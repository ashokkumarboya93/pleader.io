
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"c:\Users\Master\Desktop\Pleader IO\pleader.io\backend\.env")
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello")
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAILURE: {e}")
