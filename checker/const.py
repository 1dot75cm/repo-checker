# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os


class Constant(object):
    conf_dir = os.path.join(os.path.expanduser('~'), '.repo-checker')
    log_path = os.path.join(conf_dir, 'checker.log')
