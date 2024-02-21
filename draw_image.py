import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import numpy as np
from scipy.stats import linregress
from wordcloud import WordCloud

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['font.size'] = 18  # 设置字体大小为18

#画国家出现在新闻中的频率占比
def generate_country(file_path):
    df = pd.read_csv(file_path, encoding='UTF-8-SIG')

    country_list = []
    #清洗掉没有提及国家的新闻
    df.dropna(subset=['国家', ], inplace=True)
    for country_link in df['国家']:
        country_link = str(country_link)
        country_list.extend(country_link.split(','))

    cnt = Counter()
    for country in country_list:
        cnt[country] += 1

    #选取十个出现频率最高的国家,数据类型为元组
    most_common_country = cnt.most_common(10)
    # 提取字典中的数据
    countries = [country[0] for country in most_common_country]
    values = [country[1] for country in most_common_country]

    # 绘制饼图
    plt.figure(figsize=(10, 10))
    plt.pie(values, labels=countries, startangle=140)
    plt.title('各国家出现次数分布')
    plt.savefig('work_file/image/counties.png')

#生成新闻数量随时间变化图(只需要发布时间)
def generate_time_num_change(file_path):

    df = pd.read_csv(file_path)
    cnt = Counter()
    for pubtime in df['发布时间(y-m)']:
        cnt[pubtime] += 1

    cnt = dict(sorted(cnt.items(), key=lambda x: x[0]))

    # 获取字典的键和值
    times = list(cnt.keys())
    counts = list(cnt.values())

    # 创建一个新的图表
    plt.figure(figsize=(12, 8))
    # 绘制柱状图
    plt.bar(times, counts, color='c', label='出现次数')
    # 绘制折线图
    plt.plot(times, counts, marker='o', color='b', linewidth=2, markersize=8, label='变化趋势')
    plt.xlabel('时间')
    plt.ylabel('出现次数')
    plt.title('时间出现次数及其变化趋势')

    # 设置x轴刻度间隔为每隔10个数据点显示一个刻度
    x_ticks_interval = 10
    plt.xticks(times[::x_ticks_interval], times[::x_ticks_interval], rotation=45)

    plt.legend()  # 显示图例
    plt.grid(axis='y')  # 仅显示y轴网格
    plt.tight_layout()  # 自动调整图表布局
    plt.savefig('work_file/image/time_num_change.png')

#画芯片封锁后果预测和现状分析图
def generate_good_or_bad_compare(file_path, keyword_source_list):

    def merge_info(file_path, df):
        df_temp = pd.read_csv(file_path, encoding='UTF-8-SIG')
        df = pd.concat([df, df_temp], axis=0, join='outer', ignore_index=True)
        return df

    df = pd.DataFrame(columns=['标题', '作者', '编辑', '来源', '发布时间(y-m)', '发布时间(y-m-d)', '正文', '重复标记', '重复篇数'])
    for source in keyword_source_list:
        true_path = file_path + f'{source}_芯片封锁.csv'
        df = merge_info(true_path, df)

    # 自定义规则
    positive_keywords = [
        '开发', '破局', '攻克', '发展', '首推', '突破', '国产化', '造芯', '华为AI',
        '提高'
    ]
    negative_keywords = [
        '损害', '打压', '管制', '限制', '制裁', '禁止', '短缺', '缺芯',
                         ]

    # 判断文本情感(sentiment_count 为情感分析指数)
    def custom_sentiment_analysis(texts):
        list_sentiment = []
        for text in texts:
            sentiment_count = 0
            for word in positive_keywords:
                if word in text:
                    sentiment_count += 1
                    continue
            for word in negative_keywords:
                if word in text:
                    sentiment_count -= 1
                    continue
            list_sentiment.append(sentiment_count)
        return list_sentiment

    # 测试文本
    times = sorted(list(df['发布时间(y-m)']))
    texts = list(df['正文'])

    # 输出情感分析结果
    result_list = custom_sentiment_analysis(texts)
    df.loc[:, '情感分析指数'] = result_list

    #根据情感分析统计数量
    time_positive = Counter(times)
    time_negative = Counter(times)
    time_neutral = Counter(times)
    #将字典键加进去，值默认为0
    for element in time_positive:
        time_positive[element] = 0
        time_negative[element] = 0
        time_neutral[element] = 0

    for pubtime, count in zip(df['发布时间(y-m)'], df['情感分析指数']):
        if count > 0:
            time_positive[pubtime] += 1
        if count < 0:
            time_negative[pubtime] += 1
        if count == 0:
            time_neutral[pubtime] += 1
    positive_count_list = list(time_positive.values())
    negative_count_list = list(time_negative.values())
    neutral_count_list = list(time_neutral.values())
    time_list = list(time_positive.keys())

    #生成一张新的画板
    plt.figure(figsize=(12, 9))

    #根据三个参数绘制堆叠柱状图
    plt.bar(time_list, positive_count_list, color='r', label='正向报道')
    plt.bar(time_list, neutral_count_list, bottom=positive_count_list, color='gray', label='中立报道')
    plt.bar(time_list, negative_count_list, bottom=[i + j for i, j in zip(positive_count_list, neutral_count_list)],
            color='b', label='消极报道')

    # 判断芯片后果的预测是偏向积极还是消极
    if sum(positive_count_list) > sum(negative_count_list):
        prediction_label = '芯片后果预测：偏向积极'
    elif sum(positive_count_list) < sum(negative_count_list):
        prediction_label = '芯片后果预测：偏向消极'
    else:
        prediction_label = '芯片后果预测：尚不明朗'

    # 添加横纵坐标标签和标题
    plt.xlabel('时间')
    plt.ylabel('数量')
    plt.title(f'芯片封锁后果堆叠柱状图\n'
              f'正向报道总计:{sum(positive_count_list)}篇 负向报道总计:{sum(negative_count_list)}篇 中立报道总计:{sum(neutral_count_list)}篇\n'
              f'{prediction_label}')
    plt.xticks(rotation=45)

    # 添加图例
    plt.legend()
    # 显示图形
    plt.savefig('work_file/image/good_or_bad_compare.png')

