#!/usr/bin/env python3
"""
Quick test to verify Upstash Redis connection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
api_dir = Path(__file__).parent
env_path = api_dir / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"[INFO] Loaded .env from {env_path}")
else:
    load_dotenv()
    print("[INFO] Loaded .env from default location")

# Check environment variables
upstash_url = os.getenv("UPSTASH_REDIS_REST_URL")
upstash_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if not upstash_url:
    print("[ERROR] UPSTASH_REDIS_REST_URL not found in .env")
    sys.exit(1)

if not upstash_token:
    print("[ERROR] UPSTASH_REDIS_REST_TOKEN not found in .env")
    sys.exit(1)

# Remove quotes if present
upstash_url = upstash_url.strip('"\'')
upstash_token = upstash_token.strip('"\'')

print(f"[INFO] URL: {upstash_url[:30]}...")
print(f"[INFO] Token: {upstash_token[:20]}...")

try:
    from upstash_redis import Redis
    print("[OK] upstash_redis package is installed")
except ImportError:
    print("[ERROR] upstash_redis package not installed")
    print("Install with: pip install upstash-redis")
    sys.exit(1)

try:
    print("\n[INFO] Creating Upstash Redis client...")
    redis = Redis(url=upstash_url, token=upstash_token)
    print("[OK] Client created successfully")
    
    print("\n[INFO] Testing set operation...")
    redis.set("test_key", "test_value", ex=10)
    print("[OK] Set operation successful")
    
    print("\n[INFO] Testing get operation...")
    value = redis.get("test_key")
    if value == "test_value":
        print("[OK] Get operation successful")
        print(f"[OK] Retrieved value: {value}")
    else:
        print(f"[ERROR] Expected 'test_value', got '{value}'")
        sys.exit(1)
    
    print("\n[INFO] Cleaning up...")
    redis.delete("test_key")
    print("[OK] Cleanup complete")
    
    print("\n[SUCCESS] Upstash Redis connection test passed!")
    print("Your Redis cache should work now. Restart your FastAPI server.")
    
except Exception as e:
    print(f"\n[ERROR] Connection test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

