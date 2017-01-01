# -*- coding: utf-8 -*-
'''
Repo Checker Entry
'''

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

try:
    from PyQt5.QtWidgets import QApplication
except:
    from PyQt4.QtGui import QApplication

import argparse
import sys


__url__ = "https://github.com/1dot75cm/repo-checker"
__version__ = "0.1.0"
__license__ = "MIT"
__descript__ = "A graphical user interface version checker tool for open source project."
__author__ = "mosquito"
__email__ = "sensor.wen@gmail.com"


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
    args = parser.parse_args()

    if args.version:
        print('repo-checker installed version: %s' % __version__)

    elif args.cli:  # TODO: build command line interface
        pass

    elif args.gui:
        start_gui()

    sys.exit()


def start_gui():
    from .gui import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    helper()


if __name__ == '__main__':
    main()
