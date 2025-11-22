"""
Logging configuration for ProjectGoat
Provides structured logging for development and production environments
"""
import logging
import sys
from pathlib import Path

try:
    from .config import settings
except ImportError:
    from config import settings


def setup_logging():
    """Configure application logging based on environment"""

    # Determine log level based on environment
    log_level = logging.DEBUG if settings.is_development else logging.INFO

    # Create logs directory if it doesn't exist (only in production)
    if settings.is_production:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "projectgoat.log"
    else:
        log_file = None

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # File handler (production only)
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Apply handlers to root logger
    root_logger = logging.getLogger()
    root_logger.handlers = handlers

    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if settings.is_production else logging.INFO
    )

    return logging.getLogger(__name__)


# Create logger instance
logger = setup_logging()
