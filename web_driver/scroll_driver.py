#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class ScrollDriver:
    def __init__(self, web_driver, logger):
        self.web_driver = web_driver
        self.logger = logger

    def scroll_down(self, load_time):
        last_height = self.web_driver.execute_script("return document.body.scrollHeight")
        while 1:
            self.web_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(load_time)
            cur_height = self.web_driver.execute_script("return document.body.scrollHeight")
            # If height after scroll equals the last one, then try to scroll in case it's still scrollable
            if cur_height == last_height:
                self.web_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(load_time)
                cur_height = self.web_driver.execute_script("return document.body.scrollHeight")
                if cur_height == last_height:
                    break
            last_height = cur_height



