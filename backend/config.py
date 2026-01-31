"""Configuration management for the application"""
import os
from pathlib import Path
from typing import Optional
import subprocess

class Config:
    """Application configuration"""
    
    # MongoDB
    MONGO_URL: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME: str = os.environ.get('DB_NAME', 'pleader_ai_db')
    
    # Gemini AI
    GEMINI_API_KEY: str = os.environ.get('GEMINI_API_KEY', '')
    
    # JWT
    JWT_SECRET: str = os.environ.get('JWT_SECRET', 'pleader_ai_jwt_secret_key_2025_secure')
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', '*')
    
    # File Upload Limits
    MAX_FILE_SIZE: int = int(os.environ.get('MAX_FILE_SIZE', 30 * 1024 * 1024))  # 30MB default
    ALLOWED_EXTENSIONS: set = {'.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png'}
    
    # Rate Limiting (requests per minute)
    RATE_LIMIT_RAG: int = int(os.environ.get('RATE_LIMIT_RAG', 10))
    RATE_LIMIT_CHAT: int = int(os.environ.get('RATE_LIMIT_CHAT', 20))
    RATE_LIMIT_UPLOAD: int = int(os.environ.get('RATE_LIMIT_UPLOAD', 5))
    
    # App Info
    APP_NAME: str = "Pleader AI"
    APP_VERSION: str = "1.0.0"
    
    @staticmethod
    def get_git_version() -> str:
        """Get git commit hash for version tracking"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return 'unknown'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        if not cls.MONGO_URL:
            raise ValueError("MONGO_URL environment variable is required")
        return True

config = Config()
