import math
import requests
import json
import time
import codecs
from urllib import parse
from bs4 import BeautifulSoup
from requests import ReadTimeout, JSONDecodeError, ConnectTimeout
import csv
from collections import Counter
import os


# 获取当前时间的时间戳并返回指定格式的时间
def get_time():
    curr_time = time.time()
    curr_time_local = time.localtime(curr_time)
    curr_time_str = time.strftime("%H:%M:%S", curr_time_local)
    return curr_time_str


# 若标题或内容中含有“芯片”或“芯”则返回True
def filter_chip(title, content='', filter_list=None):
    if filter_list is None:
        filter_list = ['芯片', '芯']
    title_flag, content_flag = False, False
    for word in filter_list:
        if title.find(word) >= 0:
            title_flag = True
    if content != '':
        for word in filter_list:
            if content.find(word) >= 0:
                content_flag = True
    if title_flag or content_flag:
        return True
    else:
        return False


# 获取人民网搜索页面返回的内容
def get_people_search(keyword, current):
    cookies = {
        '__jsluid_h': 'f75ffca7f228a61235b06c9f10e43d3e',
        'sso_c': '0',
        'sfr': '1',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'http://search.people.cn',
        'Referer': '',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/117.0.0.0'
                      'Safari/537.36 Edg/117.0.2045.60',
    }

    json_data = {
        'key': '',
        'page': 1,
        'limit': 10,
        'hasTitle': True,
        'hasContent': True,
        'isFuzzy': True,
        'type': 0,
        'sortType': 2,
        'startTime': 0,
        'endTime': 0,
    }

    url = 'http://search.people.cn/s/?keyword=' + parse.quote(keyword)  # url encoding
    headers['Referer'] = url
    json_data['key'] = keyword
    json_data['page'] = current

    # 使用try-except，便于处理异常情况
    try:
        response = requests.post(
            'http://search.people.cn/search-platform/front/search',
            cookies=cookies,
            headers=headers,
            json=json_data,
            verify=False,
        )

        # 状态码200代表成功响应
        if response.status_code == 200:
            # 解析为json，并返回，附上一个成功标记
            res_json = response.json()
            return res_json, '', True
        else:
            return {}, '获取网页发生错误！网页状态码：{}'.format(response.status_code), False
    except (ReadTimeout, JSONDecodeError) as e:
        return {}, '获取网页超时！（本机网络无连接/IP被网站封锁）请稍后再试！', False


# 读取保存在本地的新闻链接列表
def read_search_list(keyword, name):
    path = 'data/list/' + name + keyword + '.json'
    if os.path.exists(path):
        load_f = codecs.open(path, 'r', encoding="utf8")
        list_json = json.load(load_f)
        return list_json['data']
    else:
        return []


# unused
def filter_search_list(keyword, name):
    path = 'data/list/' + name + keyword + '.json'
    load_f = codecs.open(path, 'r', encoding="utf8")
    list_json = json.load(load_f)
    search_list_old = list_json['data']
    search_list_new = []
    for obj in search_list_old:
        if obj['title'].find('芯片') >= 0 or obj['title'].find('芯') >= 0:
            search_list_new.append(obj)
    news_list_json = {'updateTime': int(time.time()), 'data': search_list_new}
    path = 'data/list/' + name + 'new_' + keyword + '.json'
    dump_f = open(path, 'w', encoding="utf8")
    json.dump(news_list_json, dump_f, ensure_ascii=False)


# 整体将重复出现的链接进行标记
def find_repeat_news_people(keyword):
    path = 'data/list/people_list_' + keyword + '.json'
    load_f = codecs.open(path, 'r', encoding="utf8")
    list_json = json.load(load_f)
    search_list = list_json['data']
    counter = Counter()
    for obj in search_list:
        counter[obj['title']] = counter[obj['title']] + 1
        if counter[obj['title']] > 1:
            obj['isRepeat'] = True
    news_list_json = {'updateTime': int(time.time()), 'data': search_list}
    dump_f = open(path, 'w', encoding="utf8")
    json.dump(news_list_json, dump_f, ensure_ascii=False)
    return path


