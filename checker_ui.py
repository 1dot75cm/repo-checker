# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
try:
    from PyQt5.QtCore import Qt, QSize, QRect, QThread, pyqtSignal
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout,
        QAction, QSpacerItem, QSizePolicy, QMenuBar, QMenu, QStatusBar,
        QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
        QInputDialog, QFileDialog, QMessageBox)
except:
    from PyQt4.QtCore import Qt, QSize, QRect, QThread, pyqtSignal
    from PyQt4.QtGui import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout,
        QAction, QSpacerItem, QSizePolicy, QMenuBar, QMenu, QStatusBar,
        QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
        QInputDialog, QFileDialog, QMessageBox)

from lxml import etree
from dateutil.parser import parse
from datetime import datetime
import re
import os
import sys
import time
import json
import requests
import logging

__url__ = "https://github.com/1dot75cm/repo-checker"
__version__ = "0.1.0"
__license__ = "MIT"
__descript__ = "Checker is a graphical user interface network checker for open source project."
__author__ = "mosquito"
__email__ = "sensor.wen@gmail.com"

# xpath 规则 -> 处理函数 -> 内容
tableContents = []


class WorkThread(QThread):
    triggered = pyqtSignal(int, bool)
    step = 0

    def __int__(self):
        super(WorkThread, self).__init__()

    def run(self):
        for i in tableContents:
            i.run_check()
            self.step += 100 / len(tableContents)
            self.triggered.emit(self.step, False)

        self.triggered.emit(self.step, True)


