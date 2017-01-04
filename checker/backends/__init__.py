# -*- coding: utf-8 -*-


class BaseBackend(object):
    """base class"""

    name = None
    url = None

    @classmethod
    def get_urls(cls, url, branch):
        pass  # return [release url, latest url]

    @classmethod
    def get_rules(cls, url):
        pass  # return [(release date, commit), (latest date, commit)]

    @classmethod
    def isrelease(cls, url):
        pass  # return bool

    def __repr__(self):
        return "<%s [%s]>" % (self.__name__, self.name)
