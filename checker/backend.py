# -*- coding: utf-8 -*-

import os
import re
import imp

from . import logger
from .const import Constant

log = logger.getLogger(__name__)


class BackendManager(object):
    """管理后端模块"""

    def __init__(self):
        self._backends = {}
        self.scan()

    def scan(self):
        modules_name = [b for b in os.listdir(Constant.backend_dir)
                        if re.search('^[a-zA-Z0-9].*.py$', b)]

        for module_name in modules_name:
            try:
                module_path = os.path.join(Constant.backend_dir, module_name)
                module = imp.load_source(module_name.replace('.py', ''), module_path)
                backend_name = module.__name__.capitalize()
                self._backends[backend_name] = module.__dict__['%sBackend' % backend_name]
                log.debug('detect backend: %s.' % backend_name)
            except:
                log.exception('detect a bad plugin %s' % module_name)

    def get_backends(self):
        return self._backends
