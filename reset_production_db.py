#!/usr/bin/env python
"""
Fresh migration setup for production database.
This script helps set up migrations on a fresh production database.

When to use:
- First deployment to production
- After migration conflicts
- When PostgreSQL transactions are stuck

What it does:
1. Drops all tables (if they exist)
2. Runs migrations fresh
3. Creates initial data (ProductTypes)

CAUTION: This will DELETE ALL DATA in the database!
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becathlon.settings')
django.setup()

from django.core.management import call_command
from django.db import connection


def reset_database():
    """Drop all tables and reset migrations"""
    
    print("=" * 60)
    print("PRODUCTION DATABASE RESET SCRIPT")
    print("=" * 60)
    print("\nWARNING: This will DELETE ALL DATA in the database!")
    print(f"Database: {connection.settings_dict['NAME']}")
    print(f"Host: {connection.settings_dict['HOST']}")
    
    response = input("\nType 'YES DELETE EVERYTHING' to continue: ")
    if response != 'YES DELETE EVERYTHING':
        print("Aborted.")
        sys.exit(0)
    
    print("\n1. Dropping all tables...")
    with connection.cursor() as cursor:
        # Get all tables in the current schema
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = current_schema()
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if tables:
            # Drop all tables
            for table in tables:
                print(f"   Dropping table: {table}")
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
            print(f"   Dropped {len(tables)} tables")
        else:
            print("   No tables to drop")
    
    print("\n2. Running migrations...")
    try:
        call_command('migrate', verbosity=2)
        print("   ✓ Migrations completed successfully")
    except Exception as e:
        print(f"   ✗ Migration failed: {e}")
        sys.exit(1)
    
    print("\n3. Creating initial data (ProductTypes)...")
    try:
        # Import and run the seed script
        exec(open('seed_product_types.py').read())
        print("   ✓ ProductTypes created")
    except Exception as e:
        print(f"   ✗ Failed to create ProductTypes: {e}")
    
    print("\n" + "=" * 60)
    print("DATABASE RESET COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Add products through admin: /admin/")
    print("3. Test the application")


if __name__ == '__main__':
    reset_database()
