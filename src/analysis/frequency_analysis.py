from pathlib import Path                                  # 导入 Path，用于处理文件和目录路径
import pandas as pd                                       # 导入 pandas，用于读取 CSV 数据
import numpy as np                                        # 导入 NumPy，用于 FFT 和数组计算
import matplotlib.pyplot as plt                          # 导入 matplotlib，用于绘制频谱图


DATA_DIR = Path("data/split/train")                       # 设置训练集数据所在目录
OUTPUT_DIR = Path("assets/frequency_domain")              # 设置频域分析图片保存目录

OUTPUT_DIR.mkdir(                                         # 创建频域分析图片保存目录
    parents=True,                                         # 如果上级目录不存在则自动创建
    exist_ok=True                                         # 如果目录已经存在则不会报错
)                                                         # 输出目录创建结束


LABELS = [                                                # 定义五类手势
    "left",                                               # 向左手势
    "right",                                              # 向右手势
    "up",                                                 # 向上手势
    "down",                                               # 向下手势
    "still"                                               # 静止类别
]                                                         # 手势类别定义结束


SIGNAL_COLUMNS = [                                        # 定义六个 IMU 信号通道
    "ax",                                                 # X 轴加速度
    "ay",                                                 # Y 轴加速度
    "az",                                                 # Z 轴加速度
    "gx",                                                 # X 轴角速度
    "gy",                                                 # Y 轴角速度
    "gz"                                                  # Z 轴角速度
]                                                         # 六通道定义结束


WINDOW_SIZE = 90                                          # 每个样本统一使用前 90 个采样点
SAMPLING_FREQUENCY = 45.45                                # 设置实际采样频率约为 45.45 Hz


frequencies = np.fft.rfftfreq(                            # 计算单边 FFT 对应的频率坐标
    WINDOW_SIZE,                                          # 指定 FFT 使用的采样点数量
    d=1.0 / SAMPLING_FREQUENCY                            # 指定相邻采样点之间的时间间隔
)                                                         # 频率坐标计算结束


for label in LABELS:                                      # 依次处理五类手势

    label_dir = DATA_DIR / label                          # 构造当前手势类别的数据目录

    csv_files = sorted(                                   # 获取当前类别全部训练样本
        label_dir.glob("*.csv")                           # 查找目录中的所有 CSV 文件
    )                                                     # CSV 文件列表获取结束


    spectra = []                                          # 创建列表，用于保存当前类别所有样本的频谱


    for csv_path in csv_files:                            # 依次处理当前类别的每一个样本

        df = pd.read_csv(csv_path)                        # 读取当前 CSV 文件

        signal = (                                        # 提取六轴时域信号
            df[SIGNAL_COLUMNS]                            # 选择 ax、ay、az、gx、gy、gz 六列
            .iloc[:WINDOW_SIZE]                           # 保留前 90 个采样点
            .to_numpy(dtype=np.float32)                   # 转换为 NumPy 数组
        )                                                 # 六轴信号提取结束


        signal = (                                        # 开始去除每个通道残余的直流分量
            signal                                        # 使用当前六轴信号
            - signal.mean(axis=0, keepdims=True)          # 每个通道减去自身均值
        )                                                 # 去直流分量完成


        fft_result = np.fft.rfft(                         # 对时间轴方向执行实数快速傅里叶变换
            signal,                                       # 输入六轴时域信号
            axis=0                                        # 沿时间维度进行 FFT
        )                                                 # FFT 计算结束


        amplitude = (                                     # 开始计算单边幅度谱
            2.0                                           # 单边频谱需要乘 2
            / WINDOW_SIZE                                 # 根据采样点数量进行幅值归一化
            * np.abs(fft_result)                          # 取 FFT 结果的幅值
        )                                                 # 单边幅度谱计算结束


        spectra.append(amplitude)                         # 保存当前样本的六轴幅度谱


    spectra = np.array(                                   # 将当前类别所有频谱转换为数组
        spectra,                                          # 输入全部样本频谱
        dtype=np.float32                                  # 设置数据类型为 float32
    )                                                     # 频谱数组构建结束


    mean_spectrum = spectra.mean(axis=0)                  # 对 14 个训练样本的幅度谱求平均


    plt.figure(figsize=(10, 5))                           # 创建三轴加速度平均频谱图

    plt.plot(frequencies, mean_spectrum[:, 0], label="ax")# 绘制 X 轴加速度频谱
    plt.plot(frequencies, mean_spectrum[:, 1], label="ay")# 绘制 Y 轴加速度频谱
    plt.plot(frequencies, mean_spectrum[:, 2], label="az")# 绘制 Z 轴加速度频谱

    plt.xlabel("Frequency (Hz)")                          # 设置横坐标为频率
    plt.ylabel("Amplitude")                               # 设置纵坐标为幅值

    plt.title(                                            # 设置当前加速度频谱图标题
        f"{label} - Mean Accelerometer Spectrum"
    )                                                     # 标题设置结束

    plt.xlim(0, 12)                                       # 重点显示 0～12 Hz 的低频区域
    plt.legend(loc="best")                                # 自动选择遮挡最少的图例位置
    plt.grid()                                            # 显示网格
    plt.tight_layout()                                    # 自动调整布局

    plt.savefig(                                          # 保存当前加速度频谱图
        OUTPUT_DIR / f"{label}_spectrum_acc.png",         # 设置图片保存路径
        dpi=200,                                          # 设置图片分辨率
        bbox_inches="tight"                               # 自动裁剪多余空白
    )                                                     # 图片保存结束

    plt.close()                                           # 关闭当前图像


    plt.figure(figsize=(10, 5))                           # 创建三轴陀螺仪平均频谱图

    plt.plot(frequencies, mean_spectrum[:, 3], label="gx")# 绘制 X 轴角速度频谱
    plt.plot(frequencies, mean_spectrum[:, 4], label="gy")# 绘制 Y 轴角速度频谱
    plt.plot(frequencies, mean_spectrum[:, 5], label="gz")# 绘制 Z 轴角速度频谱

    plt.xlabel("Frequency (Hz)")                          # 设置横坐标为频率
    plt.ylabel("Amplitude")                               # 设置纵坐标为幅值

    plt.title(                                            # 设置当前陀螺仪频谱图标题
        f"{label} - Mean Gyroscope Spectrum"
    )                                                     # 标题设置结束

    plt.xlim(0, 12)                                       # 重点显示 0～12 Hz 的频率范围
    plt.legend(loc="best")                                # 自动选择图例位置
    plt.grid()                                            # 显示网格
    plt.tight_layout()                                    # 自动调整布局

    plt.savefig(                                          # 保存当前陀螺仪频谱图
        OUTPUT_DIR / f"{label}_spectrum_gyro.png",        # 设置图片保存路径
        dpi=200,                                          # 设置图片分辨率
        bbox_inches="tight"                               # 自动裁剪多余空白
    )                                                     # 图片保存结束

    plt.close()                                           # 关闭当前图像


    print(                                                # 输出当前类别处理结果
        f"{label}: {len(spectra)} spectra analyzed"
    )                                                     # 当前类别提示输出结束


print()                                                   # 输出空行

print(                                                    # 输出全部频域分析完成提示
    f"Frequency-domain figures saved to: {OUTPUT_DIR}"
)                                                         # 输出结束