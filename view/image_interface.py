from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QEasingCurve, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from view.UI_ImageInterface import Ui_ImageInteface


class ImageInterface(Ui_ImageInteface, QWidget):
    def __init__(self, image_id):
        super().__init__()
        self.setupUi(self)
        self.displayImage(image_id)

    def displayImage(self, image_id):
        # 从文件中加载图像（这里假设图像文件名为image.jpg）
        image_path = f'work_file/image/{image_id}.png'
        print(image_path)
        image = QPixmap(image_path)
        size = image.size() * 0.5
        size_2 = size + QSize(10, 40)
        # 将图像显示在QLabel上
        self.setMaximumSize(size_2)
        self.PixmapLabel.resize(size)
        self.PixmapLabel.setPixmap(image.scaled(size))  # 调整图像大小以适应QLabel
        self.setWindowTitle(f'图像：{image_id}')
