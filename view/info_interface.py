import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
import pandas as pd
from PyQt5.QtCore import pyqtSignal

from view.UI_InfoInterface import Ui_InfoInterface


class DataViewWindow(Ui_InfoInterface, QWidget):
    windowClosed = pyqtSignal()

    def __init__(self, title):
        super().__init__()
        self.setupUi(self)
        self.find_info(title)

    def closeEvent(self, event):
        # 当窗口关闭时，发射自定义信号windowClosed
        self.windowClosed.emit()

    def find_info(self, title):
        # 完整信息由两个文件拼凑而成
        if os.path.exists('work_file/merge_data/merge_data_clean.csv'):
            df = pd.read_csv('work_file/merge_data/merge_data_clean.csv')
            filter_row = df[df['标题'] == title].copy()
            filter_row.fillna('未知', inplace=True)
            filter_row = filter_row.to_dict(orient='records')
            self.title_line.setText(filter_row[0]['标题'])
            self.title_line.setCursorPosition(0)
            self.pubtime_line.setText(filter_row[0]['发布时间(y-m-d)'])
            self.author_line.setText(filter_row[0]['作者'])
            self.author_line.setCursorPosition(0)
            self.source_line.setText(filter_row[0]['来源'])
            self.source_line.setCursorPosition(0)
            self.repeat_line.setText(str(filter_row[0]['重复篇数']))

        if os.path.exists('work_file/merge_data/merge_data_process.csv'):
            df = pd.read_csv('work_file/merge_data/merge_data_process.csv')
            filter_row = df[df['文章标题'] == title].copy()
            filter_row.fillna('未知', inplace=True)
            filter_row = filter_row.to_dict(orient='records')
            self.country_line.setText(filter_row[0]['国家'])
            self.country_line.setCursorPosition(0)
            self.name_line.setText(filter_row[0]['人物名'])
            self.name_line.setCursorPosition(0)
            self.keyword_line.setText(filter_row[0]['关键词'])
            self.keyword_line.setCursorPosition(0)
            self.summary_line.setText(filter_row[0]['摘要'])
