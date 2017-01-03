#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import nltk
import string

from threading import Thread
from nltk.corpus import stopwords
from nltk.stem.porter import *

from common import util
from common.util import UN_PUBLISHED, CONSUMED
from common.mysql_db_util import MySQLDBUtil


SLEEP_TIME = 3 * 60


class KeyWordExtractor(Thread):
    def __init__(self, logger):
        Thread.__init__(self)

        self._db_conn = None
        self._unnecessary_words = []
        self._stemmer = PorterStemmer()

        self.logger = logger

    def run(self):
        self.logger.info('Connect to the database...')
        self._conn_db()

        if not self._db_conn:
            self.logger.debug('No database connection, cannot perform keyword extraction')
            return

        self.logger.info('Construct unnecessary words...')
        self._construct_unnecessary_words()

        while 1:
            query = 'SELECT id,text FROM raw_text WHERE status=%s'
            results = MySQLDBUtil.fetch_multiple_rows(query, (UN_PUBLISHED,), self._db_conn)
            if not results:
                time.sleep(SLEEP_TIME)
            else:
                for result in results:
                    (record_id, text) = result
                    key_words = self._extrack_key_words(text)
                    try:
                        self._store_key_words(key_words)
                    except Exception:
                        self.logger.exception('Store key words error')
                    try:
                        self._update_status(record_id, CONSUMED)
                    except Exception:
                        self.logger.exception('Update raw_text status error')

    def _construct_unnecessary_words(self):
        self._unnecessary_words.extend(stopwords.words('english'))
        for digit in string.digits:
            self._unnecessary_words.append(digit)
        for punctuation in string.punctuation:
            self._unnecessary_words.append(punctuation)

    def _conn_db(self):
        try:
            self._db_conn = util.conn_mysql_db()
        except Exception:
            self.logger.exception('Connect database error')
            self._db_conn = None

    def _extrack_key_words(self, text):
        key_words = set()
        if not text:
            return key_words
        text = text.strip()
        try:
            tokenized_words = nltk.word_tokenize(text)
        except Exception:
            self.logger.exception('Tokenize text %s error' % text)
            return key_words

        for tokenized_word in tokenized_words:
            stemmed_word = self._stemmer.stem(tokenized_word)
            if stemmed_word in self._unnecessary_words:
                continue
            key_words.add(stemmed_word)
        return key_words

    def _store_key_words(self, key_words):
        values = []
        for key_word in key_words:
            values.append('("%s")' % key_word)

        if len(values) > 0:
            query = 'INSERT IGNORE INTO key_word (key_word) VALUES ' + ','.join(values)
            try:
                MySQLDBUtil.insert(query, None, self._db_conn)
            except Exception:
                self.logger.exception('Store key words into database fail')

    def _update_status(self, record_id, status):
        query = 'UPDATE raw_text SET status=%s WHERE id=%s'
        try:
            MySQLDBUtil.update(query, (status, record_id), self._db_conn)
        except Exception:
            self.logger.exception('Update raw_text table status error')

