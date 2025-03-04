#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description=None):
    print(f"----- {description} -----" if description else "")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode == 0:
        print(f"SUCCESS: Command completed with code {result.returncode}")
    else:
        print(f"WARNING: Command exited with code {result.returncode}")
    
    return result.returncode == 0

def main():
    print("===== Initializing Prisma for Contact Updater =====")
    
    # Get working directory
    work_dir = os.getcwd()
    print(f"Working directory: {work_dir}")
    
    # Check for .env file
    env_file = Path(work_dir) / ".env"
    if env_file.exists():
        print("Found existing .env file")
    else:
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write('DATABASE_URL="file:./sqlite3.db"\n')
        print("Created .env file")
    
    # Check for schema file
    schema_file = Path(work_dir) / "prisma" / "schema.prisma"
    if schema_file.exists():
        print(f"Found schema file at {schema_file}")
    else:
        print("Error: schema.prisma file not found. Please create it first.")
        sys.exit(1)
    
    # Check for database file
    db_file = Path(work_dir) / "sqlite3.db"
    if db_file.exists():
        print(f"Found database file at {db_file}")
    else:
        print("Database file will be created during migration")
    
    # Run prisma db push (more reliable than migrate for SQLite)
    success = run_command(
        f"{sys.executable} -m prisma db push", 
        "Pushing schema to database"
    )
    if not success:
        print("❌ Failed to push schema to database. Trying alternative method...")
        
        # Try alternative method
        success = run_command(
            f"{sys.executable} -m prisma generate", 
            "Generating Prisma client"
        )
        if not success:
            print("❌ Failed to generate Prisma client. Aborting.")
            sys.exit(1)
    
    # Create test script
    test_script = Path(work_dir) / "test_prisma.py"
    if not test_script.exists():
        print("Creating test script...")
        with open(test_script, "w") as f:
            f.write("""#!/usr/bin/env python3
from prisma import Prisma

print("Initializing Prisma client...")
prisma = Prisma()

print("Connecting to database...")
prisma.connect()

try:
    # Try a simple query
    print("Testing a query...")
    count = prisma.contact.count()
    print(f"Contact count: {count}")
    
    print("✅ Successfully connected to the database!")
finally:
    prisma.disconnect()
""")
        print(f"Created test script at {test_script}")
    
    # Test connection
    success = run_command(
        f"{sys.executable} {test_script}", 
        "Testing Prisma connection"
    )
    if not success:
        print("❌ Prisma connection test FAILED. See above for details.")
    else:
        print("✅ Prisma connection test PASSED.")
    
    print("You can now run the application with:")
    print("  python app.py")

if __name__ == "__main__":
    main() 