# File: auth.py
# Description: API key and user authentication for Crucial
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-07 12:38:53

import json
from pathlib import Path
from fastapi import HTTPException
from crucial.config import CONFIG, get_logger

logger = get_logger(__name__)


def load_keys():
    """
    Load API keys from the file specified in config.
    """
    keyfile = Path(CONFIG["AUTH"]["keys_file"])
    if not keyfile.exists():
        return set()
    with keyfile.open() as f:
        return set(json.load(f))

def validate_api_key(key: str) -> bool:
    if not CONFIG["AUTH"]["require_api_key"]:
        logger.debug("API key check bypassed (require_api_key=False)")
        return True
    valid_keys = load_keys()
    result = key in valid_keys
    logger.debug("API key %s: %s", key, "ACCEPTED" if result else "REJECTED")
    return result

def require_api_key_header(headers):
    """
    Validate incoming x-api-key header, raise HTTPException if invalid.
    """
    key = headers.get("x-api-key")
    if not validate_api_key(key):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
