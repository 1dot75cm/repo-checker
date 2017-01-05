# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class PypiBackend(BaseBackend):
    """for projects hosted on pypi.python.org"""

    name = 'PyPI'
    domain = 'pypi.python.org'
    example = 'https://pypi.python.org/pypi/arrow'

    def __init__(self, url):
        super(PypiBackend, self).__init__()
        self._url = url
        self._rule_type = "json"

    def get_urls(self, branch=None):
        return [self._url + '/json']

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("['release']['version']", ""), ("", "")]

    def _post_json(self, rules):
        log.debug("rules: %s, %s" % (rules[0], rules[1]))
        version = self.resp.json()['info']['version']
        time = self.resp.json()['releases'][version][0]['upload_time']
        return self._process_data(time), "none"  # (date, commit)

    @classmethod
    def isrelease(cls, url):
        return True
