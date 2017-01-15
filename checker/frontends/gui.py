# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

try:
    from PyQt5.QtCore import Qt, QSize, QRect, QThread, pyqtSignal, QUrl
    from PyQt5.QtWidgets import (qApp, QMainWindow, QHBoxLayout, QVBoxLayout,
        QAction, QSpacerItem, QSizePolicy, QMenuBar, QMenu, QStatusBar, QWidget,
        QPushButton, QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
        QInputDialog, QFileDialog, QInputDialog, QLineEdit, QMessageBox)
    from PyQt5.QtGui import QColor, QDesktopServices
except:
    from PyQt4.QtCore import Qt, QSize, QRect, QThread, pyqtSignal, QUrl
    from PyQt4.QtGui import (qApp, QMainWindow, QHBoxLayout, QVBoxLayout,
        QAction, QSpacerItem, QSizePolicy, QMenuBar, QMenu, QStatusBar, QWidget,
        QPushButton, QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
        QInputDialog, QFileDialog, QInputDialog, QLineEdit, QMessageBox,
        QColor, QDesktopServices)

from queue import Queue
import re
import os
import csv
import time
import json

from .. import __url__
from .. import __version__
from .. import __license__
from .. import __descript__
from .. import __author__
from .. import __email__
from .. import logger
from ..app import Checker
from ..config import config
from ..backends import BaseBackend as backend
from .settings import SettingDialog

log = logger.getLogger(__name__)


class WorkThread(QThread):
    triggered = pyqtSignal(int)

    def __init__(self, queue):
        super(WorkThread, self).__init__()
        self.queue = queue

    def run(self):
        while True:
            task = self.queue.get()
            task.run_check()
            self.triggered.emit(1)
            self.queue.task_done()


