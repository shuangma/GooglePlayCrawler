#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging import handlers


class Logger:
    def __init__(self, log_file, log_name, log_size, log_backupcount):
        handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=log_size, backupCount=log_backupcount)
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt='%b %d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def exception(self, msg):
        self.logger.exception(msg)
