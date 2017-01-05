# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class BitbucketBackend(BaseBackend):
    """for projects hosted on bitbucket.org"""

    name = 'Bitbucket'
    domain = 'bitbucket.org'
    example = 'https://bitbucket.org/zzzeek/sqlalchemy'

    def __init__(self, url):
        super(BitbucketBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return [self._url + '/downloads?tab=tags', self._url + '/commits/branch/' + branch]

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("id('tag-pjax-container')//tr[1]/td[3]//@datetime",
                 "id('tag-pjax-container')//tr[1]/td[2]/a/@href"),
                ("id('chg_1')/td[4]/div/time/@datetime",
                 "id('chg_1')/td[2]/div/a/@href")]

    @classmethod
    def isrelease(cls, url):
        if cls.domain in url and 'downloads' in url:
            return True
        else:
            return False
