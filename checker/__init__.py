# -*- coding: utf-8 -*-
'''
Repo Checker Entry
'''

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import sip
sip.setapi("QString", 2)

try:
    from PyQt5.QtCore import QTranslator
    from PyQt5.QtWidgets import QApplication
except:
    from PyQt4.QtCore import QTranslator
    from PyQt4.QtGui import QApplication

from .const import Constant
from .backend import BackendManager
from .config import config
from . import logger

import argparse
import sys
import locale


__pkgname__ = "repo-checker"
__version__ = "0.3.0"
__license__ = "MIT"
__url__ = "https://github.com/1dot75cm/repo-checker"
__descript__ = "A graphical user interface version checker for open source project."
__author__ = "mosquito"
__email__ = "sensor.wen@gmail.com"


# load backends
backmgr = BackendManager()

# log
log = logger.getLogger(__name__)


def helper():
    parser = argparse.ArgumentParser(description=__descript__)
    parser.add_argument("-v", "--version", dest="version",
                        help="show this version and exit",
                        action="store_true")
    parser.add_argument("-c", "--cli", dest="cli",
                        help="run as command line interface",
                        action="store_true")
    parser.add_argument("-g", "--gui", dest="gui",
                        help="run as graphical user interface (default)",
                        action="store_true", default=True)
    parser.add_argument("-l", "--lang", dest="lang",
                        help="run as specific language",
                        action="store", default=locale.getlocale()[0])
    parser.add_argument("-p", "--proxy", dest="proxy", metavar="scheme://host[:port]",
                        help="use proxy for network access",
                        action="store", default="")
    args = parser.parse_args()
    config.load_config(mode="cli", **args.__dict__)
    log.debug('current config[runtime, cli, file, defualts]: %s' % config().maps)

    if config['version']:
        print('repo-checker installed version: %s' % __version__)

    elif config['cli']:  # TODO: build command line interface
        pass

    elif config['gui']:
        start_gui()

    sys.exit()


def start_gui():
    from .frontends import MainWindow

    app = QApplication(sys.argv)
    trans = QTranslator()
    trans.load(config['lang'], Constant.locale_dir)
    app.installTranslator(trans)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    helper()


if __name__ == '__main__':
    main()
