# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class CustomBackend(BaseBackend):
    """processes items that don't match backend"""

    name = 'Custom'
    domain = 'Dont_Match_Backend.org'

    def __init__(self, url):
        super(CustomBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"  # default type

        if self._url:
            log.debug('use %s backend for %s package.' %
                      (self.name, self._url.split('/')[-1]))

    def get_urls(self, branch=None):
        pass

    def get_rules(self):
        pass

    @classmethod
    def isrelease(cls, url):
        return True
