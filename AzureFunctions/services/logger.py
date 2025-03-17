"""
    services/logger.py
    Module for logging service to handle logging operations.
"""

import logging
import os
from datetime import datetime
from pythonjsonlogger import jsonlogger

class Logger:
    """
    Logging service for handling operations with support for JSON formatting.
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

        Parameters:
            name (str): The name of the logger.
            level (int): The logging level.
            log_to_file (bool): Whether to log to file.
            log_file (str): The path to the log file.
            json_format (bool): Whether to format logs as JSON.

        Returns:
            logging.Logger: Configured logger instance
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
