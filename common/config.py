#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from ConfigParser import ConfigParser


class AppConfig:
    def __init__(self):
        pass

    PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
    PROJECT_DIR = os.path.normpath(PROJECT_DIR)

    CONFIG = ConfigParser()
    CONFIG.read([os.path.join(PROJECT_DIR, 'app.cfg')])

    @staticmethod
    def mysql_db_host():
        return AppConfig.CONFIG.get('mysql_db_info', 'host')

    @staticmethod
    def mysql_db_user():
        return AppConfig.CONFIG.get('mysql_db_info', 'user')

    @staticmethod
    def mysql_db_name():
        return AppConfig.CONFIG.get('mysql_db_info', 'name')

    @staticmethod
    def mysql_db_password():
        return AppConfig.CONFIG.get('mysql_db_info', 'password')

    @staticmethod
    def mysql_db_port():
        port = AppConfig.CONFIG.get('mysql_db_info', 'port')
        if not port:
            port = 3306
        try:
            port = int(port)
        except Exception:
            pass
        return port

    @staticmethod
    def mongo_db_host():
        return AppConfig.CONFIG.get('mongo_db_info', 'host')

    @staticmethod
    def mongo_db_name():
        return AppConfig.CONFIG.get('mongo_db_info', 'name')

    @staticmethod
    def mongo_db_port():
        port = AppConfig.CONFIG.get('mongo_db_info', 'port')
        if not port:
            port = 27017
        try:
            port = int(port)
        except Exception:
            pass
        return port

    @staticmethod
    def get_log_dir():
        log_dir = os.path.join(AppConfig.PROJECT_DIR, 'log')
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        return log_dir

    @staticmethod
    def get_rabbitmq_admin():
        rabbitmq_home = AppConfig.CONFIG.get('common', 'rabbitmq_home')
        return os.path.join(rabbitmq_home, 'rabbitmqadmin')