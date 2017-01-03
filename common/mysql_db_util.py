#!/usr/bin/env python
# -*- coding: utf-8 -*-


import MySQLdb


class MySQLDBUtil:
    def __init__(self):
        pass

    @staticmethod
    def connect(db_host, db_user, db_passwd, db_name, db_port=3306, encoding='utf8'):
        try:
            if not db_passwd:
                db_conn = MySQLdb.connect(host=db_host, user=db_user, db=db_name, port=db_port, charset=encoding)
            else:
                db_conn = MySQLdb.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_name, port=db_port,
                                          charset=encoding)
        except Exception:
            raise

        return db_conn

    @staticmethod
    def disconnect(db_conn):
        if db_conn:
            try:
                db_conn.commit()
                db_conn.close()
            except Exception:
                raise

    @staticmethod
    def fetch_single_row(query, para, db_conn):
        try:
            cursor = db_conn.cursor()
            cursor.execute(query, para)
            row = cursor.fetchone()
            cursor.close()
            db_conn.commit()
            return row
        except MySQLdb.Error:
            db_conn.rollback()
            raise

    @staticmethod
    def fetch_multiple_rows(query, para, db_conn):
        try:
            cursor = db_conn.cursor()
            cursor.execute(query, para)
            rows = cursor.fetchall()
            cursor.close()
            db_conn.commit()
            return rows
        except MySQLdb.Error:
            db_conn.rollback()
            raise

    @staticmethod
    def update(query, para, db_conn):
        try:
            cursor = db_conn.cursor()
            cursor.execute(query, para)
            affect_rowcount = cursor.rowcount
            cursor.close()
            db_conn.commit()
            return affect_rowcount
        except MySQLdb.Error:
            db_conn.rollback()
            raise

    @staticmethod
    def insert(query, para, db_conn):
        try:
            cursor = db_conn.cursor()
            cursor.execute(query, para)
            insert_id = db_conn.insert_id()
            cursor.close()
            db_conn.commit()
            return insert_id
        except MySQLdb.Error:
            db_conn.rollback()
            raise
