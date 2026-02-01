#!/usr/bin/env python3
"""
Script to create predefined test accounts for easy login during development
"""

import asyncio
import os
import bcrypt
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Test accounts data
TEST_ACCOUNTS = [
    {
        "name": "John Doe",
        "email": "john@test.com",
        "password": "password123"
    },
    {
        "name": "Jane Smith", 
        "email": "jane@test.com",
        "password": "password123"
    }
]

async def create_test_accounts():
    """Create test accounts in the database"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        print("Creating test accounts...")
        
        for account in TEST_ACCOUNTS:
            # Check if account already exists
            existing_user = await db.users.find_one({"email": account["email"]})
            if existing_user:
                print(f"✓ Account {account['email']} already exists")
                continue
            
            # Hash password
            password_bytes = account["password"].encode('utf-8')
            hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
            
            # Create user document
            user_doc = {
                "id": str(uuid.uuid4()),
                "name": account["name"],
                "email": account["email"],
                "password": hashed_password,
                "avatar_url": None,
                "auth_provider": "email",
                "preferences": {
                    "theme": "light",
                    "language": "en",
                    "notifications": True
                },
                "created_at": datetime.now(timezone.utc),
                "last_active": datetime.now(timezone.utc)
            }
            
            # Insert user
            await db.users.insert_one(user_doc)
            print(f"✓ Created account: {account['email']} (password: {account['password']})")
        
        print("\n" + "="*50)
        print("TEST ACCOUNTS READY!")
        print("="*50)
        print("You can now login with these credentials:")
        print()
        for account in TEST_ACCOUNTS:
            print(f"Email: {account['email']}")
            print(f"Password: {account['password']}")
            print("-" * 30)
        
        client.close()
        
    except Exception as e:
        print(f"Error creating test accounts: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_accounts())