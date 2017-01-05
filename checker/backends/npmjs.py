# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class NpmjsBackend(BaseBackend):
    """for projects hosted on npmjs.com"""

    name = 'Npmjs'
    domain = 'npmjs.com'
    example = 'https://www.npmjs.com/package/request'

    def __init__(self, url):
        super(NpmjsBackend, self).__init__()
        self._url = url
        self._rule_type = "json"

    def get_urls(self, branch=None):
        return ['http://registry.npmjs.org/' + self._url.split('/')[-1]]

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("['dist-tags']['latest']", ""), ("", "")]

    def _post_json(self, rules):
        log.debug("rules: %s, %s" % (rules[0], rules[1]))
        version = self.resp.json()['dist-tags']['latest']
        time = self.resp.json()['time'][version]
        return self._process_data(time), "none"  # (date, commit)

    @classmethod
    def isrelease(cls, url):
        return True
