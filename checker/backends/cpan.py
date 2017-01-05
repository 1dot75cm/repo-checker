# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class CpanBackend(BaseBackend):
    """for projects hosted on cpan.org"""

    name = 'CPAN'
    domain = 'cpan.org'
    example = 'http://search.cpan.org/dist/perl'

    def __init__(self, url):
        super(CpanBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return [self._url]

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("//div[3]//tr[1]/td[4]/small/text()", ""), ("", "")]

    @classmethod
    def isrelease(cls, url):
        return True
