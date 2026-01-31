"""Comprehensive API tests for Pleader AI backend"""
import pytest
import asyncio
from httpx import AsyncClient
from server import app
import os

# Set test environment variables
os.environ['MONGO_URL'] = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
os.environ['DB_NAME'] = os.environ.get('DB_NAME', 'pleader_ai_test')
os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', 'test_key')
os.environ['JWT_SECRET'] = 'test_secret_key_for_pytest'
os.environ['CORS_ORIGINS'] = '*'

# Test user credentials
TEST_USER = {
    "name": "Test User",
    "email": "test@pleader.ai",
    "password": "TestPass123"
}

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    """Create test client"""
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_token(client):
    """Create test user and return auth token"""
    # Try to signup
    response = await client.post("/api/auth/signup", json=TEST_USER)
    if response.status_code == 400:  # User might already exist
        # Try to login
        response = await client.post("/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
    
    assert response.status_code == 200
    data = response.json()
    return data["token"]

class TestHealth:
    """Test health endpoint"""
    
    @pytest.mark.anyio
    async def test_health_check(self, client):
        """Test health endpoint returns proper status"""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "database" in data
        assert "timestamp" in data

class TestAuthentication:
    """Test authentication endpoints"""
    
    @pytest.mark.anyio
    async def test_signup(self, client):
        """Test user signup"""
        # Use unique email for each test
        import time
        unique_email = f"test_{int(time.time())}@pleader.ai"
        
        response = await client.post("/api/auth/signup", json={
            "name": "New User",
            "email": unique_email,
            "password": "NewPass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email
    
    @pytest.mark.anyio
    async def test_login(self, client, auth_token):
        """Test user login"""
        response = await client.post("/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
    
    @pytest.mark.anyio
    async def test_get_me(self, client, auth_token):
        """Test get current user endpoint"""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER["email"]
    
    @pytest.mark.anyio
    async def test_logout(self, client, auth_token):
        """Test logout endpoint"""
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

class TestChat:
    """Test chat endpoints"""
    
    @pytest.mark.anyio
    async def test_send_message(self, client, auth_token):
        """Test sending a chat message"""
        # Skip if no Gemini API key
        if not os.environ.get('GEMINI_API_KEY') or os.environ['GEMINI_API_KEY'] == 'test_key':
            pytest.skip("Gemini API key not configured")
        
        response = await client.post(
            "/api/chat/send",
            json={"message": "What is the Indian Contract Act?"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "chat_id" in data
        assert "user_message" in data
        assert "ai_message" in data
    
    @pytest.mark.anyio
    async def test_get_chat_history(self, client, auth_token):
        """Test getting chat history"""
        response = await client.get(
            "/api/chat/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestDocuments:
    """Test document endpoints"""
    
    @pytest.mark.anyio
    async def test_upload_txt_document(self, client, auth_token):
        """Test uploading a text document"""
        # Skip if no Gemini API key
        if not os.environ.get('GEMINI_API_KEY') or os.environ['GEMINI_API_KEY'] == 'test_key':
            pytest.skip("Gemini API key not configured")
        
        # Create a test document
        test_content = b"""LEASE AGREEMENT
        
This Lease Agreement is made on 1st January 2025 between:
Lessor: John Doe
Lessee: Jane Smith

The Lessor agrees to lease the property at 123 Main Street for monthly rent of Rs. 50,000.

Terms:
1. Duration: 11 months
2. Security Deposit: Rs. 150,000
3. Maintenance: Lessee responsible
"""
        
        response = await client.post(
            "/api/documents/analyze",
            files={"file": ("test_lease.txt", test_content, "text/plain")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "filename" in data
        assert "analysis" in data
    
    @pytest.mark.anyio
    async def test_get_documents(self, client, auth_token):
        """Test getting user documents"""
        response = await client.get(
            "/api/documents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestRAG:
    """Test RAG endpoints"""
    
    @pytest.mark.anyio
    async def test_rag_stats(self, client, auth_token):
        """Test getting RAG index statistics"""
        response = await client.get(
            "/api/rag/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
    
    @pytest.mark.anyio
    async def test_rag_query(self, client, auth_token):
        """Test querying RAG pipeline"""
        # Skip if no Gemini API key or no documents indexed
        if not os.environ.get('GEMINI_API_KEY') or os.environ['GEMINI_API_KEY'] == 'test_key':
            pytest.skip("Gemini API key not configured")
        
        response = await client.post(
            "/api/rag/query",
            json={"query": "What are the key terms?", "top_k": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data

class TestSecurity:
    """Test security features"""
    
    @pytest.mark.anyio
    async def test_unauthorized_access(self, client):
        """Test that protected endpoints require authentication"""
        response = await client.get("/api/chat/history")
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_file_size_limit(self, client, auth_token):
        """Test file size limit enforcement"""
        # Create a large file (> 30MB)
        large_content = b"A" * (31 * 1024 * 1024)  # 31MB
        
        response = await client.post(
            "/api/documents/analyze",
            files={"file": ("large_file.txt", large_content, "text/plain")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()
    
    @pytest.mark.anyio
    async def test_invalid_file_type(self, client, auth_token):
        """Test invalid file type rejection"""
        response = await client.post(
            "/api/documents/analyze",
            files={"file": ("test.exe", b"fake content", "application/exe")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
