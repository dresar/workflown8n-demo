"""
Passenger WSGI configuration for cPanel deployment.
This file is used by Phusion Passenger (cPanel's Python app server).
"""
import sys
import os
from pathlib import Path

# Get the project directory
INTERP = os.path.join(os.environ['HOME'], 'simpleflow', 'venv', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add your project directory to the sys.path
project_home = str(Path(__file__).resolve().parent)
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpleflow.settings')

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

