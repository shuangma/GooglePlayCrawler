#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
project_dir = os.path.join(os.path.dirname(__file__), '..', '..')
project_dir = os.path.normpath(project_dir)
sys.path.insert(1, project_dir)

import multiprocessing
import requests

from lxml import html
from pika.exceptions import ConnectionClosed

from common.logger import Logger
from common.config import AppConfig
from rabbitmq.rabbit_topic import RabbitTopic
from common import util
from common.util import CONSUMED
from common.mysql_db_util import MySQLDBUtil

from similar_producer import EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT, ROUTING_KEY

SIMILAR_HOST_URL = 'https://play.google.com/store/apps/similar?id'


class SimilarConsumer:
    def __init__(self, log_file, log_name):
        self.logger = Logger(log_file, log_name, 10*1024*1024, 2)
        self._db_conn = None

    def start(self):
        rabbit_topic = RabbitTopic.init_rabbitmq_consumer(EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT,
                                                          [ROUTING_KEY], self.logger)
        if not rabbit_topic:
            self.logger.debug('Construct similar consumer error')
            return

        self._conn_db()
        if not self._db_conn:
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
        self.logger.info('----> Get body message %s and start query apps similar to this... <----' % package_name)
        try:
            url = '%s=%s' % (SIMILAR_HOST_URL, package_name)
            self.logger.info('Query similar apps with url %s' % url)
            package_names = self._extract_package_names(url)
            self.logger.info('Store package names...')
            self._store_package_names(package_names)
        except Exception:
            self.logger.exception('Query similar apps %s error' % package_name)

        channel.basic_ack(delivery_tag=method.delivery_tag)

        self.logger.info('Set package name %s as consumed' % package_name)
        self._set_package_consumed(package_name)

    def _conn_db(self):
        try:
            self._db_conn = util.conn_mysql_db()
        except Exception:
            self.logger.exception('Connect database error')

    def _extract_package_names(self, url):
        package_names = set()

        try:
            response = requests.get(url)
        except Exception:
            self.logger.exception('Get content with url %s error' % url)
            return package_names

        if response.status_code == requests.codes.ok:
            html_tree = html.fromstring(response.content)
            app_links = html_tree.xpath('//a[@class="title"]/@href')
            for app_link in app_links:
                try:
                    package_names.add(app_link.split('id=')[-1])
                except Exception:
                    self.logger.exception('Extract package from link %s error' % app_link)
        else:
            self.logger.debug('Access similar app url %s and returns wrong response code %d' % (url, response.status_code))
        return package_names

    def _store_package_names(self, package_names):
        values = []
        for package_name in package_names:
            values.append('("%s")' % package_name)

        if len(values) > 0:
            query = 'INSERT IGNORE INTO package_name (package_name) VALUES ' + ','.join(values)
            try:
                MySQLDBUtil.insert(query, None, self._db_conn)
            except Exception:
                self.logger.exception('Store package names into database fail')

    def _set_package_consumed(self, package_name):
        query = 'UPDATE similar_app SET status=%s WHERE package_name=%s'
        try:
            MySQLDBUtil.update(query, (CONSUMED, package_name), self._db_conn)
        except Exception:
            self.logger.exception('Set package name %s as consumed error' % package_name)


class MultipleConsumer:
    def __init__(self, number):
        self.number = number

    def work(self):
        pid = os.getpid()
        log_file = os.path.join(AppConfig.get_log_dir(), 'similar_consumer_%d.log' % pid)
        similar_consumer = SimilarConsumer(log_file, 'similar_consumer_%d' % pid)
        similar_consumer.start()

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










