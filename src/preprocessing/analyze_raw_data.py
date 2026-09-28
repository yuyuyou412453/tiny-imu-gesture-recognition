from pathlib import Path                                  # 导入 Path，用于处理文件夹和文件路径
import pandas as pd                                       # 导入 pandas，用于读取和统计 CSV 数据
import numpy as np                                        # 导入 NumPy，用于数值计算


DATA_DIR = Path("data/raw")                               # 设置正式原始数据所在目录

LABELS = [                                                # 定义需要分析的五类手势
    "left",                                               # 向左手势
    "right",                                              # 向右手势
    "up",                                                 # 向上手势
    "down",                                               # 向下手势
    "still"                                               # 静止类别
]                                                         # 手势标签列表定义结束

SIGNAL_COLUMNS = [                                        # 定义六轴 IMU 数据列
    "ax",                                                 # X 轴加速度
    "ay",                                                 # Y 轴加速度
    "az",                                                 # Z 轴加速度
    "gx",                                                 # X 轴角速度
    "gy",                                                 # Y 轴角速度
    "gz"                                                  # Z 轴角速度
]                                                         # 六轴数据列定义结束


all_results = []                                          # 创建列表，用于保存每个样本的统计结果


for label in LABELS:                                      # 依次遍历五类手势

    label_dir = DATA_DIR / label                          # 构造当前类别对应的文件夹路径

    csv_files = sorted(                                   # 获取当前类别下的全部 CSV 文件
        label_dir.glob("*.csv")                           # 查找扩展名为 .csv 的文件
    )                                                     # CSV 文件列表获取结束

    for csv_path in csv_files:                            # 依次处理当前类别中的每个 CSV 文件

        df = pd.read_csv(csv_path)                        # 使用 pandas 读取当前 CSV 文件

        time_diff = df["timestamp"].diff().dropna()       # 计算相邻时间戳之间的时间间隔

        result = {                                        # 创建当前样本的统计结果字典
            "label": label,                               # 保存当前样本所属类别
            "file": csv_path.name,                        # 保存当前 CSV 文件名
            "points": len(df),                            # 统计当前样本包含的数据点数量
            "missing_values": int(df.isna().sum().sum()), # 统计当前文件中所有缺失值数量
            "median_dt_ms": time_diff.median(),           # 统计采样间隔中位数，单位为 ms
            "max_dt_ms": time_diff.max()                  # 统计最大采样间隔，便于发现掉点
        }                                                 # 当前基本统计结果定义结束

        for column in SIGNAL_COLUMNS:                     # 依次统计六个传感器通道

            result[f"{column}_min"] = df[column].min()     # 保存当前通道的最小值
            result[f"{column}_max"] = df[column].max()     # 保存当前通道的最大值
            result[f"{column}_mean"] = df[column].mean()   # 保存当前通道的平均值
            result[f"{column}_std"] = df[column].std()     # 保存当前通道的标准差

        baseline = df.iloc[:10]                           # 取每个样本前 10 个采样点作为起始阶段

        for column in SIGNAL_COLUMNS:                     # 依次计算六轴起始阶段均值

            result[f"{column}_baseline"] = (              # 创建当前通道的基线统计值
                baseline[column].mean()                   # 计算前 10 个点的平均值
            )                                             # 当前通道基线计算结束

        all_results.append(result)                        # 将当前样本统计结果加入总结果列表


results_df = pd.DataFrame(all_results)                    # 将全部样本统计结果转换为 DataFrame


print("====================================")             # 输出分隔线
print("Dataset Summary")                                 # 输出数据集整体统计标题
print("====================================")             # 输出分隔线

print()                                                  # 输出空行

print(                                                   # 输出每类样本数量
    results_df.groupby("label").size()
)                                                         # 每类样本数量统计结束

print()                                                  # 输出空行

print(                                                   # 输出全部缺失值数量
    "Total missing values:",
    results_df["missing_values"].sum()
)                                                         # 缺失值统计输出结束

print()                                                  # 输出空行

print(                                                   # 输出样本长度范围
    "Points range:",
    results_df["points"].min(),
    "-",
    results_df["points"].max()
)                                                         # 样本长度范围输出结束

print()                                                  # 输出空行

print(                                                   # 输出典型采样间隔
    "Median sampling interval:",
    results_df["median_dt_ms"].median(),
    "ms"
)                                                         # 采样间隔输出结束

print()                                                  # 输出空行

print(                                                   # 输出最大的采样时间间隔
    "Maximum sampling interval:",
    results_df["max_dt_ms"].max(),
    "ms"
)                                                         # 最大采样间隔输出结束


print()                                                  # 输出空行
print("====================================")             # 输出分隔线
print("Baseline Mean by Label")                          # 输出各类别起始阶段均值标题
print("====================================")             # 输出分隔线

baseline_columns = [                                     # 定义需要显示的六轴基线列
    f"{column}_baseline"                                 # 根据六轴通道名称生成对应基线列名
    for column in SIGNAL_COLUMNS                         # 遍历六个传感器通道
]                                                         # 基线列列表生成结束

print(                                                   # 输出不同类别的平均起始基线
    results_df.groupby("label")[baseline_columns].mean()
)                                                         # 类别基线统计结束


still_results = results_df[                              # 从全部统计结果中提取 still 类数据
    results_df["label"] == "still"                       # 筛选标签为 still 的样本
]                                                         # still 数据筛选结束


print()                                                  # 输出空行
print("====================================")             # 输出分隔线
print("Still Gyroscope Statistics")                      # 输出静止状态陀螺仪统计标题
print("====================================")             # 输出分隔线

for axis in ["gx", "gy", "gz"]:                          # 依次处理三个陀螺仪轴

    print(                                               # 输出当前轴的统计结果
        f"{axis}: "
        f"mean = {still_results[f'{axis}_mean'].mean():.4f}, "
        f"std = {still_results[f'{axis}_std'].mean():.4f}"
    )                                                     # 当前陀螺仪轴统计输出结束