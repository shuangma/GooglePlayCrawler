#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient


class MongoDBUtil:
    @staticmethod
    def connect(host, port, db_name):
        client = MongoClient(host, port)
        db = client[db_name]
        return db

    @staticmethod
    def insert(document, db, collection_name):
        collection = db[collection_name]
        return collection.insert_one(document)







