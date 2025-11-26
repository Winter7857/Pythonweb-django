import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mywebsite.settings")

# Vercel looks for a top-level WSGI callable named "app"
app = get_wsgi_application()
