# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class WpsBackend(BaseBackend):
    """for projects hosted on wps-community.org"""

    name = 'WPS Community'
    domain = 'wps-community.org'
    example = 'http://wps-community.org/downloads'

    def __init__(self, url):
        super(WpsBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return self._url,

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, 'wps-office'))
        return [("substring(//h2/small/text(), 2, 10)", ""), ("", "")]

    @classmethod
    def isrelease(cls, url):
        return True
