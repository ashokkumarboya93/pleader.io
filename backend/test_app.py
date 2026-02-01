import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def print_result(name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")
    if not success:
        sys.exit(1)

def test_health():
    try:
        response = requests.get("http://127.0.0.1:8000/api/health")
        data = response.json()
        success = response.status_code == 200 and data.get("status") == "ok" and data.get("database") == "connected"
        print_result("Health Check", success, f"DB Status: {data.get('database')}")
    except Exception as e:
        print_result("Health Check", False, str(e))

def test_signup_and_chat():
    email = f"test_{requests.utils.quote('user')}_scratch@example.com"
    # Randomize email to allow repeated runs
    import random
    email = f"test_user_{random.randint(1000, 9999)}@example.com"
    
    password = "password123"
    name = "Test User"
    
    # Signup
    try:
        payload = {"name": name, "email": email, "password": password}
        response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
        
        if response.status_code == 200:
            token = response.json().get("token")
            print_result("Signup", True, f"Created user: {email}")
        else:
            print_result("Signup", False, f"Status: {response.status_code}, Error: {response.text}")
            return
            
        # Chat
        headers = {"Authorization": f"Bearer {token}"}
        chat_payload = {"message": "What is Article 21 of the Indian Constitution?"}
        
        print("   Sending chat message... (this may take a few seconds)")
        chat_response = requests.post(f"{BASE_URL}/chat/send", json=chat_payload, headers=headers)
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            ai_msg = chat_data.get("ai_message", {}).get("content", "")
            success = len(ai_msg) > 10
            print_result("Chat Response", success, f"AI replied: {ai_msg[:100]}...")
        else:
            print_result("Chat Response", False, f"Status: {chat_response.status_code}, Error: {chat_response.text}")
            
    except Exception as e:
        print_result("Signup/Chat flow", False, str(e))

if __name__ == "__main__":
    print("Starting App Verification...")
    test_health()
    test_signup_and_chat()
    print("Verification Complete.")
