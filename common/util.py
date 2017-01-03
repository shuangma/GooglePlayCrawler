#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mysql_db_util import MySQLDBUtil
from mongo_db_util import MongoDBUtil
from config import AppConfig


# db status
UN_PUBLISHED = 0
PUBLISHED = 1
CONSUMED = 2


def decode_utf8(string):
    if not string:
        return ''
    return string.decode('utf-8', 'ignore')


def conn_mysql_db():
    db_conn = MySQLDBUtil.connect(AppConfig.mysql_db_host(), AppConfig.mysql_db_user(), AppConfig.mysql_db_password(),
                                  AppConfig.mysql_db_name(), AppConfig.mysql_db_port())
    return db_conn


def conn_mongo_db():
    db_conn = MongoDBUtil.connect(AppConfig.mongo_db_host(), AppConfig.mongo_db_port(), AppConfig.mongo_db_name())
    return db_conn
