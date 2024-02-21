from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QApplication
import pandas as pd
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from qfluentwidgets import MessageBox

from data_process import extract_words, save_in_csv, generare_important_incident, generate_important_name
from draw_image import generate_time_num_change, generate_good_or_bad_compare, generate_hot_name_incident, \
    generate_country, predict_market
import os.path

import time

from view.info_interface import DataViewWindow
from view.UI_ProcessInterface import Ui_ProcessInterface


def get_time():
    curr_time = time.time()
    curr_time_local = time.localtime(curr_time)
    curr_time_str = time.strftime("%H:%M:%S", curr_time_local)
    return curr_time_str


class DataProcessThread(QThread):
    update_signal_str = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DataProcessThread, self).__init__(parent)

    def merge_info(self, file_path, df):
        df_temp = pd.read_csv(file_path, encoding='UTF-8-SIG')
        df = pd.concat([df, df_temp], axis=0, join='outer', ignore_index=True)
        return df

    def run(self):
        if os.listdir('work_file/clean_data'):
            keyword_list = ['芯片封锁', '芯片禁令', '芯片市场', '芯片制造', '中国芯片']
            name_backlist = [
                '智能化', '安全性', '智慧', '华为', '智能家居', '白皮书', '玉米', '白宫', '卫星',
                '高清', '高通', '观察', '玉环', '北斗', '彭博社', '封锁', '荣获', '龙心', '高新区', '高达', '科学城',
                '高水平', '市场秩序', '许可证', '乌克兰', '小圈子', '福祉', '龙芯', '沃土', '无人驾驶', '高昂',
                '高精尖', '卓越', '紫光', '杜绝', '双循环'
            ]
            df = pd.DataFrame(columns=['文章标题', '摘要', '国家', '人物名', '关键词'])
            source_list = ['people', 'thepaper']
            for source in source_list:
                for keyword in keyword_list:
                    clean_file_path = f"work_file/clean_data/output_text_afterclean_{source}_{keyword}.csv"
                    process_file_path = f"work_file/process_data/output_data_{source}_{keyword}.csv"
                    if os.path.exists(clean_file_path):
                        data = extract_words(clean_file_path, name_backlist, keyword, source,
                                             output_callback=self.update_signal_str.emit)
                        save_in_csv(data, keyword, source)
                        generate_important_name(process_file_path, keyword, source)
                        generare_important_incident(clean_file_path, keyword, source)
                        df = self.merge_info(process_file_path, df)
            df.to_csv('work_file/merge_data/merge_data_process.csv', encoding='UTF-8-SIG')


