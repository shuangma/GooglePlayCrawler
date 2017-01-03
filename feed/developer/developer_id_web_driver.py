#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from selenium import webdriver
from lxml import html
from selenium.common.exceptions import ElementNotVisibleException

from common.mysql_db_util import MySQLDBUtil

LOAD_TIME = 10
LOAD_FINISH_TRY_TIMES = 3


# If the developer link is a number, then use this web driver to extract package names
class DeveloperIdWebDrvier:
    def __init__(self, url, db_conn, logger):
        self._url = url
        self._db_conn = db_conn
        self.logger = logger
        self.web_driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])

    def query(self):
        try:
            self.logger.info('Try to get web content with url %s...' % self._url)
            self.web_driver.get(self._url)
        except Exception:
            self.logger.exception('Get url %s error' % self._url)
            self.web_driver.quit()
            return
        time.sleep(LOAD_TIME)

        last_app_links = set()

        buttons = self.web_driver.find_elements_by_xpath('//div[@class="button-image"]')

        while 1:
            if len(buttons) == 2:
                next_button = buttons[-1]
                try:
                    self.logger.info('Click next page button at first try...')
                    next_button.click()
                    time.sleep(LOAD_TIME)
                except ElementNotVisibleException:
                    self.logger.debug('Next page button not visible, cannot click this button, wait to load...')
                    time.sleep(LOAD_TIME)
                    try:
                        next_button.click()
                    except ElementNotVisibleException:
                        self.logger.debug('Next page button still not visible, cannot click this button')
            else:
                break

            load_finish, cur_app_links = self._is_load_finish(last_app_links, next_button)
            if load_finish:
                self.logger.info('It seems no more apps under this developer, check %d times' % LOAD_FINISH_TRY_TIMES)
                for i in range(LOAD_FINISH_TRY_TIMES):
                    load_finish, cur_app_links = self._is_load_finish(last_app_links, next_button)
                    time.sleep(LOAD_TIME)
                    if not load_finish:
                        break

            last_app_links = cur_app_links

            if load_finish:
                self.logger.info('No more apps to load, exit and parse package names...')
                break

        self.logger.info('Page loading finished, extract package names...')
        package_names = self._extract_package_names()

        self.logger.info('Store package names...')
        self._store_package_names(package_names)

        self.web_driver.quit()

    def _is_load_finish(self, last_app_links, next_button):
        try:
            next_button.click()
            time.sleep(LOAD_TIME)
        except ElementNotVisibleException:
            self.logger.debut('Next page button is not visible, cannot click this button')
        html_tree = html.fromstring(self.web_driver.page_source)
        app_links = html_tree.xpath('//a[@class="title"]/@href')
        app_links = set(app_links)
        if len(app_links & last_app_links) == len(app_links):
            return True, app_links
        return False, app_links

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
