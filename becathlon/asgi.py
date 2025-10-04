"""
ASGI config for becathlon project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

project_root = Path(__file__).resolve().parent
parent_dir = project_root.parent
parent_str = str(parent_dir)
if parent_str not in sys.path:
	sys.path.insert(0, parent_str)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_asgi_application()
