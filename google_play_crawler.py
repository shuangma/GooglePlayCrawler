#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from common.config import AppConfig
from common.logger import Logger
from common.command import Command
from feed.search.key_word_extractor import KeyWordExtractor


class GooglePlayCrawler:
    def __init__(self):
        log_file = os.path.join(AppConfig.get_log_dir(), 'google_play_crawler.log')

        self.logger = Logger(log_file, 'google_play_crawler', 10*1024*1024, 2)

    def start(self):
        self.logger.info('Start key word extractor thread....')
        self._start_key_word_extractor()

        self.logger.info('Start category feeder...')
        category_producer = os.path.join(os.getcwd(), 'feed', 'category', 'category_producer.py')
        category_consumer = os.path.join(os.getcwd(), 'feed', 'category', 'category_consumer.py')
        self._start_process(category_producer)
        self._start_process(category_consumer)

        self.logger.info('Start developer feeder...')
        developer_producer = os.path.join(os.getcwd(), 'feed', 'developer', 'developer_producer.py')
        developer_consumer = os.path.join(os.getcwd(), 'feed', 'developer', 'developer_consumer.py')
        self._start_process(developer_producer)
        self._start_process(developer_consumer)

        self.logger.info('Start search feeder...')
        search_producer = os.path.join(os.getcwd(), 'feed', 'search', 'search_producer.py')
        search_consumer = os.path.join(os.getcwd(), 'feed', 'search', 'search_consumer.py')
        self._start_process(search_producer)
        self._start_process(search_consumer)

        self.logger.info('Start similar feeder...')
        similar_producer = os.path.join(os.getcwd(), 'feed', 'similar', 'similar_producer.py')
        similar_consumer = os.path.join(os.getcwd(), 'feed', 'similar', 'similar_consumer.py')
        self._start_process(similar_producer)
        self._start_process(similar_consumer)

        self.logger.info('Start app detail crawler...')
        app_producer = os.path.join(os.getcwd(), 'crawler', 'app_producer.py')
        app_consumer = os.path.join(os.getcwd(), 'crawler', 'app_consumer.py')
        self._start_process(app_producer)
        self._start_process(app_consumer)

    def _start_key_word_extractor(self):
        key_word_extractor = KeyWordExtractor(self.logger)
        key_word_extractor.start()

    def _start_process(self, file_path):
        cmd = ['python', file_path]
        try:
            Command.run_without_wait(cmd)
        except Exception:
            self.logger.exception('Run script %s error' % file_path)


if __name__ == '__main__':
    google_play_crawler = GooglePlayCrawler()
    google_play_crawler.start()

