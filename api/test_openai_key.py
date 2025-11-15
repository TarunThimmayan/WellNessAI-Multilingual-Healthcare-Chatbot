#!/usr/bin/env python3
"""
Test OpenAI API Key
This script tests if your OpenAI API key is working correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from openai import APIError, AuthenticationError


def load_environment():
    """Load .env from api/ or project root."""
    here = Path(__file__).resolve().parent
    candidates = [
        here / ".env",
        here.parent / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            load_dotenv(candidate, override=True)
            print(f"[OK] Loaded .env from: {candidate}")
            return True
    print("[WARN] No .env file found, using environment variables")
    load_dotenv()
    return False


def test_api_key():
    """Test OpenAI API key with a simple request."""
    print("=" * 60)
    print("OpenAI API Key Test")
    print("=" * 60)
    print()
    
    # Load environment
    load_environment()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in environment variables")
        print("\nPlease set OPENAI_API_KEY in your .env file:")
        print("  OPENAI_API_KEY=sk-...")
        return False
    
    # Check if key looks valid
    if not api_key.startswith("sk-"):
        print(f"[WARN] API key doesn't start with 'sk-' (found: {api_key[:10]}...)")
        print("This might not be a valid OpenAI API key format")
        print()
    
    print(f"[OK] API Key found: {api_key[:7]}...{api_key[-4:]}")
    print()
    
    # Initialize client
    try:
        client = OpenAI(api_key=api_key)
        print("[OK] OpenAI client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize OpenAI client: {e}")
        return False
    
    # Test 1: Simple chat completion
    print("\n" + "-" * 60)
    print("Test 1: Simple Chat Completion")
    print("-" * 60)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello! Your OpenAI API key is working correctly.' in one sentence."}
            ],
            max_tokens=50,
            temperature=0.7,
        )
        
        message = response.choices[0].message.content
        print(f"[OK] API call successful!")
        print(f"[OK] Model: {response.model}")
        print(f"[OK] Response: {message}")
        print(f"[OK] Tokens used: {response.usage.total_tokens} (prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})")
        
    except AuthenticationError as e:
        print(f"[ERROR] AUTHENTICATION ERROR: {e}")
        print("\nThis usually means:")
        print("  - Your API key is invalid or expired")
        print("  - Your API key doesn't have the required permissions")
        print("  - Your account has been suspended")
        return False
        
    except APIError as e:
        print(f"[ERROR] API ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        if hasattr(e, 'status_code'):
            print(f"   Status code: {e.status_code}")
        return False
        
    except Exception as e:
        print(f"[ERROR] UNEXPECTED ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False
    
    # Test 2: Account Information (Note: Usage API requires different endpoint)
    print("\n" + "-" * 60)
    print("Test 2: Account Information")
    print("-" * 60)
    print("[INFO] Usage information is available at:")
    print("   https://platform.openai.com/usage")
    print("   (Check your OpenAI dashboard for account balance and usage)")
    
    # Test 3: List available models (optional)
    print("\n" + "-" * 60)
    print("Test 3: Available Models")
    print("-" * 60)
    try:
        models = client.models.list()
        model_names = [model.id for model in models.data if 'gpt' in model.id.lower()][:5]
        print(f"[OK] Found {len(models.data)} total models")
        print(f"[OK] Sample GPT models: {', '.join(model_names)}")
    except Exception as e:
        print(f"[WARN] Could not list models: {e}")
        print("   (This is optional)")
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUCCESS] Your OpenAI API key is working correctly!")
    print("=" * 60)
    print("\nYou can now use OpenAI in your healthcare chatbot.")
    print("The API key has been tested and is ready to use.")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_api_key()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

