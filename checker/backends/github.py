# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class GithubBackend(BaseBackend):
    """for projects hosted on github.com"""

    name = 'Github'
    url = 'github.com'

    @classmethod
    def get_urls(cls, url=None, branch=None):
        if cls.url in url:
            return [url + '/releases', url + '/commits/' + branch]
        else:
            return False

    @classmethod
    def get_rules(cls, url):
        if cls.url in url:
            log.debug('use %s backend rule for %s package.' %
                      (cls.name, url.split('/')[-1]))
            return [("//li[1]//relative-time/@datetime",
                     "//li[1]//li[1]/a/@href"),
                    ("//ol[1]/li[1]/div[2]//relative-time/@datetime",
                     "//ol[1]/li[1]/div[3]/div/a/@href")]
        else:
            return False

    @classmethod
    def isrelease(cls, url):
        if cls.url in url and 'releases' in url:
            return True
        else:
            return False
