from pathlib import Path                                  # 导入 Path，用于处理文件和目录路径
import pandas as pd                                       # 导入 pandas，用于读取 CSV 数据
import numpy as np                                        # 导入 NumPy，用于数组和均值计算
import matplotlib.pyplot as plt                          # 导入 matplotlib，用于绘制时域波形


DATA_DIR = Path("data/split/train")                       # 设置训练集数据所在目录
OUTPUT_DIR = Path("assets/time_domain")                   # 设置时域分析图片保存目录

OUTPUT_DIR.mkdir(                                         # 创建时域分析图片保存目录
    parents=True,                                         # 如果上级目录不存在则自动创建
    exist_ok=True                                         # 如果目录已经存在则不会报错
)                                                         # 输出目录创建结束


LABELS = [                                                # 定义五类手势
    "left",                                               # 向左手势
    "right",                                              # 向右手势
    "up",                                                 # 向上手势
    "down",                                               # 向下手势
    "still"                                               # 静止类别
]                                                         # 手势标签定义结束


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


time_s = (                                                # 构造横坐标时间轴
    np.arange(WINDOW_SIZE)                                # 生成 0～89 共 90 个采样点编号
    / SAMPLING_FREQUENCY                                  # 根据采样频率转换为秒
)                                                         # 时间轴构造结束


for label in LABELS:                                      # 依次分析五类手势

    label_dir = DATA_DIR / label                          # 构造当前类别训练集目录

    csv_files = sorted(                                   # 获取当前类别的全部 CSV 文件
        label_dir.glob("*.csv")                           # 查找当前目录中的全部 CSV 文件
    )                                                     # CSV 文件列表获取结束

    samples = []                                          # 创建列表，用于保存当前类别全部样本


    for csv_path in csv_files:                            # 依次读取当前类别每一个 CSV 文件

        df = pd.read_csv(csv_path)                        # 读取当前 CSV 数据

        signal = (                                        # 开始提取当前样本六轴信号
            df[SIGNAL_COLUMNS]                            # 选择六个 IMU 通道
            .iloc[:WINDOW_SIZE]                           # 只保留前 90 个采样点
            .to_numpy(dtype=np.float32)                   # 转换为 float32 NumPy 数组
        )                                                 # 当前样本六轴数据提取结束

        samples.append(signal)                            # 将当前样本加入类别样本列表


    samples = np.array(                                   # 将当前类别全部样本转换为三维数组
        samples,                                          # 输入当前类别全部样本
        dtype=np.float32                                  # 设置数组类型为 float32
    )                                                     # 样本数组转换结束


    mean_signal = samples.mean(axis=0)                    # 对当前类别全部训练样本求平均时域波形


    plt.figure(figsize=(10, 5))                           # 创建三轴加速度平均波形图

    plt.plot(time_s, mean_signal[:, 0], label="ax")       # 绘制平均 X 轴加速度
    plt.plot(time_s, mean_signal[:, 1], label="ay")       # 绘制平均 Y 轴加速度
    plt.plot(time_s, mean_signal[:, 2], label="az")       # 绘制平均 Z 轴加速度

    plt.xlabel("Time (s)")                                # 设置横坐标名称
    plt.ylabel("Acceleration (g)")                        # 设置纵坐标名称

    plt.title(                                            # 设置当前加速度图标题
        f"{label} - Mean Accelerometer Signal"
    )                                                     # 图标题设置结束

    plt.legend(loc="best")                                # 自动选择遮挡最少的图例位置
    plt.grid()                                            # 显示网格
    plt.tight_layout()                                    # 自动调整图像布局

    plt.savefig(                                          # 保存当前加速度平均波形图
        OUTPUT_DIR / f"{label}_mean_acc.png",             # 设置保存文件名
        dpi=200,                                          # 设置图片分辨率
        bbox_inches="tight"                               # 自动裁剪多余空白区域
    )                                                     # 图片保存结束

    plt.close()                                           # 关闭当前图像


    plt.figure(figsize=(10, 5))                           # 创建三轴陀螺仪平均波形图

    plt.plot(time_s, mean_signal[:, 3], label="gx")       # 绘制平均 X 轴角速度
    plt.plot(time_s, mean_signal[:, 4], label="gy")       # 绘制平均 Y 轴角速度
    plt.plot(time_s, mean_signal[:, 5], label="gz")       # 绘制平均 Z 轴角速度

    plt.xlabel("Time (s)")                                # 设置横坐标名称
    plt.ylabel("Angular Velocity (deg/s)")                # 设置纵坐标名称

    plt.title(                                            # 设置当前陀螺仪图标题
        f"{label} - Mean Gyroscope Signal"
    )                                                     # 图标题设置结束

    plt.legend(loc="best")                                # 自动选择遮挡最少的图例位置
    plt.grid()                                            # 显示网格
    plt.tight_layout()                                    # 自动调整图像布局

    plt.savefig(                                          # 保存当前陀螺仪平均波形图
        OUTPUT_DIR / f"{label}_mean_gyro.png",            # 设置保存文件名
        dpi=200,                                          # 设置图片分辨率
        bbox_inches="tight"                               # 自动裁剪多余空白区域
    )                                                     # 图片保存结束

    plt.close()                                           # 关闭当前图像


    print(                                                # 输出当前类别分析结果
        f"{label}: {len(samples)} training samples analyzed"
    )                                                     # 当前类别提示输出结束


print()                                                   # 输出空行

print(                                                    # 输出全部分析完成提示
    f"Time-domain figures saved to: {OUTPUT_DIR}"
)                                                         # 输出结束