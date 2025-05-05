"""
services/logger.py
Module for logging service to handle logging operations.

This module provides a logger class to create and configure loggers for
different services. It supports both JSON formatted and plain text logs.
It includes methods to set up console and file handlers, and to format
the logs based on the specified format. The logger can be configured
to log to a file with a timestamped filename, and it ensures that the
log directory exists before writing logs. The logger can be used
to log messages at different levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
and can be easily integrated into other modules for consistent logging
across the application.

Classes:
--------
    Logger: A class that provides methods to create and configure loggers.
"""

import os
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

class Logger:
    """
    A class that provides methods to create and configure loggers.
    This class supports both JSON formatted and plain text logs.

    Attributes:
    ----------
        None

    Methods:
    -------
        get_logger(): Returns a configured logger with either JSON formatted 
        or plain text logs.

    """

    @staticmethod
    def get_logger(
        name,
        level=logging.DEBUG,
        log_to_file=False,
        log_file=None,
        json_format=True):
        """
        Returns a configured logger with either JSON formatted or plain text logs.

        Args:
            name (str): The name of the logger.
            level (int): The logging level (default is logging.DEBUG).
            log_to_file (bool): Whether to log to a file (default is False).
            log_file (str): The path to the log file (if log_to_file is True).
            json_format (bool): Whether to use JSON formatting for logs (default is True).

        Returns:
            logger (logging.Logger): A configured logger instance.

        Raises:
            ImportError: If jsonlogger is required but not installed.
            OSError: If there is an error creating the log directory or file.
            TypeError: If the logger name is not a string.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if not logger.hasHandlers():
            # Create console handler
            ch = logging.StreamHandler()
            ch.setLevel(level)

            # Choose formatter based on json_format flag
            if json_format:
                if jsonlogger is None:
                    raise ImportError("jsonlogger is required for JSON logging.")
                formatter = jsonlogger.JsonFormatter(
                    '%(asctime)s %(name)s %(levelname)s %(message)s'
                    )
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )

            ch.setFormatter(formatter)
            logger.addHandler(ch)

            # Optional: log to file if log_to_file is True
            if log_to_file:

                # Create a timestamped log file name if not provided
                if log_file is None:
                    log_file = f'{name}_{datetime.now().strftime("%Y%m%d%H%M%S")}.log'

                # Ensure log directory exists
                os.makedirs(os.path.dirname(log_file), exist_ok=True)

                fh = logging.FileHandler(log_file)
                fh.setLevel(level)
                fh.setFormatter(formatter)
                logger.addHandler(fh)

        return logger
