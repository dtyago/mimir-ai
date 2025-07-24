# gunicorn_conf.py
import os
import multiprocessing

# Basic configuration
bind = "0.0.0.0:" + os.environ.get("PORT", "8000")
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
loglevel = os.environ.get('LOG_LEVEL', 'info')
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr

# Performance tuning
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', 5))
preload_app = True

# Security
# Ensure you have proper proxy setup if using these
# forwarded_allow_ips = '*'
# secure_scheme_headers = { 'X-FORWARDED-PROTO': 'https' }

print(f"Gunicorn config:")
print(f"  - Bind: {bind}")
print(f"  - Workers: {workers}")
print(f"  - Timeout: {timeout}")
print(f"  - Log Level: {loglevel}")
