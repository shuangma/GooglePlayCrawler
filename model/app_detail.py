#!/usr/bin/env python
# -*- coding: utf-8 -*-


class AppDetail:
    def __init__(self):
        self.package_name = ''
        self.app_name = ''
        self.developer_name = ''
        self.developer_link = ''
        self.genres = []
        self.app_icon_url = ''
        self.screenshots = []
        self.description = []
        self.review = None
        self.update_date = ''
        self.installs_count = ''

    def to_json(self):
        return {'package_name': self.package_name,
                'app_name': self.app_name,
                'developer_name': self.developer_name,
                'developer_link': self.developer_link,
                'genres': self.genres,
                'app_icon_url': self.app_icon_url,
                'screenshots': [screenshot.to_json() for screenshot in self.screenshots],
                'description': self.description,
                'review': None if not self.review else self.review.to_json(),
                'update_date': self.update_date,
                'installs_count': self.installs_count}


class Screenshot:
    def __init__(self, img_url, img_title):
        self.img_url = img_url
        self.img_title = img_title

    def to_json(self):
        return {'img_url': self.img_url,
                'img_title': self.img_title}


class Review:
    def __init__(self, score, review_num, one_star, two_star, three_star, four_star, five_star):
        self.score = score
        self.review_num = review_num
        self.one_star = one_star
        self.two_star = two_star
        self.three_star = three_star
        self.four_star = four_star
        self.five_star = five_star

    def to_json(self):
        return {'score': self.score,
                'review_num': self.review_num,
                'one_star': self.one_star,
                'two_star': self.two_star,
                'three_star': self.three_star,
                'four_star': self.four_star,
                'five_star': self.five_star}

