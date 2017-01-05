# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class RubygemsBackend(BaseBackend):
    """for projects hosted on rubygems.org"""

    name = 'Rubygems'
    domain = 'rubygems.org'
    example = 'https://rubygems.org/gems/bio'

    def __init__(self, url):
        super(RubygemsBackend, self).__init__()
        self._url = url
        self._rule_type = "json"

    def get_urls(self, branch=None):
        return ['http://rubygems.org/api/v1/versions/%(name)s.json' % {
                'name': self._url.split('/')[-1]}]

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("['created_at']", ""), ("", "")]

    def _post_json(self, rules):
        log.debug("rules: %s, %s" % (rules[0], rules[1]))
        times = [i['created_at'] for i in self.resp.json()]
        return self._process_data(times), "none"  # (date, commit)

    @classmethod
    def isrelease(cls, url):
        return True
