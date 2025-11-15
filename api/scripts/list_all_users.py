"""
List all users from the Neon database in a tabular format
"""
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from database.db_client import db_client

def format_table(users: List[Dict[str, Any]]) -> None:
    """Format and display users in a table"""
    if not users:
        print("\n[INFO] No users found in the database.")
        return
    
    # Define column widths
    col_widths = {
        'id': 38,
        'email': 30,
        'role': 10,
        'age': 6,
        'sex': 8,
        'diabetes': 10,
        'hypertension': 13,
        'pregnancy': 10,
        'city': 20,
        'is_active': 10,
        'created_at': 20,
        'last_login': 20,
    }
    
    # Print header
    header = (
        f"{'ID':<{col_widths['id']}} "
        f"{'Email':<{col_widths['email']}} "
        f"{'Role':<{col_widths['role']}} "
        f"{'Age':<{col_widths['age']}} "
        f"{'Sex':<{col_widths['sex']}} "
        f"{'Diabetes':<{col_widths['diabetes']}} "
        f"{'Hypertension':<{col_widths['hypertension']}} "
        f"{'Pregnancy':<{col_widths['pregnancy']}} "
        f"{'City':<{col_widths['city']}} "
        f"{'Active':<{col_widths['is_active']}} "
        f"{'Created At':<{col_widths['created_at']}} "
        f"{'Last Login':<{col_widths['last_login']}}"
    )
    
    print("\n" + "=" * len(header))
    print(header)
    print("=" * len(header))
    
    # Print rows
    for user in users:
        user_id = str(user.get('id', 'N/A'))[:36] + '...' if len(str(user.get('id', ''))) > 36 else str(user.get('id', 'N/A'))
        email = str(user.get('email', 'N/A'))[:28] + '..' if len(str(user.get('email', ''))) > 28 else str(user.get('email', 'N/A'))
        role = str(user.get('role', 'N/A'))
        age = str(user.get('age', 'N/A')) if user.get('age') is not None else 'N/A'
        sex = str(user.get('sex', 'N/A')) if user.get('sex') else 'N/A'
        diabetes = 'Yes' if user.get('diabetes') else 'No'
        hypertension = 'Yes' if user.get('hypertension') else 'No'
        pregnancy = 'Yes' if user.get('pregnancy') else 'No'
        city = str(user.get('city', 'N/A'))[:18] + '..' if user.get('city') and len(str(user.get('city'))) > 18 else (str(user.get('city', 'N/A')) if user.get('city') else 'N/A')
        is_active = 'Yes' if user.get('is_active', True) else 'No'
        
        # Format dates
        created_at = user.get('created_at')
        if created_at:
            if isinstance(created_at, datetime):
                created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
            else:
                created_at = str(created_at)[:19]
        else:
            created_at = 'N/A'
        
        last_login = user.get('last_login')
        if last_login:
            if isinstance(last_login, datetime):
                last_login = last_login.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_login = str(last_login)[:19]
        else:
            last_login = 'Never'
        
        row = (
            f"{user_id:<{col_widths['id']}} "
            f"{email:<{col_widths['email']}} "
            f"{role:<{col_widths['role']}} "
            f"{age:<{col_widths['age']}} "
            f"{sex:<{col_widths['sex']}} "
            f"{diabetes:<{col_widths['diabetes']}} "
            f"{hypertension:<{col_widths['hypertension']}} "
            f"{pregnancy:<{col_widths['pregnancy']}} "
            f"{city:<{col_widths['city']}} "
            f"{is_active:<{col_widths['is_active']}} "
            f"{created_at:<{col_widths['created_at']}} "
            f"{last_login:<{col_widths['last_login']}}"
        )
        print(row)
    
    print("=" * len(header))
    print(f"\nTotal users: {len(users)}")

async def list_all_users():
    """List all users from the database"""
    # Load environment
    api_dir = Path(__file__).parent.parent
    env_file = api_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
    
    print("=" * 100)
    print("All Users in Neon Database")
    print("=" * 100)
    
    # Connect to database
    if not await db_client.connect():
        print("\n[ERROR] Failed to connect to database")
        print("Please check your NEON_DB_URL in .env file")
        return
    
    try:
        # Query all users
        print("\n[INFO] Fetching all users from database...")
        users = await db_client.fetch("""
            SELECT 
                id,
                email,
                role,
                age,
                sex,
                diabetes,
                hypertension,
                pregnancy,
                city,
                is_active,
                created_at,
                last_login
            FROM customers
            ORDER BY created_at DESC
        """)
        
        # Convert to list of dicts
        users_list = [dict(user) for user in users]
        
        # Display in table format
        format_table(users_list)
        
    except Exception as e:
        print(f"\n[ERROR] Failed to fetch users: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_client.disconnect()
        print("\n[INFO] Database connection closed.")

if __name__ == "__main__":
    asyncio.run(list_all_users())

