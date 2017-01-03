#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
project_dir = os.path.join(os.path.dirname(__file__), '..', '..')
project_dir = os.path.normpath(project_dir)
sys.path.insert(1, project_dir)

import multiprocessing

from pika.exceptions import ConnectionClosed

from common.logger import Logger
from common.config import AppConfig
from rabbitmq.rabbit_topic import RabbitTopic
from common import util
from common.util import CONSUMED
from common.mysql_db_util import MySQLDBUtil
from search_web_driver import SearchWebDriver

from key_word_producer import EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT, ROUTING_KEY


class KeyWordConsumer:
    def __init__(self, log_file, log_name):
        self.logger = Logger(log_file, log_name, 10*1024*1024, 2)
        self._db_conn = None

    def start(self):
        rabbit_topic = RabbitTopic.init_rabbitmq_consumer(EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT,
                                                          [ROUTING_KEY], self.logger)
        if not rabbit_topic:
            self.logger.debug('Construct key word consumer error')
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

    def _callback(self, channel, method, properties, key_word):
        self.logger.info(os.linesep)
        self.logger.info('----> Get body message %s and start searching this key word...<----' % key_word)
        try:
            url = 'https://play.google.com/store/search?q=%s&c=apps' % key_word
            search_web_driver = SearchWebDriver(url, self._db_conn, self.logger)
            search_web_driver.search()
        except Exception:
            self.logger.exception('Search key word %s error' % key_word)

        channel.basic_ack(delivery_tag=method.delivery_tag)

        self.logger.info('Set key word %s as consumed' % key_word)
        self._set_key_word_consumed(key_word)

    def _conn_db(self):
        try:
            self._db_conn = util.conn_mysql_db()
        except Exception:
            self.logger.exception('Connect to database error')

    def _set_key_word_consumed(self, key_word):
        query = 'UPDATE key_word SET status=%s WHERE key_word=%s'
        try:
            MySQLDBUtil.update(query, (CONSUMED, key_word), self._db_conn)
        except Exception:
            self.logger.exception('Set key word %s as consumed error' % key_word)


class MultipleConsumer:
    def __init__(self, number):
        self.number = number

    def work(self):
        pid = os.getpid()
        log_file = os.path.join(AppConfig.get_log_dir(), 'key_word_consumer_%d.log' % pid)
        key_word_consumer = KeyWordConsumer(log_file, 'key_word_consumer_%d' % pid)
        key_word_consumer.start()

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










