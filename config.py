"""
Configuration file for scraper settings.
"""

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

# Async request timeout (seconds)
REQUEST_TIMEOUT = 30

# Retry config
MAX_RETRIES = 3
RETRY_DELAY = 1  # base delay between retries
