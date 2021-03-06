# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class Arch_cgitBackend(BaseBackend):
    """for projects hosted on archlinux.org"""

    name = 'Arch CGit'
    domain = 'git.archlinux.org'
    example = 'https://git.archlinux.org/pacman.git'

    def __init__(self, url):
        super(Arch_cgitBackend, self).__init__()
        self._url = url
        self._rule_type = "xpath"

    def get_urls(self, branch=None):
        return [self._url, self._url + '/log/']

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("substring(//div[@class='content']//tr[@class='nohover'][3]/following::*/td[4]/span/@title, 1, 19)", ""),
                ("substring(//tr[2]/td[1]/span/@title, 1, 19)",
                 "//tr[2]/td[2]/a/@href")]

    @classmethod
    def isrelease(cls, url):
        if cls.domain in url and 'log' in url:
            return False
        else:
            return True
