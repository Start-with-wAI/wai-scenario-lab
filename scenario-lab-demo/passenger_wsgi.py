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

# Import the WSGI-adapted FastAPI app as 'application' for Passenger
try:
    from main import wsgi_app as application
except Exception as e:
    # Diagnostic fallback for Passenger log output
    print("Error importing main wsgi_app in passenger_wsgi.py:", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise e
