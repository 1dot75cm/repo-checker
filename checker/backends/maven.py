# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger
import re

log = logger.getLogger(__name__)


class MavenBackend(BaseBackend):
    """for projects hosted on maven.org"""

    name = 'Maven'
    domain = 'maven.org'
    example = 'http://repo1.maven.org/maven2/com/google/inject/guice/'

    def __init__(self, url):
        super(MavenBackend, self).__init__()
        self._url = url
        self._rule_type = "regex"

    def get_urls(self, branch=None):
        return self._url,

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("\d{4}-\d{2}-\d{2}", ""), ("", "")]

    def _post_regex(self, rules):
        log.debug("rules: %s, %s" % (rules[0], rules[1]))
        pattern = '\d{4}-\d{2}-\d{2}'
        time = re.findall(pattern, self.resp.text)
        return self._process_data(time), "none"  # (date, commit)

    @classmethod
    def isrelease(cls, url):
        return True
