import csv
import os

import jieba
import jieba.analyse
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import time

allcountry_list = [
    '阿富汗', '阿尔巴尼亚', '阿尔及利亚', '安道尔', '安哥拉', '安提瓜和巴布达', '阿根廷', '亚美尼亚', '澳大利亚',
    '奥地利',
    '阿塞拜疆', '巴哈马', '巴林', '孟加拉', '巴巴多斯', '白俄罗斯', '比利时', '伯利兹', '贝宁', '不丹', '玻利维亚',
    '波黑', '博茨瓦纳', '巴西', '文莱', '保加利亚', '布基纳法索', '布隆迪', '柬埔寨', '喀麦隆', '加拿大', '佛得角',
    '中非', '乍得', '智利', '中国', '哥伦比亚', '科摩罗', '刚果', '哥斯达黎加', '克罗地亚', '古巴', '塞浦路斯',
    '捷克', '刚果(扎伊尔)', '丹麦', '吉布提', '多米尼加', '东帝汶', '厄瓜多尔', '埃及', '萨尔瓦多', '赤道几内亚',
    '厄立特里亚', '爱沙尼亚', '埃斯瓦蒂尼', '埃塞俄比亚', '斐济', '芬兰', '法国', '加蓬', '冈比亚', '格鲁吉亚',
    '德国', '加纳', '希腊', '格林纳达', '危地马拉', '几内亚', '几内亚比绍', '圭亚那', '海地', '洪都拉斯', '匈牙利',
    '冰岛', '印度', '印度尼西亚', '伊朗', '伊拉克', '爱尔兰', '以色列', '意大利', '牙买加', '日本', '约旦',
    '哈萨克斯坦',
    '肯尼亚', '基里巴斯', '朝鲜', '韩国', '科威特', '吉尔吉斯斯坦', '老挝', '拉脱维亚', '黎巴嫩', '莱索托', '利比里亚',
    '利比亚', '列支敦士登', '立陶宛', '卢森堡', '马其顿', '马达加斯加', '马拉维', '马来西亚', '马尔代夫', '马里',
    '马耳他',
    '马绍尔群岛', '毛里塔尼亚', '毛里求斯', '墨西哥', '密克罗尼西亚', '摩尔多瓦', '摩纳哥', '蒙古', '黑山', '摩洛哥',
    '莫桑比克',
    '缅甸', '纳米比亚', '瑙鲁', '尼泊尔', '荷兰', '新西兰', '尼加拉瓜', '尼日尔', '尼日利亚', '挪威', '阿曼',
    '巴基斯坦',
    '帕劳', '巴勒斯坦', '巴拿马', '巴布亚新几内亚', '巴拉圭', '秘鲁', '菲律宾', '波兰', '葡萄牙', '卡塔尔', '罗马尼亚',
    '俄罗斯',
    '卢旺达', '圣基茨和尼维斯', '圣卢西亚', '圣文森特和格林纳丁斯', '萨摩亚', '圣马力诺', '圣多美和普林西比',
    '沙特阿拉伯',
    '塞内加尔', '塞尔维亚', '塞舌尔', '塞拉利昂', '新加坡', '斯洛伐克', '斯洛文尼亚', '所罗门群岛', '索马里', '南非',
    '南苏丹',
    '西班牙', '斯里兰卡', '苏丹', '苏里南', '斯威士兰', '瑞典', '瑞士', '叙利亚', '塔吉克斯坦', '坦桑尼亚', '泰国',
    '东帝汶',
    '多哥', '汤加', '特立尼达和多巴哥', '突尼斯', '土耳其', '土库曼斯坦', '图瓦卢', '乌干达', '乌克兰',
    '阿拉伯联合酋长国',
    '英国', '美国', '乌拉圭', '乌兹别克斯坦', '瓦努阿图', '梵蒂冈', '委内瑞拉', '越南', '也门', '赞比亚', '津巴布韦'
]


# 合并信息
def merge_info(file_path, df):
    df_temp = pd.read_csv(file_path, encoding='UTF-8-SIG')
    df = pd.concat([df, df_temp], axis=0, join='outer', ignore_index=True)
    return df


