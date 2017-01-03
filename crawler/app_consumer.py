#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
project_dir = os.path.join(os.path.dirname(__file__), '..', '..')
project_dir = os.path.normpath(project_dir)
sys.path.insert(1, project_dir)

import multiprocessing
import requests

from pika.exceptions import ConnectionClosed

from common.logger import Logger
from common.config import AppConfig
from rabbitmq.rabbit_topic import RabbitTopic
from common import util
from common.util import CONSUMED
from common.mysql_db_util import MySQLDBUtil
from common.mongo_db_util import MongoDBUtil
from crawler.parser.app_detail_b4_parser import AppDetailB4Parser
from crawler.parser.app_detail_lxml_parser import AppDetailLxmlParser

from app_producer import EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT, ROUTING_KEY

APP_HOST_URL = 'https://play.google.com/store/apps/details?id'


class AppConsumer:
    def __init__(self, log_file, log_name):
        self.logger = Logger(log_file, log_name, 10*1024*1024, 2)
        self._mysql_db_conn = None
        self._mongo_db_conn = None

    def start(self):
        rabbit_topic = RabbitTopic.init_rabbitmq_consumer(EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT,
                                                          [ROUTING_KEY], self.logger)
        if not rabbit_topic:
            self.logger.debug('Construct app consumer error')
            return

        self._conn_db()
        if not self._mysql_db_conn or not self._mongo_db_conn:
            self.logger.exception('Connect to database error')
            return

        while 1:
            try:
                rabbit_topic.start_consuming(self._callback, QUEUE_NAME)
            except ConnectionClosed:
                self.logger.debug('Connection to rabbitmq server closed, re-connecting...')
                rabbit_topic = RabbitTopic.init_rabbitmq_consumer(EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT,
                                                                  [ROUTING_KEY], self.logger)

    def _callback(self, channel, method, properties, package_name):
        self.logger.info(os.linesep)
        self.logger.info('----> Get body message %s and start get app detail... <-----' % package_name)
        try:
            url = '%s=%s' % (APP_HOST_URL, package_name)
            self.logger.info('Query app detail with url %s' % url)
            app_detail = self._parse_web_content(url)

            if not app_detail:
                self.logger.info('App detail extraction fail')
            else:
                self.logger.info('Store app detail...')
                app_detail.package_name = package_name
                self._store_app_detail(app_detail)

            self.logger.info('Insert package name %s into similar app table...' % package_name)
            self._store_package_name_similar(package_name)

            self.logger.info('Store app description...')
            self._store_app_description(app_detail)

            self.logger.info('Store app developer...')
            self._store_app_developer(app_detail)

        except Exception:
            self.logger.exception('Query app detail %s error' % package_name)

        channel.basic_ack(delivery_tag=method.delivery_tag)

        self.logger.info('Set package name %s as consumed' % package_name)
        self._set_package_consumed(package_name)

    def _conn_db(self):
        try:
            self._mysql_db_conn = util.conn_mysql_db()
            self._mongo_db_conn = util.conn_mongo_db()
        except Exception:
            self.logger.exception('Connect database error')

    def _parse_web_content(self, url):
        app_detail = None
        try:
            response = requests.get(url)
        except Exception:
            self.logger.exception('Get web content from url %s error' % url)
            return app_detail
        try:
            web_content = util.decode_utf8(response.content)
        except Exception:
            self.logger.exception('Decode web content error')
            return app_detail
        if not web_content:
            self.logger.debug('Web content is empty, no need to parse')
            return app_detail
        else:
            self.logger.info('Get web content successfully,try to parse it...')

        app_detail_lxml_parser = AppDetailLxmlParser(web_content, self.logger)
        try:
            app_detail_lxml_parser.parse()
            app_detail = app_detail_lxml_parser.app_detail
        except Exception:
            self.logger.exception('Use lxml to parse the web content error, try to use the backup one beautiful soup...')
            app_detail_b4_parser = AppDetailB4Parser(response.content, self.logger)
            try:
                app_detail_b4_parser.parse()
                app_detail = app_detail_b4_parser.app_detail
            except Exception:
                self.logger.exception('Use beautiful soup to parse the web content error')

        return app_detail

    def _store_app_detail(self, app_detail):
        if not app_detail:
            self.logger.debug('No app detail content, cannot store into database')
            return
        app_detail_json = app_detail.to_json()
        try:
            MongoDBUtil.insert(app_detail_json, self._mongo_db_conn, 'app_detail')
        except Exception:
            self.logger.exception('Store app detail content into mongo db error')

    def _store_package_name_similar(self, package_name):
        query = 'INSERT IGNORE INTO similar_app (package_name) VALUES ("%s")' % package_name
        try:
            MySQLDBUtil.insert(query, None, self._mysql_db_conn)
        except Exception:
            self.logger.exception('Store package name into similar app database fail')

    def _store_app_description(self, app_detail):
        if not app_detail:
            return
        description = ' '.join(app_detail.description)
        description = description.replace('"', '').replace('\'', '')
        if not description:
            return
        query = 'INSERT INTO raw_text (text) VALUES ("%s")' % description
        try:
            MySQLDBUtil.insert(query, None, self._mysql_db_conn)
        except Exception:
            self.logger.exception('Store app description error')

    def _store_app_developer(self, app_detail):
        if not app_detail:
            return
        developer_link = app_detail.developer_link
        if not developer_link:
            return
        items = developer_link.split('id=')
        if len(items) == 2:
            developer_name = items[-1]
            query = 'INSERT IGNORE INTO developer (name) VALUES ("%s")' % developer_name
            try:
                MySQLDBUtil.insert(query, None, self._mysql_db_conn)
                self.logger.info('Stored app developer %s' % developer_name)
            except Exception:
                self.logger.exception('Store app developer error')
        else:
            return

    def _set_package_consumed(self, package_name):
        query = 'UPDATE package_name SET status=%s WHERE package_name=%s'
        try:
            MySQLDBUtil.update(query, (CONSUMED, package_name), self._mysql_db_conn)
        except Exception:
            self.logger.exception('Set package name %s as consumed error' % package_name)


class MultipleConsumer:
    def __init__(self, number):
        self.number = number

    def work(self):
        pid = os.getpid()
        log_file = os.path.join(AppConfig.get_log_dir(), 'app_consumer_%d.log' % pid)
        app_consumer = AppConsumer(log_file, 'app_consumer_%d' % pid)
        app_consumer.start()

    def start(self):
        process_list = []
        for i in xrange(self.number):
            process = multiprocessing.Process(target=self.work)
            process.daemon = True
            process.start()
            process_list.append(process)

        for process in process_list:
            process.join()


if __name__ == '__main__':
    multiple_consumer = MultipleConsumer(1)
    multiple_consumer.start()
