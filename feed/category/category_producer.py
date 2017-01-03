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


LOG_FILE = os.path.join(AppConfig.get_log_dir(), 'category_producer.log')
LOG_NAME = 'category_producer'
EXCHANGE_NAME = 'category'
QUEUE_NAME = 'category_queue'
ROUTING_KEY = 'category.query'
QUEUE_LIMIT = 10
PRODUCE_WAIT_TIME = 3 * 60


class CategoryProducer:
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
                    self.logger.info('There are no more records, wait...')
                    time.sleep(PRODUCE_WAIT_TIME)
                    # Still no more available records, then reset...
                    if self._is_no_more_records():
                        self.logger.info('Still there are no more records, reset all records...')
                        self._reset_category()

                category_list = self._fetch_category_list()
                for category in category_list:
                    if RabbitTopic.is_queue_full(QUEUE_NAME, QUEUE_LIMIT, self.logger):
                        self.logger.info('Queue %s is full, wait...' % QUEUE_NAME)
                        time.sleep(PRODUCE_WAIT_TIME)
                        continue
                    try:
                        rabbit_topic.publish(ROUTING_KEY, category)
                        self.logger.info('Publish category %s and update the status' % category)
                        self._update_status(PUBLISHED, category)
                    except ConnectionClosed:
                        self.logger.debug('Connection to rabbitmq server closed, re-connecting...')
                        rabbit_topic = RabbitTopic.init_rabbitmq_producer(EXCHANGE_NAME, self.logger)
            except Exception:
                self.logger.exception('Publish category error')

    def _conn_db(self):
        try:
            self._db_conn = util.conn_mysql_db()
        except Exception:
            self.logger.exception('Connect database error')

    def _fetch_category_list(self):
        category_list = []

        self.logger.info('Get un-published category list...')
        query = 'SELECT category FROM category WHERE status=%s LIMIT %s'
        try:
            results = MySQLDBUtil.fetch_multiple_rows(query, (UN_PUBLISHED, QUEUE_LIMIT), self._db_conn)
            for result in results:
                (category,) = result
                category_list.append(category)
        except Exception:
            self.logger.exception('Query un-published category error')
        return category_list

    def _is_no_more_records(self):
        query = 'SELECT COUNT(*) FROM category WHERE status=%s'
        try:
            result = MySQLDBUtil.fetch_single_row(query, (UN_PUBLISHED,), self._db_conn)
            if result:
                (count,) = result
                if count == 0:
                    return True
        except Exception:
            self.logger.exception('Check available records error')
        return False

    def _reset_category(self):
        try:
            self.logger.info('All category have been published, reset all to un-published status')
            self._update_status(UN_PUBLISHED)
        except Exception:
            self.logger.exception('Reset category table error')
            return

    def _update_status(self, status, category=None):
        if not category:
            query = 'UPDATE category SET status=%s'
        else:
            query = 'UPDATE category SET status=%s WHERE category=%s'
        try:
            if not category:
                MySQLDBUtil.update(query, (status,), self._db_conn)
            else:
                MySQLDBUtil.update(query, (status, category), self._db_conn)
        except Exception:
            self.logger.exception('Update record status')


if __name__ == '__main__':
    category_producer = CategoryProducer()
    category_producer.start()







