# -*- coding: utf-8 -*-

try:
    from ConfigParser import ConfigParser  # Python 2
    from ConfigParser import _Chainmap
    class ChainMap(_Chainmap, object):
        def __init__(self, *args):
            super(ChainMap, self).__init__(*args)
            self.maps = [mapping for mapping in self._maps]
except:
    from configparser import ConfigParser  # Python 3
    from collections import ChainMap

from .const import Constant
from . import logger

log = logger.getLogger(__name__)


class Config(object):

    defaults = {
        'version': False,
        'cli': False,
        'gui': True,
        'lang': '',
        'proxy': {'https': '', 'http': ''},
        'worker_num': Constant.worker_num,
        'retry': Constant.retry,
        'retry_time': Constant.retry_time
    }
    _bool = {
        'True': 1, 'enable': 1, 'yes': 1, 'on': 1, '1': 1,
        'False': 0, 'disable': 0, 'no': 0, 'off':0, '0': 0, 'None': 0
    }
    _cp = ConfigParser()
    file = {}  # config file arguments
    cli = {}  # cli arguments
    runtime = {}  # load config from gui
    opts = ChainMap(runtime, cli, file, defaults)

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
    def load_config(cls, mode='runtime', **kwargs):
        """从配置文件或命令行载入配置"""

        if mode is 'file':
            if cls._cp.read(Constant.user_conf_file):
                _dt = {k: cls._bool.get(v, v) for k, v in cls._cp.items('main')}
                cls.file.update({k: cls._int(v) for k, v in _dt.items() if v})

                if cls.file.get('proxy'):
                    cls.file['proxy'] = {'https': cls.file.get('proxy', ''),
                                         'http': cls.file.get('proxy', '')}

        elif mode is 'cli':
            cls.cli.update({k: cls._int(v) for k, v in kwargs.items() if v})

            if cls.cli.get('proxy'):
                cls.cli['proxy'] = {'https': cls.cli.get('proxy', ''),
                                    'http': cls.cli.get('proxy', '')}

        elif mode is 'runtime':
            log.debug('update config: %s' % kwargs)
            cls.runtime.update({k: cls._int(v) for k, v in kwargs.items() if v})

            if cls.runtime.get('proxy'):
                cls.runtime['proxy'] = {'https': cls.runtime.get('proxy', ''),
                                        'http': cls.runtime.get('proxy', '')}

    @classmethod
    def save_config(cls):
        """保存配置"""
        if not cls._cp.has_section('main'):
            cls._cp.add_section('main')

        for k, v in cls.opts.items():
            val = str(cls._bool.get(str(v), v))
            if isinstance(v, dict):
                val = v['http']
            cls._cp.set('main', k, val)

        cls._cp.write(open(Constant.user_conf_file, 'w'))
        log.debug('saved config: %s' % cls._cp.items('main'))

    @staticmethod
    def _int(value):
        try:
            return int(value)
        except ValueError:
            return value


config = Config()
