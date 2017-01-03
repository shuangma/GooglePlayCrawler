#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lxml import html

from app_detail_base_parser import AppDetailBaseParser
from model.app_detail import Screenshot, Review


class AppDetailLxmlParser(AppDetailBaseParser):
    def __init__(self, web_content, logger):
        AppDetailBaseParser.__init__(self, web_content, logger)

    def parse(self):
        html_tree = html.fromstring(self._web_content)

        try:
            app_icon_url = html_tree.xpath('//div[@class="cover-container"]/img[@class="cover-image"]/@src')[0].strip()
            if not app_icon_url.startswith('https'):
                app_icon_url = 'https:%s' % app_icon_url
            self.app_detail.app_icon_url = app_icon_url
        except Exception:
            self.logger.exception('Parse app icon error')

        try:
            self.app_detail.app_name = html_tree.xpath('//div[@class="details-info"]//div[@class="id-app-title"]/text()')[0].strip()
        except Exception:
            self.logger.exception('Parse app name error')

        try:
            developer_name = html_tree.xpath('//div[@itemprop="author"]/a[@class="document-subtitle primary"]/span[@itemprop="name"]/text()')
            if developer_name:
                self.app_detail.developer_name = developer_name[0].strip()
        except Exception:
            self.logger.exception('Parse developer name error')

        try:
            developer_link = html_tree.xpath('//div[@itemprop="author"]/a[@class="document-subtitle primary"]/@href')
            if developer_link:
                self.app_detail.developer_link = developer_link[0].strip()
        except Exception:
            self.logger.exception('Parse developer link error')

        try:
            self.app_detail.genres = html_tree.xpath('//a[@class="document-subtitle category"]/span[@itemprop="genre"]/text()')
        except Exception:
            self.logger.exception('Parse genres error')

        try:
            for screenshot in html_tree.xpath('//img[@class="screenshot"]'):
                img_url = screenshot.get('src').strip()
                if not img_url.startswith('https'):
                    img_url = 'https:%s' % img_url
                img_title = screenshot.get('title').strip()
                self.app_detail.screenshots.append(Screenshot(img_url, img_title))
        except Exception:
            self.logger.exception('Parse screenshots error')

        try:
            self.app_detail.description = html_tree.xpath('//div[@itemprop="description"]//*/text()')
        except Exception:
            self.logger.exception('Parse app description error')

        try:
            review_num = html_tree.xpath('//span[@class="reviews-num"]/text()')
            if review_num:
                review_num = review_num[0].strip()
                score = html_tree.xpath('//div[@class="score"]/text()')[0].strip()
                one_star = html_tree.xpath('//div[@class="rating-bar-container one"]/span[@class="bar-number"]/text()')[0].strip()
                two_star = html_tree.xpath('//div[@class="rating-bar-container two"]/span[@class="bar-number"]/text()')[0].strip()
                three_star = html_tree.xpath('//div[@class="rating-bar-container three"]/span[@class="bar-number"]/text()')[0].strip()
                four_star = html_tree.xpath('//div[@class="rating-bar-container four"]/span[@class="bar-number"]/text()')[0].strip()
                five_star = html_tree.xpath('//div[@class="rating-bar-container five"]/span[@class="bar-number"]/text()')[0].strip()
                review = Review(score, review_num, one_star, two_star, three_star, four_star, five_star)
                self.app_detail.review = review
        except Exception:
            self.logger.exception('Parse app review error')

        try:
            self.app_detail.update_date = html_tree.xpath('//div[@itemprop="datePublished"]/text()')[0].strip()
        except Exception:
            self.logger.exception('Parse app update date error')

        try:
            installs_count = html_tree.xpath('//div[@itemprop="numDownloads"]/text()')
            if installs_count and len(installs_count) > 0:
                self.app_detail.installs_count = installs_count[0].strip()
        except Exception:
            self.logger.exception('Parse app installs count error')
