# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class GnomeBackend(BaseBackend):
    """for projects hosted on gnome.org"""

    name = 'Gnome'
    domain = 'gnome.org'
    example = 'https://download.gnome.org/sources/gnome-control-center'

    def __init__(self, url):
        super(GnomeBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return self._url,

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("//tr/td[3][contains(text(), '-')]/text()", ""), ("", "")]

    @classmethod
    def isrelease(cls, url):
        return True
