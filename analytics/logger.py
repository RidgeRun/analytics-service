# Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
# All Rights Reserved.
#
# The contents of this software are proprietary and confidential to RidgeRun,
# LLC.  No part of this program may be photocopied, reproduced or translated
# into another programming language without prior written consent of
# RidgeRun, LLC.  The user is free to modify the source code after obtaining
# a software license from RidgeRun.  All source code changes must be provided
# back to RidgeRun without any encumbrance.

"""Service Logger
"""

import logging
import logging.config
import os


class CustomFormatter(logging.Formatter):
    """Custom formatter for logging
    """

    def __init__(self, format_str):
        super().__init__()
        self.__grey = "\x1b[38;20m"
        self.__yellow = "\x1b[33;20m"
        self.__red = "\x1b[31;20m"
        self.__green = "\x1b[32;20m"
        self.__bold_red = "\x1b[31;1m"
        self.__reset = "\x1b[0m"
        self.__format = format_str

        self.FORMATS = {
            logging.DEBUG: self.__grey + self.__format + self.__reset,
            logging.INFO: self.__green + self.__format + self.__reset,
            logging.WARNING: self.__yellow + self.__format + self.__reset,
            logging.ERROR: self.__red + self.__format + self.__reset,
            logging.CRITICAL: self.__bold_red + self.__format + self.__reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    """ This class contains the methods used to configure the service logger. """

    LOGGER_NAME = 'analytics'

    @classmethod
    def get_logger(cls):
        """Get logger with the given name

        Returns:
            logging: A logger object
        """
        return logging.getLogger(cls.LOGGER_NAME)

    @classmethod
    def init(cls, log_level=logging.INFO, log_file: str = None):
        """initialize the service logger

        Args:
            log_level (optional): Logging level as in logging. Defaults to logging.INFO.
            log_file (str, optional): Log file path. Defaults to None.
        """

        # Set log level
        logger = logging.getLogger(cls.LOGGER_NAME)
        logger.setLevel(log_level)

        # Add console handler
        cls._create_console_handler(name=cls.LOGGER_NAME)

        if log_file is not None:
            # Check that directory of log file exists to add file handler
            if os.path.isdir(os.path.dirname(log_file)):
                cls._create_file_handler(name=cls.LOGGER_NAME, file=log_file)
            else:
                logger.warning(
                    'Directory of selected log file does not exist, logging only to console')

    @classmethod
    def _create_console_handler(cls, name: str):
        """Create console logger

        Args:
            name (str): Logger name
        """
        # Create handler
        c_handler = logging.StreamHandler()
        # Set log format
        c_format = CustomFormatter(
            f'{name} - %(filename)-13s %(lineno)3d - %(levelname)7s: %(message)s')
        c_handler.setFormatter(c_format)
        # Add handler to logger
        logging.getLogger(name).addHandler(c_handler)

    @classmethod
    def _create_file_handler(cls, name: str, file: str):
        """ Create a file handler for the logger.

        Args:
            name (str): Logger name.
            file (str): Log file path.

        """
        # Create handler
        f_handler = logging.FileHandler(file)
        # Set log format
        f_format = CustomFormatter(
            f'%(asctime)s - {name} - %(filename)-13s %(lineno)3d - %(levelname)7s: %(message)s')
        f_handler.setFormatter(f_format)
        logging.getLogger(name).addHandler(f_handler)
