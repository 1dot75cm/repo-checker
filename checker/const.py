# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
from pkg_resources import get_entry_info


class Constant(object):
    own = get_entry_info('repo-checker', 'console_scripts', 'checker')
    base_dir = os.path.join(own.dist.location)
    locale_dir = os.path.join(base_dir, own.module_name, 'locale')
    backend_dir = os.path.join(base_dir, own.module_name, 'backends')

    user_conf_dir = os.path.join(os.path.expanduser('~'), '.repo-checker')
    user_log_path = os.path.join(user_conf_dir, 'checker.log')
    user_backend_dir = os.path.join(user_conf_dir, 'backends')

    worker_num = 5
