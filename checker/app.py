# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from datetime import datetime
import time

from . import logger
from . import backmgr
from .backends.custom import CustomBackend

log = logger.getLogger(__name__)


class Checker(object):
    mktimestamp = lambda _, ts: str(int(time.mktime(
        datetime.strptime(str(ts), "%y%m%d").timetuple())))

    def __init__(self, item=None):
        if isinstance(item, list):  # csv
            self.name = item[2]
            self.url = item[3]
            self.branch = item[4]
            self.rpm_commit = item[5]
            self.rpm_date = self.mktimestamp(item[6])
            self.rules = [("", ""), ("", "")]
            self.comment = ""

        else:  # json
            self.name = item["name"] if item else ""
            self.url = item["url"] if item else ""
            self.branch = item["branch"] if item else ""
            self.rpm_date = item["rpm_date"] if item else "none"
            self.rpm_commit = item["rpm_commit"] if item else "none"
            self.rules = item["rules"] if item else [("", ""), ("", "")]
            self.comment = item["comment"] if item else ""

        self.release_date = "none"
        self.release_commit = "none"
        self.latest_date = "none"
        self.latest_commit = "none"
        self.status = "none"
        self.check_date = ""

        self.isbackend = backmgr.get_backend(self.url)
        self.backend = self.isbackend if self.isbackend else CustomBackend(self.url)

    def ctime(self, timestamp):
        """Convert time format"""
        if len(str(timestamp)) == 10:
            # timestamp -> string
            return datetime.fromtimestamp(float(timestamp))\
                           .strftime("%y%m%d")
        elif len(str(timestamp)) == 6:
            # string -> timestamp
            return self.mktimestamp(timestamp)
        else:
            return timestamp

    def dump_meta(self, dump_type="rpm"):
        """导出时间/提交信息"""
        if dump_type == "rpm":
            return "%s [%s]" % (self.ctime(self.rpm_date), self.rpm_commit)
        elif dump_type == "release":
            return "%s [%s]" % (self.ctime(self.release_date), self.release_commit)
        elif dump_type == "latest":
            return "%s [%s]" % (self.ctime(self.latest_date), self.latest_commit)

    def load_meta(self, data, load_type="rpm"):
        """导入时间/提交信息"""
        try:
            if load_type == "rpm":
                self.rpm_date = self.ctime(data.split()[0])
                self.rpm_commit = data.split()[1][1:-1]
            elif load_type == "release":
                self.release_date = self.ctime(data.split()[0])
                self.release_commit = data.split()[1][1:-1]
            elif load_type == "latest":
                self.latest_date = self.ctime(data.split()[0])
                self.latest_commit = data.split()[1][1:-1]
        except ValueError:
            pass

    def load(self, column, value):
        """按列导入项"""
        if column == 0:
            self.name = value
        elif column == 1:
            self.url = value
        elif column == 2:
            self.branch = value
        elif column == 3:
            self.load_meta(value)
        elif column == 4:
            self.load_meta(value, "release")
        elif column == 5:
            self.load_meta(value, "latest")
        elif column == 6:
            self.status = value
        elif column == 7:
            self.comment = value
        else:
            self.rules = value

    def dump(self, mode="human"):
        """输出对象信息"""
        if mode == "human":
            return (self.name, self.url, self.branch,
                    self.dump_meta(), self.dump_meta("release"),
                    self.dump_meta("latest"), self.status, self.comment)

        elif mode == "raw":
            return dict(
                name=self.name,
                url=self.url,
                branch=self.branch,
                rpm_date=self.rpm_date,
                rpm_commit=self.rpm_commit,
                rules=self.rules,
                comment=self.comment
            )

    def get_urls(self):
        """获取 url 列表"""
        if self.isbackend:
            return self.backend.get_urls(self.branch)

        return [self.url]

    def get_rules(self, ui=False):
        """获取 xpath 规则"""
        if self.rules[0][0]:
            return self.rules

        elif not ui:
            if self.isbackend:
                return self.backend.get_rules()

        return [("", ""), ("", "")]  # ui show this

    def set_rules(self, rules):
        """设置 xpath 规则"""
        if isinstance(rules, (list, tuple)):
            self.rules = rules
        elif isinstance(rules, str):
            self.rules = eval(rules)
        else:
            self.rules = [("", ""), ("", "")]

    def isrelease(self, url):
        ok = self.backend.isrelease(url)
        if ok: return ok

        return False

    def _check_update(self):
        """检查更新"""
        for i, url in enumerate(self.get_urls()):
            rules = self.get_rules()[i]

            if self.isrelease(url):
                self.release_date, self.release_commit = \
                    self.backend.extract_info(url, rules)  # 从后端获取信息
            else:
                self.latest_date, self.latest_commit = \
                    self.backend.extract_info(url, rules)

        self.check_date = int(time.time())

    def run_check(self):
        """检查更新, 并更新状态"""
        log.info("starting...")
        if not self.get_rules()[0][0]:  # 空行
            log.debug('none rules for %s, skip!' % self.name)
            return

        self._check_update()

        if self.rpm_date == self.latest_date or \
                self.rpm_date >= self.release_date:
            self.status = "normal"
        elif self.rpm_date == self.latest_date and \
                self.release_date == "error":
            self.status = "normal"
        elif self.latest_date == "error":
            self.status = "error"
        else:
            self.status = "update"

    def __repr__(self):
        return "<Checker [%s]>" % self.name
