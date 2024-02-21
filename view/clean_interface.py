from PyQt5.QtGui import QColor, QTextCursor
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QCompleter, QApplication, QTableWidgetItem
import time
from count_remove_repeat import count_remove_repeat_news, draw_pie
import pandas as pd
from PyQt5.QtCore import pyqtSignal
import os.path

from view.UI_CleanInterface import Ui_CleanInterface


def get_time():
    curr_time = time.time()
    curr_time_local = time.localtime(curr_time)
    curr_time_str = time.strftime("%H:%M:%S", curr_time_local)
    return curr_time_str


class CleanInterface(Ui_CleanInterface, QWidget):
    log = ''

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.start_clean.clicked.connect(self.start_clean_data)
        self.clean_log.clicked.connect(self.logPlainTextEdit.clear)
        self.loadPushButton.clicked.connect(self.load_data)

        # add shadow effect to card
        self.setShadowEffect(self.CleanCard)

        self.logPlainTextEdit.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)

        if not os.path.exists('work_file/merge_data'):
            os.makedirs('work_file/merge_data')
        if not os.path.exists('work_file/clean_data'):
            os.makedirs('work_file/clean_data')

        self.load_data()

    def load_data(self):
        self.loadPushButton.setEnabled(False)
        original_list = os.listdir('data')
        if original_list:
            df = pd.DataFrame(columns=['标题', '作者', '编辑', '来源', '发布时间', '正文', '重复标记'])
            for file in original_list:
                if not file.endswith('.csv'):
                    continue
                file_path = f'data/{file}'
                df = self.merge_info(file_path, df)
            df.to_csv('work_file/merge_data/merge_data_original.csv', encoding='UTF-8-SIG')

        # info_table的函数以及参数更新
        if os.path.exists('work_file/merge_data/merge_data_original.csv'):
            self.info_table.setColumnCount(2)
            column_names = ['标题', '发布时间']
            self.info_table.setHorizontalHeaderLabels(column_names)  # 自定义列名称
            self.info_table.setColumnWidth(0, 600)  # 设置第一列的宽度为600像素
            self.info_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # 设置表格无法被编辑
            df = pd.read_csv('work_file/merge_data/merge_data_original.csv', encoding='UTF-8-SIG')
            ser_title = df['标题']
            ser_pubtime = df['发布时间']
            data = {
                '标题': [element for element in ser_title],
                '发布时间': [element for element in ser_pubtime]
            }
            df = pd.DataFrame(data)
            self.loadPandasData(df)
        self.loadPushButton.setEnabled(True)

    def merge_info(self, file_path, df):
        df_temp = pd.read_csv(file_path, encoding='UTF-8-SIG')
        df = pd.concat([df, df_temp], axis=0, join='outer', ignore_index=True)
        return df

    def loadPandasData(self, data):
        # 获取行数和列数
        numRows, numCols = data.shape

        # 设置表格行数
        self.info_table.setRowCount(numRows)

        # 遍历pandas数据，将数据逐行添加到QTableWidget中
        for row in range(numRows):
            for col in range(numCols):
                item = QTableWidgetItem(str(data.iloc[row, col]))
                self.info_table.setItem(row, col, item)

    def setShadowEffect(self, card: QWidget):
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 15))
        shadowEffect.setBlurRadius(10)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)

    def insert_log(self, log):
        self.logPlainTextEdit.insertPlainText('\n' + get_time() + '    ' + log)
        scroll_bar = self.logPlainTextEdit.verticalScrollBar()
        scroll_bar.setSliderPosition(scroll_bar.maximum())
        QApplication.processEvents()

    def start_clean_data(self):
        self.start_clean.setEnabled(False)
        keyword_list = ['芯片封锁', '芯片禁令', '芯片市场', '芯片制造', '中国芯片']
        source_list = ['people', 'thepaper']
        num = 0
        bool = 0  # 判断是否存在文件
        self.insert_log('数据清洗中')
        df = pd.DataFrame(
            columns=['标题', '作者', '编辑', '来源', '发布时间(y-m)', '发布时间(y-m-d)', '正文', '重复标记',
                     '重复篇数'])
        for source in source_list:
            for keyword in keyword_list:
                file_path = f"data/{source}_{keyword}.csv"
                if os.path.exists(file_path):
                    bool = 1
                    num += count_remove_repeat_news(file_path, keyword, source)
                    file_path_clean = f"work_file/clean_data/output_text_afterclean_{source}_{keyword}.csv"
                    df = self.merge_info(file_path_clean, df)

        if bool == 1:
            # 清洗合并后重复的数据并进行统计
            df.drop_duplicates('标题', keep='first', inplace=True)
            num_clean_repeat = len(df)
            num_repeat = num - num_clean_repeat
            df = df.drop(columns='Unnamed: 0')
            df.to_csv('work_file/merge_data/merge_data_clean.csv', encoding='UTF-8-SIG')
            self.insert_log('数据清洗完毕')
            draw_pie(num_repeat, num_clean_repeat)
            self.insert_log(f"一共有:{num}篇新闻")
            self.insert_log(f"重复的篇数:{num_repeat}")
            self.insert_log(f"删除重复后的篇数:{num_clean_repeat}")
        self.start_clean.setEnabled(True)
