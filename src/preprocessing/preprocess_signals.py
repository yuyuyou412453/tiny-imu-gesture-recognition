from pathlib import Path                                      # 导入 Path，用于处理文件夹和文件路径
import pandas as pd                                           # 导入 pandas，用于读取和保存 CSV 数据
import numpy as np                                            # 导入 NumPy，用于数值计算
from scipy.signal import butter, filtfilt                     # 导入 Butterworth 滤波器设计函数和零相位滤波函数


RAW_DATA_DIR = Path("data/raw")                               # 设置原始数据所在目录
PROCESSED_DATA_DIR = Path("data/processed")                   # 设置预处理后数据的保存目录

LABELS = [                                                    # 定义项目中的五类手势
    "left",                                                   # 向左手势
    "right",                                                  # 向右手势
    "up",                                                     # 向上手势
    "down",                                                   # 向下手势
    "still"                                                   # 静止类别
]                                                             # 手势类别定义结束

SIGNAL_COLUMNS = [                                            # 定义六轴 IMU 信号列
    "ax",                                                     # X 轴加速度
    "ay",                                                     # Y 轴加速度
    "az",                                                     # Z 轴加速度
    "gx",                                                     # X 轴角速度
    "gy",                                                     # Y 轴角速度
    "gz"                                                      # Z 轴角速度
]                                                             # 六轴信号列定义结束

BASELINE_POINTS = 10                                          # 使用每个样本最开始的 10 个点估计初始基线

CUTOFF_FREQUENCY = 8.0                                        # 设置低通滤波器截止频率为 8 Hz

FILTER_ORDER = 4                                              # 设置 Butterworth 低通滤波器阶数为 4 阶


def estimate_sampling_frequency(df):                          # 定义函数，用于根据时间戳估计实际采样频率

    time_diff = df["timestamp"].diff().dropna()               # 计算相邻两个采样点之间的时间间隔

    median_dt_ms = time_diff.median()                         # 计算采样时间间隔的中位数，单位为毫秒

    sampling_frequency = 1000.0 / median_dt_ms                # 根据采样周期计算采样频率，单位为 Hz

    return sampling_frequency                                 # 返回估计得到的实际采样频率


def low_pass_filter(signal, sampling_frequency):              # 定义低通滤波函数

    nyquist_frequency = sampling_frequency / 2.0              # 计算 Nyquist 频率，即采样频率的一半

    normalized_cutoff = (                                     # 开始计算归一化截止频率
        CUTOFF_FREQUENCY                                      # 使用设定的截止频率
        / nyquist_frequency                                   # 除以 Nyquist 频率得到 0～1 范围的归一化频率
    )                                                         # 归一化截止频率计算结束

    b, a = butter(                                            # 设计 Butterworth 数字低通滤波器
        FILTER_ORDER,                                         # 设置滤波器阶数
        normalized_cutoff,                                    # 设置归一化截止频率
        btype="low"                                           # 指定滤波器类型为低通滤波器
    )                                                         # Butterworth 滤波器设计结束

    filtered_signal = filtfilt(                               # 对信号进行零相位双向滤波
        b,                                                    # 使用滤波器分子系数
        a,                                                    # 使用滤波器分母系数
        signal                                                # 输入需要滤波的一维信号
    )                                                         # 零相位滤波结束

    return filtered_signal                                    # 返回滤波后的信号


for label in LABELS:                                          # 依次遍历五类手势

    raw_label_dir = RAW_DATA_DIR / label                      # 构造当前类别原始数据文件夹路径

    processed_label_dir = PROCESSED_DATA_DIR / label          # 构造当前类别处理后数据文件夹路径

    processed_label_dir.mkdir(                                # 创建当前类别的输出目录
        parents=True,                                         # 如果上级目录不存在则自动创建
        exist_ok=True                                         # 如果目录已经存在则不报错
    )                                                         # 输出目录创建结束

    csv_files = sorted(                                       # 获取当前类别下所有 CSV 文件
        raw_label_dir.glob("*.csv")                           # 查找扩展名为 .csv 的文件
    )                                                         # CSV 文件列表获取结束

    print()                                                   # 输出空行，方便观察不同类别结果

    print(                                                    # 输出当前正在处理的手势类别
        f"Processing {label}: {len(csv_files)} files"
    )                                                         # 类别信息输出结束

    for csv_path in csv_files:                                # 依次处理当前类别的每一个 CSV 文件

        df = pd.read_csv(csv_path)                            # 使用 pandas 读取当前原始 CSV 文件

        processed_df = df.copy()                              # 创建当前数据副本，避免直接修改原始 DataFrame

        sampling_frequency = estimate_sampling_frequency(     # 根据当前样本的时间戳估计采样频率
            df                                                # 将当前 DataFrame 传入采样频率估计函数
        )                                                     # 采样频率估计结束

        baseline_data = df.iloc[:BASELINE_POINTS]             # 取当前样本最开始的 10 个采样点

        for column in SIGNAL_COLUMNS:                         # 依次处理六个 IMU 信号通道

            baseline = baseline_data[column].mean()           # 计算当前通道前 10 个采样点的平均值

            corrected_signal = (                              # 开始进行基线校正
                df[column]                                    # 获取当前通道的原始信号
                - baseline                                    # 减去该通道的初始基线
            )                                                 # 基线校正完成

            filtered_signal = low_pass_filter(                # 对基线校正后的信号进行低通滤波
                corrected_signal,                             # 输入已经完成基线校正的信号
                sampling_frequency                            # 输入当前样本的实际采样频率
            )                                                 # 低通滤波完成

            processed_df[column] = filtered_signal            # 将处理后的信号写回对应的数据列

        output_path = (                                       # 构造当前处理后 CSV 的保存路径
            processed_label_dir                               # 使用当前类别对应的输出目录
            / csv_path.name                                   # 保持原始 CSV 文件名不变
        )                                                     # 输出路径构造完成

        processed_df.to_csv(                                  # 将处理后的数据保存为 CSV 文件
            output_path,                                      # 指定输出文件路径
            index=False                                       # 不额外保存 pandas 的行号
        )                                                     # CSV 文件保存结束

        print(                                                # 在终端输出当前文件处理结果
            f"Saved: {output_path}"
        )                                                     # 当前文件处理结果输出结束


print()                                                       # 输出空行

print(                                                        # 输出全部数据处理完成提示
    "All signals have been baseline-corrected and filtered."
)                                                             # 完成提示输出结束