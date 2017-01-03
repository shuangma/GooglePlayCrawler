#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
project_dir = os.path.join(os.path.dirname(__file__), '..', '..')
project_dir = os.path.normpath(project_dir)
sys.path.insert(1, project_dir)

import multiprocessing
import requests
import time

from lxml import html
from pika.exceptions import ConnectionClosed


from common.logger import Logger
from common.config import AppConfig
from rabbitmq.rabbit_topic import RabbitTopic
from common import util
from common.util import CONSUMED
from common.mysql_db_util import MySQLDBUtil

from category_web_driver import CategoryWebDriver
from category_producer import EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT, ROUTING_KEY

CATEGORY_HOST_URL = 'https://play.google.com/store/apps/category'


class CategoryConsumer:
    def __init__(self, log_file, log_name):
        self.logger = Logger(log_file, log_name, 10*1024*1024, 2)
        self._db_conn = None

    def start(self):
        rabbit_topic = RabbitTopic.init_rabbitmq_consumer(EXCHANGE_NAME, QUEUE_NAME, QUEUE_LIMIT,
                                                          [ROUTING_KEY], self.logger)
        if not rabbit_topic:
            self.logger.debug('Construct category consumer error')
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

    def _callback(self, channel, method, properties, category):
        self.logger.info(os.linesep)
        self.logger.info('----> Get body message %s and start query this category... <----' % category)
        try:
            detail_urls = self._parse_detail_urls(category)
            if not detail_urls:
                self.logger.debug('No detail category urls got')
                return
            for detail_url in detail_urls:
                self.logger.info('Query detail category url %s' % detail_url)
                category_web_driver = CategoryWebDriver(detail_url, self._db_conn, self.logger)
                category_web_driver.query()
                time.sleep(10)
        except Exception:
            self.logger.exception('Query category %s error' % category)

        channel.basic_ack(delivery_tag=method.delivery_tag)

        self.logger.info('Set category %s as consumed' % category)
        self._set_category_consumed(category)

    def _conn_db(self):
        try:
            self._db_conn = util.conn_mysql_db()
        except Exception:
            self.logger.exception('Connect database error')

    def _parse_detail_urls(self, category):
        detail_urls = set()
        category_url = '%s/%s' % (CATEGORY_HOST_URL, category)
        try:
            response = requests.get(category_url)
            if response.status_code == requests.codes.ok:
                html_tree = html.fromstring(response.content)
                category_detail_links = html_tree.xpath('//a[@class="see-more play-button small id-track-click apps id-responsive-see-more"]//@href')
                for category_detail_link in category_detail_links:
                    category_detail_link = category_detail_link.strip()
                    detail_urls.add('https://play.google.com%s' % category_detail_link)
            else:
                self.logger.debug('Access category url %s and returns wrong response code %d' % (category_url, response.status_code))
        except Exception:
            self.logger.exception('Get category web page error')
        return detail_urls

    def _set_category_consumed(self, category):
        query = 'UPDATE category SET status=%s WHERE category=%s'
        try:
            MySQLDBUtil.update(query, (CONSUMED, category), self._db_conn)
        except Exception:
            self.logger.exception('Set category %s as consumed error' % category)


class MultipleConsumer:
    def __init__(self, number):
        self.number = number

    def work(self):
        pid = os.getpid()
        log_file = os.path.join(AppConfig.get_log_dir(), 'category_consumer_%d.log' % pid)
        category_consumer = CategoryConsumer(log_file, 'category_consumer_%d' % pid)
        category_consumer.start()

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










