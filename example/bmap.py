#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @mail: sensor.wen@gmail.com
# @date: Mar 3, 2016
# @reference: http://www.oschina.net/code/snippet_90475_9224
#

import sys
import time
import json
import urllib.request
import urllib.parse

class BaiduMap:
    """ get baidu map infomation.
    """
    def __init__(self, keyword):
        self.keyword = keyword
        self.query = [
                ('newmap', '1'),
                ('from', 'webmap'),
                ('qt', 's'),
                ('wd', keyword),
                ('wd2', ''),
                ('c', '1'),
                ('b', '(-1599062.039999999,811604.75;24779177.96,8168020.75)'),
                ('tn', 'B_NORMAL_MAP'),
                ('ie', 'utf-8'),
                ('t', time.time().__int__()),
                 ]
        self.mapurl = 'http://map.baidu.com/'
        self.file = open('{}.txt'.format(keyword), 'w')
        self.count = 0
        self.count_c = 0
        self.total_num = 0
        self._get_city()

    def _fetch(self, query=None, json=True):
        data = urllib.parse.urlencode(query)
        url = self.mapurl + '?' + data
        opener = urllib.request.FancyURLopener()
        data = opener.open(url).read()

        if json:
            return self._tojson(data.decode())
        else:
            return data.decode()

    def _tojson(self, data):
        try:
            js = json.loads(data, 'utf-8')
        except:
            js = None

        return js

    def _get_city(self):
        data = self._fetch(self.query)

        if type(data['content']) is not list:
            print('keyworld error.')
            sys.exit()

        self.city = data['content']

        if 'more_city' in data:
            for c in data['more_city']:
                self.city.extend(c['city'])

        for city in self.city:
            self.total_num += city['num']

    def _get_data(self, city, page=0):
        query = [
                ('newmap', '1'),
                ('from', 'webmap'),
                ('qt', 'con'),
                ('wd', self.keyword),
                ('wd2', ''),
                ('c', city['code']),
                ('pn', page),
                ('b', '(%s)' % city['geo'].split('|')[1]),
                ('tn', 'B_NORMAL_MAP'),
                ('ie', 'utf-8'),
                ('t', time.time().__int__()),
                 ]

        data = self._fetch(query)
        return data

    def _save(self, content, city):
        for c in content:
            self.count += 1
            self.count_c += 1
            if 'tel' in c:
                tel = c['tel']
            else:
                tel = ''

            _data = '{},{},{},{}\n'.format(city['name'], c['name'], c['addr'], tel)
            self.file.write(_data)
            print('({}/{}) {}[{}/{}]'.format(self.count, self.total_num, city['name'], self.count_c, city['num']))

    def get(self, city):
        self.count_c = 0
        pages = abs(-city['num'] // 10)
        for page in range(0, pages):
            data = self._get_data(city, page)
            if 'content' in data:
                self._save(data['content'], city)

    def get_all(self):
        for city in self.city:
            self.get(city)

        self.file.close()


if __name__ == '__main__':
    if sys.argv.__len__() > 1:
        keyword = sys.argv[1]
    else:
        keyword = '酒店'

    baidumap = BaiduMap(keyword)
    print('_' * 20)
    print('City: {}'.format(baidumap.city.__len__()))
    print('Data: {}'.format(baidumap.total_num))
    print('(当前/总数) 城市 [当前/总数(城市)]')
    baidumap.get_all()

