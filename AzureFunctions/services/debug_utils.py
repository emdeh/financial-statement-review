"""
services/debug_utils.py
Module for debugging utilities.

This module provides utility functions for debugging purposes.
It includes a function to write debug information to a file
and a function to check if the application is running in debug mode.

Functions:
--------
    write_debug_file(): Writes debug information to a file.
    is_debug_mode(): Checks if the application is running in debug mode.

"""

import os
import time
import json

def write_debug_file(content: str, prefix: str = "debug_output") -> str:
    """
    A utility function to write debug information to a file.
    This function creates a directory named 'debug' if it does not exist,
    and writes the provided content to a file with a timestamped name.

    Args:
        content (str): The content to be written to the debug file.
        prefix (str): The prefix for the debug file name (default is "debug_output").

    Returns:
        str: The path to the created debug file.

    Raises:
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
    Checks if the application is running in debug mode.

    This function checks the environment variable "DEBUG_MODE" to determine
    if the application is in debug mode. If the variable is set to "true",
    the function returns True; otherwise, it returns False.

    Args:
        None

    Returns:
        bool: True if the application is in debug mode, False otherwise.

    Raises:
        KeyError: If the "DEBUG_MODE" environment variable is not set.
        ValueError: If the value of "DEBUG_MODE" is not a valid boolean string.
        TypeError: If the value of "DEBUG_MODE" is not a string.
        OSError: If there is an error accessing the environment variable.
    """
    return os.environ.get("DEBUG_MODE", "false").lower() == "true"
