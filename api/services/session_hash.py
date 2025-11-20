"""
Session ID hashing service for URL-safe session identifiers
Maps hashed session IDs to real session IDs for security
"""
import hashlib
import base64
import os
import logging
from typing import Optional

logger = logging.getLogger("health_assistant")

# Secret key for hashing (should be in environment variable)
SESSION_HASH_SECRET = os.getenv("SESSION_HASH_SECRET", "healthcare-chatbot-session-hash-v1")


def hash_session_id(session_id: str) -> str:
    """
    Hash a session ID to create a URL-safe identifier
    
    Args:
        session_id: The original session ID (UUID)
    
    Returns:
        A hashed, URL-safe identifier (16 characters)
    """
    try:
        # Combine session ID with secret
        data = (session_id + SESSION_HASH_SECRET).encode('utf-8')
        
        # Hash using SHA-256
        hash_digest = hashlib.sha256(data).digest()
        
        # Use first 12 bytes and encode as base64 URL-safe
        base64_hash = base64.urlsafe_b64encode(hash_digest[:12]).decode('utf-8')
        
        # Remove padding and take first 16 characters
        base64_hash = base64_hash.rstrip('=')
        return base64_hash[:16]
    except Exception as e:
        logger.error(f"Error hashing session ID: {e}")
        # Fallback: use a simple hash
        return hashlib.md5((session_id + SESSION_HASH_SECRET).encode()).hexdigest()[:16]


def is_hashed_session_id(session_id: str) -> bool:
    """
    Check if a string looks like a hashed session ID (not a UUID)
    UUIDs have format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    """
    return not session_id.count('-') == 4 and len(session_id) <= 16


async def resolve_session_id(hashed_id: str, db_service, customer_id: Optional[str] = None) -> Optional[str]:
    """
    Resolve a hashed session ID to the real session ID
    Uses cache first, then database lookup if needed (for old sessions)
    
    Args:
        hashed_id: The hashed session ID from URL
        db_service: Database service instance
        customer_id: Optional customer ID for fallback lookup (for old sessions)
    
    Returns:
        Real session ID or None if not found
    """
    from .cache import cache_service
    
    # Try cache first
    if cache_service.is_available():
        try:
            cache_key = f"session_hash:{hashed_id}"
            real_session_id = await cache_service.get(cache_key)
            if real_session_id:
                return real_session_id
        except Exception as e:
            logger.warning(f"Error getting session hash from cache: {e}")
    
    # If it's not a hashed ID (looks like UUID), return as-is
    if not is_hashed_session_id(hashed_id):
        return hashed_id
    
    # Fallback: For old sessions that weren't hashed, search through customer's sessions
    if customer_id and db_service:
        try:
            logger.info(f"Hash mapping not in cache for {hashed_id}, searching customer sessions...")
            # Get all sessions for the customer
            sessions = await db_service.get_customer_sessions(customer_id, limit=1000)
            
            # Hash each session ID and compare
            for session in sessions:
                real_session_id = session.get("id")
                if real_session_id:
                    computed_hash = hash_session_id(real_session_id)
                    if computed_hash == hashed_id:
                        # Found it! Store in cache for future use
                        logger.info(f"Found matching session for hash {hashed_id}: {real_session_id}")
                        await store_session_hash_mapping(real_session_id, hashed_id)
                        return real_session_id
            
            logger.warning(f"No matching session found for hash: {hashed_id}")
        except Exception as e:
            logger.error(f"Error during fallback session lookup: {e}", exc_info=True)
    
    # If not in cache and fallback didn't work, return None
    logger.warning(f"Session hash mapping not found in cache: {hashed_id}")
    return None


async def store_session_hash_mapping(session_id: str, hashed_id: Optional[str] = None) -> str:
    """
    Store mapping between hashed ID and real session ID in cache
    
    Args:
        session_id: The real session ID
        hashed_id: Optional pre-computed hash (will compute if not provided)
    
    Returns:
        The hashed session ID
    """
    from .cache import cache_service
    
    if not hashed_id:
        hashed_id = hash_session_id(session_id)
    
    # Store in cache with long TTL (30 days)
    if cache_service.is_available():
        try:
            cache_key = f"session_hash:{hashed_id}"
            await cache_service.set(cache_key, session_id, ttl=30 * 24 * 60 * 60)  # 30 days
            logger.debug(f"Stored session hash mapping: {hashed_id} -> {session_id}")
        except Exception as e:
            logger.warning(f"Error storing session hash mapping: {e}")
    
    return hashed_id

