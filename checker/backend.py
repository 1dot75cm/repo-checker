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
        modules_file = [b for b in os.listdir(Constant.backend_dir)
                        if re.search('^[a-zA-Z0-9].*.py$', b)]
        modules_file.extend([b for b in os.listdir(Constant.user_backend_dir)
                             if re.search('^[a-zA-Z0-9].*.py$', b)])

        for module_file in modules_file:
            try:
                module_name = module_file.replace('.py', '')  # github
                module_path = os.path.join(Constant.backend_dir, module_file)
                module = imp.load_source(module_name, module_path)
                backend_name = module.__name__.capitalize()  # Github
                self._backends[module_name] = module.__dict__['%sBackend' % backend_name]
                log.debug('detect backend: %s.' % backend_name)
            except:
                log.exception('detect a bad plugin %s' % module_name)

    def get_backends(self):
        return self._backends

    def get_backend(self, url):
        if not url:
            return False  # 无url

        for back in self._backends.values():
            if back.domain in url:
                return back(url)  # 初始化后端实例，保存url

        return False  # 未匹配后端
