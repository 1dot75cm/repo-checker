# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from dateutil.parser import parse
from lxml import etree
import requests
import time
import six
import re

from .. import logger
from ..const import Constant

log = logger.getLogger(__name__)
session = requests.session()


@six.add_metaclass(ABCMeta)
class BaseBackend(object):
    """base class"""

    name = None
    domain = None

    def __init__(self):
        pass

    @abstractmethod
    def get_urls(self, branch):
        pass  # return [release url, latest url]

    @abstractmethod
    def get_rules(self):
        pass  # return [(release date, commit), (latest date, commit)]

    @classmethod
    @abstractmethod
    def isrelease(cls, url):
        pass  # return bool

    @staticmethod
    def get(url, **kwargs):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'
        }
        return session.get(url, headers=headers, **kwargs)

    def extract_info(self, url, rules):
        """根据规则, 提取更新信息"""
        for i in range(Constant.retry):
            try:
                self.resp = self.get(url)
                if self.resp.ok:
                    break
            except Exception as e:
                log.debug("network error[%s]: %s" % (self.name, e))
                time.sleep(Constant.retry_time * (i + 1))
                if i == Constant.retry - 1:
                    return ("error", "error")  # 网络错误

        if self._rule_type == "xpath":
            return self._post_xpath(rules)

        elif self._rule_type == "json":
            return self._post_json(rules)

        elif self._rule_type == "regex":
            return self._post_regex(rules)

    def _post_xpath(self, rules):
        """对数据进行后处理"""
        _data = []
        log.debug("rules: %s, %s" % (rules[0], rules[1]))
        tree = etree.HTML(self.resp.content)

        for rule in rules:
            if not rule:
                _data.append("none")  # 无规则
                break

            try:
                log.debug("match: %s" % tree.xpath(rule)[0])
                _data.append(self._process_data(tree.xpath(rule)))
            except IndexError:
                _data.append("error")  # 规则匹配错误

        return _data  # (date, commit)

    def _post_json(self, rules):
        """对数据进行后处理"""
        pass

    def _post_regex(self, rules):
        """对数据进行后处理"""
        pass

    @staticmethod
    def _process_data(data):
        """处理数据"""
        try:
            if isinstance(data, (list, tuple)):
                dt = sorted([parse(i) for i in data], reverse=True)[0]
            else:
                dt = parse(data)
            return str(int(time.mktime(dt.timetuple())))  # int(dt.timestamp())
        except ValueError:
            return re.search('[a-z0-9]{12,40}', data[0]).group()[:7]  # commit
        except IndexError:  # no data
            return ""

    def __repr__(self):
        return "<%s [%s]>" % (self.__name__, self.name)
