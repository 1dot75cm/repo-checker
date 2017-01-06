# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import logging

from .const import Constant


FILE_NAME = Constant.user_log_path
if not os.path.isdir(Constant.user_conf_dir):
    os.mkdir(Constant.user_conf_dir)

if not os.path.isdir(Constant.user_backend_dir):
    os.mkdir(Constant.user_backend_dir)

with open(FILE_NAME, 'a+') as f:
    f.write('#' * 80)
    f.write('\n')


def getLogger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # File output handler
    fh = logging.FileHandler(FILE_NAME)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s:%(lineno)s: %(message)s'))  # NOQA
    log.addHandler(fh)

    return log
