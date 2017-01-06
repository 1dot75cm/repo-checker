# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger
import re

log = logger.getLogger(__name__)


class OperaBackend(BaseBackend):
    """for projects hosted on opera.com"""

    name = 'Opera'
    domain = 'opera.com'
    example = 'http://ftp.opera.com/pub/opera/desktop/'

    def __init__(self, url):
        super(OperaBackend, self).__init__()
        self._url = url
        self._rule_type = "regex"

    def get_urls(self, branch=None):
        return self._url,

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("\d{2}-\w{3}-\d{4}", ""), ("", "")]

    def _post_regex(self, rules):
        log.debug("rules: %s, %s" % (rules[0], rules[1]))
        time = re.findall(rules[0], self.resp.text)
        return self._process_data(time), "none"  # (date, commit)

    @classmethod
    def isrelease(cls, url):
        return True