class MainWindow(QMainWindow):
    tableContents = []
    tableColumnCount = 8
    tableRowCount = 10
    workerCount = config['worker_num']  # 线程数
    workers = []  # 保存线程对象
    q = Queue()
    wtime = [0, 0]
    bgColor = QColor(180, 200, 230, 40)
    progressVal = 0
    taskVal = 0

    def __init__(self):
        super(MainWindow, self).__init__()
        self.description = self.tr("""<b>Checker</b><br /><br />
            Version: %s<br />
            %s<br /><br />
            Project: <a href=\"%s\">1dot75cm/repo-checker</a><br />
            License: %s<br />
            Author: <a href=\"mailto:%s\">%s</a>""") % (__version__,
            __descript__, __url__, __license__, __email__, __author__)
        self.tableHeaders = [self.tr("Name"), self.tr("URL"), self.tr("Branch"),
                             self.tr("RPM date [commit]"), self.tr("Release date [commit]"),
                             self.tr("Latest date [commit]"), self.tr("Status"), self.tr("Comment")]
        self.setupUi(self)

    def setupUi(self, MainWindow):
        """初始化主窗口"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(QSize(910, 450))
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
        self.addButton.setText("+")
        self.horizontalLayout.addWidget(self.addButton)

        self.delButton = QPushButton(self.centralwidget)
        self.delButton.setFixedSize(QSize(25, 25))
        self.delButton.setText("-")
        self.horizontalLayout.addWidget(self.delButton)

        self.upButton = QPushButton(self.centralwidget)
        self.upButton.setFixedSize(QSize(25, 25))
        self.upButton.setText("↑")
        self.upButton.setObjectName("up")
        self.horizontalLayout.addWidget(self.upButton)

        self.downButton = QPushButton(self.centralwidget)
        self.downButton.setFixedSize(QSize(25, 25))
        self.downButton.setText("↓")
        self.horizontalLayout.addWidget(self.downButton)

        spacerItem = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.hide()
        self.horizontalLayout.addWidget(self.progressBar)

        self.label = QLabel(self.centralwidget)
        self.horizontalLayout.addWidget(self.label)

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

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

        # 菜单
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 780, 34))
        MainWindow.setMenuBar(self.menubar)

        self.fileMenu = QMenu(self.menubar)
        self.fileMenu.setTitle(self.tr("File"))
        self.menubar.addAction(self.fileMenu.menuAction())

        self.toolMenu = QMenu(self.menubar)
        self.toolMenu.setTitle(self.tr("Tool"))
        self.menubar.addAction(self.toolMenu.menuAction())

        self.helpMenu = QMenu(self.menubar)
        self.helpMenu.setTitle(self.tr("Help"))
        self.menubar.addAction(self.helpMenu.menuAction())

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
        self.openAction.setStatusTip(self.tr('Open a file'))
        self.openAction.setObjectName("open")
        self.openUrlAction = QAction(MainWindow)
        self.openUrlAction.setText(self.tr("Open &url"))
        self.openUrlAction.setShortcut('Ctrl+U')
        self.openUrlAction.setStatusTip(self.tr('Open a file with url'))
        self.saveAction = QAction(MainWindow)
        self.saveAction.setText(self.tr("&Save"))
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip(self.tr('Save a file'))
        self.saveAction.setObjectName("save")
        self.saveAsAction = QAction(MainWindow)
        self.saveAsAction.setText(self.tr("Save As"))
        self.saveAsAction.setObjectName("save_as")
        self.closeAction = QAction(MainWindow)
        self.closeAction.setText(self.tr("&Close"))
        self.closeAction.setShortcut('Ctrl+W')
        self.closeAction.setStatusTip(self.tr('Close current page'))
        self.exitAction = QAction(MainWindow)
        self.exitAction.setText(self.tr("&Exit"))
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip(self.tr('Exit application'))
        self.settingAction = QAction(MainWindow)
        self.settingAction.setText(self.tr("&Settings"))
        self.settingAction.setShortcut('Ctrl+P')
        self.settingAction.setStatusTip(self.tr('Open settings dialog'))

        self.helpMenu.addAction(self.aboutAction)
        self.helpMenu.addAction(self.aboutQtAction)
        self.toolMenu.addAction(self.settingAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.openUrlAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        # Signal & Slot
        self.addButton.clicked.connect(self.addRowSlot)
        self.delButton.clicked.connect(self.delRowSlot)
        self.upButton.clicked.connect(self.moveRowSlot)
        self.downButton.clicked.connect(self.moveRowSlot)
        self.checkButton.clicked.connect(self.checkUpdateSlot)
        self.updateButton.clicked.connect(self.updateTableItemSlot)
        self.editRuleButton.clicked.connect(self.editTableItemRuleSlot)
        self.settingAction.triggered.connect(self.showSettingDialogSlot)
        self.aboutAction.triggered.connect(self.showAboutDialogSlot)
        self.aboutQtAction.triggered.connect(self.showAboutDialogSlot)
        self.openAction.triggered.connect(self.showFileDialogSlot)
        self.openUrlAction.triggered.connect(self.showOpenUrlDialogSlot)
        self.saveAction.triggered.connect(self.showFileDialogSlot)
        self.saveAsAction.triggered.connect(self.showFileDialogSlot)
        self.closeAction.triggered.connect(self.tableWidget.clearContents)
        self.exitAction.triggered.connect(self.close)
        self.tableWidget.itemChanged.connect(self.itemChangedSlot)
        self.tableWidget.itemClicked.connect(self.itemClickedForOpenUrlSlot)

    def closeEvent(self, event):
        """关闭应用提示"""
        reply = QMessageBox.question(self, self.tr('Message'),
            self.tr("Are you sure to quit?"), QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()  # 接受关闭事件
        else:
            event.ignore()  # 拒绝关闭事件

    def itemClickedForOpenUrlSlot(self, item):
        """Ctrl+left 打开链接"""
        # http://stackoverflow.com/questions/3100090/
        if item.column() == 1 and item.text() and \
                qApp.keyboardModifiers() == Qt.ControlModifier:
            QDesktopServices.openUrl(QUrl(item.text()))  # open url

    def itemChangedSlot(self, item):  # QTableWidgetItem
        """捕获itemChanged信号, 修改表项"""
        try:
            self.tableContents[item.row()].load(item.column(), item.text())
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
                log.debug(self.tableContents)
        except AttributeError:
            if self.sender().objectName() == "up":
                QMessageBox.warning(self, self.tr("Warning"), self.tr("The row is to top."))
            else:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("The row is to bottom."))

    def getRow(self, rowIndex):
        """获取行"""
        rowItems = []
        for i in range(7):
            item = self.tableWidget.item(rowIndex, i)
            rowItems.append(item.text())
        rowItems.append(self.tableContents[rowIndex].get_rules(ui=True))
        return rowItems

    def setRow(self, rowIndex, rowItems):
        """设置行"""
        for n, i in enumerate(rowItems):
            if n == len(rowItems) - 1:
                self.tableContents[rowIndex].set_rules(i)
            else:
                item = self.tableWidget.item(rowIndex, n)
                item.setText(i)

    def addRowSlot(self):
        """添加行"""
        rowIndex = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rowIndex + 1)
        self.tableContents.append(Checker())
        self.updateTableSlot(0)  # 更新列表控件
        log.debug(self.tableContents)

    def delRowSlot(self):
        """删除行"""
        # 焦点默认在第一行，要设置setFocusPolicy(Qt.NoFocus)
        rowIndex = self.tableWidget.currentRow()
        if rowIndex != -1:
            self.tableWidget.removeRow(rowIndex)
            self.tableContents.remove(self.tableContents[rowIndex])
            log.debug(self.tableContents)
        else:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a row."))

    def loadData(self, data):
        """载入数据"""
        self.tableContents = []  # list.clear() Python 3
        for i in data:
            self.tableContents.append(Checker(i))

    def checkUpdateSlot(self):
        """执行更新检查"""
        self.wtime[0] = int(time.time())  # 计时
        self.statusbar.showMessage(self.tr("checking..."))
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.progressVal = 0
        self.taskVal = 0

        for t in range(self.workerCount):
            t = WorkThread(self.q)  # 耗时任务需要用线程执行，再刷新进度条
            t.triggered.connect(self.updateTableSlot)
            self.workers.append(t)
            t.start()  # 执行工作线程

        # 填充队列
        for item in self.tableContents:
            self.q.put(item)

    def updateTableSlot(self, val):
        """线程通过该槽，刷新进度条，表格内容"""
        if val:
            self.taskVal += val
            self.progressVal = self.taskVal / len(self.tableContents) * 100
            self.progressBar.setValue(self.progressVal)
            self.label.setText("%s/%s" % (self.taskVal, len(self.tableContents)))
        self.tableWidget.setRowCount(len(self.tableContents))  # 行数

        for n, i in enumerate(self.tableContents):
            items = i.dump()
            for j in range(self.tableWidget.columnCount()):
                item = QTableWidgetItem(items[j])
                if j in [0, 1]:
                    item.setToolTip(item.text())
                self.tableWidget.setItem(n, j, item)
            self.setStatusColor(n)

        self.setBackgroundColor(self.bgColor)

        if self.progressVal == 100:
            self.wtime[1] = int(time.time())
            self.statusbar.showMessage(self.tr(
                "finished (work time %ds)") % (self.wtime[1] - self.wtime[0]))

    def updateTableItemSlot(self):
        """更新指定的 RPM 日期为 Release 日期"""
        rowIndex = self.tableWidget.currentRow()
        if rowIndex != -1:
            try:
                item = self.tableWidget.item(rowIndex, 4)
                self.tableWidget.item(rowIndex, 3).setText(item.text())
                self.tableContents[rowIndex].load_meta(item.text())
            except (IndexError, AttributeError):
                QMessageBox.warning(self, self.tr("Warning"), self.tr("The row is empty."))
        else:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a row."))

    def editTableItemRuleSlot(self):
        """编辑列表项规则"""
        rowIndex = self.tableWidget.currentRow()
        if rowIndex != -1:
            try:
                # 父控件, 标题, 标签提示, 默认值, window flags
                rules, ok = QInputDialog.getMultiLineText(self, self.tr("Edit rule"),
                    self.tr("XPath rule(format: \"[(time, commit), (time, commit)]\"):"),
                    re.sub("\),|],|',", lambda x: "%s\n" % x.group(),
                        str(self.tableContents[rowIndex].get_rules(ui=True)) ))

                if ok:
                    self.tableContents[rowIndex].set_rules(rules)
            except (IndexError, UnboundLocalError):
                QMessageBox.warning(self, self.tr("Warning"), self.tr("The row is empty."))
        else:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a row."))

    def showSettingDialogSlot(self):
        """显示设置对话框"""
        settingDialog = SettingDialog()
        settingDialog.exec_()

    def showAboutDialogSlot(self):
        """显示关于对话框"""
        if self.sender().objectName() == "about":
            QMessageBox.about(self, self.tr("Checker"), self.description)
        else:
            QMessageBox.aboutQt(self, self.tr("Checker"))

    def showOpenUrlDialogSlot(self):
        """通过 Url 打开文件"""
        url, _ = QInputDialog.getText(self, self.tr("Open url"),
                     self.tr("Enter url:"), QLineEdit.Normal, "")
        try:
            resp = backend.get(url)
            self.loadData(resp.json())
            self.updateTableSlot(0)  # 更新列表控件
            self.statusbar.showMessage(self.tr("open url successfully"))
        except Exception as e:
            QMessageBox.warning(self, self.tr("Error"),
                                self.tr("Open url failed. See below:\n%s") % e)
            self.statusbar.showMessage(self.tr("open url failed"))

    def loadCsvFile(self, fname):
        """load csv file (old format)"""
        _data = []
        with open(fname, 'r') as fp:
            content = csv.reader(fp)
            for row in content:
                if len(row) and row[0][0] != "#":
                    _data.append(row)
            self.loadData(_data)

    def showFileDialogSlot(self):
        """打开/保存数据至文件"""
        if self.sender().objectName() == "open":
            fname = QFileDialog.getOpenFileName(self, self.tr("Open file"), os.getcwd())
            fname = fname[0] if isinstance(fname, tuple) else fname  # qt5 tuple, qt4 str

            if fname:
                try:
                    with open(fname, 'r') as fp:
                        self.loadData(json.load(fp))
                except AttributeError as e:
                    QMessageBox.warning(self, self.tr("Error"),
                        self.tr("Open file failed. See below:\n%s") % e)
                except:  # json.decoder.JSONDecodeError Python 3
                    try:  # load csv file (old format)
                        self.loadCsvFile(fname)
                    except Exception as e:
                        QMessageBox.warning(self, self.tr("Error"),
                            self.tr("The file does not contain JSON or CSV. See below:\n%s") % e)

                self.updateTableSlot(0)  # 更新列表控件
                self.statusbar.showMessage(self.tr("open file successfully"))

        elif self.sender().objectName() in ["save", "save_as"]:
            fname = QFileDialog.getSaveFileName(self, self.tr("Save file"), os.getcwd())
            fname = fname[0] if isinstance(fname, tuple) else fname  # qt5 tuple, qt4 str

            if fname:
                try:
                    with open(fname, 'w') as fp:
                        json.dump([i.dump(mode="raw") for i in self.tableContents],
                                  fp, ensure_ascii=False)
                    self.statusbar.showMessage(self.tr("saved successfully"))
                except AttributeError as e:
                    QMessageBox.warning(self, self.tr("Error"),
                        self.tr("Save file failed. See below:\n%s") % e)

    def setBackgroundColor(self, color):
        """修改背景色"""
        for i in range(self.tableWidget.rowCount()):
            if i % 2 != 0:
                for j in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(i, j)
                    if item:
                        item.setBackground(color)

    def setStatusColor(self, rowIndex):
        """修改状态文字颜色"""
        item = self.tableWidget.item(rowIndex, 6)
        if item.text() == "normal":
            item.setForeground(Qt.darkGreen)
        elif item.text() == "update":
            item.setForeground(Qt.darkRed)
        elif item.text() == "error":
            item.setForeground(Qt.darkYellow)
        elif item.text() == "none":
            item.setForeground(Qt.gray)

    def setupTable(self):
        """初始化列表"""
        self.tableWidget.setFocusPolicy(Qt.NoFocus)  # 无焦点
        self.tableWidget.setGridStyle(Qt.DashDotLine)  # 线类型
        self.tableWidget.setWordWrap(True)
        self.tableWidget.setCornerButtonEnabled(True)
        self.tableWidget.horizontalHeader().setVisible(True)  # 显示表头
        #self.tableWidget.horizontalHeader().setSortIndicatorShown(True)  # 排序指示器
        self.tableWidget.horizontalHeader().setStretchLastSection(True)  # 扩展最后一列

        self.tableWidget.setColumnCount(self.tableColumnCount)  # 列数
        self.tableWidget.setRowCount(self.tableRowCount)  # 行数

        # 行头
        for i in range(self.tableRowCount):
            item = QTableWidgetItem("%s" % (i+1))
            self.tableWidget.setVerticalHeaderItem(i, item)  # 行号

        # 列头
        for i in range(self.tableColumnCount):
            item = QTableWidgetItem(self.tableHeaders[i])  # QIcon, str
            self.tableWidget.setHorizontalHeaderItem(i, item)  # 初始化表头

        for i in [3, 4, 5]:
            self.tableWidget.resizeColumnToContents(i)  # 根据内容调整列宽

        # 初始化项目
        for i in range(self.tableRowCount):
            self.tableContents.append(Checker())
            for j in range(self.tableColumnCount):
                item = QTableWidgetItem()
                self.tableWidget.setItem(i, j, item)

        self.setBackgroundColor(self.bgColor)
