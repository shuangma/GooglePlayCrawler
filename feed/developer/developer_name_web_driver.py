#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web_driver.app_list_scroll_driver import AppListScrollDriver


class DeveloperNameWebDriver(AppListScrollDriver):
    def __init__(self, url, db_conn, logger):
        self.logger = logger
        AppListScrollDriver.__init__(self, url, db_conn, logger)

    def query(self):
        self.load_store_package_names()