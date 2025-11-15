#!/usr/bin/env python3
"""
Quick test to check Redis connection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
api_dir = Path(__file__).parent
env_path = api_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)

redis_uri = os.getenv("REDIS_URI")
if not redis_uri:
    print("[ERROR] REDIS_URI not found in .env")
    sys.exit(1)

print(f"[INFO] Testing Redis connection...")
print(f"  REDIS_URI: {redis_uri[:30]}...")

try:
    import redis
    print("  [OK] redis package is installed")
except ImportError:
    print("  [ERROR] redis package not installed")
    print("  Install with: pip install redis hiredis")
    sys.exit(1)

try:
    # Parse URI
    if redis_uri.startswith("rediss://"):
        client = redis.from_url(
            redis_uri,
            decode_responses=True,
            ssl_cert_reqs=None,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        print("  [OK] Created Redis client (SSL)")
    else:
        client = redis.from_url(
            redis_uri,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        print("  [OK] Created Redis client (non-SSL)")
    
    # Test connection
    print("  Testing connection...")
    result = client.ping()
    if result:
        print("  [OK] Connection successful! Redis is working.")
        
        # Test set/get
        print("  Testing set/get operations...")
        client.set("test:key", "test:value", ex=10)
        value = client.get("test:key")
        if value == "test:value":
            print("  [OK] Set/Get operations working!")
        else:
            print(f"  [ERROR] Set/Get failed: expected 'test:value', got '{value}'")
        
        # Cleanup
        client.delete("test:key")
        print("  [OK] Cleanup complete")
        
except redis.ConnectionError as e:
    print(f"  [ERROR] Connection failed: {e}")
    print("  Check your REDIS_URI and network connection")
    sys.exit(1)
except redis.AuthenticationError as e:
    print(f"  [ERROR] Authentication failed: {e}")
    print("  Check your REDIS_URI token/password")
    sys.exit(1)
except Exception as e:
    print(f"  [ERROR] Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SUCCESS] Redis connection test passed!")

