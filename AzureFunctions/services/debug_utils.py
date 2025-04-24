"""
services/debug_utils.py
This module contains utility functions for debugging purposes.
"""

import os
import time
import json

def write_debug_file(content: str, prefix: str = "debug_output") -> str:
    """
    Writes the provided content to a debug file and returns the file path.
    """
    debug_dir = "debug"
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = int(time.time())
    file_path = f"{debug_dir}/{prefix}_{timestamp}.txt"
    if not isinstance(content, str):
        try:
            content = json.dumps(content, indent=2)
        except (TypeError, ValueError):
            content = str(content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def is_debug_mode() -> bool:
    """
    Determines if debug mode is enabled by checking the DEBUG_MODE environment variable.
    """
    return os.environ.get("DEBUG_MODE", "false").lower() == "true"
