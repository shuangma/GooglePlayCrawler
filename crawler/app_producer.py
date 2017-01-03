#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
project_dir = os.path.join(os.path.dirname(__file__), '..', '..')
project_dir = os.path.normpath(project_dir)
sys.path.insert(1, project_dir)

import time
from pika.exceptions import ConnectionClosed

from common.config import AppConfig
from common.logger import Logger
from rabbitmq.rabbit_topic import RabbitTopic
from common import util
from common.util import UN_PUBLISHED, PUBLISHED

from common.mysql_db_util import MySQLDBUtil


LOG_FILE = os.path.join(AppConfig.get_log_dir(), 'app_producer.log')
LOG_NAME = 'app_producer'
EXCHANGE_NAME = 'app'
QUEUE_NAME = 'app_queue'
ROUTING_KEY = 'app.crawl'
QUEUE_LIMIT = 50
PRODUCE_WAIT_TIME = 3 * 60


class AppProducer:
    def __init__(self):
        self.logger = Logger(LOG_FILE, LOG_NAME, 10*1024*1024, 2)
        self._db_conn = None

    def start(self):
        rabbit_topic = RabbitTopic.init_rabbitmq_producer(EXCHANGE_NAME, self.logger)
        if not rabbit_topic:
            return

        self._conn_db()
        if not self._db_conn:
            self.logger.exception('Connect database error')
            return

        while 1:
            try:
                if self._is_no_more_records():
                    self.logger.info('There are no more available records, wait...')
                    time.sleep(PRODUCE_WAIT_TIME)

                package_list = self._fetch_package_list()
                for package_name in package_list:
                    if RabbitTopic.is_queue_full(QUEUE_NAME, QUEUE_LIMIT, self.logger):
                        self.logger.info('Queue %s is full, wait to consume...' % QUEUE_NAME)
                        time.sleep(PRODUCE_WAIT_TIME)
                        continue
                    try:
                        rabbit_topic.publish(ROUTING_KEY, package_name)
                        self.logger.info('Publish package %s and update status' % package_name)
                        self._update_status(PUBLISHED, package_name)
                    except ConnectionClosed:
                        self.logger.debug('Connection to rabbitmq server closed, re-connecting...')
                        rabbit_topic = RabbitTopic.init_rabbitmq_producer(EXCHANGE_NAME, self.logger)
            except Exception:
                self.logger.exception('Publish similar app package name error')

    def _init_rabbitmq(self):
        try:
            rabbit_topic = RabbitTopic(EXCHANGE_NAME)
            rabbit_topic.construct_producer()
        except Exception:
            self.logger.exception('Construct app producer error')
            return None
        return rabbit_topic

    def _conn_db(self):
        try:
            self._db_conn = util.conn_mysql_db()
        except Exception:
            self.logger.exception('Connect database error')

    def _fetch_package_list(self):
        package_list = []

        self.logger.info('Get un-published package list...')
        query = 'SELECT package_name FROM package_name WHERE status=%s LIMIT %s'
        try:
            results = MySQLDBUtil.fetch_multiple_rows(query, (UN_PUBLISHED, QUEUE_LIMIT), self._db_conn)
            for result in results:
                (package_name,) = result
                package_list.append(package_name)
        except Exception:
            self.logger.exception('Query un-used package name error')
        return package_list

    def _is_no_more_records(self):
        query = 'SELECT COUNT(*) FROM package_name WHERE status=%s'
        try:
            result = MySQLDBUtil.fetch_single_row(query, (UN_PUBLISHED,), self._db_conn)
            if result:
                (count, ) = result
                if count == 0:
                    return True
        except Exception:
            self.logger.exception('Check if there is no more packages error')
        return False

    def _update_status(self, status, package_name=None):
        if not package_name:
            query = 'UPDATE package_name SET status=%s'
        else:
            query = 'UPDATE package_name SET status=%s WHERE package_name=%s'
        try:
            if not package_name:
                MySQLDBUtil.update(query, (status,), self._db_conn)
            else:
                MySQLDBUtil.update(query, (status, package_name), self._db_conn)
        except Exception:
            self.logger.exception('Update record status')


if __name__ == '__main__':
    app_producer = AppProducer()
    app_producer.start()