# 提取关键词(输入搜索后自动)
def extract_words(file_path, name_backlist, keyword, keyword_source, output_callback=None):
    data = []
    df = pd.read_csv(file_path)
    count = 1
    name_blackset = set(name_backlist)
    for index, title, text in zip(df.index, df['标题'], df['正文']):
        processing_message = f"正在处理{keyword_source}的'{keyword}'关键词的第{count}篇文章"
        if output_callback:
            output_callback(processing_message)
        # print(processing_message)  # 如果需要在控制台中看到输出

        count += 1
        text = str(text)

        # 关键词后续还可增加别的
        summary = get_summary(text, 2)

        country_list = jieba.analyse.extract_tags(text, withWeight=False, allowPOS=('ns',))
        country_list = [c for c in country_list if c in allcountry_list]
        country = ','.join(map(str, country_list))

        name_list = jieba.analyse.extract_tags(text, topK=5, withWeight=False, allowPOS=('nr',))
        name_list = [name for name in name_list if name not in name_blackset]
        name = ','.join(map(str, name_list))

        hot_word_list = jieba.analyse.extract_tags(
            text, topK=10, withWeight=False, allowPOS=('n', 'nr', 'ns', 'nt', 'nz',)
        )
        hot_word = ','.join(map(str, hot_word_list))

        data_info = {
            "文章标题": title,
            "摘要": summary,
            "国家": country,
            "人物名": name,
            "关键词": hot_word,
        }

        data.append(data_info)
        time.sleep(0.1)

    return data


# 存储文件csv形式
def save_in_csv(data, keyword, keyword_source):
    with open(f'work_file/process_data/output_data_{keyword_source}_{keyword}.csv', 'w', encoding='UTF-8-SIG',
              newline='') as csvfile:
        fieldnames = ['文章标题', '摘要', '国家', '人物名', '关键词']
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        csvwriter.writeheader()
        for data_info in data:
            csvwriter.writerow(data_info)
    print('文件存储完毕')


# 自定义基于句子位置的摘要函数
def get_summary(text, n):
    sentences = text.split('。')  # 假设文章以句号分隔
    sentences = [sentence.strip() + '。' for sentence in sentences if sentence.strip()]  # 去除空句子

    # 选择前 n 个句子作为摘要
    summary = ''.join(sentences[:n])

    return summary


# 生成关键人物
def generate_important_name(file_path, keyword, keyword_source):
    df = pd.read_csv(file_path, encoding='UTF-8-SIG')
    name_count = Counter()
    for name_line in df['人物名']:
        name_list = [name.strip() for name in str(name_line).split(',')]
        if name_list is not []:
            for name in name_list:
                if name != 'nan':
                    name_count[name] += 1

    # 获取出现次数最多的20个元素
    most_common_names = name_count.most_common(20)

    if not os.path.exists('work_file/important_name'):
        os.makedirs('work_file/important_name')
    with open(f"work_file/important_name/{keyword_source}_{keyword}.csv", 'w', encoding='UTF-8-SIG',
              newline='') as csvfile:
        fieldnames = ['姓名', '出现次数']
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        csvwriter.writeheader()
        data = []
        for name, count in most_common_names:
            data_info = {
                '姓名': name,
                '出现次数': count,
            }
            data.append(data_info)
        for data_info in data:
            csvwriter.writerow(data_info)


# 生成热点事件
def generare_important_incident(file_path, keyword, keyword_source):
    df = pd.read_csv(file_path, encoding='UTF-8-SIG')
    df.sort_values(by='重复篇数', inplace=True, ascending=False)
    try:
        df = df.head(5)
    except Exception as e:
        print(f"出现了个错误 {e}")
    if not os.path.exists('work_file/important_incident'):
        os.makedirs('work_file/important_incident')
    with open(f"work_file/important_incident/{keyword_source}_{keyword}.csv", 'w', encoding='UTF-8-SIG',
              newline='') as csvfile:
        fieldnames = ['事件', '出现次数']
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        csvwriter.writeheader()
        data = []
        for title, count in zip(df['标题'], df['重复篇数']):
            data_info = {
                '事件': title,
                '出现次数': count,
            }
            data.append(data_info)
        for data_info in data:
            csvwriter.writerow(data_info)


if __name__ == "__main__":
    keyword_list = ['芯片封锁', '芯片禁令', '芯片市场', '芯片制造', '中国芯片']
    name_backlist = [
        '智能化', '安全性', '智慧', '华为', '智能家居', '白皮书', '玉米', '白宫', '卫星',
        '高清',
    ]
    source_list = ['people', 'thepaper']
    df = pd.DataFrame(columns=['文章标题', '摘要', '国家', '人物名', '关键词'])
    for source in source_list:
        for keyword in keyword_list:
            clean_file_path = f"work_file/clean_data/output_text_afterclean_{source}_{keyword}.csv"

            processed_file_path = f"work_file/process_data/output_data_{source}_{keyword}.csv"

            data = extract_words(clean_file_path, name_backlist, keyword, source)

            save_in_csv(data, keyword, source)

            generate_important_name(processed_file_path, keyword, source)

            generare_important_incident(clean_file_path, keyword, source)

            df = merge_info(processed_file_path, df)

    df.to_csv('work_file/merge_data/merge_data_process.csv', encoding='UTF-8-SIG')
