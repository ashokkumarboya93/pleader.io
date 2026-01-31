"""Middleware for rate limiting, security, and request tracking"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

# In-memory rate limiting (for production, use Redis)
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {
            '/api/rag/query': (10, 60),  # 10 requests per minute
            '/api/chat/send': (20, 60),   # 20 requests per minute  
            '/api/documents/analyze': (5, 60),  # 5 requests per minute
            'default': (100, 60)  # 100 requests per minute for other endpoints
        }
    
    def is_allowed(self, client_id: str, endpoint: str) -> bool:
        """Check if request is allowed based on rate limits"""
        now = time.time()
        
        # Get limit for this endpoint
        limit, window = self.limits.get(endpoint, self.limits['default'])
        
        # Clean old requests
        key = f"{client_id}:{endpoint}"
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address or user ID from token)
        client_id = request.client.host
        
        # Extract endpoint path
        path = request.url.path
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_id, path):
            logger.warning(f"Rate limit exceeded for {client_id} on {path}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} Time: {process_time:.3f}s"
            )
            
            # Add process time header
            response.headers['X-Process-Time'] = str(process_time)
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"Error: {str(e)} Time: {process_time:.3f}s"
            )
            raise
