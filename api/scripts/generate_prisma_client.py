#!/usr/bin/env python3
"""
Generate Prisma client manually to work around ENOENT error
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Generate Prisma client"""
    api_dir = Path(__file__).parent.parent
    schema_path = api_dir / "prisma" / "schema.prisma"
    
    print("Generating Prisma client...")
    print(f"Schema: {schema_path}")
    
    # Try using the Prisma Python package's generation
    try:
        # Import prisma and try to generate
        sys.path.insert(0, str(api_dir))
        
        # Method 1: Try using prisma generate command via subprocess with full path
        python_exe = sys.executable
        result = subprocess.run(
            [python_exe, "-m", "prisma", "generate", "--schema", str(schema_path)],
            cwd=str(api_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Prisma client generated successfully!")
            print(result.stdout)
            return True
        else:
            print("Method 1 failed, trying alternative...")
            print(result.stderr)
    except Exception as e:
        print(f"Method 1 error: {e}")
    
    # Method 2: Try using npx with skip-generate workaround
    print("\nTrying alternative method...")
    try:
        # The issue is that prisma-client-python binary is missing
        # Let's try to manually create the client directory structure
        output_dir = api_dir / "prisma_client"
        output_dir.mkdir(exist_ok=True)
        
        print(f"Creating client directory: {output_dir}")
        print("\n⚠ Note: The Prisma client generation requires the prisma-client-python binary.")
        print("This binary should be installed with the prisma package but is missing.")
        print("\nWorkaround options:")
        print("1. The database is already synced (tables created)")
        print("2. You can use Prisma Client at runtime - it will generate on first use")
        print("3. Or install Prisma CLI globally: npm install -g prisma")
        print("   Then run: npx prisma generate --schema prisma/schema.prisma")
        
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



