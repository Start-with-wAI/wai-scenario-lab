#!/usr/bin/env python3
import sys
import os

# Set up paths for DreamHost user-installed packages
dh_site_packages = "/home/dh_webmistress_v/.local/lib/python3.10/site-packages"
if dh_site_packages not in sys.path:
    sys.path.insert(0, dh_site_packages)

# Insert the current directory to import main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from wsgiref.handlers import CGIHandler
    from main import wsgi_app
except Exception as e:
    # Diagnostic fallback output in case imports or main file fail
    print("Content-Type: text/plain")
    print("Status: 500 Internal Server Error\n")
    print("Error initializing CGI WSGI wrapper:")
    import traceback
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)

if __name__ == "__main__":
    CGIHandler().run(wsgi_app)
