#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup


from app_detail_base_parser import AppDetailBaseParser
from model.app_detail import Screenshot, Review


class AppDetailB4Parser(AppDetailBaseParser):
    def __init__(self, web_content, logger):
        AppDetailBaseParser.__init__(self, web_content, logger)

    def parse(self):
        html_soup = BeautifulSoup(self._web_content, 'html.parser')
        try:
            app_icon_img_item = html_soup.find('div', {"class": "cover-container"}).find('img', {"class": "cover-image"})
            if app_icon_img_item:
                app_icon_url = app_icon_img_item.get('src')
                if app_icon_url:
                    app_icon_url = app_icon_url.strip()
                    if not app_icon_url.startswith('https'):
                        app_icon_url = 'https:%s' % app_icon_url
                    self.app_detail.app_icon_url = app_icon_url
        except Exception:
            self.logger.exception('Parse app icon error')

        try:
            self.app_detail.app_name = html_soup.find('div', {"class": "details-info"})\
                .find('div', {"class": "id-app-title"}).text.strip()
        except Exception:
            self.logger.exception('Parse app name error')

        try:
            developer_name = html_soup.find('div', itemprop="author").find('a', {"class": "document-subtitle primary"}).find(
                'span', itemprop="name").text.strip()
        except Exception:
            developer_name = ''
        self.app_detail.developer_name = developer_name

        try:
            developer_link = html_soup.find('a', {"class": "document-subtitle primary"})
            if developer_link:
                developer_link = developer_link.get('href', '').strip()
                self.app_detail.developer_link = developer_link
        except Exception:
            self.logger.exception('Parse developer link error')

        try:
            genres = html_soup.find_all('a', {"class": "document-subtitle category"})
            for genre in genres:
                self.app_detail.genres.append(genre.text.strip())
        except Exception:
            self.logger.exception('Parse genres error')

        try:
            screenshot_items = html_soup.find_all('img', {"class": "screenshot"})
            for screenshot_item in screenshot_items:
                img_url = screenshot_item.get('src', '').strip()
                if not img_url.startswith('https'):
                    img_url = 'https:%s' % img_url
                img_title = screenshot_item.get('title', '').strip()
                self.app_detail.screenshots.append(Screenshot(img_url, img_title))
        except Exception:
            self.logger.exception('Parse screenshots error')

        try:
            description_items = html_soup.find_all('div', itemprop="description")
            for description_item in description_items:
                self.app_detail.description.append(description_item.get_text().strip())
        except Exception:
            self.logger.exception('Parse description items error')

        try:
            review_num = html_soup.find('span', {"class": "reviews-num"})
            if review_num:
                review_num = review_num.text.strip()
                score = html_soup.find('div', {"class": "score"}).text.strip()
                one_star = html_soup.find('div', {"class": "rating-bar-container one"}).find('span', {
                    "class": "bar-number"}).text.strip()
                two_star = html_soup.find('div', {"class": "rating-bar-container two"}).find('span', {
                    "class": "bar-number"}).text.strip()
                three_star = html_soup.find('div', {"class": "rating-bar-container three"}).find('span', {
                    "class": "bar-number"}).text.strip()
                four_star = html_soup.find('div', {"class": "rating-bar-container four"}).find('span', {
                    "class": "bar-number"}).text.strip(),
                five_star = html_soup.find('div', {"class": "rating-bar-container five"}).find('span', {
                    "class": "bar-number"}).text.strip()
                review = Review(score, review_num, one_star, two_star, three_star, four_star, five_star)
                self.app_detail.review = review
        except Exception:
            self.logger.exception('Parse app review error')

        try:
            self.app_detail.update_date = html_soup.find('div', itemprop="datePublished").text.strip()
        except Exception:
            self.logger.exception('Parse app update date error')

        try:
            installs_count = html_soup.find('div', itemprop="numDownloads")
            if installs_count:
                self.app_detail.installs_count = installs_count.text.strip()
        except Exception:
            self.logger.exception('Parse app installs count error')
