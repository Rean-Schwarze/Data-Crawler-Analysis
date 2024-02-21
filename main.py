import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QLocale, QUrl
from qfluentwidgets import FluentTranslator, SplitFluentWindow, NavigationItemPosition, \
    MessageBox, NavigationAvatarWidget
from qfluentwidgets import FluentIcon as FIF

from view.crawler_interface import CrawlerInterface
from view.clean_interface import CleanInterface
from view.image_interface import ImageInterface
from view.process_interface import ProcessInterface
from view.mdi_interface import MdiInterface


class Window(SplitFluentWindow):

    def __init__(self):
        super().__init__()

        # create sub interface
        self.crawlerInterface = CrawlerInterface(self)
        self.cleanInterface = CleanInterface(self)
        self.processInterface = ProcessInterface(self)
        self.mdiInterface = MdiInterface(self)

        # initialization
        self.initNavigation()
        self.initWindow()

        self.setMaximumSize(960, 540)

    def initNavigation(self):
        # add sub interface
        self.addSubInterface(self.crawlerInterface, FIF.BASKETBALL, '新闻爬虫')
        self.addSubInterface(self.cleanInterface, FIF.BROOM, '数据清洗')
        self.addSubInterface(self.processInterface, FIF.LIBRARY_FILL, '数据处理')
        self.addSubInterface(self.mdiInterface, FIF.PHOTO, '图像结果')

        self.navigationInterface.addItem(
            routeKey='settingInterface',
            icon=FIF.INFO,
            text='关于软件',
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )
        self.navigationInterface.setExpandWidth(200)

    def initWindow(self):
        self.resize(960, 540)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('"芯"闻热点')

        # 显示在屏幕中央
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    # 创建显示数据处理图像的窗口
    def create_image_window(self, image_id):
        self.image_window = ImageInterface(image_id)
        size = self.image_window.size()
        mdi_subwindow = QtWidgets.QMdiSubWindow()
        mdi_subwindow.setMaximumSize(size)
        mdi_subwindow.resize(size)
        mdi_subwindow.setWidget(self.image_window)
        # 添加到子界面中
        self.mdiInterface.mdiArea.addSubWindow(mdi_subwindow)
        mdi_subwindow.resize(300, 40)
        self.image_window.show()

    def showMessageBox(self):
        w = MessageBox(
            '关于软件',
            '作者：Rean、dj\n\n提示：\n在系统设置（以Windows11为例）-个性化-颜色-关闭“在标题栏和窗口边框上显示强调色”\n以获得更好体验',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        if w.exec():
            w.yesButton.setText('确定')


if __name__ == "__main__":
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QtWidgets.QApplication(sys.argv)

    # Internationalization
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)

    w = Window()
    w.show()
    sys.exit(app.exec_())