#画热点事件和热点人物词云图
def generate_hot_name_incident(file_path,tip_list,keyword_source_list, keyword):
    def merge_info(file_path, df):
        df_temp = pd.read_csv(file_path, encoding='UTF-8-SIG')
        df = pd.concat([df, df_temp], axis=0, join='outer', ignore_index=True)
        return df

    #提取热点事件
    df_incident = pd.DataFrame(columns=['事件', '重复次数'])
    for source in keyword_source_list:
        true_path = file_path+tip_list[0]+f"{source}_{keyword}.csv"
        df_incident = merge_info(true_path, df_incident)

    #提取热点人物
    df_name = pd.DataFrame(columns=['姓名', '出现次数'])
    for source in keyword_source_list:
        true_path = file_path+tip_list[1]+f"{source}_{keyword}.csv"
        df_name = merge_info(true_path, df_name)


    word_list = [title for title in df_incident['事件']]
    words = ','.join(map(str, word_list))
    word_list = [name for name in df_name['姓名']]
    words += ','.join(map(str, word_list))


    chinese_font_path ='C:/Windows/Fonts/msyh.ttc'

    # 生成词云
    wordcloud = WordCloud(
        font_path=chinese_font_path, width=800, height=400, background_color='white'
    ).generate(words)

    # 绘制词云图
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")  # 不显示坐标轴
    plt.savefig(f"work_file/image/wordcloud_{keyword}.png")
    plt.close()

