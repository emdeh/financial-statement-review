"""
services/debug_utils.py
This module contains utility functions for debugging purposes.

Functions
---------
    write_debug_file()
        Writes the provided content to a debug file and returns the file path.
    is_debug_mode()
        Determines if debug mode is enabled by checking the DEBUG_MODE environment variable.
"""

import os
import time
import json

def write_debug_file(content: str, prefix: str = "debug_output") -> str:
    """
    A utility function to write debug information to a file.
    This function creates a directory named 'debug' if it doesn't exist,
    and writes the provided content to a file with a timestamp in its name.
    The file is saved in the 'debug' directory.

    Parameters
    ----------
        content (str):  The content to be written to the debug file.
        prefix (str):   The prefix for the debug file name. Default is 
                        "debug_output".

    Returns
    -------
        str: The path to the created debug file.

    Raises
    ------
        OSError: If there is an error creating the directory or writing to the file.
        TypeError: If the content is not a string and cannot be converted to a string.
        ValueError: If the content cannot be serialized to JSON.
        
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
    A utility function to check if the application is running in debug mode.
    This function checks the environment variable 'DEBUG_MODE' and returns
    True if it is set to 'true' (case insensitive), otherwise returns False.
    This is useful for enabling or disabling debug-specific features or
    logging in the application.

    Returns
    -------
        bool: True if debug mode is enabled, False otherwise.
    """
    return os.environ.get("DEBUG_MODE", "false").lower() == "true"
