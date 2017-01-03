#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model.app_detail import AppDetail


class AppDetailBaseParser:
    def __init__(self, web_content, logger):
        self._web_content = web_content
        self.app_detail = AppDetail()
        self.logger = logger

    def parse(self):
        pass