class ProcessInterface(Ui_ProcessInterface, QWidget):
    log = ''

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.create_image_window = parent.create_image_window
        self.setupUi(self)

        if not os.path.exists('work_file/process_data'):
            os.makedirs('work_file/process_data')
        if not os.path.exists('work_file/important_incident'):
            os.makedirs('work_file/important_incident')
        if not os.path.exists('work_file/important_name'):
            os.makedirs('work_file/important_name')
        if not os.path.exists('work_file/image'):
            os.makedirs('work_file/image')

        # add shadow effect to card
        self.setShadowEffect(self.ProcessCard)

        self.progressBar.hide()
        self.disable_interactive_controls()
        self.logPlainTextEdit.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)

        # 将信息窗口参数化
        self.new_window = None

        self.load_data()

        self.start_process.clicked.connect(self.start_data_process)
        self.info_table.itemClicked.connect(self.on_table_item_clicked)
        self.clean_log.clicked.connect(self.logPlainTextEdit.clear)
        self.draw.clicked.connect(self.select_checkbox)
        self.loadPushButton.clicked.connect(self.load_data)

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

    def showMessageBox(self, title, content):
        w = MessageBox(
            title,
            content,
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        if w.exec():
            w.yesButton.setText('确定')

    def load_data(self):
        # info_table的函数以及参数更新
        if os.path.exists('work_file/merge_data/merge_data_clean.csv'):
            self.info_table.setColumnCount(2)
            column_names = ['标题', '发布时间']
            self.info_table.setHorizontalHeaderLabels(column_names)  # 自定义列名称
            self.info_table.setColumnWidth(0, 400)  # 设置第一列的宽度为400像素
            self.info_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # 设置表格无法被编辑
            df = pd.read_csv('work_file/merge_data/merge_data_clean.csv', encoding='UTF-8-SIG')
            ser_title = df['标题']
            ser_pubtime = df['发布时间(y-m-d)']
            data = {
                '标题': [element for element in ser_title],
                '发布时间': [element for element in ser_pubtime]
            }
            df = pd.DataFrame(data)
            self.loadPandasData(df)

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

    # 禁用控件函数
    def disable_interactive_controls(self):
        if not os.path.exists('work_file/merge_data/merge_data_process.csv'):
            self.country_count.setEnabled(False)
        if not os.path.exists('work_file/merge_data/merge_data_clean.csv'):
            self.time_num_change.setEnabled(False)
        if not os.path.exists('work_file/merge_data/merge_data_clean.csv'):
            self.repeat_news.setEnabled(False)
        if (os.path.exists('work_file/clean_data/output_text_afterclean_people_芯片市场.csv') and os.path.exists(
                'work_file/clean_data/output_text_afterclean_people_芯片制造.csv')) or (os.path.exists(
            'work_file/clean_data/output_text_afterclean_thepaper_芯片制造.csv') and os.path.exists(
            'work_file/clean_data/output_text_afterclean_thepaper_芯片市场.csv')):
            self.predict_market.setEnabled(True)
        else:
            self.predict_market.setEnabled(False)
        if os.path.exists('work_file/clean_data/output_text_afterclean_people_芯片封锁.csv') or os.path.exists(
                'work_file/clean_data/output_text_afterclean_thepaper_芯片封锁.csv'):
            self.good_or_bad.setEnabled(True)
        else:
            self.good_or_bad.setEnabled(False)
        if os.listdir('work_file/important_incident') and os.listdir('work_file/important_name'):
            self.hot_wordcloud.setEnabled(True)
        else:
            self.hot_wordcloud.setEnabled(False)
        self.clean_log.setEnabled(False)

    # 重新启用控件
    def enable_interactive_controls(self):
        self.country_count.setEnabled(True)
        self.time_num_change.setEnabled(True)
        self.draw.setEnabled(True)
        self.clean_log.setEnabled(True)
        # 开启绘制重复新闻饼图选项
        if os.path.exists('work_file/merge_data/merge_data_clean.csv'):
            self.repeat_news.setEnabled(True)
        # 开启绘制芯片市场、制造预测
        if (os.path.exists('work_file/clean_data/output_text_afterclean_people_芯片市场.csv') and os.path.exists(
                'work_file/clean_data/output_text_afterclean_people_芯片制造.csv')) or (os.path.exists(
            'work_file/clean_data/output_text_afterclean_thepaper_芯片制造.csv') and os.path.exists(
            'work_file/clean_data/output_text_afterclean_thepaper_芯片市场.csv')):
            self.predict_market.setEnabled(True)
        # 开启芯片封锁后果预测
        if os.path.exists('work_file/clean_data/output_text_afterclean_people_芯片封锁.csv') or os.path.exists(
                'work_file/clean_data/output_text_afterclean_thepaper_芯片封锁.csv'):
            self.good_or_bad.setEnabled(True)
        # 开启芯片封锁人点词云
        if os.listdir('work_file/important_incident') and os.listdir('work_file/important_name'):
            self.hot_wordcloud.setEnabled(True)

    def show_process_bar(self):
        self.progressBar.show()

    def finish_process(self):
        self.progressBar.hide()
        self.start_process.setEnabled(True)
        self.parent.navigationInterface.setEnabled(True)
        self.insert_log('处理完毕！')

    # 点击获取信息
    def on_table_item_clicked(self, item):
        # 获取点击的行和列
        row = item.row()
        # 获取点击行的数据
        title = self.info_table.item(row, 0).text()  # 获取标题

        # 如果窗口已经存在，则不再创建新窗口
        if self.new_window is None:
            self.new_window = DataViewWindow(title)
            self.new_window.windowClosed.connect(self.on_window_closed)  # 连接destroyed信号到槽函数
            self.new_window.show()

    # 窗口关闭时置为None方便后续创建新窗口
    def on_window_closed(self):
        # 窗口被关闭时，将 new_window 置为 None
        self.new_window = None

    # 绘图
    def draw_image(self, image_id):
        self.create_image_window(image_id)
        self.showMessageBox('提示', '图像{}已生成在左侧“图像结果”子界面！'.format(image_id))

    def select_checkbox(self):
        if self.country_count.isChecked():
            # 执行国家在新闻中占比的操作
            country_path = 'work_file/merge_data/merge_data_process.csv'
            if os.path.exists(country_path):
                generate_country(country_path)
            self.draw_image('counties')

        if self.repeat_news.isChecked():
            # 执行重复新闻占比的操作
            self.draw_image('pie_chart')

        if self.time_num_change.isChecked():
            # 执行新闻时间数量变化图的操作
            time_num_change_file_path = 'work_file/merge_data/merge_data_clean.csv'
            if os.path.exists(time_num_change_file_path):
                generate_time_num_change(time_num_change_file_path)
            self.draw_image('time_num_change')

        if self.predict_market.isChecked():
            # 执行芯片市场、制造趋势的操作
            source_list = []
            keyword_list = ['芯片市场', '芯片制造']
            predict_market_path = f'work_file/clean_data/output_text_afterclean_'
            for keyword in keyword_list:
                path = f'{predict_market_path}people_{keyword}.csv'
                if os.path.exists(path):
                    source_list.append('people')
                    break
            for keyword in keyword_list:
                path = f'{predict_market_path}thepaper_{keyword}.csv'
                if os.path.exists(path):
                    source_list.append('thepaper')
                    break
            if len(source_list) != 0:
                predict_market(predict_market_path, source_list, keyword_list)
            self.draw_image('predict_market')

        if self.good_or_bad.isChecked():
            # 执行芯片封锁后果预测的操作
            source_list = []
            good_or_bad_compare_file_path = f'work_file/clean_data/output_text_afterclean_'
            if os.path.exists(f'{good_or_bad_compare_file_path}people_芯片封锁.csv'):
                source_list.append('people')
            if os.path.exists(f'{good_or_bad_compare_file_path}thepaper_芯片封锁.csv'):
                source_list.append('thepaper')
            if len(source_list) != 0:
                generate_good_or_bad_compare(good_or_bad_compare_file_path, source_list)
            self.draw_image('good_or_bad_compare')

        if self.hot_wordcloud.isChecked():
            # 执行热点词云的操作
            source_list = []
            hot_name_incident_path = f'work_file/'
            if os.path.exists(f'{hot_name_incident_path}important_incident/people_芯片封锁.csv'):
                source_list.append('people')
            if os.path.exists(f'{hot_name_incident_path}important_incident/thepaper_芯片封锁.csv'):
                source_list.append('thepaper')
            if len(source_list) != 0:
                tip_list = ['important_incident/', 'important_name/']
                keyword = '芯片封锁'
                generate_hot_name_incident(hot_name_incident_path, tip_list, source_list, keyword)
            self.draw_image('wordcloud_芯片封锁')

    def start_data_process(self):
        self.start_process.setEnabled(False)
        self.parent.navigationInterface.setEnabled(False)
        # 创建并启动线程
        self.show_process_bar()
        self.data_process_thread = DataProcessThread()
        self.data_process_thread.update_signal_str.connect(self.insert_log)
        self.data_process_thread.finished.connect(self.enable_interactive_controls)
        self.data_process_thread.finished.connect(self.finish_process)
        self.data_process_thread.start()
