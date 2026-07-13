"""
Logging configuration module for structured logging.
"""

import logging
import logging.config
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configures the python built-in logging module to output structured logs.
    
    If the environment is set to 'production', logs are output as JSON strings.
    Otherwise, standard readable logs are printed to stdout.
    """
    log_level: str = settings.log_level.upper()

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "formatter": "json" if settings.environment == "production" else "standard",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": log_level,
                "propagate": True,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
