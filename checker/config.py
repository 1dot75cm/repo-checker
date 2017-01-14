# -*- coding: utf-8 -*-

try:
    from ConfigParser import ConfigParser  # Python 2
except:
    from configparser import ConfigParser  # Python 3

from collections import ChainMap
from const import Constant


class Config(object):

    defaults = {
        'version': False,
        'cli': False,
        'gui': True,
        'lang': ''
    }
    _bool = {
        'True': 1, 'enable': 1, 'yes': 1, 'on': 1, '1': 1,
        'False': 0, 'disable': 0, 'no': 0, 'off':0, '0': 0
    }
    file = {}  # config file arguments
    cli = {}  # cli arguments
    opts = ChainMap(cli, file, defaults)

    def __init__(self):
        self.load_config(mode='file')
        # 从dir读取配置文件 checker.ini
        # 命令行参数优先于配置文件参数

    def __call__(self):
        return self.opts

    def __getitem__(self, key):
        return self.opts.get(key)

    def get(self, key, default=None):
        return self.opts.get(key, default)

    @classmethod
    def load_config(cls, mode='cli', **kwargs):
        """从配置文件或命令行载入配置"""

        if mode is 'file':
            config = ConfigParser()

            if config.read(Constant.user_conf_file):
                _dt = {k: cls._bool.get(v, v) for k, v in config.items('main')}
                cls.file.update({k: v for k, v in _dt.items() if v})

        elif mode is 'cli':
            cls.cli.update({k: v for k, v in kwargs.items() if v})

    @classmethod
    def save_config(cls):
        pass


config = Config()
