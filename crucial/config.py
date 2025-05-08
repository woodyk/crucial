# File: config.py
# Description: Central configuration for Crucial platform
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-07 22:20:03

import os
import logging
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "SERVER": {
        "host": os.getenv("CRUCIAL_HOST", "0.0.0.0"),
        "port": int(os.getenv("CRUCIAL_PORT", 8000)),
        "ssl_enabled": os.getenv("CRUCIAL_SSL", "false").lower() == "true",
        "ssl_cert": os.getenv("CRUCIAL_SSL_CERT", "cert.pem"),
        "ssl_key": os.getenv("CRUCIAL_SSL_KEY", "key.pem"),
        "log_level": os.getenv("CRUCIAL_LOG_LEVEL", "info")
    },
    "CANVAS": {
        "default_width": int(os.getenv("CANVAS_WIDTH", 800)),
        "default_height": int(os.getenv("CANVAS_HEIGHT", 600)),
        "default_bg": os.getenv("CANVAS_BACKGROUND", "#000000"),
        "validate_schema": os.getenv("CANVAS_VALIDATE", "false").lower() == "true"
    },
    "FRONTEND": {
        "enable_websocket": os.getenv("FRONTEND_ENABLE_WS", "true").lower() == "true",
        "replay_delay_ms": int(os.getenv("FRONTEND_REPLAY_DELAY", 30)),
        "theme": os.getenv("FRONTEND_THEME", "dark")
    },
    "DATABASE": {
        "path": os.getenv("CRUCIAL_DB_PATH", "crucial.db")
    },
    "AUTH": {
        "require_api_key": os.getenv("AUTH_REQUIRE_API_KEY", "true").lower() == "true",
        "keys_file": os.getenv("AUTH_KEYS_FILE", "keys.json")
    },
    "TOOLS": {
        "api_base_url": os.getenv("TOOLS_API_URL", "http://localhost:8000/canvas"),
        "timeout": int(os.getenv("TOOLS_TIMEOUT", 10)),
        "retries": int(os.getenv("TOOLS_RETRIES", 3))
    },
    "LOGGING": {
        "log_to_file": os.getenv("CRUCIAL_LOG_TO_FILE", "true").lower() == "true",
        "log_path": os.getenv("CRUCIAL_LOG_PATH", "logs/crucial.log"),
        "debug": os.getenv("CRUCIAL_LOG_DEBUG", "false").lower() == "true"
    },
    "SAVE": {
        "output_dir": os.getenv("CRUCIAL_SAVE_IMAGES_PATH", "images")
    }
}

def get_logger(name: str) -> logging.Logger:
    os.makedirs(os.path.dirname(CONFIG["LOGGING"]["log_path"]), exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Prevent duplicate handlers

    level = logging.DEBUG if CONFIG["LOGGING"]["debug"] else logging.INFO
    logger.setLevel(level)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    logger.addHandler(stream)

    if CONFIG["LOGGING"]["log_to_file"]:
        file_handler = logging.FileHandler(CONFIG["LOGGING"]["log_path"])
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger

