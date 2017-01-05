# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class SourceforgeBackend(BaseBackend):
    """for projects hosted on sourceforge.net"""

    name = 'Sourceforge'
    domain = 'sourceforge.net'
    example = 'https://sourceforge.net/projects/filezilla'

    def __init__(self, url):
        super(SourceforgeBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return [self._url + '/rss?limit=10']

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("//item/pubdate/text()", ""), ("", "")]

    @classmethod
    def isrelease(cls, url):
        return True
