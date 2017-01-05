# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class LaunchpadBackend(BaseBackend):
    """for projects hosted on launchpad.net"""

    name = 'Launchpad'
    domain = 'launchpad.net'
    example = 'https://launchpad.net/terminator'

    def __init__(self, url):
        super(LaunchpadBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return [self._url + '/+download', self._url.replace('launch', 'code.launch')]

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("substring(//h3/span/@title, 1, 19)", ""),
                ("//tr[1]/td[4]/span[2]/@title", "")]

    @classmethod
    def isrelease(cls, url):
        if cls.domain in url and '+download' in url:
            return True
        else:
            return False
