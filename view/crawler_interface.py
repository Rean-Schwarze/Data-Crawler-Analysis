# coding:utf-8
import math
import os
import time

from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QCompleter, QApplication
from qfluentwidgets import MessageBox

from view.UI_CrawlerInterface import Ui_CrawlerInterface
import crawler


class CrawlerInterface(Ui_CrawlerInterface, QWidget):
    log = ''

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        # 创建目录
        if not os.path.exists('data/list'):
            os.makedirs('data/list')

        # add shadow effect to card
        self.setShadowEffect(self.CrawlerCard)

        # 绑定槽函数
        self.peopleCheckBox.stateChanged.connect(lambda: self.check_box_state(self.peopleCheckBox))
        self.thepaperCheckBox.stateChanged.connect(lambda: self.check_box_state(self.thepaperCheckBox))

        # 给combobox添加item
        self.modeComboBox.addItem('获取链接及文章内容')
        self.modeComboBox.addItem('获取链接')
        self.modeComboBox.addItem('获取文章内容（需链接）')

        # 设置自动填充内容
        keywords = ['芯片封锁', '芯片禁令', '芯片制造', '芯片市场', '中国芯片', '芯片']
        self.completer = QCompleter(keywords, self.SearchLineEdit)
        self.completer.setMaxVisibleItems(10)
        self.SearchLineEdit.setCompleter(self.completer)

        self.SearchLineEdit.searchSignal.connect(lambda: self.search(self.SearchLineEdit))

        # 将日志区域的光标移到末尾
        self.logPlainTextEdit.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)

    def setShadowEffect(self, card: QWidget):
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 15))
        shadowEffect.setBlurRadius(10)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)

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

    def get_contain_list(self):
        contain_str = self.containLineEdit.text()
        filter_list = contain_str.split()
        return filter_list

    # 检查两个新闻源是否都选上了，否则弹出提示
    def check_box_state(self, box):
        if self.peopleCheckBox.isChecked() and self.thepaperCheckBox.isChecked():
            self.peopleCheckBox.setChecked(True)
            self.thepaperCheckBox.setChecked(True)
        else:
            self.showMessageBox('提示', '全选以获得完整体验')

    # 往日志区域添加日志
    def insert_log(self, log):
        self.logPlainTextEdit.insertPlainText('\n' + crawler.get_time() + '    ' + log)
        # 将滚动条移到末尾
        scroll_bar = self.logPlainTextEdit.verticalScrollBar()
        scroll_bar.setSliderPosition(scroll_bar.maximum())
        QApplication.processEvents()  # 实时刷新

    # 获取人民网新闻链接（通过搜索）
    def search_people(self, keyword, start, end):
        self.insert_log('开始搜索：人民网')

        # 如果不是从第一页开始，则读取此前保存的文件，接着写
        if start != 1:
            search_result = crawler.read_search_list(keyword, 'people_list_')
        else:
            search_result = []
        current = start
        prev_title = ''
        curr_title = ''
        total_pages = 0
        size = 10

        while True:
            res_json, return_log, state = crawler.get_people_search(keyword, current)
            if state:
                records = res_json['data']['records']
                total = res_json['data']['total']
                total_pages = math.floor(total / size)
                for i in range(len(records)):
                    curr_title = records[i]['title']
                    content = records[i]['content']
                    inputTime = int(records[i]['inputTime'] / 1000)  # 人民网使用的是Long型时间戳，转换一下
                    # 过滤掉和芯片无关的结果
                    if crawler.filter_chip(curr_title, content, self.get_contain_list()):
                        repeat = False
                        # 先简单标记重复内容
                        if curr_title == prev_title:
                            repeat = True
                        dict_result = {'title': curr_title, 'inputTime': inputTime, 'url': records[i]['url'],
                                       'isRepeat': repeat}
                        search_result.append(dict_result)
                        prev_title = curr_title
                log = '成功获取第{0}页，当前链接数：{1}'.format(current, len(search_result))
                self.insert_log(log)
            else:
                log = return_log + '  当前页数：{}'.format(current)
                self.insert_log('发生错误：' + log)
                self.insert_log('已停止')
                break

            current += 1
            if current > end or current > total_pages:
                if current > total_pages:
                    self.insert_log('到达搜索结果最后一页，已停止')
                break
            else:
                time.sleep(0.2)  # sleep一下，保持界面流畅

        # 保存并标记重复内容
        path = crawler.save_search(keyword, search_result, 'people_list_')
        path = crawler.find_repeat_news_people(keyword)
        self.insert_log('结果已保存至：' + path + '\n')

    # 获取澎湃新闻网新闻链接（通过搜索）
    def search_thepaper(self, keyword, start, end):
        self.insert_log('开始搜索：澎湃新闻网')

        if start != 1:
            search_result = crawler.read_search_list(keyword, 'thepaper_list_')
        else:
            search_result = []
        current = start
        prev_title = ''
        curr_title = ''
        total_pages = 0

        while True:
            res_json, return_log, state = crawler.get_thepaper_search(keyword, current)
            if state:
                res_list = res_json['data']['list']
                total_pages = res_json['data']['pages']
                for i in range(len(res_list)):
                    contId = res_list[i]['contId']
                    curr_title = res_list[i]['name']
                    is_repeat = False
                    if curr_title == prev_title:
                        is_repeat = True
                    pubTime = int(math.floor(res_list[i]['pubTimeLong'] / 1000))
                    dict_result = {'contId': contId, 'title': curr_title, 'pubTime': pubTime, 'isRepeat': is_repeat}
                    search_result.append(dict_result)
                    prev_title = curr_title
                log = '成功获取第{0}页，当前链接数：{1}'.format(current, len(search_result))
                self.insert_log(log)
            else:
                log = return_log + '  当前页数：{}'.format(current)
                self.insert_log('发生错误：' + log)
                self.insert_log('已停止')
                break

            current += 1
            if current > end or current > total_pages:
                if current > total_pages:
                    self.insert_log('到达搜索结果最后一页，已停止')
                break
            else:
                time.sleep(0.2)

        path = crawler.save_search(keyword, search_result, 'thepaper_list_')
        self.insert_log('结果已保存至：' + path + '\n')

    # 获取人民网新闻内容
    def get_news_people(self, keyword, start, search_list):
        self.insert_log('开始获取：人民网')
        news_list = []
        for i in range(start - 1, len(search_list)):
            # 只获取最多10000篇新闻
            if i % 10000 == 0 and i != 0:
                break
            url = search_list[i]['url']
            inputTime = search_list[i]['inputTime']
            is_repeat = search_list[i]['isRepeat']
            self.insert_log('正在获取第{0}篇文章【{1}】\n链接：{2}'.format(i, search_list[i]['title'], url))

            news_object, log, state = crawler.get_people_news(keyword, url, is_repeat, inputTime)
            if state:
                news_list.append(news_object)
                self.insert_log('成功获取【{}】\n'.format(news_object['标题']))
                time.sleep(0.1)
            else:
                self.insert_log('发生错误：' + log + '  当前索引：{}\n'.format(i + 1))
                # 如果网页Not Found，则直接跳过
                if log == '网页无法连接，已跳过' or log.find('404') >= 0:
                    continue
                # 其余错误则停止获取
                else:
                    self.insert_log('已停止')
                    break
        path = crawler.save_news(keyword, news_list, start, 'people_')
        self.insert_log('结果已保存至：' + path + '\n')

    # 获取澎湃新闻网新闻内容
    def get_news_thepaper(self, keyword, start, search_list):
        self.insert_log('开始获取：澎湃新闻网')
        news_list = []
        for i in range(start - 1, len(search_list)):
            url = 'https://www.thepaper.cn/newsDetail_forward_' + search_list[i]['contId']
            pubTime = search_list[i]['pubTime']
            is_repeat = search_list[i]['isRepeat']
            self.insert_log('正在获取第{0}篇文章【{1}】\n链接：{2}'.format(i, search_list[i]['title'], url))
            news_object, log, state = crawler.get_thepaper_news(keyword, url, is_repeat, pubTime)
            if state:
                news_list.append(news_object)
                self.insert_log('成功获取【{}】\n'.format(news_object['标题']))
                time.sleep(0.1)
            else:
                self.insert_log('发生错误：' + log + '  当前索引：{}\n'.format(i + 1))
                if log == '网页无法连接，已跳过':
                    continue
                else:
                    self.insert_log('已停止')
                    break
        path = crawler.save_news(keyword, news_list, start, 'thepaper_')
        self.insert_log('结果已保存至：' + path + '\n')

    # 点击搜索按钮的槽函数
    def search(self, line):
        # 先禁用按钮，避免出现bug
        self.SearchLineEdit.setEnabled(False)
        # 从各组件获取关键词、起止页面、搜索模式
        keyword = self.SearchLineEdit.text()
        start = self.startSpinBox.value()
        end = self.endSpinBox.value()
        mode = self.modeComboBox.currentIndex()

        self.insert_log('输入关键词：' + keyword)

        # 获取链接
        if mode == 1:
            if start <= end:
                self.insert_log('搜索模式：' + self.modeComboBox.currentText())
                if self.peopleCheckBox.isChecked():
                    self.search_people(keyword, start, end)
                if self.thepaperCheckBox.isChecked():
                    self.search_thepaper(keyword, start, end)
            else:
                self.showMessageBox('警告', '起始范围应小于终止范围！')
        # 获取正文（需链接）
        elif mode == 2:
            self.insert_log('搜索模式：' + self.modeComboBox.currentText())
            if self.peopleCheckBox.isChecked():
                path = 'data/list/people_list_' + keyword + '.json'
                if not os.path.exists(path):
                    self.showMessageBox('警告', '{}不存在！'.format(path))
                else:
                    self.get_news_people(keyword, start, crawler.read_search_list(keyword, 'people_list_'))
            if self.thepaperCheckBox.isChecked():
                path = 'data/list/thepaper_list_' + keyword + '.json'
                if not os.path.exists(path):
                    self.showMessageBox('警告', '{}不存在！'.format(path))
                else:
                    self.get_news_thepaper(keyword, start, crawler.read_search_list(keyword, 'thepaper_list_'))
        # 获取链接和正文
        elif mode == 0:
            if start <= end:
                self.insert_log('搜索模式：' + self.modeComboBox.currentText())
                if self.peopleCheckBox.isChecked():
                    self.search_people(keyword, start, end)
                    self.get_news_people(keyword, start, crawler.read_search_list(keyword, 'people_list_'))
                if self.thepaperCheckBox.isChecked():
                    self.search_thepaper(keyword, start, end)
                    self.get_news_thepaper(keyword, start, crawler.read_search_list(keyword, 'thepaper_list_'))
            else:
                self.showMessageBox('警告', '起始范围应小于终止范围！')
        # 流程结束，启用按钮
        self.SearchLineEdit.setEnabled(True)
