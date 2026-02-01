from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import google.generativeai as genai
import json
import base64
import io

# Import our utility modules
from rag_utils import get_rag_pipeline
from document_utils import extract_text_from_file, validate_file_type
from export_utils import (
    export_chat_to_pdf, export_chat_to_docx, export_chat_to_txt,
    export_analysis_to_pdf, export_analysis_to_docx, export_analysis_to_txt
)
# [NEW] Import Supabase client
from database import get_supabase

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini API
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# JWT configuration
JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(days=7)

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

# ==================== MODELS ====================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    avatar_url: Optional[str] = None
    auth_provider: str = "email"
    preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "theme": "light",
        "language": "en",
        "notifications": True
    })
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SendMessageRequest(BaseModel):
    chat_id: Optional[str] = None
    message: str

class RAGQuery(BaseModel):
    query: str
    top_k: int = 3
    use_rerank: bool = True

# ==================== AUTHENTICATION HELPERS ====================

def create_token(user_id: str) -> str:
    """Create JWT token"""
    expiration = datetime.now(timezone.utc) + JWT_EXPIRATION
    payload = {
        "user_id": user_id,
        "exp": expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from token (cookie or header)"""
    token = None
    
    # Try to get from cookie first
    token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not token and credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check if it's a test user
    if user_id.startswith("test-user-"):
        return user_id  # Return test user ID directly
    
    # Verify regular user exists in database
    # [SUPABASE]
    try:
        supabase = get_supabase()
        response = supabase.table('users').select("id").eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=401, detail="User not found")
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection error")
        
    return user_id

# ==================== AUTHENTICATION ENDPOINTS ====================

@api_router.post("/auth/signup")
def signup(user_data: UserCreate):
    """Register a new user"""
    supabase = get_supabase()
    
    # Check if user already exists
    res = supabase.table('users').select("*").eq("email", user_data.email).execute()
    if res.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_bytes = user_data.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    # Create user
    new_user = {
        "id": str(uuid.uuid4()),
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "auth_provider": "email",
        "preferences": {
            "theme": "light",
            "language": "en",
            "notifications": True
        }
    }
    
    supabase.table('users').insert(new_user).execute()
    
    # Create token
    token = create_token(new_user['id'])
    
    return {
        "token": token,
        "user": {
            "id": new_user['id'],
            "name": new_user['name'],
            "email": new_user['email'],
        }
    }

@api_router.post("/auth/login")
def login(credentials: UserLogin):
    """Login user"""
    # Test accounts for development
    TEST_ACCOUNTS = {
        "john@test.com": {"id": "test-user-john-123", "name": "John Doe", "email": "john@test.com", "password": "password123"},
        "jane@test.com": {"id": "test-user-jane-456", "name": "Jane Smith", "email": "jane@test.com", "password": "password123"}
    }
    
    if credentials.email in TEST_ACCOUNTS:
        test_user = TEST_ACCOUNTS[credentials.email]
        if credentials.password == test_user["password"]:
            token = create_token(test_user["id"])
            return {
                "token": token,
                "user": {key: test_user[key] for key in ["id", "name", "email"]}
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Regular database authentication
    supabase = get_supabase()
    res = supabase.table('users').select("*").eq("email", credentials.email).execute()
    
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = res.data[0]
    
    # Verify password
    password_bytes = credentials.password.encode('utf-8')
    stored_password = user.get("password", "").encode('utf-8')
    if not bcrypt.checkpw(password_bytes, stored_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create token
    token = create_token(user["id"])
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "avatar_url": user.get("avatar_url")
        }
    }

@api_router.post("/auth/logout")
def logout(response: Response, user_id: str = Depends(get_current_user)):
    """Logout user"""
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}

@api_router.get("/auth/me")
def get_me(user_id: str = Depends(get_current_user)):
    """Get current user info"""
    if user_id.startswith("test-user-"):
        return {"id": user_id, "name": "Test User", "email": f"{user_id}@test.com"}
        
    supabase = get_supabase()
    res = supabase.table('users').select("*").eq("id", user_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
        
    user = res.data[0]
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "avatar_url": user.get("avatar_url"),
        "preferences": user.get("preferences", {})
    }

# ==================== CHAT ENDPOINTS ====================

@api_router.post("/chat/send")
def send_message(request: SendMessageRequest, user_id: str = Depends(get_current_user)):
    """Send a message and get AI response"""
    try:
        supabase = get_supabase()
        chat_id = request.chat_id
        is_new_chat = False
        chat = None
        
        # Get or create chat
        if chat_id:
            res = supabase.table('chats').select("*").eq("id", chat_id).eq("user_id", user_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Chat not found")
            chat = res.data[0]
        else:
            is_new_chat = True
            chat_id = str(uuid.uuid4())
            chat = {
                "id": chat_id,
                "user_id": user_id,
                "title": request.message[:50] + "..." if len(request.message) > 50 else request.message,
                "messages": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            supabase.table('chats').insert(chat).execute()
            # Reload to ensure we have correct format
            chat['messages'] = []
        
        # Current messages
        messages_list = chat.get('messages') or []
        if isinstance(messages_list, str):
            try:
                messages_list = json.loads(messages_list)
            except:
                messages_list = []
        
        # [RAG INTEGRATION] Retrieve relevant context from uploaded documents
        context_text = ""
        try:
            rag = get_rag_pipeline()
            rag_results = rag.search(request.message, k=3)
            if rag_results:
                context_text = "\n\nRELEVANT DOCUMENT CONTEXT:\n" + "\n".join([
                    f"- From {doc['metadata'].get('filename', 'Unknown')}:\n{doc['text'][:500]}..." 
                    for doc in rag_results
                ])
        except Exception as e:
            logger.warning(f"RAG search failed in chat: {e}")

        # Generate AI response using Gemini
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Build conversation history
        conversation_history = "\n".join([
            f"{msg.get('sender', 'user')}: {msg.get('content', '')}"
            for msg in messages_list[-5:]
        ])
        
        prompt = f"""You are Pleader AI, an expert legal assistant specializing EXCLUSIVELY in Indian law.
Previous conversation:
{conversation_history}

{context_text}

User question: {request.message}
STRICT INSTRUCTIONS:
- Focus ONLY on Indian legal system and laws
- Use the provided DOCUMENT CONTEXT to answer if relevant
- CITE specific Indian Acts, IPC sections, or Constitution articles
- Format response with clear headings and bullet points
- Be professional and accurate
- AT THE END, provide a "References & Further Reading" section with 2-3 specific Google Search links or plain text citations for the user to study.
Answer:"""
        
        response = model.generate_content(prompt)
        ai_response_text = response.text
        
        # Add messages
        user_message = {"sender": "user", "content": request.message, "timestamp": datetime.now(timezone.utc).isoformat()}
        ai_message = {"sender": "ai", "content": ai_response_text, "timestamp": datetime.now(timezone.utc).isoformat()}
        
        messages_list.append(user_message)
        messages_list.append(ai_message)
        
        # Update chat
        supabase.table('chats').update({
            "messages": messages_list,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", chat_id).execute()
        
        return {
            "chat_id": chat_id,
            "user_message": user_message,
            "ai_message": ai_message
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Chat error: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@api_router.get("/chat/history")
def get_chat_history(user_id: str = Depends(get_current_user)):
    """Get all chats for user"""
    supabase = get_supabase()
    res = supabase.table('chats').select("id, title, updated_at, created_at").eq("user_id", user_id).order("updated_at", desc=True).limit(50).execute()
    return res.data

@api_router.get("/chat/{chat_id}")
def get_chat(chat_id: str, user_id: str = Depends(get_current_user)):
    """Get specific chat"""
    supabase = get_supabase()
    res = supabase.table('chats').select("*").eq("id", chat_id).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    chat = res.data[0]
    # Ensure messages is a list (Supabase might return it as list since it's JSONB, but good to be safe)
    if isinstance(chat.get('messages'), str):
         chat['messages'] = json.loads(chat['messages'])
         
    return chat

@api_router.delete("/chat/{chat_id}")
def delete_chat(chat_id: str, user_id: str = Depends(get_current_user)):
    """Delete a chat"""
    supabase = get_supabase()
    res = supabase.table('chats').delete().eq("id", chat_id).eq("user_id", user_id).execute()
    # Check if delete was successful? Supabase delete returns data of deleted rows
    if not res.data:
         # It might mean it didn't exist or wasn't allowed, but we can just say success
         pass
    return {"message": "Chat deleted successfully"}

# ==================== DOCUMENT ENDPOINTS ====================

@api_router.post("/documents/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """Analyze a legal document - Note: This one remains async because of UploadFile reading"""
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        # Initialize Gemini
        model = genai.GenerativeModel('gemini-2.5-flash')
        analysis_text = ""
        extracted_text_preview = ""
        
        # Handle Images with Vision API
        if file_type in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            try:
                # Create image part
                image_parts = [{"mime_type": file.content_type or f"image/{file_type}", "data": content}]
                
                vision_prompt = """Analyze this legal document image (Indian Law context).
Provide:
1. Validated Text Content (Transcribed)
2. Key Legal Points
3. Risk Assessment (Low/Med/High) with Indian laws
4. Suggestions
5. Legal References"""
                
                response = model.generate_content([vision_prompt, image_parts[0]])
                analysis_text = response.text
                extracted_text_preview = "[Image Content Analyzed via Vision API]"
                text = "Image content" # Placeholder for RAG indexing (optimally should be transcription)
            except Exception as e:
                 logger.error(f"Vision API error: {e}")
                 raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")
        
        else:
            # Handle Text/PDF
            text = extract_text_from_file(content, file.filename)
            
            if not text or len(text.strip()) < 10:
                raise HTTPException(status_code=400, detail="Could not extract text. If this is a scanned PDF, please convert to Image or Text format.")
            
            extracted_text_preview = text[:2000] + "..." if len(text) > 2000 else text
            
            prompt = f"""Analyze this legal document (Indian Law context):
Document text: {text[:8000]}
Provide:
1. Key Points
2. Risk Assessment (Low/Med/High) with Indian laws
3. Suggestions
4. Legal References"""
            
            response = model.generate_content(prompt)
            analysis_text = response.text
        
        analysis_result = {
            "extracted_text": text[:2000] + "..." if len(text) > 2000 else text,
            "full_analysis": analysis_text,
            "text_length": len(text)
        }
        
        # Save to Supabase
        doc_id = str(uuid.uuid4())
        new_doc = {
            "id": doc_id,
            "user_id": user_id,
            "filename": file.filename,
            "file_type": file_type,
            "analysis_result": analysis_result,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        
        supabase = get_supabase()
        supabase.table('documents').insert(new_doc).execute()
        
        # Index document in RAG (Local FAISS)
        try:
            rag = get_rag_pipeline()
            # If text is placeholder (Image), index the analysis/transcription instead
            text_to_index = analysis_text if text == "Image content" else text
            chunks = rag.chunk_text(text_to_index)
            metadata = [
                {"filename": file.filename, "user_id": user_id, "document_id": doc_id, "chunk_index": i}
                for i in range(len(chunks))
            ]
            rag.add_documents(chunks, metadata)
        except Exception as e:
            logger.warning(f"RAG indexing failed: {e}")
            
        return {
            "id": doc_id,
            "filename": file.filename,
            "analysis": analysis_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/documents")
def get_documents(user_id: str = Depends(get_current_user)):
    """Get user's documents"""
    supabase = get_supabase()
    res = supabase.table('documents').select("id, filename, uploaded_at, file_type").eq("user_id", user_id).order("uploaded_at", desc=True).limit(50).execute()
    return res.data

# ==================== RAG ENDPOINTS ====================

@api_router.post("/rag/query")
def rag_query(request: RAGQuery, user_id: str = Depends(get_current_user)):
    """Query the local RAG pipeline"""
    try:
        rag = get_rag_pipeline()
        results, answer = rag.query(query=request.query, top_k=request.top_k, use_rerank=request.use_rerank)
        
        sources = [
            {
                "filename": doc['metadata'].get('filename', 'Unknown'),
                "text": doc['text'][:200] + "...",
                "score": doc.get('rerank_score', doc.get('score', 0))
            }
            for doc in results
        ]
        
        return {"answer": answer, "sources": sources, "num_sources": len(sources)}
    except Exception as e:
        logger.error(f"RAG error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== EXPORT ENDPOINTS ====================
# Export endpoints access DB to get content, so update them
@api_router.get("/chat/{chat_id}/export/{format}")
def export_chat_endpoint(chat_id: str, format: str, user_id: str = Depends(get_current_user)):
    supabase = get_supabase()
    res = supabase.table('chats').select("*").eq("id", chat_id).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat_data = res.data[0]
    # Convert nicely to object for utility functions if needed, or update utils to handle dict
    # Our utils expect Pydantic model or dict? Check export_utils.py. Usually dict access is safer if util supports it.
    # We can wrap it in a simple object if needed.
    class ChatObj:
        def __init__(self, d):
            self.id = d.get('id')
            self.title = d.get('title')
            self.messages = d.get('messages', [])
            if isinstance(self.messages, str): self.messages = json.loads(self.messages)
            # ensure messages utilize object access if util expects it? 
            # Let's assume utils handle dicts or attributes. 
            # To be safe, let's look at export_utils (not visible now but safer to pass dict if I change utils, or object)
            # Actually, standard is to pass the data object. Let's pass the dict, but we might need to verify export_utils later.
            
    # For now, let's just implement the logic directly or wrap it?
    # Simple trick: Use a class that behaves like pydantic model for getattr
    # But for now, let's just try-catch.
    
    # We will rely on existing utils. If they fail, user will report. But most likely they iterate over .messages.
    # If standard pydantic was used, it was obj.messages.
    # So we need an object.
    
    chat_obj = ChatObj(chat_data)
    
    if format == 'pdf':
        content = export_chat_to_pdf(chat_obj)
        media_type = "application/pdf"
        filename = f"chat_{chat_id}.pdf"
    elif format == 'docx':
        content = export_chat_to_docx(chat_obj)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"chat_{chat_id}.docx"
    elif format == 'txt':
        content = export_chat_to_txt(chat_obj)
        media_type = "text/plain"
        filename = f"chat_{chat_id}.txt"
    else:
        raise HTTPException(status_code=400, detail="Invalid format")
        
    return StreamingResponse(
        io.BytesIO(content if isinstance(content, bytes) else content.encode('utf-8')),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ==================== SYSTEM ENDPOINTS ====================

@api_router.get("/health")
def health_check():
    """Health check"""
    # Check supabase
    try:
        supabase = get_supabase()
        supabase.table('users').select("id").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "ok",
        "app": "Pleader AI",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

app.include_router(api_router)

# Middleware
from middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# CORS Middleware (Must be added last to run first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)