# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImageInterface.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ImageInteface(object):
    def setupUi(self, ImageInteface):
        ImageInteface.setObjectName("ImageInteface")
        ImageInteface.resize(900, 480)
        ImageInteface.setMaximumSize(QtCore.QSize(1200, 1000))
        self.PixmapLabel = PixmapLabel(ImageInteface)
        self.PixmapLabel.setGeometry(QtCore.QRect(0, 0, 900, 480))
        self.PixmapLabel.setObjectName("PixmapLabel")

        self.retranslateUi(ImageInteface)
        QtCore.QMetaObject.connectSlotsByName(ImageInteface)

    def retranslateUi(self, ImageInteface):
        _translate = QtCore.QCoreApplication.translate
        ImageInteface.setWindowTitle(_translate("ImageInteface", "Form"))
from qfluentwidgets import PixmapLabel