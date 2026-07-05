# DreamHost Scenario Lab Demo

This directory contains a minimal smoke test to verify if a FastAPI application can be hosted on a DreamHost shared hosting environment under a subdirectory, using CGI to WSGI translation (`a2wsgi` + `wsgiref.handlers.CGIHandler`). This avoids having to configure Phusion Passenger (which is deprecated on DreamHost shared plans) and allows the application to co-exist with a root WordPress installation.

## File Tree

```text
scenario-lab-demo/
├── .htaccess            # Apache configuration for CGI execution and URL routing
├── index.cgi            # CGI script acting as the entry point for the WSGI adapter
├── passenger_wsgi.py    # Passenger-compatible WSGI wrapper (alternative/fallback)
├── main.py              # FastAPI application wrapped in A2WSGI
└── README_SCENARIO_LAB_DEMO.md # Setup & verification guide (this file)
```

---

## File Contents

### 1. `main.py`
The core FastAPI application. It includes a root endpoint `/`, a `/health` endpoint, and a `/capabilities` endpoint that checks which packages can be imported.
```python
import sys
import os
import platform

# Ensure DreamHost user site-packages are in the path
dh_site_packages = "/home/dh_webmistress_v/.local/lib/python3.10/site-packages"
if dh_site_packages not in sys.path:
    sys.path.insert(0, dh_site_packages)

from fastapi import FastAPI
from a2wsgi import ASGIMiddleware

app = FastAPI(
    title="DreamHost Scenario Lab Demo",
    description="A minimal FastAPI application running via WSGI/CGI on DreamHost",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "FastAPI via A2WSGI is responding",
        "runtime": "dreamhost-wsgi-smoke-test"
    }

@app.get("/health")
def read_health():
    return {
        "status": "healthy",
        "environment": "dreamhost-shared-hosting"
    }

@app.get("/capabilities")
def read_capabilities():
    modules_to_test = [
        "fastapi",
        "pydantic",
        "a2wsgi",
        "uvicorn",
        "mcp",
        "google.adk"
    ]
    
    import_status = {}
    for module in modules_to_test:
        try:
            __import__(module)
            import_status[module] = True
        except ImportError:
            import_status[module] = False
            
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "current_working_directory": os.getcwd(),
        "sys_path": sys.path,
        "imports": import_status
    }

wsgi_app = ASGIMiddleware(app)
```

### 2. `index.cgi`
The CGI script that invokes Python's standard `wsgiref.handlers.CGIHandler` to run our FastAPI application.
```python
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
```

### 3. `passenger_wsgi.py`
A standard wrapper file. If the DreamHost plan supports Phusion Passenger (or you decide to create a separate subdomain where Passenger is enabled), Passenger will load this file directly.
```python
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
    from main import wsgi_app as application
except Exception as e:
    print("Error importing main wsgi_app in passenger_wsgi.py:", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise e
```

### 4. `.htaccess`
Handles URL routing and enables CGI execution for this folder.
```apache
# Enable CGI execution in this directory
Options +ExecCGI
AddHandler cgi-script .cgi

# Serve index.cgi when accessing the root directory
DirectoryIndex index.cgi

# URL Rewriting for Routing requests to the CGI application
RewriteEngine On
RewriteBase /scenario-lab-demo/

# If the request is for an actual file or folder, serve it directly
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d

# Otherwise, rewrite all paths to index.cgi (e.g. /health -> index.cgi/health)
RewriteRule ^(.*)$ index.cgi/$1 [L,QSA]
```

---

## Upload Instructions

Use `scp` or `rsync` from your local machine to upload the entire directory to DreamHost.

### Option A: Using `scp` (Windows PowerShell or Git Bash)
From the root of your local workspace:
```powershell
scp -r scenario-lab-demo dh_webmistress_v@startwithwai.tech:/home/dh_webmistress_v/startwithwai.tech/
```

### Option B: Using `rsync` (WSL, Linux, or Git Bash)
```bash
rsync -avz --exclude="*.git*" scenario-lab-demo/ dh_webmistress_v@startwithwai.tech:/home/dh_webmistress_v/startwithwai.tech/scenario-lab-demo/
```

---

## SSH Commands to Set Permissions

After uploading, you **must** configure permissions and line endings. Files created on Windows have CRLF line endings which will crash Apache's CGI wrapper on Linux.

1. Connect to DreamHost via SSH:
   ```bash
   ssh dh_webmistress_v@startwithwai.tech
   ```

2. Change to the target directory:
   ```bash
   cd /home/dh_webmistress_v/startwithwai.tech/scenario-lab-demo
   ```

3. Convert Windows line endings (CRLF) to Unix line endings (LF) for the CGI script:
   ```bash
   sed -i 's/\r$//' index.cgi
   ```

4. Make the CGI entry point executable:
   ```bash
   chmod +x index.cgi
   ```

5. Set permissions for security:
   ```bash
   chmod 755 .
   chmod 644 .htaccess main.py passenger_wsgi.py
   ```