# 获取人民网新闻主体内容
def get_people_news(keyword, url, is_repeat, inputTime):
    cookies = {
        'sso_c': '0',
        'sfr': '1',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Encoding': 'gzip,deflate',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'http://search.people.cn/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60',
    }

    try:
        response = requests.get(
            url=url,
            cookies=cookies,
            headers=headers,
            verify=False,
        )

        if response.status_code == 200:
            # 获取并指定response的编码格式
            response.encoding = response.text.split('charset=')[1].split("\"/>")[0]
            res_html = response.text
            # 使用bs4对html进行处理
            soup = BeautifulSoup(res_html, 'html.parser')
            title, author, source, editor = '', '', '', ''
            is_video = False
            # 针对不同格式获取标题、作者、编辑、来源、正文
            if soup.find(attrs={'class': 'col col-1 fl'}) is not None:
                print('found: col col-1 fl')
                content = soup.find(attrs={'class': 'col col-1 fl'})
                title = content.find(name='h1').string
                author = content.find(attrs={'class': 'author cf'}).string
                if content.find(attrs={'class': 'col-1-1 fl'}) is not None:
                    if content.find(attrs={'class': 'col-1-1 fl'}).a is not None:
                        source = content.find(attrs={'class': 'col-1-1 fl'}).a.string
                elif content.find(attrs={'class': 'col-1-1'}) is not None:
                    if content.find(attrs={'class': 'col-1-1'}).a is not None:
                        source = content.find(attrs={'class': 'col-1-1'}).a.string
                p = content.find(attrs={'class': 'rm_txt_con cf'}).find_all(name='p')
            elif soup.find(attrs={'class': 'layout rm_txt cf'}) is not None:
                print('found: layout rm_txt cf')
                layout = soup.find(attrs={'class': 'layout rm_txt cf'})
                content = layout.find(attrs={'class': 'col col-1'})
                title = content.find(name='h1').string
                if content.find(attrs={'class': 'author cf'}) is not None:
                    author = content.find(attrs={'class': 'author cf'}).string
                if content.find(attrs={'class': 'col-1-1'}) is not None:
                    if content.find(attrs={'class': 'col-1-1'}).a is not None:
                        source = content.find(attrs={'class': 'col-1-1'}).a.string
                p = content.find(attrs={'class': 'rm_txt_con cf'}).find_all(name='p')
            elif soup.find(attrs={'class': 'text_c'}) is not None:
                print('found: text_c')
                content = soup.find(attrs={'class': 'text_c'})
                title = content.find(name='h1').string
                # if content.find(attrs={'class': 'author cf'}) is not None:
                #     author = content.find(attrs={'class': 'author cf'}).string
                if content.find(attrs={'class': 'sou'}) is not None:
                    if content.find(attrs={'class': 'sou'}).a is not None:
                        source = content.find(attrs={'class': 'sou'}).a.string
                p = content.find(attrs={'class': 'show_text'}).find_all(name='p')
            elif soup.find(attrs={'class': 'articleCont'}) is not None:
                print('found: articleCont')
                content = soup.find(attrs={'class': 'articleCont'})
                title = content.find(name='h2').string
                if content.find(attrs={'class': 'artOri'}) is not None:
                    if content.find(attrs={'class': 'artOri'}).a is not None:
                        source = content.find(attrs={'class': 'artOri'}).a.string
                p = content.find(attrs={'class': 'artDet'}).find_all(name='p')
                editor = content.find(attrs={'class': 'editor'}).string
            elif soup.find(attrs={'class': 'clearfix w1000_320 text_title'}) is not None:
                print('found: clearfix w1000_320 text_title')
                content = soup.find(attrs={'class': 'clearfix w1000_320 text_con'})
                text_title = soup.find(attrs={'class': 'clearfix w1000_320 text_title'})
                title = text_title.find(name='h1').string
                author = ''
                if text_title.find(attrs={'class': 'fl'}) is not None:
                    if text_title.find(attrs={'class': 'fl'}).a is not None:
                        source = text_title.find(attrs={'class': 'fl'}).a.string
                if soup.find(attrs={'class': 'video video-wide fl'}) is not None:
                    is_video = True
                else:
                    p = content.find(attrs={'class': 'box_con'})
            elif soup.find(attrs={'class': 'w1000 clearfix tit-ld'}) is not None:
                print('found: w1000 clearfix tit-ld')
                text_title = soup.find(attrs={'class': 'w1000 clearfix tit-ld'})
                title = text_title.find(name='h2').string
                content = soup.find(attrs={'class': 'clearfix w1000_320 text_con'})
                author = ''
                if text_title.find(name='p').a is not None:
                    source = text_title.find(name='p').a.string
                if soup.find(attrs={'class': 'video fl'}) is not None:
                    is_video = True
                else:
                    p = content.find(attrs={'class': 'box_con'})
            elif soup.find(attrs={'class': 'col col-1 context-box'}) is not None:
                print('found: col col-1 context-box')
                content = soup.find(attrs={'class': 'col col-1 context-box'})
                title = content.find(name='h1').string
                if content.find(attrs={'class': 'author cf'}) is not None:
                    author = content.find(attrs={'class': 'author cf'}).string
                if content.find(attrs={'class': 'col-1-1'}).a is not None:
                    source = content.find(attrs={'class': 'col-1-1'}).a.string
                if soup.find(attrs={'class': 'video fl'}) is not None:
                    is_video = True
                else:
                    p = content.find(attrs={'class': 'rm_txt_con cf'}).find_all(name='p')
            elif soup.find(attrs={'class': 'p2j_text fl'}) is not None:
                print('found: p2j_text fl')
                content = soup.find(attrs={'class': 'p2j_text fl'})
                title = content.find(name='h1').string
                author = content.find(attrs={'class': 'author'}).string
                if content.find(name='h2').a is not None:
                    source = content.find(name='h2').a.string
                p = content.find(attrs={'class': 'gray box_text'}).find_all(name='p')
            elif soup.find(attrs={'class': 'pic_content clearfix'}) is not None:
                print('found: pic_content clearfix')
                title_con = soup.find(attrs={'class': 'pic_content clearfix'})
                title = title_con.find(name='h1').string
                # author = content.find(attrs={'class': 'author'}).string
                content = soup.find(attrs={'class': 'content clear clearfix'})
                # if content.find(name='h2').a is not None:
                #     source = content.find(name='h2').a.string
                p = content.find_all(name='p')
            elif soup.find(attrs={'class': 'lypic rm_txt cf'}) is not None:
                print('found: lypic rm_txt cf')
                content = soup.find(attrs={'class': 'lypic rm_txt cf'})
                title = content.find(attrs={'id': 'newstit'}).string
                if content.find(attrs={'class': 'author cf'}) is not None:
                    author = content.find(attrs={'class': 'author cf'}).string
                if content.find(attrs={'class': 'col-1-1 fl'}).a is not None:
                    source = content.find(attrs={'class': 'col-1-1 fl'}).a.string
                p = content.find(attrs={'class': 'rm_txt_con cf'}).find_all(name='p')
            elif soup.find(attrs={'class': 'w1200 rm_txt cf'}) is not None:
                print('found: w1200 rm_txt cf')
                content = soup.find(attrs={'class': 'w1200 rm_txt cf'})
                title = content.find(name='h1').string
                if content.find(attrs={'class': 'author cf'}) is not None:
                    author = content.find(attrs={'class': 'author cf'}).string
                if content.find(attrs={'class': 'col-1-1'}).a is not None:
                    source = content.find(attrs={'class': 'col-1-1'}).a.string
                p = content.find(attrs={'class': 'rm_txt_con cf'}).find_all(name='p')
            elif soup.find(attrs={'class': 'w1000 d2_content txt_content clearfix'}) is not None:
                print('found: w1000 d2_content txt_content clearfix')
                content = soup.find(attrs={'class': 'w1000 d2_content txt_content clearfix'})
                title = content.find(name='h1').string
                if content.find(attrs={'class': 'day'}) is not None:
                    if content.find(attrs={'class': 'day'}).a is not None:
                        source = content.find(attrs={'class': 'day'}).a.string
                p = content.find(attrs={'class': 'txt clearfix'}).find_all(name='p')
                editor = content.find(attrs={'class': 'edit'}).string
            # 如果获取的html无法解析，则raise一个exception人工处理（
            else:
                raise Exception("HtmlNotKnown")

            body = ''
            # 如果不是重复出现的文章或视频才获取正文内容，减小文件体积及处理压力
            if not is_repeat:
                if not is_video:
                    for j in p:
                        paragraph = j.string
                        if paragraph is not None:
                            body += (paragraph + '\n')
            is_repeat = 0
            if is_repeat:
                is_repeat = 1
            if title == '':
                raise Exception("TitleNotFound")
            # 返回处理好的字典
            news_object = {'标题': title, '作者': author, '编辑': editor, '来源': source,
                           '发布时间': inputTime, '正文': body,
                           '重复标记': is_repeat}
            return news_object, '', True
        # 根据不同的错误类型返回不同日志
        else:
            return {}, '获取网页发生错误！网页状态码：{}'.format(response.status_code), False
    except ReadTimeout:
        return {}, '获取网页超时！（本机网络无连接/IP被网站封锁）请稍后再试！', False
    except ConnectTimeout:
        return {}, '网页无法连接，已跳过', False
    except Exception as e:
        return {}, repr(e), False


