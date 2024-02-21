from PyQt5.QtWidgets import QWidget

from view.UI_MdiInterface import Ui_MdiInterface

class MdiInterface(Ui_MdiInterface, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)