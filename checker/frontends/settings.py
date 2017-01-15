# -*- coding: utf-8 -*-

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QTabWidget, QWidget, QLabel,
        QSpinBox, QRadioButton, QLineEdit, QGridLayout, QSpacerItem, QSizePolicy)
except:
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import (QDialog, QDialogButtonBox, QTabWidget, QWidget, QLabel,
        QSpinBox, QRadioButton, QLineEdit, QGridLayout, QSpacerItem, QSizePolicy)

from ..config import config


class SettingDialog(QDialog):

    def __init__(self):
        super(SettingDialog, self).__init__()
        self.setupUi(self)

    def setupUi(self, setDialog):
        setDialog.setObjectName("setDialog")
        setDialog.setWindowTitle(self.tr("Settings"))
        setDialog.resize(540, 330)

        ##### main dialog #####
        self.mainGridLayout = QGridLayout(setDialog)

        self.tabWidget = QTabWidget(setDialog)
        self.tabWidget.setLayoutDirection(Qt.LeftToRight)  # 内容布局方向
        self.tabWidget.setTabPosition(QTabWidget.North)  # 标签位置
        self.tabWidget.setTabShape(QTabWidget.Rounded)  # 标签形状 Rounded, Triangular
        self.mainGridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)  # 行, 列, 占行数, 占列数

        self.buttonBox = QDialogButtonBox(setDialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel |
            QDialogButtonBox.Ok | QDialogButtonBox.Save)
        self.mainGridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        ##### Basic tab #####
        self.basicTab = QWidget()
        self.tabWidget.addTab(self.basicTab, self.tr("Basic"))

        self.basicGridLayout = QGridLayout(self.basicTab)
        self.basicGridLayout.setContentsMargins(15, 10, 15, 20)

        self.workerNumLabel = QLabel(self.basicTab)
        self.workerNumLabel.setText(self.tr("worker number"))
        self.workerNumLabel.setToolTip(self.tr("number of worker for crawler"))
        self.basicGridLayout.addWidget(self.workerNumLabel, 0, 0, 1, 1)

        self.workerNumBox = QSpinBox(self.basicTab)
        self.workerNumBox.setMinimum(1)
        self.workerNumBox.setMaximum(30)
        self.workerNumBox.setValue(config['worker_num'])
        self.basicGridLayout.addWidget(self.workerNumBox, 0, 1, 1, 1)

        self.retryTimeLabel = QLabel(self.basicTab)
        self.retryTimeLabel.setText(self.tr("retry times"))
        self.retryTimeLabel.setToolTip(self.tr("retry times if network fails"))
        self.basicGridLayout.addWidget(self.retryTimeLabel, 1, 0, 1, 1)

        self.retryTimeBox = QSpinBox(self.basicTab)
        self.retryTimeBox.setValue(config['retry'])
        self.basicGridLayout.addWidget(self.retryTimeBox, 1, 1, 1, 1)

        self.retryWaitLabel = QLabel(self.basicTab)
        self.retryWaitLabel.setText(self.tr("retry wait time"))
        self.retryWaitLabel.setToolTip(self.tr("wait time before retry network access"))
        self.basicGridLayout.addWidget(self.retryWaitLabel, 2, 0, 1, 1)

        self.retryWaitBox = QSpinBox(self.basicTab)
        self.retryWaitBox.setValue(config['retry_time'])
        self.basicGridLayout.addWidget(self.retryWaitBox, 2, 1, 1, 1)

        ##### Network tab #####
        self.networkTab = QWidget()
        self.tabWidget.addTab(self.networkTab, self.tr("Network"))

        self.networkGridLayout = QGridLayout(self.networkTab)
        self.networkGridLayout.setContentsMargins(15, 20, 15, 20)

        self.addrLabel = QLabel(self.networkTab)
        self.addrLabel.setText(self.tr("proxy address"))
        self.addrLabel.setToolTip(self.tr("proxy address"))
        self.networkGridLayout.addWidget(self.addrLabel, 0, 0, 1, 1)

        self.addr = config['proxy']['http'].split('://') + ['']
        self.addrEdit = QLineEdit(self.networkTab)
        self.addrEdit.setText(self.addr[1])
        self.addrEdit.setToolTip(self.tr("[user:pass@]hostname[:port]"))
        self.networkGridLayout.addWidget(self.addrEdit, 0, 1, 1, 4)

        horSpacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.networkGridLayout.addItem(horSpacerItem, 1, 0, 1, 1)

        self.httpBtn = QRadioButton(self.networkTab)
        self.httpBtn.setText(self.tr("http"))
        self.networkGridLayout.addWidget(self.httpBtn, 1, 1, 1, 1)

        self.httpsBtn = QRadioButton(self.networkTab)
        self.httpsBtn.setText(self.tr("https"))
        self.networkGridLayout.addWidget(self.httpsBtn, 1, 2, 1, 1)

        self.socks4Btn = QRadioButton(self.networkTab)
        self.socks4Btn.setText(self.tr("socks4"))
        self.networkGridLayout.addWidget(self.socks4Btn, 1, 3, 1, 1)

        self.socks5Btn = QRadioButton(self.networkTab)
        self.socks5Btn.setText(self.tr("socks5"))
        self.networkGridLayout.addWidget(self.socks5Btn, 1, 4, 1, 1)

        verSpacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.networkGridLayout.addItem(verSpacerItem, 2, 0, 1, 1)

        self.radios = self.httpBtn, self.httpsBtn, self.socks4Btn, self.socks5Btn
        self.setRadioBtn(self.addr[0])  # 根据协议按下按钮

        # Signal & Slot
        self.buttonBox.accepted.connect(self.saveOptionSlot)
        self.buttonBox.accepted.connect(setDialog.accept)
        self.buttonBox.rejected.connect(setDialog.reject)
        self.buttonBox.clicked.connect(self.saveOptionToFileSlot)

    def setRadioBtn(self, scheme):
        """click btn"""
        for btn in self.radios:
            if btn.text() == scheme:
                btn.click()

    def getRadioBtn(self):
        """get clicked btn"""
        for btn in self.radios:
            if btn.isChecked():
                return btn.text()

        return None

    def saveOptionSlot(self):
        """save options"""
        config.load_config(**{
            'worker_num': self.workerNumBox.value(),
            'retry': self.retryTimeBox.value(),
            'retry_time': self.retryWaitBox.value(),
            'proxy': "%s://%s" % (self.getRadioBtn(), self.addrEdit.text()) \
                         if self.getRadioBtn() else ""
        })

    def saveOptionToFileSlot(self, btn):
        """save options to file via save_config func"""
        if btn.text() == 'Save':
            config.save_config()
