#!/usr/bin/env python
"""
Quick migration script - generates and applies initial migration.
Run this after configuring your DATABASE_URL in .env
"""

import subprocess
import sys


def run_cmd(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    
    print(result.stdout)
    print(f"✅ {description} - Done!")
    return True


def main():
    print("="*70)
    print("🗄️  ApplyFlow Database Migration Generator")
    print("="*70)
    
    print("\n📋 This script will:")
    print("   1. Generate an initial Alembic migration")
    print("   2. Apply the migration to create all tables")
    print("\n⚠️  Prerequisites:")
    print("   - PostgreSQL must be running")
    print("   - DATABASE_URL must be configured in .env")
    print("   - Database must exist (e.g., applyflow_db)")
    
    response = input("\n▶️  Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Generate migration
    if not run_cmd(
        'alembic revision --autogenerate -m "Initial migration - create all tables"',
        "Generating initial migration"
    ):
        print("\n❌ Failed to generate migration.")
        print("   Check that:")
        print("   - PostgreSQL is running")
        print("   - DATABASE_URL in .env is correct")
        print("   - Database exists")
        sys.exit(1)
    
    # Apply migration
    print("\n" + "="*70)
    response = input("▶️  Apply migration to database? (y/n): ")
    if response.lower() != 'y':
        print("\n⏸️  Migration generated but not applied.")
        print("   Run manually: alembic upgrade head")
        sys.exit(0)
    
    if not run_cmd("alembic upgrade head", "Applying migration"):
        print("\n❌ Failed to apply migration.")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🎉 Success! Database tables created.")
    print("="*70)
    print("\n📝 Next steps:")
    print("   1. Seed sample data: python seed_data.py")
    print("   2. Start server: uvicorn app.main:app --reload")
    print("   3. Visit docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
