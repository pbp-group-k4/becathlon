#!/usr/bin/env python
"""
Collect static files for deployment.
This should be run after every deployment to ensure all CSS/JS files are available.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becathlon.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

print("=" * 60)
print("COLLECTING STATIC FILES FOR PRODUCTION")
print("=" * 60)

print(f"\nSTATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")

print("\nCollecting static files...")
try:
    call_command('collectstatic', '--noinput', '--clear', verbosity=2)
    print("\n✓ Static files collected successfully")
    
    # Verify files were collected
    import os
    static_root = settings.STATIC_ROOT
    if os.path.exists(static_root):
        file_count = sum([len(files) for r, d, files in os.walk(static_root)])
        print(f"✓ {file_count} files in {static_root}")
    else:
        print(f"✗ Warning: {static_root} does not exist")
        
except Exception as e:
    print(f"✗ Error collecting static files: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("STATIC FILES READY FOR PRODUCTION")
print("=" * 60)
