from .base import *
import logging
from logging.handlers import RotatingFileHandler
import os

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Ensure logs directory exists
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure Python logger for live console + file logging
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)  # Capture all logs

# Console handler (live logging)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # INFO+ goes to console
console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(console_formatter)

# File handler (persistent log)
file_handler = RotatingFileHandler(
    LOG_DIR / "server_errors.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB per file
    backupCount=3
)
file_handler.setLevel(logging.WARNING)  # WARNING+ goes to file
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(file_formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Optional: suppress Django server error duplication in console
logging.getLogger("django.server").setLevel(logging.WARNING)
