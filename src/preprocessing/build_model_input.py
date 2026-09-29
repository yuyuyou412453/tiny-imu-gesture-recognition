from pathlib import Path                                  # 导入 Path，用于处理文件和目录路径
import pandas as pd                                       # 导入 pandas，用于读取 CSV 数据
import numpy as np                                        # 导入 NumPy，用于数组计算和保存数据


SOURCE_DIR = Path("data/split")                           # 设置已经划分好的 train/val/test 数据目录
OUTPUT_DIR = Path("data/model_input")                     # 设置最终模型输入数据的保存目录

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

SIGNAL_COLUMNS = [                                        # 定义作为模型输入的六个 IMU 通道
    "ax",                                                 # X 轴加速度
    "ay",                                                 # Y 轴加速度
    "az",                                                 # Z 轴加速度
    "gx",                                                 # X 轴角速度
    "gy",                                                 # Y 轴角速度
    "gz"                                                  # Z 轴角速度
]                                                         # 六通道定义结束

WINDOW_SIZE = 90                                          # 设置每个样本统一保留 90 个时间点


OUTPUT_DIR.mkdir(                                         # 创建最终模型输入保存目录
    parents=True,                                         # 如果上级目录不存在则自动创建
    exist_ok=True                                         # 如果目录已经存在则不会报错
)                                                         # 输出目录创建结束


all_data = {}                                             # 创建字典，用于临时保存 train/val/test 的数据和标签


for split_name in SPLITS:                                 # 依次处理训练集、验证集和测试集

    split_samples = []                                    # 创建列表，用于保存当前数据子集中的所有样本
    split_labels = []                                     # 创建列表，用于保存当前数据子集中的所有标签

    for label in LABELS:                                  # 依次处理五类手势

        label_dir = (                                     # 构造当前数据子集和当前类别对应的目录
            SOURCE_DIR                                    # 使用数据集划分后的根目录
            / split_name                                  # 添加 train、val 或 test
            / label                                       # 添加当前手势类别
        )                                                 # 当前类别目录构造结束

        csv_files = sorted(                               # 获取当前目录中的全部 CSV 文件
            label_dir.glob("*.csv")                       # 查找扩展名为 .csv 的文件
        )                                                 # CSV 文件列表获取结束

        for csv_path in csv_files:                        # 依次读取当前类别中的每一个 CSV 文件

            df = pd.read_csv(csv_path)                    # 使用 pandas 读取当前 CSV 文件

            signal = (                                    # 开始提取六轴 IMU 信号
                df[SIGNAL_COLUMNS]                        # 选择 ax、ay、az、gx、gy、gz 六列
                .to_numpy(dtype=np.float32)               # 转换为 float32 类型的 NumPy 数组
            )                                             # 六轴信号提取结束

            if len(signal) < WINDOW_SIZE:                 # 判断当前样本是否少于 90 个采样点

                print(                                    # 输出长度不足的样本提示
                    f"Skip: {csv_path} "
                    f"only contains {len(signal)} points"
                )                                         # 提示信息输出结束

                continue                                  # 跳过当前长度不足的样本

            signal = signal[:WINDOW_SIZE]                 # 保留当前样本前 90 个采样点

            split_samples.append(signal)                  # 将当前固定长度样本加入当前数据子集

            split_labels.append(label)                    # 保存当前样本对应的手势标签


    X = np.array(                                         # 将当前数据子集中的全部样本转换为 NumPy 数组
        split_samples,                                    # 输入所有固定长度样本
        dtype=np.float32                                  # 设置数组数据类型为 float32
    )                                                     # 当前输入数组构建结束

    y = np.array(split_labels)                            # 将当前数据子集的标签转换为 NumPy 数组

    all_data[split_name] = {                              # 将当前子集的数据保存到临时字典
        "X": X,                                           # 保存六轴时序样本
        "y": y                                            # 保存对应标签
    }                                                     # 当前数据子集保存结束

    print(                                                # 输出当前固定长度样本构建结果
        f"{split_name}: "
        f"X shape = {X.shape}, "
        f"y shape = {y.shape}"
    )                                                     # 当前数据子集信息输出结束


X_train = all_data["train"]["X"]                          # 获取训练集六轴时序数据

channel_mean = X_train.mean(                              # 计算训练集六个通道的整体均值
    axis=(0, 1)                                           # 同时对样本维度和时间维度求均值
)                                                         # 六通道均值计算结束

channel_std = X_train.std(                                # 计算训练集六个通道的整体标准差
    axis=(0, 1)                                           # 同时对样本维度和时间维度求标准差
)                                                         # 六通道标准差计算结束

channel_std = np.where(                                   # 防止某个通道标准差意外为 0
    channel_std == 0,                                     # 判断标准差是否等于 0
    1.0,                                                  # 如果为 0，则使用 1.0 代替
    channel_std                                           # 否则保留原标准差
)                                                         # 标准差安全处理结束


print()                                                   # 输出空行

print("Channel mean from training set:")                  # 输出训练集六通道均值标题
print(channel_mean)                                       # 输出训练集六通道均值

print()                                                   # 输出空行

print("Channel std from training set:")                   # 输出训练集六通道标准差标题
print(channel_std)                                        # 输出训练集六通道标准差


for split_name in SPLITS:                                 # 依次处理 train、val 和 test

    X = all_data[split_name]["X"]                         # 获取当前数据子集的六轴输入数据
    y = all_data[split_name]["y"]                         # 获取当前数据子集的标签

    X_normalized = (                                      # 开始执行标准化
        X                                                 # 使用当前数据子集的原始固定长度数据
        - channel_mean                                    # 减去训练集六通道均值
    ) / channel_std                                       # 除以训练集六通道标准差

    np.save(                                              # 保存标准化后的当前数据子集
        OUTPUT_DIR / f"X_{split_name}.npy",               # 设置当前输入数据文件名
        X_normalized.astype(np.float32)                   # 保存为 float32 类型
    )                                                     # 输入数据保存结束

    np.save(                                              # 保存当前数据子集对应的标签
        OUTPUT_DIR / f"y_{split_name}.npy",               # 设置标签文件名
        y                                                 # 保存标签数组
    )                                                     # 标签保存结束


np.save(                                                  # 保存训练集计算得到的六通道均值
    OUTPUT_DIR / "channel_mean.npy",                      # 设置均值参数文件名
    channel_mean.astype(np.float32)                       # 保存为 float32 类型
)                                                         # 六通道均值保存结束

np.save(                                                  # 保存训练集计算得到的六通道标准差
    OUTPUT_DIR / "channel_std.npy",                       # 设置标准差参数文件名
    channel_std.astype(np.float32)                        # 保存为 float32 类型
)                                                         # 六通道标准差保存结束


print()                                                   # 输出空行

print("Model input construction completed.")              # 输出最终处理完成提示