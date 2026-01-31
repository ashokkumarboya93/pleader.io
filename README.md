# Pleader AI - Legal Assistant Application

> **Production-ready legal assistant powered by AI for Indian law**

Pleader AI is a full-stack legal assistance platform that combines RAG (Retrieval-Augmented Generation) with Google's Gemini AI to provide accurate, document-grounded legal advice focused exclusively on Indian law.

## 🌟 Features

### Backend
- **Authentication System**: Secure JWT-based auth with bcrypt password hashing
- **RAG Pipeline**: FAISS vector store + Gemini embeddings for document-grounded responses
- **Document Analysis**: Support for PDF, DOCX, TXT, JPG, PNG with OCR
- **Export Functionality**: Export chats and analyses as PDF, DOCX, or TXT
- **Rate Limiting**: Built-in API rate limiting for security
- **Health Monitoring**: `/api/health` endpoint with version tracking
- **Indian Law Focus**: All responses strictly based on Indian legal framework

### Frontend
- **Adaptive Themes**: 6 color presets (Green, Blue, Purple, Orange, Pink, Gray)
- **ChatGPT-Style UI**: Professional message formatting with animations
- **Voice Input**: Web Speech API integration for hands-free typing
- **Document Upload**: Drag-and-drop interface for easy file uploads
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Export Options**: One-click export of conversations and analyses

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ and Yarn
- MongoDB (local or MongoDB Atlas)
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Local Development

#### 1. Clone Repository
```bash
git clone https://github.com/ashokkumarboya93/Pleader.ai.git
cd Pleader.ai
```

#### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run backend
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
yarn install

# Configure environment
cp .env.example .env
# Edit .env with backend URL

# Run frontend
yarn start
```

### Demo Credentials
- **Email**: `test@pleader.ai`
- **Password**: `TestPass123`

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

## 🚢 Deployment

See detailed deployment guide in [DEPLOY.md](./DEPLOY.md)

**Quick Links:**
- [MongoDB Atlas Setup](https://www.mongodb.com/cloud/atlas)
- [Railway Deployment](https://railway.app)
- [Vercel Deployment](https://vercel.com)

## 📖 Documentation

- **API Docs**: Available at `http://localhost:8000/docs` when running locally
- **Deployment Guide**: See [DEPLOY.md](./DEPLOY.md)
- **Change Log**: See [AUDIT.md](./AUDIT.md)

## 🔒 Security

- JWT authentication
- Bcrypt password hashing
- Rate limiting
- File size limits (30MB)
- CORS configuration
- Security headers

## 🎨 Themes

6 color presets available: Green, Blue, Purple, Orange, Pink, Gray

## 📞 Support

For issues, create a GitHub issue or contact support.

---

**Built with ❤️ for the Indian legal community**
