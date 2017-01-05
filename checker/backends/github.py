# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class GithubBackend(BaseBackend):
    """for projects hosted on github.com"""

    name = 'Github'
    domain = 'github.com'
    example = 'https://github.com/atom/atom'

    def __init__(self, url):
        super(GithubBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return [self._url + '/tags', self._url + '/commits/' + branch]

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("//tr[1]/td[1]//relative-time/@datetime",
                 "//tr[1]/td[2]//li[1]/a/@href"),
                ("//ol[1]/li[1]/div[2]//relative-time/@datetime",
                 "//ol[1]/li[1]/div[3]/div/a/@href")]

    @classmethod
    def isrelease(cls, url):
        if cls.domain in url and 'tags' in url:
            return True
        else:
            return False
