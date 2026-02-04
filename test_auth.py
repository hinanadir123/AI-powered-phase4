#!/usr/bin/env python3
"""
Test script to verify the backend authentication is working properly
"""

import sys
import os
import requests
import json

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend():
    print("Testing backend authentication endpoints...")
    
    # Test if the server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ Backend server is running")
        else:
            print("✗ Backend server is not responding properly")
            return False
    except Exception as e:
        print(f"✗ Backend server is not running: {e}")
        return False
    
    # Test API documentation is available
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✓ API documentation is accessible")
        else:
            print("✗ API documentation is not accessible")
            return False
    except Exception as e:
        print(f"✗ Could not access API documentation: {e}")
        return False
    
    # Test registration endpoint
    print("\nTesting registration...")
    try:
        register_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        
        response = requests.post("http://localhost:8000/auth/register", json=register_data)
        print(f"Registration response: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Registration successful")
            user_data = response.json()
            print(f"  User ID: {user_data.get('id')}")
        elif response.status_code == 400:
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"! Registration failed (may be OK if user already exists): {error_detail}")
        else:
            print(f"✗ Registration failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"✗ Registration test failed: {e}")
        return False
    
    # Test login endpoint
    print("\nTesting login...")
    try:
        login_data = {
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        
        response = requests.post("http://localhost:8000/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Login successful")
            token_data = response.json()
            print(f"  Token type: {token_data.get('token_type')}")
        elif response.status_code == 401:
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"✗ Login failed: {error_detail}")
            return False
        else:
            print(f"✗ Login failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Login test failed: {e}")
        return False
    
    print("\n✓ All authentication tests passed!")
    return True

if __name__ == "__main__":
    success = test_backend()
    if not success:
        print("\nBackend authentication is not working properly.")
        sys.exit(1)
    else:
        print("\nBackend authentication is working properly!")
        sys.exit(0)