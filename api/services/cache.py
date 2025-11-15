"""
3-Level Caching Service (Improved)
L1: Browser Storage (HTTP Cache Headers)
L2: Redis Cache (Server-side with connection pooling)
L3: Database (PostgreSQL)
"""

import hashlib
import json
import logging
import os
import gzip
import base64
import asyncio
from typing import Any, Dict, Optional, Tuple
from datetime import timedelta
from collections import defaultdict
from threading import Lock
import time

try:
    import redis
    from redis import Redis
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None
    ConnectionPool = None

logger = logging.getLogger("health_assistant")


class CacheService:
    """3-level caching service for chat responses (Improved)"""
    
    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.connection_pool: Optional[ConnectionPool] = None
        self.cache_enabled = os.getenv("ENABLE_CACHE", "1").lower() == "1"
        self.cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # Default 1 hour
        self.cache_version = os.getenv("CACHE_VERSION", "1")  # For cache invalidation on schema changes
        self.compress_threshold = int(os.getenv("CACHE_COMPRESS_THRESHOLD", "1024"))  # Compress if > 1KB
        
        # Cache statistics
        self.stats = {
            "hits": defaultdict(int),
            "misses": defaultdict(int),
            "errors": defaultdict(int),
            "total_requests": 0,
            "total_hits": 0,
            "total_misses": 0,
        }
        self.stats_lock = Lock()
        
        # Initialize Redis connection
        if REDIS_AVAILABLE and self.cache_enabled:
            self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis client with connection pooling (Upstash Redis compatible)"""
        try:
            redis_uri = os.getenv("REDIS_URI")
            if not redis_uri:
                logger.warning("REDIS_URI not found in environment, Redis caching disabled")
                return
            
            # Upstash Redis supports both redis:// and rediss:// (SSL)
            # Configure connection pool for better performance
            connection_kwargs = {
                "decode_responses": True,
                "socket_connect_timeout": 10,  # Increased timeout
                "socket_timeout": 10,  # Increased timeout
                "retry_on_timeout": True,
                "health_check_interval": 30,
                "max_connections": 50,  # Connection pool size
            }
            
            if redis_uri.startswith("rediss://"):
                # SSL/TLS connection (Upstash uses SSL by default)
                connection_kwargs["ssl_cert_reqs"] = None
                connection_kwargs["ssl_check_hostname"] = False  # Upstash compatibility
                try:
                    self.connection_pool = ConnectionPool.from_url(redis_uri, **connection_kwargs)
                except Exception as pool_error:
                    # Fallback: try without connection pool
                    logger.debug(f"Connection pool failed, trying direct connection: {pool_error}")
                    self.redis_client = redis.from_url(redis_uri, **connection_kwargs)
                    # Test connection
                    self._test_connection_with_retry()
                    logger.info("Upstash Redis cache (L2) initialized successfully (direct connection)")
                    return
            else:
                # Regular connection
                try:
                    self.connection_pool = ConnectionPool.from_url(redis_uri, **connection_kwargs)
                except Exception as pool_error:
                    # Fallback: try without connection pool
                    logger.debug(f"Connection pool failed, trying direct connection: {pool_error}")
                    self.redis_client = redis.from_url(redis_uri, **connection_kwargs)
                    # Test connection
                    self._test_connection_with_retry()
                    logger.info("Upstash Redis cache (L2) initialized successfully (direct connection)")
                    return
            
            # Create Redis client from connection pool
            self.redis_client = Redis(connection_pool=self.connection_pool)
            
            # Test connection with retry
            self._test_connection_with_retry()
            logger.info("Upstash Redis cache (L2) initialized successfully with connection pooling")
            
        except redis.ConnectionError as e:
            logger.warning(f"Failed to connect to Upstash Redis: {e}. Caching will use L1 and L3 only.")
            self.redis_client = None
            self.connection_pool = None
        except redis.AuthenticationError as e:
            logger.warning(f"Upstash Redis authentication failed: {e}. Check your REDIS_URI token.")
            self.redis_client = None
            self.connection_pool = None
        except Exception as e:
            logger.warning(f"Failed to initialize Upstash Redis cache: {type(e).__name__}: {e}. Caching will use L1 and L3 only.")
            logger.debug(f"Redis initialization error details: {e}", exc_info=True)
            self.redis_client = None
            self.connection_pool = None
    
    def _test_connection_with_retry(self, max_retries: int = 3):
        """Test Redis connection with retry logic"""
        for attempt in range(max_retries):
            try:
                self.redis_client.ping()
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 0.5
                    time.sleep(wait_time)
                    logger.debug(f"Redis connection test retry {attempt + 1}/{max_retries}")
                else:
                    raise e
        return False
    
    def generate_cache_key(
        self,
        text: str,
        lang: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a cache key from query text, language, and profile
        
        Args:
            text: User's query text
            lang: Language code
            profile: User profile dict
            
        Returns:
            Cache key string
        """
        # Normalize text (lowercase, strip whitespace)
        normalized_text = text.lower().strip()
        
        # Create key components
        key_parts = {
            "text": normalized_text,
            "lang": lang or "en",
        }
        
        # Add profile components if provided (only relevant fields)
        if profile:
            profile_key = {
                "age": profile.get("age"),
                "sex": profile.get("sex"),
                "diabetes": profile.get("diabetes", False),
                "hypertension": profile.get("hypertension", False),
                "pregnancy": profile.get("pregnancy", False),
            }
            key_parts["profile"] = profile_key
        
        # Create JSON string and hash it
        key_string = json.dumps(key_parts, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        # Include cache version for schema changes
        return f"chat:response:v{self.cache_version}:{key_hash}"
    
    def _decompress_data(self, data: str) -> str:
        """Decompress gzipped data"""
        try:
            compressed_bytes = base64.b64decode(data.encode())
            decompressed = gzip.decompress(compressed_bytes)
            return decompressed.decode('utf-8')
        except Exception:
            # If decompression fails, assume it's not compressed
            return data
    
    def _compress_data(self, data: str) -> Tuple[str, bool]:
        """Compress data if it exceeds threshold"""
        data_bytes = data.encode('utf-8')
        if len(data_bytes) > self.compress_threshold:
            compressed = gzip.compress(data_bytes, compresslevel=6)
            compressed_b64 = base64.b64encode(compressed).decode('utf-8')
            return compressed_b64, True
        return data, False
    
    async def get_from_cache(
        self,
        cache_key: str,
        retry_count: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response from L2 (Upstash Redis) with retry logic
        L1 (browser) is handled by HTTP headers
        L3 (Database) is handled separately in main.py
        
        Args:
            cache_key: Cache key string
            retry_count: Number of retries on failure
            
        Returns:
            Cached response dict or None
        """
        # Ensure Redis connection is active
        self.ensure_redis_connection()
        
        # Try L2: Upstash Redis
        if self.redis_client:
            for attempt in range(retry_count):
                try:
                    cached_data = self.redis_client.get(cache_key)
                    if cached_data:
                        # Check if data is compressed (starts with base64 gzip header)
                        if cached_data.startswith('H4sI'):  # gzip magic bytes in base64
                            cached_data = self._decompress_data(cached_data)
                        
                        response_data = json.loads(cached_data)
                        self._record_stat("hits", "L2")
                        logger.debug(f"Cache HIT (L2 Upstash Redis): {cache_key[:20]}...")
                        return response_data
                    else:
                        self._record_stat("misses", "L2")
                        return None
                        
                except redis.ConnectionError as e:
                    self._record_stat("errors", "L2-Connection")
                    if attempt < retry_count - 1:
                        # Try to reconnect
                        try:
                            self._test_connection_with_retry()
                        except:
                            pass
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
                    logger.warning(f"Upstash Redis connection error: {e}")
                except redis.TimeoutError as e:
                    self._record_stat("errors", "L2-Timeout")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
                    logger.warning(f"Upstash Redis timeout error: {e}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to decode cached data: {e}")
                    # Invalid cache entry, delete it
                    try:
                        self.redis_client.delete(cache_key)
                    except:
                        pass
                    return None
                except Exception as e:
                    self._record_stat("errors", "L2-Other")
                    logger.warning(f"Upstash Redis get error: {e}")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
        
        # L3: Database (handled separately in main.py)
        # This function only handles L2
        return None
    
    async def set_to_cache(
        self,
        cache_key: str,
        response_data: Dict[str, Any],
        ttl: Optional[int] = None,
        retry_count: int = 2
    ) -> bool:
        """
        Store response in L2 (Upstash Redis) cache with compression
        L1 (browser) is handled by HTTP headers
        L3 (database) is handled separately in main.py
        
        Args:
            cache_key: Cache key string
            response_data: Response data to cache
            ttl: Time to live in seconds (defaults to self.cache_ttl)
            retry_count: Number of retries on failure
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure Redis connection is active
        self.ensure_redis_connection()
        
        if not self.redis_client:
            return False
        
        ttl = ttl or self.cache_ttl
        
        for attempt in range(retry_count):
            try:
                serialized = json.dumps(response_data)
                
                # Compress if data is large
                compressed_data, is_compressed = self._compress_data(serialized)
                
                # Store with compression flag in metadata (optional)
                self.redis_client.setex(cache_key, ttl, compressed_data)
                
                compression_info = f" (compressed)" if is_compressed else ""
                logger.debug(f"Cache SET (L2 Upstash Redis): {cache_key[:20]}... (TTL: {ttl}s{compression_info})")
                return True
                
            except redis.ConnectionError as e:
                self._record_stat("errors", "L2-Connection")
                if attempt < retry_count - 1:
                    try:
                        self._test_connection_with_retry()
                    except:
                        pass
                    await asyncio.sleep(0.1 * (attempt + 1))
                    continue
                logger.warning(f"Upstash Redis connection error: {e}")
                return False
            except redis.TimeoutError as e:
                self._record_stat("errors", "L2-Timeout")
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))
                    continue
                logger.warning(f"Upstash Redis timeout error: {e}")
                return False
            except Exception as e:
                self._record_stat("errors", "L2-Other")
                logger.warning(f"Upstash Redis set error: {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))
                    continue
                return False
        
        return False
    
    def get_cache_headers(
        self,
        cache_hit: bool = False,
        max_age: Optional[int] = None,
        content_hash: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate HTTP cache headers for L1 (Browser Storage)
        Uses content hash for proper ETag generation
        
        Args:
            cache_hit: Whether this is a cache hit
            max_age: Max age in seconds (defaults to self.cache_ttl)
            content_hash: Optional content hash for ETag (generated if not provided)
            
        Returns:
            Dictionary of HTTP headers
        """
        max_age = max_age or self.cache_ttl
        
        # Generate ETag from content hash if provided, otherwise use cache status
        if content_hash:
            etag = f'"{content_hash[:16]}"'  # Use first 16 chars of hash
        else:
            etag = f'"{hashlib.md5(str(cache_hit).encode()).hexdigest()}"'
        
        headers = {
            "Cache-Control": f"public, max-age={max_age}, stale-while-revalidate=300",
            "ETag": etag,
            "Vary": "Accept-Encoding",  # Important for compression
        }
        
        if cache_hit:
            headers["X-Cache"] = "HIT"
        else:
            headers["X-Cache"] = "MISS"
        
        return headers
    
    def _generate_content_hash(self, content: Any) -> str:
        """Generate hash from response content for ETag"""
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _record_stat(self, stat_type: str, level: str):
        """Record cache statistics"""
        with self.stats_lock:
            self.stats[stat_type][level] += 1
            if stat_type == "hits":
                self.stats["total_hits"] += 1
            elif stat_type == "misses":
                self.stats["total_misses"] += 1
            self.stats["total_requests"] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.stats_lock:
            total = self.stats["total_requests"]
            hit_rate = (self.stats["total_hits"] / total * 100) if total > 0 else 0
            return {
                **self.stats,
                "hit_rate_percent": round(hit_rate, 2),
                "cache_enabled": self.cache_enabled,
                "redis_available": self.is_available(),
            }
    
    def reset_statistics(self):
        """Reset cache statistics"""
        with self.stats_lock:
            self.stats = {
                "hits": defaultdict(int),
                "misses": defaultdict(int),
                "errors": defaultdict(int),
                "total_requests": 0,
                "total_hits": 0,
                "total_misses": 0,
            }
    
    async def invalidate_cache(
        self,
        pattern: Optional[str] = None,
        cache_key: Optional[str] = None
    ) -> int:
        """
        Invalidate cache entries matching a pattern or specific key
        
        Args:
            pattern: Redis key pattern (e.g., "chat:response:*")
            cache_key: Specific cache key to invalidate
            
        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0
        
        try:
            if cache_key:
                # Delete specific key
                deleted = self.redis_client.delete(cache_key)
                return deleted if deleted else 0
            elif pattern:
                # Delete keys matching pattern (use SCAN for large datasets)
                deleted_count = 0
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(cursor, match=pattern, count=100)
                    if keys:
                        deleted_count += self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
                return deleted_count
            return 0
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
            return 0
    
    async def invalidate_all_cache(self) -> int:
        """Invalidate all chat response cache entries"""
        return await self.invalidate_cache("chat:response:*")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache system information"""
        info = {
            "enabled": self.cache_enabled,
            "ttl_seconds": self.cache_ttl,
            "version": self.cache_version,
            "redis_available": self.is_available(),
            "compress_threshold": self.compress_threshold,
        }
        
        if self.redis_client and self.connection_pool:
            try:
                pool_info = self.connection_pool.connection_kwargs
                info["redis_pool"] = {
                    "max_connections": pool_info.get("max_connections", "unknown"),
                    "connected": self.redis_client.ping() if self.redis_client else False,
                }
            except:
                pass
        
        return info
    
    def is_available(self) -> bool:
        """Check if Redis cache is available"""
        if self.redis_client is None:
            return False
        # Test connection if available
        try:
            self.redis_client.ping()
            return True
        except:
            # Connection lost, try to reconnect
            try:
                self._init_redis()
                return self.redis_client is not None
            except:
                return False
    
    def ensure_redis_connection(self):
        """Ensure Redis connection is active, reconnect if needed"""
        if not self.redis_client:
            if REDIS_AVAILABLE and self.cache_enabled:
                try:
                    self._init_redis()
                except Exception as e:
                    logger.debug(f"Redis reconnection attempt failed: {e}")
        else:
            # Test if connection is still alive
            try:
                self.redis_client.ping()
            except:
                # Connection lost, try to reconnect
                logger.debug("Redis connection lost, attempting reconnection...")
                self.redis_client = None
                self.connection_pool = None
                if REDIS_AVAILABLE and self.cache_enabled:
                    try:
                        self._init_redis()
                    except Exception as e:
                        logger.debug(f"Redis reconnection failed: {e}")


# Global cache service instance
cache_service = CacheService()

