# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CrawlerInterface.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CrawlerInterface(object):
    def setupUi(self, CrawlerInterface):
        CrawlerInterface.setObjectName("CrawlerInterface")
        CrawlerInterface.resize(900, 575)
        self.CrawlerCard = CardWidget(CrawlerInterface)
        self.CrawlerCard.setGeometry(QtCore.QRect(30, 50, 560, 460))
        self.CrawlerCard.setObjectName("CrawlerCard")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.CrawlerCard)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 541, 441))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.TitleLabel = TitleLabel(self.verticalLayoutWidget)
        self.TitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.TitleLabel.setObjectName("TitleLabel")
        self.verticalLayout.addWidget(self.TitleLabel)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.SearchLineEdit = SearchLineEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SearchLineEdit.sizePolicy().hasHeightForWidth())
        self.SearchLineEdit.setSizePolicy(sizePolicy)
        self.SearchLineEdit.setMinimumSize(QtCore.QSize(0, 40))
        self.SearchLineEdit.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.SearchLineEdit.setFont(font)
        self.SearchLineEdit.setToolTip("")
        self.SearchLineEdit.setStatusTip("")
        self.SearchLineEdit.setInputMask("")
        self.SearchLineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.SearchLineEdit.setObjectName("SearchLineEdit")
        self.verticalLayout.addWidget(self.SearchLineEdit)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(20, 10, 20, 10)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.containLabel = BodyLabel(self.verticalLayoutWidget)
        self.containLabel.setObjectName("containLabel")
        self.horizontalLayout_3.addWidget(self.containLabel)
        self.containLineEdit = LineEdit(self.verticalLayoutWidget)
        self.containLineEdit.setObjectName("containLineEdit")
        self.horizontalLayout_3.addWidget(self.containLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(20, 10, 20, 10)
        self.horizontalLayout.setSpacing(30)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sourceLabel = BodyLabel(self.verticalLayoutWidget)
        self.sourceLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.sourceLabel.setObjectName("sourceLabel")
        self.horizontalLayout.addWidget(self.sourceLabel)
        self.peopleCheckBox = CheckBox(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.peopleCheckBox.setFont(font)
        self.peopleCheckBox.setCheckable(True)
        self.peopleCheckBox.setChecked(True)
        self.peopleCheckBox.setObjectName("peopleCheckBox")
        self.horizontalLayout.addWidget(self.peopleCheckBox)
        self.thepaperCheckBox = CheckBox(self.verticalLayoutWidget)
        self.thepaperCheckBox.setChecked(True)
        self.thepaperCheckBox.setTristate(False)
        self.thepaperCheckBox.setObjectName("thepaperCheckBox")
        self.horizontalLayout.addWidget(self.thepaperCheckBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(20, 10, 20, 10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.modeLabel = BodyLabel(self.verticalLayoutWidget)
        self.modeLabel.setObjectName("modeLabel")
        self.horizontalLayout_2.addWidget(self.modeLabel)
        self.modeComboBox = ComboBox(self.verticalLayoutWidget)
        self.modeComboBox.setObjectName("modeComboBox")
        self.horizontalLayout_2.addWidget(self.modeComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(20, 10, 20, 10)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.rangeLabel = BodyLabel(self.verticalLayoutWidget)
        self.rangeLabel.setObjectName("rangeLabel")
        self.horizontalLayout_4.addWidget(self.rangeLabel)
        self.startSpinBox = SpinBox(self.verticalLayoutWidget)
        self.startSpinBox.setMinimum(1)
        self.startSpinBox.setMaximum(9999)
        self.startSpinBox.setObjectName("startSpinBox")
        self.horizontalLayout_4.addWidget(self.startSpinBox)
        self.rangeLabel_2 = BodyLabel(self.verticalLayoutWidget)
        self.rangeLabel_2.setMinimumSize(QtCore.QSize(50, 0))
        self.rangeLabel_2.setMaximumSize(QtCore.QSize(50, 16777215))
        self.rangeLabel_2.setAlignment(QtCore.Qt.AlignCenter)
        self.rangeLabel_2.setObjectName("rangeLabel_2")
        self.horizontalLayout_4.addWidget(self.rangeLabel_2)
        self.endSpinBox = SpinBox(self.verticalLayoutWidget)
        self.endSpinBox.setMinimum(1)
        self.endSpinBox.setMaximum(10000)
        self.endSpinBox.setProperty("value", 10000)
        self.endSpinBox.setObjectName("endSpinBox")
        self.horizontalLayout_4.addWidget(self.endSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.logPlainTextEdit = PlainTextEdit(CrawlerInterface)
        self.logPlainTextEdit.setGeometry(QtCore.QRect(620, 50, 251, 460))
        self.logPlainTextEdit.setReadOnly(True)
        self.logPlainTextEdit.setBackgroundVisible(False)
        self.logPlainTextEdit.setCenterOnScroll(False)
        self.logPlainTextEdit.setObjectName("logPlainTextEdit")

        self.retranslateUi(CrawlerInterface)
        QtCore.QMetaObject.connectSlotsByName(CrawlerInterface)

    def retranslateUi(self, CrawlerInterface):
        _translate = QtCore.QCoreApplication.translate
        CrawlerInterface.setWindowTitle(_translate("CrawlerInterface", "Form"))
        self.TitleLabel.setText(_translate("CrawlerInterface", "新闻爬虫"))
        self.SearchLineEdit.setPlaceholderText(_translate("CrawlerInterface", "请输入搜索关键词"))
        self.containLabel.setToolTip(_translate("CrawlerInterface", "<html><head/><body><p>如果新闻标题或内容没有输入框内的词语，则不会获取</p></body></html>"))
        self.containLabel.setText(_translate("CrawlerInterface", "指定包含词语（空格隔开）"))
        self.containLineEdit.setText(_translate("CrawlerInterface", "芯片 芯"))
        self.sourceLabel.setText(_translate("CrawlerInterface", "新闻源"))
        self.peopleCheckBox.setText(_translate("CrawlerInterface", "人民网"))
        self.thepaperCheckBox.setText(_translate("CrawlerInterface", "澎湃新闻网"))
        self.modeLabel.setToolTip(_translate("CrawlerInterface", "<html><head/><body><p><br/></p></body></html>"))
        self.modeLabel.setText(_translate("CrawlerInterface", "获取模式"))
        self.rangeLabel.setToolTip(_translate("CrawlerInterface", "<html><head/><body><p>搜索页面的起止范围，上限为10000。</p><p>注意：如果选择获取文章内容，此处设置的终止范围将不起作用，默认为到最后一篇（最多10000）。</p></body></html>"))
        self.rangeLabel.setWhatsThis(_translate("CrawlerInterface", "<html><head/><body><p><br/></p></body></html>"))
        self.rangeLabel.setText(_translate("CrawlerInterface", "页起止范围"))
        self.rangeLabel_2.setText(_translate("CrawlerInterface", "到"))
        self.logPlainTextEdit.setPlainText(_translate("CrawlerInterface", "欢迎使用新闻爬虫！"))
from qfluentwidgets import BodyLabel, CardWidget, CheckBox, ComboBox, LineEdit, PlainTextEdit, SearchLineEdit, SpinBox, TitleLabel
