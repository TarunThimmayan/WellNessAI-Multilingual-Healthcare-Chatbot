#!/usr/bin/env python3
"""
Test Redis initialization to diagnose connection issues
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("test_redis")

# Load .env
api_dir = Path(__file__).parent
env_path = api_dir / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    logger.info(f"Loaded .env from {env_path}")
else:
    load_dotenv()
    logger.info("Loaded .env from default location")

# Check REDIS_URI
redis_uri = os.getenv("REDIS_URI")
if not redis_uri:
    logger.error("REDIS_URI not found in environment")
    sys.exit(1)

logger.info(f"REDIS_URI found: {redis_uri[:30]}...")

# Try to import and initialize cache service
try:
    from services.cache import cache_service
    logger.info("Cache service imported successfully")
    
    # Check if Redis is available
    logger.info("Checking Redis availability...")
    is_available = cache_service.is_available()
    logger.info(f"Redis available: {is_available}")
    
    if not is_available:
        logger.warning("Redis is not available. Checking why...")
        logger.info(f"redis_client is None: {cache_service.redis_client is None}")
        logger.info(f"REDIS_AVAILABLE: {cache_service.cache_enabled}")
        
        # Try to force reconnection
        logger.info("Attempting to force reconnection...")
        cache_service.ensure_redis_connection()
        is_available = cache_service.is_available()
        logger.info(f"Redis available after reconnection: {is_available}")
    
    if is_available:
        logger.info("SUCCESS: Redis is working!")
        # Test a simple operation
        try:
            import redis
            test_key = "test:init"
            cache_service.redis_client.set(test_key, "test_value", ex=10)
            value = cache_service.redis_client.get(test_key)
            if value == "test_value":
                logger.info("SUCCESS: Redis set/get operation works!")
            else:
                logger.error(f"FAILED: Expected 'test_value', got '{value}'")
            cache_service.redis_client.delete(test_key)
        except Exception as e:
            logger.error(f"FAILED: Redis operation error: {e}")
    else:
        logger.error("FAILED: Redis is still not available")
        sys.exit(1)
        
except Exception as e:
    logger.error(f"Error importing or testing cache service: {e}", exc_info=True)
    sys.exit(1)

print("\n[SUCCESS] Redis initialization test passed!")