# 将获取的新闻保存到csv文件中
def save_news(keyword, news_list, start, name):
    path = 'data/' + name + keyword + '.csv'
    headers_csv = ['标题', '作者', '编辑', '来源', '发布时间', '正文', '重复标记']
    if start == 1:
        if os.path.exists(path):
            os.remove(path)
    # 以追加形式写入
    with open(path, 'a', encoding='UTF-8-SIG', newline='') as f:
        writer = csv.DictWriter(f, headers_csv)
        # 如果是从第一页获取的，则写入header
        if start == 1:
            writer.writeheader()
        writer.writerows(news_list)
    return path


# 将获取的链接保存到json文件中
def save_search(keyword, search_result, name):
    path = 'data/list/' + name + keyword + '.json'
    news_list_json = {'updateTime': int(time.time()), 'data': search_result}
    dump_f = open(path, 'w', encoding="utf8")
    json.dump(news_list_json, dump_f, ensure_ascii=False)
    return path


# 获取澎湃新闻网搜索页面返回的内容
def get_thepaper_search(keyword, current):
    cookies = {
        'acw_tc': 'ac11000116972817777207374e008a2bc970529a09634592d869c486a7c102',
        'ariaDefaultTheme': 'undefined',
    }

    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'https://www.thepaper.cn',
        'Referer': 'https://www.thepaper.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60',
        'sec-ch-ua': '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {'word': keyword, 'orderType': 3, 'pageNum': current, 'pageSize': 10, 'searchType': 1}
    try:
        response = requests.post('https://api.thepaper.cn/search/web/news', cookies=cookies, headers=headers,
                                 json=json_data)
        if response.status_code == 200:
            res_json = response.json()
            return res_json, '', True
        else:
            return {}, '获取网页发生错误！网页状态码：{}'.format(response.status_code), False
    except (ReadTimeout, JSONDecodeError) as e:
        return {}, '获取网页超时！（本机网络无连接/IP被网站封锁）请稍后再试！', False


