# Gunicorn configuration for SSE streaming

bind = "0.0.0.0:10000"
workers = 2
worker_class = "sync"
timeout = 0  # Disable timeout for SSE streaming (infinite)
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
