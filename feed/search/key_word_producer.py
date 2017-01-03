#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
project_dir = os.path.join(os.path.dirname(__file__), '..', '..')
project_dir = os.path.normpath(project_dir)
sys.path.insert(1, project_dir)
print project_dir

import time
from pika.exceptions import ConnectionClosed

from common.config import AppConfig
from common.logger import Logger
from rabbitmq.rabbit_topic import RabbitTopic
from common import util
from common.util import UN_PUBLISHED, PUBLISHED
from common.mysql_db_util import MySQLDBUtil


LOG_FILE = os.path.join(AppConfig.get_log_dir(), 'keyword_producer.log')
LOG_NAME = 'keyword_producer'
EXCHANGE_NAME = 'keyword'
QUEUE_NAME = 'keyword_queue'
ROUTING_KEY = 'keyword.search'
QUEUE_LIMIT = 10
PRODUCE_WAIT_TIME = 3 * 60


class KeyWordProducer:
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

                key_words = self._fetch_key_words()
                for key_word in key_words:
                    if RabbitTopic.is_queue_full(QUEUE_NAME, QUEUE_LIMIT, self.logger):
                        self.logger.info('Queue %s is full, wait...' % QUEUE_NAME)
                        time.sleep(PRODUCE_WAIT_TIME)
                        continue
                    try:
                        rabbit_topic.publish(ROUTING_KEY, key_word)
                        self.logger.info('Publish key word %s and update status' % key_word)
                        self._update_status(PUBLISHED)
                    except ConnectionClosed:
                        self.logger.debug('Connection to rabbitmq server closed, re-connecting...')
                        rabbit_topic = RabbitTopic.init_rabbitmq_producer(EXCHANGE_NAME, self.logger)
            except Exception:
                self.logger.exception('Publish key word error')

    def _conn_db(self):
        try:
            self._db_conn = util.conn_mysql_db()
        except Exception:
            self.logger.exception('Connect database error')

    def _fetch_key_words(self):
        key_words = []

        self.logger.info('Get un-published keywords...')
        query = 'SELECT key_word FROM key_word WHERE status=%s LIMIT %s'
        try:
            results = MySQLDBUtil.fetch_multiple_rows(query, (UN_PUBLISHED, QUEUE_LIMIT), self._db_conn)
            for result in results:
                (key_word,) = result
                key_words.append(key_word)
        except Exception:
            self.logger.exception('Query un-published keywords error')
        return key_words

    def _is_no_more_records(self):
        query = 'SELECT COUNT(*) FROM key_word WHERE status=%s'
        try:
            result = MySQLDBUtil.fetch_single_row(query, (UN_PUBLISHED,), self._db_conn)
            if result:
                (count,) = result
                if count == 0:
                    return True
        except Exception:
            self.logger.exception('Check if there is no more key words error')
        return False

    def _update_status(self, status, key_word=None):
        if not key_word:
            query = 'UPDATE key_word SET status=%s'
        else:
            query = 'UPDATE key_word SET status=%s WHERE key_word=%s'
        try:
            if not key_word:
                MySQLDBUtil.update(query, (status,), self._db_conn)
            else:
                MySQLDBUtil.update(query, (status, key_word), self._db_conn)
        except Exception:
            self.logger.exception('Update record status')


if __name__ == '__main__':
    key_word_producer = KeyWordProducer()
    key_word_producer.start()







