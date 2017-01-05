# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class PagureBackend(BaseBackend):
    """for projects hosted on pagure.io"""

    name = 'Pagure'
    domain = 'pagure.io'
    example = 'https://pagure.io/pagure'

    def __init__(self, url):
        super(PagureBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return ['https://releases.pagure.org/%s/' % self._url.split('/')[-1],
                '%s/commits/%s' % (self._url, branch)]

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("//td[3][contains(text(), '-')]/text()", ""),
                ("//h5/a//span/@title", "//div[1]/h5/a/@href")]

    @classmethod
    def isrelease(cls, url):
        if cls.domain in url and 'commits' in url:
            return False
        else:
            return True
