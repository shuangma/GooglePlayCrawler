#!/usr/bin/env python
# -*- coding: utf-8 -*-

from developer_id_web_driver import DeveloperIdWebDrvier
from developer_name_web_driver import DeveloperNameWebDriver


class DeveloperWebDriver:
    def __init__(self, url, db_conn, logger, is_developer_id=False):
        self.web_driver = None
        self.logger = logger

        if is_developer_id:
            self.web_driver = DeveloperIdWebDrvier(url, db_conn, logger)
        else:
            self.web_driver = DeveloperNameWebDriver(url, db_conn, logger)

    def query(self):
        if not self.web_driver:
            self.logger.debug('No web driver to extract package names')
            return
        try:
            self.web_driver.query()
        except Exception:
            self.logger.exception('Try to extract package names error')


