#!/usr/bin/env python
"""
Script to reset Django migrations in the database.
Use this ONLY if migrations are stuck in a failed state.

Usage:
    python reset_migrations.py --app main
    python reset_migrations.py --all
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becathlon.settings')
django.setup()

from django.db import connection
from django.core.management import call_command


def reset_migrations(app_label=None):
    """Reset migrations for a specific app or all apps"""
    
    with connection.cursor() as cursor:
        if app_label:
            print(f"Resetting migrations for app: {app_label}")
            cursor.execute(
                "DELETE FROM django_migrations WHERE app = %s",
                [app_label]
            )
            print(f"Deleted {cursor.rowcount} migration records for {app_label}")
        else:
            print("Resetting ALL migrations")
            cursor.execute("SELECT app, COUNT(*) FROM django_migrations GROUP BY app")
            apps = cursor.fetchall()
            print("Current migration counts:")
            for app, count in apps:
                print(f"  {app}: {count} migrations")
            
            response = input("\nAre you sure you want to delete ALL migrations? (yes/no): ")
            if response.lower() == 'yes':
                cursor.execute("DELETE FROM django_migrations")
                print(f"Deleted {cursor.rowcount} migration records")
            else:
                print("Aborted")
                return
    
    print("\nNow run: python manage.py migrate --fake-initial")
    print("This will mark all migrations as applied without running them.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Reset Django migrations')
    parser.add_argument('--app', help='App label to reset (e.g., main, cart)')
    parser.add_argument('--all', action='store_true', help='Reset all migrations')
    
    args = parser.parse_args()
    
    if args.all:
        reset_migrations(None)
    elif args.app:
        reset_migrations(args.app)
    else:
        print("Please specify --app APP_NAME or --all")
        sys.exit(1)