class MainWindow(QMainWindow):
    description = """<b>Checker</b><br /><br />
    Version: %s<br />
    %s<br /><br />
    Project: <a href="%s">1dot75cm/repo-checker</a><br />
    License: %s<br />
    Author: <a href="mailto:%s">%s</a>
    """ % (__version__, __descript__, __url__, __license__, __email__, __author__)
    tableHeaders = ["Name", "URL", "Branch", "RPM date/commit", "Release date/commit",
                    "Latest date/commit", "Status", "Comment"]
    wtime = [0, 0]

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    def setupUi(self, MainWindow):
        """初始化主窗口"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(QSize(905, 450))
        MainWindow.setWindowTitle(self.tr("Checker"))
        MainWindow.setAnimated(True)

        self.centralwidget = QWidget(MainWindow)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.centralwidget.setSizePolicy(sizePolicy)

        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)

        self.tableWidget = QTableWidget(self.centralwidget)
        self.setupTable()
        self.verticalLayout.addWidget(self.tableWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)

        self.addButton = QPushButton(self.centralwidget)
        self.addButton.setFixedSize(QSize(25, 25))
        self.addButton.setText(self.tr("+"))
        self.horizontalLayout.addWidget(self.addButton)

        self.delButton = QPushButton(self.centralwidget)
        self.delButton.setFixedSize(QSize(25, 25))
        self.delButton.setText(self.tr("-"))
        self.horizontalLayout.addWidget(self.delButton)

        self.upButton = QPushButton(self.centralwidget)
        self.upButton.setFixedSize(QSize(25, 25))
        self.upButton.setText(self.tr("↑"))
        self.upButton.setObjectName("up")
        self.horizontalLayout.addWidget(self.upButton)

        self.downButton = QPushButton(self.centralwidget)
        self.downButton.setFixedSize(QSize(25, 25))
        self.downButton.setText(self.tr("↓"))
        self.horizontalLayout.addWidget(self.downButton)

        spacerItem = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.workThread = WorkThread()  # 耗时任务需要用线程执行，再刷新进度条
        self.horizontalLayout.addWidget(self.progressBar)

        self.label = QLabel(self.centralwidget)
        self.label.setText(self.tr("TextLabel"))
        self.horizontalLayout.addWidget(self.label)

        self.checkButton = QPushButton(self.centralwidget)
        self.checkButton.setText(self.tr("Check"))
        self.horizontalLayout.addWidget(self.checkButton)

        self.updateButton = QPushButton(self.centralwidget)
        self.updateButton.setText(self.tr("Update item"))
        self.horizontalLayout.addWidget(self.updateButton)

        self.editRuleButton = QPushButton(self.centralwidget)
        self.editRuleButton.setText(self.tr("Edit rule"))
        self.horizontalLayout.addWidget(self.editRuleButton)

        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 780, 34))
        self.fileMenu = QMenu(self.menubar)
        self.fileMenu.setTitle(self.tr("File"))
        self.helpMenu = QMenu(self.menubar)
        self.helpMenu.setTitle(self.tr("Help"))
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        # 菜单项
        self.aboutAction = QAction(MainWindow)
        self.aboutAction.setText(self.tr("About"))
        self.aboutAction.setObjectName("about")
        self.aboutQtAction = QAction(MainWindow)
        self.aboutQtAction.setText(self.tr("About Qt"))
        self.aboutQtAction.setObjectName("about_qt")
        self.openAction = QAction(MainWindow)
        self.openAction.setText(self.tr("&Open"))
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open a file')
        self.openAction.setObjectName("open")
        self.saveAction = QAction(MainWindow)
        self.saveAction.setText(self.tr("&Save"))
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save a file')
        self.saveAction.setObjectName("save")
        self.saveAsAction = QAction(MainWindow)
        self.saveAsAction.setText(self.tr("Save As"))
        self.saveAsAction.setObjectName("save_as")
        self.closeAction = QAction(MainWindow)
        self.closeAction.setText(self.tr("&Close"))
        self.closeAction.setShortcut('Ctrl+W')
        self.closeAction.setStatusTip('Close current page')
        self.exitAction = QAction(MainWindow)
        self.exitAction.setText(self.tr("&Exit"))
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')

        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        self.menubar.addAction(self.fileMenu.menuAction())
        self.menubar.addAction(self.helpMenu.menuAction())

        # Signal & Slot
        self.addButton.clicked.connect(self.addRowSlot)
        self.delButton.clicked.connect(self.delRowSlot)
        self.upButton.clicked.connect(self.moveRowSlot)
        self.downButton.clicked.connect(self.moveRowSlot)
        self.checkButton.clicked.connect(self.checkUpdateSlot)
        self.updateButton.clicked.connect(self.updateTableItemSlot)
        self.editRuleButton.clicked.connect(self.editTableItemRuleSlot)
        self.workThread.triggered.connect(self.updateTableSlot)
        self.aboutAction.triggered.connect(self.showAboutDialogSlot)
        self.aboutQtAction.triggered.connect(self.showAboutDialogSlot)
        self.openAction.triggered.connect(self.showFileDialogSlot)
        self.saveAction.triggered.connect(self.showFileDialogSlot)
        self.saveAsAction.triggered.connect(self.showFileDialogSlot)
        self.closeAction.triggered.connect(self.tableWidget.clearContents)
        self.exitAction.triggered.connect(self.close)
        self.tableWidget.itemChanged.connect(self.itemChangedSlot)

    def closeEvent(self, event):
        """关闭应用提示"""
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()  # 接受关闭事件
        else:
            event.ignore()  # 拒绝关闭事件

    def itemChangedSlot(self, item):  # QTableWidgetItem
        """捕获itemChanged信号, 修改表项"""
        try:
            tableContents[item.row()].load(item.column(), item.text())
        except IndexError:
            pass

    def moveRowSlot(self):
        """移动行"""
        try:
            sourceRow = self.tableWidget.currentRow()
            destRow = sourceRow-1 if self.sender().objectName() == "up" else sourceRow+1
            if sourceRow != -1:
                sourceItems = self.getRow(sourceRow)
                destItems = self.getRow(destRow)
                self.setRow(destRow, sourceItems)
                self.setRow(sourceRow, destItems)
                self.tableWidget.selectRow(destRow)  # 修改焦点
                logging.debug(tableContents)
        except AttributeError:
            if self.sender().objectName() == "up":
                QMessageBox.warning(self, "Warning", "The row is to top.")
            else:
                QMessageBox.warning(self, "Warning", "The row is to bottom.")

    def getRow(self, rowIndex):
        """获取行"""
        rowItems = []
        for i in range(7):
            item = self.tableWidget.item(rowIndex, i)
            rowItems.append(item.text())
        rowItems.append(tableContents[rowIndex].rules)
        return rowItems

    def setRow(self, rowIndex, rowItems):
        """设置行"""
        for n, i in enumerate(rowItems):
            if n == len(rowItems) - 1:
                tableContents[rowIndex].rules = i
            else:
                item = self.tableWidget.item(rowIndex, n)
                item.setText(i)

    def addRowSlot(self):
        """添加行"""
        rowIndex = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rowIndex + 1)
        tableContents.append(Checker())
        self.updateTableSlot(0)  # 更新列表控件
        logging.debug(tableContents)

    def delRowSlot(self):
        """删除行"""
        #焦点默认在第一行，要设置setFocusPolicy(Qt.NoFocus)
        rowIndex = self.tableWidget.currentRow()
        if rowIndex != -1:
            self.tableWidget.removeRow(rowIndex)
            tableContents.remove(tableContents[rowIndex])
            logging.debug(tableContents)
        else:
            QMessageBox.warning(self, "Warning", "Please select a row.")

    def loadData(self, data):
        """载入数据"""
        global tableContents
        tableContents = []  # list.clear() Python 3
        for i in data:
            tableContents.append(Checker(i))

    def checkUpdateSlot(self):
        """执行更新检查"""
        self.wtime[0] = int(time.time())
        self.statusbar.showMessage("checking...")
        self.progressBar.setValue(0)
        self.progressBar.show()
        # 执行工作线程
        self.workThread.start()

    def updateTableSlot(self, val, end=False):
        """线程通过该槽，刷新进度条，表格内容"""
        self.progressBar.setValue(val)
        self.tableWidget.setRowCount(len(tableContents))  # 行数

        for n, i in enumerate(tableContents):
            items = i.dump_info()
            for j in range(8):
                item = QTableWidgetItem(items[j])
                self.tableWidget.setItem(n, j, item)

        if end:
            self.wtime[1] = int(time.time())
            self.statusbar.showMessage(
                "finished (work time %ds)" % (self.wtime[1] - self.wtime[0]))

    def updateTableItemSlot(self):
        """更新指定的 RPM 日期为 Release 日期"""
        rowIndex = self.tableWidget.currentRow()
        if rowIndex != -1:
            try:
                item = self.tableWidget.item(rowIndex, 4)
                self.tableWidget.item(rowIndex, 3).setText(item.text())
                tableContents[rowIndex].load_status(item.text())
            except (IndexError, AttributeError):
                QMessageBox.warning(self, "Warning", "The row is empty.")
        else:
            QMessageBox.warning(self, "Warning", "Please select a row.")

    def editTableItemRuleSlot(self):
        """编辑列表项规则"""
        rowIndex = self.tableWidget.currentRow()
        if rowIndex != -1:
            try:
                # 父控件, 标题, 标签提示, 默认值, window flags
                rules, ok = QInputDialog.getMultiLineText(self, "Edit rule",
                    "XPath rule(format: \"[(time, commit), (time, commit)]\"):",
                    re.sub("\),|],|',", lambda x: "%s\n" % x.group(),
                        str(tableContents[rowIndex].get_rules()) ))

                if ok:
                    tableContents[rowIndex].rules = eval(rules)
            except (IndexError, UnboundLocalError):
                QMessageBox.warning(self, "Warning", "The row is empty.")
        else:
            QMessageBox.warning(self, "Warning", "Please select a row.")

    def showAboutDialogSlot(self):
        """显示关于对话框"""
        if self.sender().objectName() == "about":
            QMessageBox.about(self, "Checker", self.description)
        else:
            QMessageBox.aboutQt(self, "Checker")

    def showFileDialogSlot(self):
        """打开/保存数据至文件"""
        if self.sender().objectName() == "open":
            fname, _ = QFileDialog.getOpenFileName(self, "Open file", os.getcwd())
            if fname:
                try:
                    with open(fname, 'r') as fp:
                        self.loadData(json.load(fp))
                    self.updateTableSlot(0)  # 更新列表控件
                    self.statusbar.showMessage("open successfully")
                except AttributeError:
                    QMessageBox.warning(self, "Error", "Open file failed.")
                except json.decoder.JSONDecodeError:
                    QMessageBox.warning(self, "Error", "The file does not contain JSON.")

        elif self.sender().objectName() in ["save", "save_as"]:
            fname, _ = QFileDialog.getSaveFileName(self, "Save file", os.getcwd())
            if fname:
                try:
                    with open(fname, 'w') as fp:
                        json.dump([i.dump() for i in tableContents], fp, ensure_ascii=False)
                    self.statusbar.showMessage("saved successfully")
                except AttributeError:
                    QMessageBox.warning(self, "Error", "Save file failed.")

    def setupTable(self):
        """初始化列表"""
        self.tableWidget.setFocusPolicy(Qt.NoFocus)  # 无焦点
        self.tableWidget.setGridStyle(Qt.DashDotLine)  # 线类型
        self.tableWidget.setWordWrap(True)
        self.tableWidget.setCornerButtonEnabled(True)
        self.tableWidget.horizontalHeader().setVisible(True)  # 显示表头
        #self.tableWidget.horizontalHeader().setSortIndicatorShown(True)  # 排序指示器
        self.tableWidget.horizontalHeader().setStretchLastSection(True)  # 扩展最后一列

        self.tableWidget.setColumnCount(8)  # 列数
        self.tableWidget.setRowCount(10)  # 行数

        # 行头
        for i in range(10):
            item = QTableWidgetItem(self.tr("%s"%(i+1)))
            self.tableWidget.setVerticalHeaderItem(i, item)  # 行号

        # 列头
        for i in range(8):
            item = QTableWidgetItem(self.tr(self.tableHeaders[i]))  # QIcon, str
            self.tableWidget.setHorizontalHeaderItem(i, item)  # 初始化表头

        for i in [3, 4, 5]:
            self.tableWidget.resizeColumnToContents(i)  # 根据内容调整列宽

        # 初始化项目
        for i in range(10):
            tableContents.append(Checker())
            for j in range(7):
                item = QTableWidgetItem()
                self.tableWidget.setItem(i, j, item)


class Checker(object):
    def __init__(self, item=None):
        self.name = item['name'] if item else ""
        self.url = item['url'] if item else ""
        self.branch = item['branch'] if item else ""
        self.rpm_date = item['rpm_date'] if item else "none"
        self.rpm_commit = item['rpm_commit'] if item else "none"
        self.rules = item['rules'] if item else [("", ""), ("", "")]
        #self.urls = item['urls']
        self.comment = item['comment'] if item else ""

        self.release_date = "none"
        self.release_commit = "none"
        self.latest_date = "none"
        self.latest_commit = "none"
        self.status = "none"
        self.check_date = ""
        self.type = ""

    def load(self, column, value):
        if column == 0:
            self.name = value
        elif column == 1:
            self.url = value
        elif column == 2:
            self.branch = value
        elif column == 3:
            self.load_status(value)
        elif column == 4:
            self.load_status(value, "release")
        elif column == 5:
            self.load_status(value, "latest")
        elif column == 6:
            self.status = value
        elif column == 7:
            self.comment = value
        else:
            self.rules = value

    def dump(self):
        return dict(
            name = self.name,
            url = self.url,
            branch = self.branch,
            rpm_date = self.rpm_date,
            rpm_commit = self.rpm_commit,
            rules = self.rules,
            comment = self.comment
        )

    @staticmethod
    def ctime(timestamp):
        """Convert time format"""
        if len(str(timestamp)) == 10:
            # timestamp -> string
            return datetime.fromtimestamp(float(timestamp))\
                           .strftime("%y%m%d")
        elif len(str(timestamp)) == 6:
            # string -> timestamp
            #int(datetime.strptime(str(timestamp), "%y%m%d").timestamp())  # Python 3
            return int(time.mktime(
                        datetime.strptime(str(timestamp), "%y%m%d")\
                                .timetuple()))
        else:
            return timestamp

    def dump_status(self, dump_type="rpm"):
        """导出状态信息"""
        if dump_type == "rpm":
            return "%s [%s]" % (self.ctime(self.rpm_date), self.rpm_commit)
        elif dump_type == "release":
            return "%s [%s]" % (self.ctime(self.release_date), self.release_commit)
        elif dump_type == "latest":
            return "%s [%s]" % (self.ctime(self.latest_date), self.latest_commit)

    def load_status(self, data, load_type="rpm"):
        """导入状态信息"""
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

    def dump_info(self):
        """输出对象信息"""
        return (self.name, self.url, self.branch,
                self.dump_status(), self.dump_status("release"),
                self.dump_status("latest"), self.status, self.comment)

    def get_urls(self):
        """获取 url 列表"""
        if re.search('github', self.url):
            self.type = "github"
            return [self.url + '/releases', self.url + '/commits/' + self.branch]
        elif re.search('sogou', self.url):
            return [self.url]
        else:
            return False

    def get_rules(self):
        """获取 xpath 规则"""
        return self.rules

    def get(self, url, params=None, **kwargs):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'
        }
        return requests.get(url, params, headers=headers, **kwargs)

    def _get_info(self, url, rules):
        """根据规则, 提取更新信息"""
        _data = []
        resp = self.get(url)
        if not resp.ok:
            return [("none", "error"), ("none", "error")]

        logging.debug("rules: %s, %s" % (rules[0], rules[1]))
        tree = etree.HTML(resp.text)
        if isinstance(rules, (list, tuple)):
            for rule in rules:
                if not rule:
                    _data.append("")
                    break

                logging.debug("match: %s" % tree.xpath(rule)[0])
                _data.append(
                    self._process_data(tree.xpath(rule)[0]))

            return _data  # (date, commit)

    def _process_data(self, data):
        """处理数据"""
        try:
            dt = parse(data)
            return int(time.mktime(dt.timetuple()))  # int(dt.timestamp())
        except ValueError:
            return data.split("/")[-1][:7]
        except IndexError:  # no data
            return ""

    def isrelease(self, url):
        if re.search('releases', url):
            return True
        elif re.search('sogou', url):
            return True

        return False

    def _check_update(self):
        """检查更新"""
        for i, url in enumerate(self.get_urls()):
            rules = self.get_rules()[i]

            if self.isrelease(url):
                self.release_date, self.release_commit = \
                    self._get_info(url, rules)
            else:
                self.latest_date, self.latest_commit = \
                    self._get_info(url, rules)

        self.check_date = int(time.time())

    def run_check(self):
        """检查更新, 并更新状态"""
        logging.info("starting...")
        if not self.rules[0][0]:  # 空行
            return

        self._check_update()

        if self.rpm_date == self.latest_date or self.rpm_date >= self.release_date:
            self.status = "normal"
        else:
            self.status = "update"

    def __repr__(self):
        return "<Checker [%s]>" % self.name


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())