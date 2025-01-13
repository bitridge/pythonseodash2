import multiprocessing

# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 4
timeout = 120
keepalive = 5

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "seo_work_log"

# SSL Configuration (if not using nginx)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Worker process settings
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 50

# Server mechanics
daemon = False
pidfile = "logs/gunicorn.pid"
user = None
group = None
umask = 0
reload = False

# Server hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def when_ready(server):
    pass 