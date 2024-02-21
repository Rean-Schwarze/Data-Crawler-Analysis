from collections import Counter
import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import os


# 绘制饼图
def draw_pie(num1, num2):
    if not os.path.exists('work_file/image'):
        os.makedirs('work_file/image')

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['font.size'] = 18  # 设置字体大小为18
    labels = ['重复的篇数', '不重复的篇数']
    sizes = [num1, num2]
    colors = ['#ff9999', '#66b3ff']
    explode = (0.1, 0)  # 突出显示第一块（即“重复的篇数”）

    plt.figure(figsize=(10, 10))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title('新闻重复情况分布')
    plt.savefig('work_file/image/pie_chart.png')


# 生成一张所有爬取数据汇总大表用于绘饼图
def merge_info(file_path, df):
    df_temp = pd.read_csv(file_path, encoding='UTF-8-SIG')
    df = pd.concat([df, df_temp], axis=0, join='outer', ignore_index=True)
    return df


# 数据清洗
def count_remove_repeat_news(file_path, keyword, keyword_sorce):
    df = pd.read_csv(file_path, encoding='UTF-8-SIG')
    num_part = len(df)
    # 用于统计具体某一条新闻的重复次数
    cnt = Counter()
    for title in df['标题']:
        cnt[title] += 1

    # 数据清洗部分
    # 删除重复数据保留第一条
    df.drop_duplicates('标题', keep='first', inplace=True)

    # 删除正文、标题为空的视频新闻
    df.dropna(subset=['正文', '标题'], inplace=True)

    # 获取重复次数追加入信息表中
    list_repeat = []
    for title in df['标题']:
        list_repeat.append(cnt[title])
    df.loc[:, '重复篇数'] = list_repeat

    # 作者数据清洗
    list_author = []
    # 定义需要剔除的词列表列表中的''是关键不能去掉代表就算没有捕捉组依然会捕捉一个
    exclude_words = [
        '记者', '作者', '编辑', '河南日报社全媒体', '本报记者', '来源', '黑龙江日报', '人名网日报',
        '新甘肃·甘肃日报记者', '人民网记者', '实习生', '通讯员', '电子科技大学校长', '黑河日报', '文/图', '  '
    ]
    pattern = r'|'.join(re.escape(word) for word in exclude_words)
    for author in df['作者']:
        author = str(author)
        author = re.sub(pattern, ' ', author)
        author = re.sub(
            r'[&#8203;``oaicite:{"number":4,"invalid_reason":"Malformed citation 【】"}``&#8203;\[\]()（）□\n:： ]',
            ' ',
            author
        )
        author = re.sub('、', ' ', author)
        author = author.strip()
        list_author.append(author)

    df.drop(['作者'], axis=1, inplace=True)
    df.insert(1, '作者', list_author)

    # 责编数据清洗
    if not keyword_sorce == 'thepaper':
        list_editor = []
        for editor in df['编辑']:
            editor = str(editor)
            editor = editor.strip()
            editor = re.sub(r'[责任编辑:：]', '', editor)
            editor = re.sub(
                r'[&#8203;``oaicite:{"number":4,"invalid_reason":"Malformed citation 【】"}``&#8203;\[\]()]',
                '', editor
            )
            editor = editor.replace('\n', '')
            list_editor.append(editor)
        df.drop(['编辑'], axis=1, inplace=True)
        df.insert(2, '编辑', list_editor)

    # 发布时间转化
    list_pubtime_ym = []
    list_pubtime_ymd = []
    for pubtime in df['发布时间']:
        # 将时间戳转换为日期对象
        date_object_ymd = datetime.fromtimestamp(pubtime)
        formatted_date = date_object_ymd.strftime('%Y-%m-%d')
        list_pubtime_ymd.append(formatted_date)

        date_object_ym = datetime.fromtimestamp(pubtime)
        formatted_date = date_object_ym.strftime('%Y-%m')
        list_pubtime_ym.append(formatted_date)

    df.drop(['发布时间'], axis=1, inplace=True)
    df.insert(4, '发布时间(y-m)', list_pubtime_ym)
    df.insert(5, '发布时间(y-m-d)', list_pubtime_ymd)

    df.to_csv(f'work_file/clean_data/output_text_afterclean_{keyword_sorce}_{keyword}.csv', encoding='UTF-8-SIG')

    return num_part


if __name__ == "__main__":
    keyword_list = ['芯片封锁', '芯片禁令', '芯片市场', '芯片制造', '中国芯片']
    source_list = ['people', 'thepaper']
    num = 0

    print("数据清洗中")
    df = pd.DataFrame(
        columns=['标题', '作者', '编辑', '来源', '发布时间(y-m)', '发布时间(y-m-d)', '正文', '重复标记', '重复篇数'])
    for source in source_list:
        for keyword in keyword_list:
            file_path = f"work_file/original_data/{source}_{keyword}.csv"

            num += count_remove_repeat_news(file_path, keyword, source)

            file_path_clean = f"work_file/clean_data/output_text_afterclean_{source}_{keyword}.csv"

            df = merge_info(file_path_clean, df)

    # 清洗合并后重复的数据并进行统计
    df.drop_duplicates('标题', keep='first', inplace=True)
    num_clean_repeat = len(df)
    num_repeat = num - num_clean_repeat
    df.to_csv('work_file/merge_data/merge_data_clean.csv', encoding='UTF-8-SIG')

    print("数据清洗完毕")

    draw_pie(num_repeat, num_clean_repeat)

    print(f"一共有:{num}篇新闻")
    print(f"重复的篇数:{num_repeat}")
    print(f"删除重复后的篇数:{num_clean_repeat}")
