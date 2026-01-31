#!/usr/bin/env python3
"""Live API testing script for Pleader AI"""
import requests
import sys
import time

BASE_URL = "http://localhost:8001"
TEST_USER = {
    "name": "Test User",
    "email": f"test_{int(time.time())}@pleader.ai",
    "password": "TestPass123"
}

def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'ok'
    print(f"✅ Health check passed - Version: {data['version']}")

def test_signup():
    """Test user signup"""
    print(f"\nTesting signup with {TEST_USER['email']}...")
    r = requests.post(f"{BASE_URL}/api/auth/signup", json=TEST_USER)
    assert r.status_code == 200
    data = r.json()
    assert 'token' in data
    print("✅ Signup successful")
    return data['token']

def test_login(token):
    """Test user login"""
    print("\nTesting login...")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER['email'],
        "password": TEST_USER['password']
    })
    assert r.status_code == 200
    data = r.json()
    assert 'token' in data
    print("✅ Login successful")
    return data['token']

def test_get_me(token):
    """Test get current user"""
    print("\nTesting /api/auth/me...")
    r = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    data = r.json()
    assert data['email'] == TEST_USER['email']
    print(f"✅ Get user info successful - Email: {data['email']}")

def test_chat(token):
    """Test chat functionality"""
    print("\nTesting chat...")
    r = requests.post(
        f"{BASE_URL}/api/chat/send",
        json={"message": "What is Section 420 IPC?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    data = r.json()
    assert 'ai_message' in data
    print(f"✅ Chat working - Response length: {len(data['ai_message']['content'])} chars")
    return data['chat_id']

def test_chat_history(token):
    """Test chat history"""
    print("\nTesting chat history...")
    r = requests.get(
        f"{BASE_URL}/api/chat/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    print(f"✅ Chat history working - {len(data)} chats found")

def test_document_upload(token):
    """Test document upload"""
    print("\nTesting document upload...")
    test_doc = """LEASE AGREEMENT

This agreement is made on January 1, 2025 between Landlord and Tenant.

Terms:
1. Monthly Rent: Rs. 50,000
2. Security Deposit: Rs. 150,000
3. Duration: 11 months
"""
    
    files = {'file': ('test_lease.txt', test_doc, 'text/plain')}
    r = requests.post(
        f"{BASE_URL}/api/documents/analyze",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    data = r.json()
    assert 'analysis' in data
    print(f"✅ Document upload working - Analysis length: {len(data['analysis']['full_analysis'])} chars")
    return data['id']

def test_rag_stats(token):
    """Test RAG stats"""
    print("\nTesting RAG stats...")
    r = requests.get(
        f"{BASE_URL}/api/rag/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    data = r.json()
    assert 'total_documents' in data
    print(f"✅ RAG stats working - {data['total_documents']} documents indexed")

def test_rag_query(token):
    """Test RAG query"""
    print("\nTesting RAG query...")
    r = requests.post(
        f"{BASE_URL}/api/rag/query",
        json={"query": "What is the rent amount?", "top_k": 3},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    data = r.json()
    assert 'answer' in data
    print(f"✅ RAG query working - {len(data['sources'])} sources retrieved")

def test_export_chat(token, chat_id):
    """Test chat export"""
    print("\nTesting chat export (PDF)...")
    r = requests.get(
        f"{BASE_URL}/api/chat/{chat_id}/export/pdf",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/pdf'
    print(f"✅ Chat export working - PDF size: {len(r.content)} bytes")

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Pleader AI - Live API Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        test_health()
        token = test_signup()
        token = test_login(token)
        test_get_me(token)
        chat_id = test_chat(token)
        test_chat_history(token)
        doc_id = test_document_upload(token)
        time.sleep(2)  # Wait for indexing
        test_rag_stats(token)
        test_rag_query(token)
        test_export_chat(token, chat_id)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
