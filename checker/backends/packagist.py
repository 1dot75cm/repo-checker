# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class PackagistBackend(BaseBackend):
    """for projects hosted on packagist.org"""

    name = 'Packagist'
    domain = 'packagist.org'
    example = 'https://packagist.org/packages/phpunit/php-code-coverage'

    def __init__(self, url):
        super(PackagistBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        # https://packagist.org/p/%(user)s/%(name)s.json
        return self._url,

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("//span[@class='release-date']/text()",
                 "//span[@class='source-reference']/text()"), ("", "")]

    @classmethod
    def isrelease(cls, url):
        return True
