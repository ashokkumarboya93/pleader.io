# Pleader AI - Deployment Guide

This guide covers deploying Pleader AI to various platforms including Railway, Vercel, Heroku, and self-hosted solutions.

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended)
Railway provides excellent support for full-stack applications with databases.

#### Backend Deployment
1. **Connect Repository**
   ```bash
   # Push your code to GitHub first
   git push origin main
   ```

2. **Create Railway Project**
   - Go to [Railway](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `pleader.io` repository
   - Choose the `backend` folder

3. **Environment Variables**
   ```env
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/pleader_ai_db
   GEMINI_API_KEY=your_gemini_api_key_here
   JWT_SECRET=your_secure_jwt_secret_here
   CORS_ORIGINS=https://your-frontend-domain.com
   PORT=8000
   ```

4. **Build Configuration**
   - Railway will auto-detect Python
   - Ensure `requirements.txt` is in the backend folder
   - Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

#### Frontend Deployment
1. **Create Another Railway Service**
   - Add new service to same project
   - Select `frontend` folder
   - Railway will auto-detect React

2. **Environment Variables**
   ```env
   REACT_APP_BACKEND_URL=https://your-backend-railway-url.railway.app
   ```

3. **Build Configuration**
   - Build command: `yarn build`
   - Start command: `yarn start`

### Option 2: Vercel + Railway
Perfect combination for modern web apps.

#### Backend on Railway
Follow Railway backend steps above.

#### Frontend on Vercel
1. **Connect Repository**
   - Go to [Vercel](https://vercel.com)
   - Import your GitHub repository
   - Set root directory to `frontend`

2. **Build Settings**
   ```
   Framework Preset: Create React App
   Build Command: yarn build
   Output Directory: build
   Install Command: yarn install
   ```

3. **Environment Variables**
   ```env
   REACT_APP_BACKEND_URL=https://your-backend-railway-url.railway.app
   ```

### Option 3: Heroku
Traditional but reliable platform.

#### Backend Deployment
1. **Prepare Heroku Files**
   ```bash
   # In backend folder, create Procfile
   echo "web: uvicorn server:app --host 0.0.0.0 --port \$PORT" > Procfile
   
   # Create runtime.txt
   echo "python-3.11.0" > runtime.txt
   ```

2. **Deploy**
   ```bash
   # Install Heroku CLI
   heroku create pleader-ai-backend
   heroku config:set MONGO_URL="your_mongodb_url"
   heroku config:set GEMINI_API_KEY="your_api_key"
   heroku config:set JWT_SECRET="your_jwt_secret"
   
   # Deploy
   git subtree push --prefix backend heroku main
   ```

#### Frontend Deployment
1. **Create Heroku App**
   ```bash
   heroku create pleader-ai-frontend
   heroku config:set REACT_APP_BACKEND_URL="https://pleader-ai-backend.herokuapp.com"
   
   # Deploy
   git subtree push --prefix frontend heroku main
   ```

## 🗄️ Database Setup

### MongoDB Atlas (Recommended)
1. **Create Cluster**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create free cluster
   - Choose region closest to your users

2. **Configure Access**
   - Add IP addresses (0.0.0.0/0 for development)
   - Create database user
   - Get connection string

3. **Connection String Format**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/pleader_ai_db?retryWrites=true&w=majority
   ```

### Local MongoDB
```bash
# Install MongoDB
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Start MongoDB
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # macOS

# Connection string
MONGO_URL=mongodb://localhost:27017
```

## 🔑 API Keys Setup

### Google Gemini API
1. **Get API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create new API key
   - Copy the key

2. **Set Environment Variable**
   ```env
   GEMINI_API_KEY=AIzaSyCWAZFUZS375ODu2Sl_bgkQTI_XQ9JW_fI
   ```

### JWT Secret
Generate a secure secret:
```bash
# Generate random secret
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🐳 Docker Deployment

### Docker Compose (Full Stack)
```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: pleader_mongo
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongodb_data:/data/db

  backend:
    build: ./backend
    container_name: pleader_backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://admin:password@mongodb:27017/pleader_ai_db?authSource=admin
      - GEMINI_API_KEY=your_gemini_api_key
      - JWT_SECRET=your_jwt_secret
      - CORS_ORIGINS=http://localhost:3000
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    container_name: pleader_frontend
    restart: always
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  mongodb_data:
```

### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN yarn build

# Install serve to run the build
RUN yarn global add serve

# Expose port
EXPOSE 3000

# Start application
CMD ["serve", "-s", "build", "-l", "3000"]
```

## 🔧 Environment Configuration

### Production Environment Variables

#### Backend (.env)
```env
# Database
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/pleader_ai_db
DB_NAME=pleader_ai_db

# AI Service
GEMINI_API_KEY=your_gemini_api_key_here

# Security
JWT_SECRET=your_super_secure_jwt_secret_here
JWT_ALGORITHM=HS256

# CORS
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-domain.com

# File Upload
MAX_FILE_SIZE=31457280  # 30MB in bytes

# Rate Limiting
RATE_LIMIT_RAG=10
RATE_LIMIT_CHAT=20
RATE_LIMIT_UPLOAD=5
```

#### Frontend (.env)
```env
# Backend API URL
REACT_APP_BACKEND_URL=https://your-backend-domain.com

# WebSocket port (for development)
WDS_SOCKET_PORT=443
```

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Code pushed to GitHub
- [ ] Environment variables configured
- [ ] MongoDB database created
- [ ] Gemini API key obtained
- [ ] Domain names configured (if using custom domains)

### Backend Deployment
- [ ] Dependencies installed correctly
- [ ] Database connection working
- [ ] API endpoints responding
- [ ] File upload working
- [ ] Authentication working
- [ ] CORS configured for frontend domain

### Frontend Deployment
- [ ] Build process successful
- [ ] Backend API URL configured
- [ ] Authentication flow working
- [ ] File upload working
- [ ] All pages loading correctly
- [ ] Responsive design working

### Post-deployment
- [ ] Health check endpoint responding
- [ ] User registration working
- [ ] Chat functionality working
- [ ] Document analysis working
- [ ] Export functionality working
- [ ] Error handling working
- [ ] Performance monitoring set up

## 🔍 Troubleshooting

### Common Issues

#### Backend Issues
1. **MongoDB Connection Failed**
   ```
   Error: MongoServerError: Authentication failed
   ```
   - Check MongoDB URL format
   - Verify username/password
   - Check IP whitelist in MongoDB Atlas

2. **Gemini API Error**
   ```
   Error: 403 API key not valid
   ```
   - Verify API key is correct
   - Check API key permissions
   - Ensure billing is enabled

3. **CORS Error**
   ```
   Error: CORS policy blocked
   ```
   - Add frontend domain to CORS_ORIGINS
   - Check protocol (http vs https)

#### Frontend Issues
1. **API Connection Failed**
   ```
   Error: Network Error
   ```
   - Check REACT_APP_BACKEND_URL
   - Verify backend is running
   - Check CORS configuration

2. **Build Failed**
   ```
   Error: Module not found
   ```
   - Run `yarn install`
   - Check Node.js version (18+)
   - Clear node_modules and reinstall

### Performance Optimization

#### Backend
- Use connection pooling for MongoDB
- Implement caching for frequent queries
- Optimize FAISS index size
- Use CDN for file uploads

#### Frontend
- Enable gzip compression
- Optimize bundle size
- Use lazy loading for components
- Implement service worker for caching

## 📊 Monitoring

### Health Checks
- Backend: `GET /api/health`
- Frontend: Check if app loads

### Logging
- Backend: FastAPI automatic logging
- Frontend: Browser console errors
- Database: MongoDB logs

### Metrics to Monitor
- Response times
- Error rates
- Database connections
- File upload success rates
- User authentication success

## 🔐 Security Considerations

### Production Security
- Use HTTPS everywhere
- Secure JWT secrets
- Implement rate limiting
- Validate all inputs
- Use environment variables for secrets
- Regular security updates
- Monitor for suspicious activity

### Database Security
- Use strong passwords
- Enable authentication
- Restrict IP access
- Regular backups
- Monitor access logs

---

For additional help, create an issue on GitHub or contact support.