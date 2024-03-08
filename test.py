import glob
import os
import jieba
import pandas as pd
# 获取当前目录
directory = os.getcwd()

# 获取所有文件
project_path = glob.glob(directory + "/10914.csv")[0]

msg = pd.read_csv(project_path)

def datacleansing(data):
    # 过滤分享的链接等数据
    data_processed = data[data['StrContent'].str.contains('http') == False]
    data_processed = data_processed[data_processed['StrContent'].str.contains('<msg>') == False]
    # 过滤撤回数据
    data_processed = data_processed[data_processed['StrContent'].str.contains('撤回了一条') == False]
    return data_processed
 
# 运行
msg_processed = datacleansing(msg)


# 首先划定需要分析的聊天记录时间范围，我这边选取了2023一整年的记录作为分析样本
msg_processed_time = msg_processed.loc[(msg_processed['StrTime'] >= '2023-01-01') & (msg_processed['StrTime'] <= '2024-01-01')]
# 下面利用IsSender字段将主对方分开
msg_total = msg_processed_time # 总
msg_i = msg_processed_time[msg_processed_time["IsSender"] == 1] # 我自己
msg_u = msg_processed_time[msg_processed_time["IsSender"] == 0] # 对方
# 加时间索引
msg_total['StrTime'] = pd.to_datetime(msg_total['StrTime'])
msg_total = msg_total.set_index('StrTime')
msg_i['StrTime'] = pd.to_datetime(msg_i['StrTime'])
msg_i = msg_i.set_index('StrTime')
msg_u['StrTime'] = pd.to_datetime(msg_u['StrTime'])
msg_u = msg_u.set_index('StrTime')
# 设计统计字段count
msg_total["count"] = 1
msg_i["count"] = 1
msg_u["count"] = 1
# 按天统计聊天频次
result_total_day = msg_total.resample('D').sum()
result_i_day = msg_i.resample('D').sum()
result_u_day = msg_u.resample('D').sum()


# copy一份数据
msg_phase_total = msg_processed_time
# 由于我们要根据StrTime字段划分时段，因此先将其转为字符串，便于后续操作
msg_phase_total['StrTime'] = msg_phase_total['StrTime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
# 取每日时段（小时部分）：将StrTime字段重构成time_phase字段
time_phase = msg_phase_total.pop('StrTime')
time_phase = time_phase.str[11:13]
msg_phase_total.insert(1, 'time_phase', time_phase)
# 取主对方
msg_phase_i = msg_phase_total[msg_phase_total["IsSender"] == 1]
msg_phase_u = msg_phase_total[msg_phase_total["IsSender"] == 0]
# 算出各时段聊天次数
result_total_tp = msg_phase_total['time_phase'].value_counts()
result_i_tp = msg_phase_i['time_phase'].value_counts()
result_u_tp = msg_phase_u['time_phase'].value_counts()




# 分词函数
def obtain_word(data):
    word = jieba.cut(data)
    return list(word)
 
# copy一份数据
msg_word_total = msg_processed_time
# 将StrContent字段分词形成word字段
msg_word_total['word'] = msg_word_total['StrContent'].apply(obtain_word)
# 统计word字段中各词汇频次
result_word = pd.Series(msg_word_total['word'].sum()).value_counts()
# 需要将Series转换为DataFrame格式，便于画图
result_word_list = {'labels': result_word.index, 'counts': result_word.values}
result_word_new = pd.DataFrame(result_word_list)



import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


# 要配置这些，否则会出现中文乱码
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 聊天频次折线图
plt.plot(result_total_day.loc[:, ['count']])
# plt.show()
plt.savefig('times.png', transparent = True)


# 要配置这些，否则会出现中文乱码
# plt.rcParams["font.sans-serif"] = ["SimHei"]
# plt.rcParams["axes.unicode_minus"] = False
 
# 从二-3的结果中提取数据和标签
top = result_word_new.head(20)
labels = top.iloc[:, 0]
counts = top.iloc[:, 1]
 
# 创建条形图
plt.barh(labels, counts, color='skyblue')
plt.xlabel('出现次数')
plt.ylabel('词汇')
plt.title('Top 20 出现词汇')
 
# 反转y轴，使得指标显示正确
plt.gca().invert_yaxis()
 
# 紧凑布局，确保y轴完全显示
plt.tight_layout()
# plt.show()
plt.savefig('word.png', transparent = True)