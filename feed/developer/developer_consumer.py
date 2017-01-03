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

from developer_web_driver import DeveloperWebDriver
from developer_producer import EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT, ROUTING_KEY

DEVELOPER_NAME_HOST_URL = 'https://play.google.com/store/apps/developer?id'
DEVELOPER_ID_HOST_URL = 'https://play.google.com/store/apps/dev?id'


class DeveloperConsumer:
    def __init__(self, log_file, log_name):
        self.logger = Logger(log_file, log_name, 10*1024*1024, 2)
        self._db_conn = None

    def start(self):
        rabbit_topic = RabbitTopic.init_rabbitmq_consumer(EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT,
                                                          [ROUTING_KEY], self.logger)
        if not rabbit_topic:
            self.logger.debug('Construct developer consumer error')
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

    def _callback(self, channel, method, properties, developer):
        self.logger.info(os.linesep)
        self.logger.info('----> Get body message %s and start query this developer... <----' % developer)
        try:
            if developer.isdigit():
                self.logger.info('Developer info is all digit numbers')
                url = '%s=%s' % (DEVELOPER_ID_HOST_URL, developer)
            else:
                self.logger.info('Developer info is non digit numbers')
                url = '%s=%s' % (DEVELOPER_NAME_HOST_URL, developer)
            self.logger.info('Query developer apps with url %s' % url)
            developer_web_driver = DeveloperWebDriver(url, self._db_conn, self.logger)
            developer_web_driver.query()
        except Exception:
            self.logger.exception('Query developer %s error' % developer)

        channel.basic_ack(delivery_tag=method.delivery_tag)

        self.logger.info('Set developer %s as consumed' % developer)
        self._set_developer_consumed(developer)

    def _conn_db(self):
        try:
            self._db_conn = util.conn_mysql_db()
        except Exception:
            self.logger.exception('Connect database error')

    def _set_developer_consumed(self, developer):
        query = 'UPDATE developer SET status=%s WHERE name=%s'
        try:
            MySQLDBUtil.update(query, (CONSUMED, developer), self._db_conn)
        except Exception:
            self.logger.exception('Set devloper %s as consumed error' % developer)


class MultipleConsumer:
    def __init__(self, number):
        self.number = number

    def work(self):
        pid = os.getpid()
        log_file = os.path.join(AppConfig.get_log_dir(), 'developer_consumer_%d.log' % pid)
        developer_consumer = DeveloperConsumer(log_file, 'developer_consumer_%d' % pid)
        developer_consumer.start()

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










