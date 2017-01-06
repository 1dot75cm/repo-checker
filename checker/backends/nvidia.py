# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger
import re

log = logger.getLogger(__name__)


class NvidiaBackend(BaseBackend):
    """for projects hosted on nvidia.com"""

    name = 'NVIDIA'
    domain = 'nvidia.com'
    example = 'http://http.download.nvidia.com/XFree86/Linux-x86_64'

    def __init__(self, url):
        super(NvidiaBackend, self).__init__()
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
