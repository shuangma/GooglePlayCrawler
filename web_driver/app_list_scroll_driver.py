#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from lxml import html
from selenium import webdriver

from common import util
from web_driver.scroll_driver import ScrollDriver
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from common.mysql_db_util import MySQLDBUtil

LOAD_TIME = 5
SCROLL_LOAD_TIME = 5


class AppListScrollDriver(ScrollDriver):
    def __init__(self, url, db_conn, logger):
        self._url = url
        self._db_conn = db_conn

        self.logger = logger
        self.web_driver = webdriver.Chrome()

        ScrollDriver.__init__(self, self.web_driver, logger)

    def load_store_package_names(self):
        try:
            self.logger.info('Try to get web content with url %s...' % self._url)
            self.web_driver.get(self._url)
        except Exception:
            self.logger.exception('Use web driver to connect url error')
            return

        time.sleep(LOAD_TIME)

        show_more_button_xpath = '//button[@class="play-button" and @id="show-more-button"]'

        while 1:
            self.logger.info('Try to scroll down...')
            self.scroll_down(SCROLL_LOAD_TIME)
            try:
                show_more_button = self.web_driver.find_element_by_xpath(show_more_button_xpath)
            except NoSuchElementException:
                self.logger.debug('No show more button found')
                break

            if show_more_button:
                self.logger.info('Found show more button, try to click this button to load web page...' + str(show_more_button))
                if not self._show_more(show_more_button):
                    break
                time.sleep(LOAD_TIME)
            else:
                break

        self.logger.info('Extract package names from current search results...')
        try:
            package_names = self._extract_package_names()
        except Exception:
            self.logger.exception('Extract package names error')
            return
        finally:
            self.logger.info('Quit web driver')
            self.web_driver.quit()

        self.logger.info('Store package names...')
        self._store_package_names(package_names)

    def _show_more(self, show_more_button):
        try:
            show_more_button.click()
        except ElementNotVisibleException:
            self.logger.debug('Show more button is not visible, cannot click this button')
            return False
        return True

    def _extract_package_names(self):
        package_names = set()
        html_tree = html.fromstring(self.web_driver.page_source)
        app_links = html_tree.xpath('//a[@class="title"]/@href')
        for app_link in app_links:
            try:
                package_names.add(app_link.split('id=')[-1])
            except Exception:
                self.logger.exception('Extract package from link %s error' % app_link)
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
