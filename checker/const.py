# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
from pkg_resources import get_entry_info
from . import __pkgname__


class Constant(object):
    own = get_entry_info(__pkgname__, 'console_scripts', 'checker')
    base_dir = os.path.join(own.dist.location)
    locale_dir = os.path.join(base_dir, own.module_name, 'locale')

    conf_dir = os.path.join(os.path.expanduser('~'), '.repo-checker')
    log_path = os.path.join(conf_dir, 'checker.log')