#画芯片市场趋势预测图
def predict_market(file_path, keyword_source_list, keyword_list):

    def merge_info(file_path, df):
        df_temp = pd.read_csv(file_path, encoding='UTF-8-SIG')
        df = pd.concat([df, df_temp], axis=0, join='outer', ignore_index=True)
        return df

    df = pd.DataFrame(columns=['标题', '作者', '编辑', '来源', '发布时间(y-m)', '发布时间(y-m-d)', '正文', '重复标记', '重复篇数'])
    for source in keyword_source_list:
        for keyword in keyword_list:
            true_path = file_path + f'{source}_{keyword}.csv'
            df = merge_info(true_path, df)


    # 自定义规则
    positive_keywords = [
        '开发', '破局', '攻克', '发展', '首推', '突破', '国产化', '造芯', '华为AI',
        '提高', '好转',
    ]
    negative_keywords = [
        '损害', '打压', '管制', '限制', '制裁', '禁止', '短缺', '缺芯', '下跌', '低迷',
        '亏损', '滞销', '税收上涨'
                         ]

    # 判断文本情感(sentiment_count 为情感分析指数)
    def custom_sentiment_analysis(texts):
        list_sentiment = []
        for text in texts:
            sentiment_count = 0
            for word in positive_keywords:
                if word in text:
                    sentiment_count += 1
                    continue
            for word in negative_keywords:
                if word in text:
                    sentiment_count -= 1
                    continue
            list_sentiment.append(sentiment_count)
        return list_sentiment
    # 测试文本
    times = sorted(list(df['发布时间(y-m)']))
    texts = list(df['正文'])

    # 输出情感分析结果
    result_list = custom_sentiment_analysis(texts)
    df.loc[:, '情感分析指数'] = result_list

    #根据情感分析统计数量
    time_positive = Counter(times)
    time_negative = Counter(times)
    time_neutral = Counter(times)
    #将字典键加进去，值默认为0
    for element in time_positive:
        time_positive[element] = 0
        time_negative[element] = 0
        time_neutral[element] = 0

    for pubtime, count in zip(df['发布时间(y-m)'], df['情感分析指数']):
        if count > 0:
            time_positive[pubtime] += 1
        if count < 0:
            time_negative[pubtime] += 1
        if count == 0:
            time_neutral[pubtime] += 1
    positive_count_list = list(time_positive.values())
    negative_count_list = list(time_negative.values())
    neutral_count_list = list(time_neutral.values())
    time_list = list(time_positive.keys())

    # 计算拟合曲线的斜率和截距
    slope_positive, intercept_positive, _, _, _ = linregress(np.arange(len(positive_count_list)), positive_count_list)
    slope_negative, intercept_negative, _, _, _ = linregress(np.arange(len(negative_count_list)), negative_count_list)
    slope_neutral, intercept_neutral, _, _, _ = linregress(np.arange(len(neutral_count_list)), neutral_count_list)

    # 计算拟合曲线上的点
    fit_line_positive = slope_positive * np.arange(len(positive_count_list)) + intercept_positive
    fit_line_negative = slope_negative * np.arange(len(negative_count_list)) + intercept_negative
    fit_line_neutral = slope_neutral * np.arange(len(neutral_count_list)) + intercept_neutral

    # 绘制拟合曲线
    plt.figure(figsize=(12, 8))
    plt.plot(time_list, fit_line_positive, label='积极新闻拟合曲线', color='green')
    plt.plot(time_list, fit_line_negative, label='消极新闻拟合曲线', color='red')
    plt.plot(time_list, fit_line_neutral, label='中立新闻拟合曲线', color='blue')

    # 绘制实际数据点
    plt.scatter(time_list, positive_count_list, color='green', marker='o', label='积极新闻报道数量')
    plt.scatter(time_list, negative_count_list, color='red', marker='o', label='消极新闻报道数量')
    plt.scatter(time_list, neutral_count_list, color='blue', marker='o', label='中立新闻报道数量')

    # 设置图表标题和标签
    plt.title('新闻报道数量趋势拟合曲线')
    plt.xlabel('日期')
    plt.ylabel('新闻报道数量')

    # 设置间隔，只显示每隔interval个刻度的日期
    interval = 150

    # 设置横坐标的间隔，只显示每隔interval个刻度的日期
    plt.xticks(times[::interval], rotation=45)
    # 显示图例
    plt.legend()

    # 自动调整日期标签的位置，避免重叠
    plt.gcf().autofmt_xdate()

    # 显示图表
    plt.savefig('work_file/image/predict_market.png')


if __name__ == "__main__":

    time_num_change_file_path = 'work_file/merge_data/merge_data_clean.csv'
    generate_time_num_change(time_num_change_file_path)

    source_list = ['people', 'thepaper']
    good_or_bad_compare_file_path = f'work_file/clean_data/output_text_afterclean_'
    generate_good_or_bad_compare(good_or_bad_compare_file_path, source_list)

    source_list = ['people', 'thepaper']
    keyword_list = ['芯片市场', '芯片制造']
    predict_market_path = f'work_file/clean_data/output_text_afterclean_'
    predict_market(predict_market_path, source_list, keyword_list)

    source_list = ['people', 'thepaper']
    tip_list = ['important_incident/', 'important_name/']
    keyword ='芯片封锁'
    hot_name_incident_path = f'work_file/'
    generate_hot_name_incident(hot_name_incident_path,tip_list, source_list, keyword)

    country_path = 'work_file/merge_data/merge_data_process.csv'
    generate_country(country_path)
