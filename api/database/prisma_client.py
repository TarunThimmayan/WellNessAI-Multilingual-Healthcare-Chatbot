import os
import logging
from typing import Optional, Any
from pathlib import Path

logger = logging.getLogger("health_assistant")

# Lazy import Prisma to avoid errors at module level
# Prisma will be imported when needed
PRISMA_AVAILABLE = None  # Will be set dynamically
Prisma = None
Customer = None
ChatSession = None
ChatMessage = None

def _try_import_prisma():
    """Try to import Prisma, set global variables"""
    global PRISMA_AVAILABLE, Prisma, Customer, ChatSession, ChatMessage
    
    if PRISMA_AVAILABLE is not None:
        return PRISMA_AVAILABLE
    
    try:
        from prisma import Prisma
        from prisma.models import Customer, ChatSession, ChatMessage
        PRISMA_AVAILABLE = True
        return True
    except (ImportError, RuntimeError) as e:
        # RuntimeError can occur if client hasn't been generated yet
        if "hasn't been generated" in str(e):
            logger.warning("Prisma client not generated yet. It will be generated on first use.")
        else:
            logger.warning(f"Prisma not available: {e}")
        PRISMA_AVAILABLE = False
        Prisma = None
        Customer = None
        ChatSession = None
        ChatMessage = None
        return False


class PrismaClient:
    """Prisma client wrapper for database operations"""
    
    def __init__(self):
        self.client: Optional[Any] = None  # Prisma type will be set after import
        self._is_connected = False
    
    async def connect(self) -> bool:
        """Connect to the database"""
        # Try to import Prisma if not already available
        if not _try_import_prisma():
            logger.error("Prisma is not available. The client may need to be generated.")
            logger.error("Please run: npx prisma generate --schema prisma/schema.prisma")
            return False
        
        if self._is_connected and self.client:
            return True
        
        try:
            self.client = Prisma()
            await self.client.connect()
            self._is_connected = True
            logger.info("Successfully connected to database using Prisma")
            return True
        except RuntimeError as e:
            if "hasn't been generated" in str(e):
                logger.error("Prisma client not generated. Please run: npx prisma generate --schema prisma/schema.prisma")
            else:
                logger.error(f"Failed to connect to database: {e}")
            self._is_connected = False
            return False
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        if self.client:
            try:
                await self.client.disconnect()
                self._is_connected = False
                logger.info("Disconnected from database")
            except Exception as e:
                logger.error(f"Error disconnecting from database: {e}")
        self.client = None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._is_connected and self.client is not None
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        if not self.is_connected():
            return False
        
        try:
            # Try a simple query
            await self.client.customer.find_first(take=1)
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    async def ensure_connected(self) -> bool:
        """Ensure database is connected, connect if not"""
        if not self.is_connected():
            return await self.connect()
        return True


# Global Prisma client instance
prisma_client = PrismaClient()


async def get_prisma_client() -> Any:
    """Get Prisma client instance"""
    await prisma_client.ensure_connected()
    if not prisma_client.client:
        raise Exception("Prisma client not initialized")
    return prisma_client.client

