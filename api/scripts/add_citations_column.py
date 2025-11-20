"""
Migration script to add citations column to chat_messages table if it doesn't exist
This ensures the column exists in existing databases
"""
import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from database.db_client import db_client

# SQL to add citations column if it doesn't exist
ADD_CITATIONS_COLUMN_SQL = """
-- Add citations column to chat_messages if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'chat_messages' 
        AND column_name = 'citations'
    ) THEN
        ALTER TABLE chat_messages 
        ADD COLUMN citations JSONB;
        
        RAISE NOTICE 'Added citations column to chat_messages table';
    ELSE
        RAISE NOTICE 'citations column already exists in chat_messages table';
    END IF;
END $$;
"""

async def add_citations_column():
    """Add citations column to chat_messages table if it doesn't exist"""
    # Load environment
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
    else:
        # Try loading from current directory
        load_dotenv(override=True)
    
    print("=" * 60)
    print("Adding citations column to chat_messages table")
    print("=" * 60)
    print()
    
    # Connect to database
    print("Connecting to database...")
    if not await db_client.connect():
        print("[ERROR] Failed to connect to database")
        print("Please check your NEON_DB_URL in .env file")
        return False
    
    print("[OK] Successfully connected to PostgreSQL database")
    print()
    
    # Add column
    print("Checking if citations column exists...")
    try:
        # Check if column exists
        check_query = """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'chat_messages' 
                AND column_name = 'citations'
            );
        """
        exists = await db_client.fetchval(check_query)
        
        if exists:
            print("[OK] citations column already exists in chat_messages table")
        else:
            print("[INFO] citations column does not exist, adding it...")
            # Execute the SQL to add the column
            await db_client.execute(ADD_CITATIONS_COLUMN_SQL)
            print("[OK] citations column added successfully!")
        
        print()
        print("=" * 60)
        print("[OK] Migration complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] Failed to add citations column: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False
    
    await db_client.disconnect()
    return True

if __name__ == "__main__":
    success = asyncio.run(add_citations_column())
    sys.exit(0 if success else 1)

