from pathlib import Path                                  # 导入 Path，用于处理文件和目录路径
import pandas as pd                                       # 导入 pandas，用于读取和保存 CSV 数据
import numpy as np                                        # 导入 NumPy，用于数值和特征计算


DATA_DIR = Path("data/split")                             # 设置已经划分好的 train、val、test 数据目录
OUTPUT_DIR = Path("data/features")                        # 设置提取后的特征数据保存目录

OUTPUT_DIR.mkdir(                                         # 创建特征数据保存目录
    parents=True,                                         # 如果上级目录不存在则自动创建
    exist_ok=True                                         # 如果目录已经存在则不会报错
)                                                         # 输出目录创建结束


SPLITS = [                                                # 定义需要处理的三个数据子集
    "train",                                              # 训练集
    "val",                                                # 验证集
    "test"                                                # 测试集
]                                                         # 数据子集定义结束


LABELS = [                                                # 定义五类手势标签
    "left",                                               # 向左手势
    "right",                                              # 向右手势
    "up",                                                 # 向上手势
    "down",                                               # 向下手势
    "still"                                               # 静止类别
]                                                         # 手势标签定义结束


SIGNAL_COLUMNS = [                                        # 定义六个需要分析的 IMU 通道
    "ax",                                                 # X 轴加速度
    "ay",                                                 # Y 轴加速度
    "az",                                                 # Z 轴加速度
    "gx",                                                 # X 轴角速度
    "gy",                                                 # Y 轴角速度
    "gz"                                                  # Z 轴角速度
]                                                         # 六通道定义结束


WINDOW_SIZE = 90                                          # 每个样本统一使用前 90 个采样点


def extract_channel_features(signal):                     # 定义函数，用于提取单个通道的时域特征

    features = {                                          # 创建字典，用于保存当前通道的所有特征

        "mean": np.mean(signal),                          # 计算均值，反映信号整体偏移水平

        "std": np.std(signal),                            # 计算标准差，反映信号波动程度

        "min": np.min(signal),                            # 获取信号最小值

        "max": np.max(signal),                            # 获取信号最大值

        "ptp": np.ptp(signal),                            # 计算峰峰值，即最大值减最小值

        "rms": np.sqrt(                                   # 开始计算均方根 RMS
            np.mean(signal ** 2)                          # 先计算信号平方后的平均值
        ),                                                # 再开平方得到 RMS

        "energy": np.sum(signal ** 2)                     # 计算信号能量，即所有采样值平方和
    }                                                     # 当前通道特征字典定义结束

    return features                                       # 返回当前通道的时域特征


for split_name in SPLITS:                                 # 依次处理训练集、验证集和测试集

    feature_rows = []                                     # 创建列表，用于保存当前数据子集中的所有特征记录


    for label in LABELS:                                  # 依次处理五类手势

        label_dir = (                                     # 构造当前数据子集和手势类别对应的路径
            DATA_DIR                                      # 使用数据集划分根目录
            / split_name                                  # 添加 train、val 或 test
            / label                                       # 添加当前手势类别
        )                                                 # 当前类别目录构造结束


        csv_files = sorted(                               # 获取当前类别中的所有 CSV 文件
            label_dir.glob("*.csv")                       # 查找当前目录中的所有 CSV 文件
        )                                                 # CSV 文件列表获取结束


        for csv_path in csv_files:                        # 依次处理当前类别中的每个完整手势样本

            df = pd.read_csv(csv_path)                    # 使用 pandas 读取当前 CSV 文件

            df = df.iloc[:WINDOW_SIZE]                    # 保留当前样本前 90 个采样点

            row = {                                       # 创建当前样本的特征记录
                "file": csv_path.name,                    # 保存当前样本的原始文件名
                "label": label                            # 保存当前样本对应的手势标签
            }                                             # 当前样本基础信息定义结束


            for column in SIGNAL_COLUMNS:                 # 依次处理六个 IMU 通道

                signal = (                                # 获取当前通道的 90 个时域采样值
                    df[column]                            # 选择当前信号通道
                    .to_numpy(dtype=np.float32)           # 转换为 float32 NumPy 数组
                )                                         # 当前通道信号提取结束


                channel_features = (                      # 调用函数提取当前通道的时域特征
                    extract_channel_features(signal)      # 将当前通道信号传入特征提取函数
                )                                         # 当前通道特征提取结束


                for feature_name, value in (              # 遍历当前通道提取出的所有特征
                    channel_features.items()              # 获取特征名称和对应数值
                ):                                        # 特征遍历开始

                    column_name = (                       # 构造最终特征列名
                        f"{column}_{feature_name}"         # 例如 ax_mean、gx_rms
                    )                                     # 特征列名构造结束

                    row[column_name] = value              # 将当前特征加入当前样本的特征记录


            feature_rows.append(row)                     # 将当前样本完整特征记录加入列表


    feature_df = pd.DataFrame(                            # 将当前数据子集的所有特征转换为 DataFrame
        feature_rows                                     # 输入全部样本特征记录
    )                                                     # 特征 DataFrame 构建结束


    output_path = (                                       # 构造当前数据子集的特征文件保存路径
        OUTPUT_DIR                                        # 使用特征数据输出目录
        / f"time_features_{split_name}.csv"               # 设置 train、val 或 test 特征文件名
    )                                                     # 输出文件路径构造结束


    feature_df.to_csv(                                    # 将当前数据子集的时域特征保存为 CSV
        output_path,                                      # 指定输出文件路径
        index=False                                       # 不保存 pandas 自动生成的行号
    )                                                     # 特征 CSV 保存结束


    print(                                                # 输出当前数据子集特征提取结果
        f"{split_name}: "
        f"{len(feature_df)} samples, "
        f"{len(feature_df.columns) - 2} features"
    )                                                     # 当前结果输出结束


print()                                                   # 输出空行

print(                                                    # 输出全部特征提取完成提示
    f"Time-domain features saved to: {OUTPUT_DIR}"
)                                                         # 输出结束