---

## Verification and Test URLs

Once uploaded and configured, verify by visiting the following URLs in your web browser:

1. **Root Endpoint**:
   - URL: `https://startwithwai.tech/scenario-lab-demo/`
   - Expected Output:
     ```json
     {
       "status": "ok",
       "message": "FastAPI via A2WSGI is responding",
       "runtime": "dreamhost-wsgi-smoke-test"
     }
     ```

2. **Health Check Endpoint**:
   - URL: `https://startwithwai.tech/scenario-lab-demo/health`
   - Expected Output:
     ```json
     {
       "status": "healthy",
       "environment": "dreamhost-shared-hosting"
     }
     ```

3. **Capabilities Endpoint**:
   - URL: `https://startwithwai.tech/scenario-lab-demo/capabilities`
   - Expected Output:
     ```json
     {
       "python_version": "3.10.12 (default, Nov 20 2023, 15:14:05) \n[GCC 11.4.0]",
       "platform": "Linux-5.15.0-...",
       "current_working_directory": "/home/dh_webmistress_v/startwithwai.tech/scenario-lab-demo",
       "sys_path": [
         "/home/dh_webmistress_v/.local/lib/python3.10/site-packages",
         "/home/dh_webmistress_v/startwithwai.tech/scenario-lab-demo",
         ...
       ],
       "imports": {
         "fastapi": true,
         "pydantic": true,
         "a2wsgi": true,
         "uvicorn": true,
         "mcp": true,
         "google.adk": false
       }
     }
     ```

---

## Troubleshooting & Failure Interpretations

If you encounter errors, here is how to interpret and resolve them:

### 1. `404 Not Found`
* **Interpretation**: Apache cannot find the folder or is failing to apply rewrite rules.
* **Troubleshooting**:
  * Double check that the folder was uploaded to `/home/dh_webmistress_v/startwithwai.tech/scenario-lab-demo`.
  * Try accessing the CGI script directly at `https://startwithwai.tech/scenario-lab-demo/index.cgi`. If this works, the `.htaccess` Rewrite rules are not being processed (verify `.htaccess` filename has the leading dot and correct capitalization).

### 2. `403 Forbidden`
* **Interpretation**: Permission issue. Apache is blocked from executing or reading directory contents.
* **Troubleshooting**:
  * Ensure the directory is executable (`chmod 755 .`).
  * Ensure the CGI script is executable (`chmod +x index.cgi`).
  * Ensure `.htaccess` and Python scripts are readable (`chmod 644`).

### 3. `500 Internal Server Error`
* **Interpretation**: The script crashed during execution or has bad formatting.
* **Troubleshooting**:
  * **Windows Line Endings (CRLF)**: The most common failure mode. Run `sed -i 's/\r$//' index.cgi` via SSH to strip Windows carriage returns.
  * **Script Errors**: Run the CGI script manually in SSH:
    ```bash
    python3 index.cgi
    ```
    If it displays import errors or tracebacks, correct the python code.

### 4. Raw Source Code Displayed
* **Interpretation**: Apache is serving `index.cgi` as a text file instead of executing it.
* **Troubleshooting**:
  * Ensure `Options +ExecCGI` and `AddHandler cgi-script .cgi` are set in `.htaccess`.
  * Ensure the file ends with `.cgi` and is located in the directory where ExecCGI is permitted.

### 5. Blank Page with `200 OK`
* **Interpretation**: The script started but exited without sending valid headers.
* **Troubleshooting**:
  * Check the DreamHost web server error logs at `/home/dh_webmistress_v/logs/startwithwai.tech/http/error.log` (or similar logs directory).
  * Run the script in the shell to see if it writes anything to stdout.

### 6. Import Errors
* **Interpretation**: Python cannot find your packages.
* **Troubleshooting**:
  * Verify the path `/home/dh_webmistress_v/.local/lib/python3.10/site-packages` exists and has the installed libraries.
  * Ensure the path prefix is loaded correctly in `sys.path`.

---

## Feasibility Recommendation

**Does a successful smoke test prove enough to attempt a hosted Scenario Lab demo on this shared plan?**

* **Yes, but with caveats**:
  * **Feasible for prototyping**: A successful response proves that Apache, CGI, WSGI, A2WSGI, and FastAPI work together perfectly, and we can host APIs/runtimes without root access and without interfering with WordPress.
  * **Latency (Cold Start)**: Because CGI spawns a new Python process for *each individual request*, the latency will be around **150ms to 400ms** per request just for Python to boot up and load packages. This is fine for a smoke test and low-traffic proof-of-concept, but will be slow for production or chat-heavy UIs.
  * **Recommendation**: If latency is acceptable for the early demo, proceed here. If a responsive user experience is required, we recommend creating a subdomain (e.g., `api.startwithwai.tech`) in the DreamHost panel, **enabling Passenger** on that subdomain (which keeps Python processes alive and eliminates the CGI startup overhead), or using a modern platform like Render or Railway.