# 获取澎湃新闻网新闻的主体内容
def get_thepaper_news(keyword, url, is_repeat, pubTime):
    cookies = {
        'menuIds': '[25949,26916,25950,122908,25951,119908,36079,119489,25952,25953,26161,-8,-21,-24,122153,-1]',
        'ariaDefaultTheme': 'undefined',
    }

    headers = {
        'authority': 'www.thepaper.cn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'referer': '',
        'sec-ch-ua': '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60',
    }
    headers['referer'] = 'https://www.thepaper.cn/searchResult?id=' + parse.quote(keyword)
    try:
        response = requests.get(url=url, cookies=cookies, headers=headers)
        if response.status_code == 200:
            res_html = response.text
            soup = BeautifulSoup(res_html, 'html.parser')
            title, author, editor, source = '', '', '', ''
            if soup.find(attrs={'class': 'index_wrapper__L_zqV'}) is not None:
                content = soup.find(attrs={'class': 'index_wrapper__L_zqV'})
                title = content.find(name='h1').string
                author = content.find(attrs={'class': 'index_left__LfzyH'}).div.string
                source = content.find(name='a', attrs={'class': 'index_inherit__A1ImK'}).get_text().split(' ')[0]
                editor_all = content.find(attrs={'class': 'index_copyrightBox__3Hx3O'}).find(
                    attrs={'class': 'ant-space ant-space-horizontal ant-space-align-center'}).find_all(
                    name='div')
                p = content.find(attrs={'class': 'index_cententWrap__Jv8jK'}).find_all(name='p')
            elif soup.find(attrs={'class': 'header_title__vP_8V'}) is not None:
                title = soup.find(attrs={'class': 'header_title__vP_8V'}).string
                content = soup.find(attrs={'class': 'header_title__vP_8V'}).parent
                source = content.find(name='a', attrs={'class': 'index_inherit__A1ImK'}).get_text().split('>')[0]
                p = content.find_all(name='p')
                source_all = content.find_all(attrs={'class': 'header_source__pJWco'})
                editor_all = source_all[1].find(
                    attrs={'class': 'ant-space ant-space-horizontal ant-space-align-center'}).find_all(
                    name='div')
            else:
                raise ConnectTimeout

            body = ''
            for j in p:
                paragraph = j.string
                if paragraph is not None:
                    body += (paragraph + '\n')
            for k in editor_all:
                edt = k.get_text()
                if edt.find('记者') > 0:
                    author = edt
                else:
                    editor += (edt + ' ')
            is_repeat = 0
            if is_repeat:
                is_repeat = 1
            news_object = {'标题': title, '作者': author, '编辑': editor, '来源': source,
                           '发布时间': pubTime, '正文': body,
                           '重复标记': is_repeat}
            return news_object, '', True
        else:
            return {}, '获取网页发生错误！网页状态码：{}'.format(response.status_code), False
    except ReadTimeout:
        return {}, '获取网页超时！（本机网络无连接/IP被网站封锁）请稍后再试！', False
    except ConnectTimeout:
        return {}, '网页无法连接，已跳过', False
    except Exception as e:
        return {}, repr(e), False
