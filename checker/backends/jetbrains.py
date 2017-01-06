# -*- coding: utf-8 -*-

from checker.backends import BaseBackend
from checker import logger

log = logger.getLogger(__name__)


class JetbrainsBackend(BaseBackend):
    """for projects hosted on jetbrains.com"""

    name = 'JetBrains'
    domain = 'www.jetbrains.com'
    example = 'https://www.jetbrains.com/idea/'
    p = {   # product
        'idea': 'IIC',  # IIU
        'pycharm-edu': 'PCC',
        'pycharm': 'PCP',
        'phpstorm': 'PS',
        'webstorm': 'WS',
        'ruby': 'RM',
        'objc': 'AC',
        'clion': 'CL',
        'datagrip': 'DG',
        'rider': 'RD'
    }

    def __init__(self, url):
        super(JetbrainsBackend, self).__init__()
        self._url = url
        self._rule_type = "json"

        if self.domain in self._url:
            self.pk = [self.p[i] for i in self.p.keys()
                                    if i in self._url][0]  # product key

    def get_urls(self, branch=None):
        json_url = 'https://data.services.jetbrains.com/products/releases' \
                   '?code=%(code)s&latest=true&type=%(branch)s'
        return json_url % {'code': self.pk, 'branch': branch},  # release|eap

    def get_rules(self):
        log.debug('use %s backend rule for %s package.' %
                  (self.name, self._url.split('/')[-1]))
        return [("['%s'][0]['date']" % self.pk, ""), ("", "")]

    def _post_json(self, rules):
        log.debug("rules: %s, %s" % (rules[0], rules[1]))
        time = eval("self.resp.json()%s" % rules[0])
        return self._process_data(time), "none"  # (date, commit)

    @classmethod
    def isrelease(cls, url):
        return True
