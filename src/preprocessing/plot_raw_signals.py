from pathlib import Path                              # 导入 Path，用于处理文件夹和文件路径
import pandas as pd                                   # 导入 pandas，用于读取 CSV 数据
import matplotlib.pyplot as plt                      # 导入 matplotlib.pyplot，用于绘制时序波形


DATA_DIR = Path("data/raw")                           # 设置原始 IMU 数据所在的根目录
OUTPUT_DIR = Path("assets/raw_signals")               # 设置绘制完成后的图片保存目录

OUTPUT_DIR.mkdir(                                     # 创建图片保存目录
    parents=True,                                     # 如果上级目录不存在，则自动一并创建
    exist_ok=True                                     # 如果目录已经存在，则不会报错
)                                                     # 图片保存目录创建结束


LABELS = [                                            # 定义需要依次处理的五类手势
    "left",                                           # 向左手势
    "right",                                          # 向右手势
    "up",                                             # 向上手势
    "down",                                           # 向下手势
    "still"                                           # 静止类别
]                                                     # 手势标签列表定义结束


for label in LABELS:                                  # 依次遍历五类手势

    label_dir = DATA_DIR / label                      # 构造当前类别对应的数据文件夹路径

    csv_files = sorted(                               # 获取当前类别下的所有 CSV 文件，并按照文件名排序
        label_dir.glob("*.csv")                       # 查找当前文件夹下所有扩展名为 .csv 的文件
    )                                                 # CSV 文件列表获取结束

    if len(csv_files) == 0:                           # 判断当前类别文件夹中是否没有 CSV 文件
        print(f"No CSV files found for {label}.")     # 如果没有文件，则在终端输出提示
        continue                                      # 跳过当前类别，继续处理下一个类别

    csv_path = csv_files[0]                           # 选择当前类别中的第一个 CSV 文件作为代表样本

    df = pd.read_csv(csv_path)                        # 使用 pandas 读取当前 CSV 文件

    time_s = (                                        # 开始计算相对于当前样本起点的时间
        df["timestamp"]                               # 读取当前样本的时间戳列
        - df["timestamp"].iloc[0]                     # 减去第一个时间戳，使时间从 0 开始
    ) / 1000.0                                        # 将时间单位由毫秒转换为秒


    # =========================                     # 分隔说明
    # 加速度计原始波形                             # 当前部分用于绘制三轴加速度
    # =========================                     # 分隔说明

    plt.figure(                                       # 创建新的绘图窗口
        figsize=(10, 5)                               # 设置图像尺寸为 10 × 5 英寸
    )                                                 # 绘图窗口创建结束

    plt.plot(                                         # 绘制 X 轴加速度曲线
        time_s,                                       # 设置横轴为相对时间
        df["ax"],                                     # 设置纵轴为 X 轴加速度
        label="ax"                                    # 设置当前曲线图例名称
    )                                                 # X 轴加速度绘制结束

    plt.plot(                                         # 绘制 Y 轴加速度曲线
        time_s,                                       # 设置横轴为相对时间
        df["ay"],                                     # 设置纵轴为 Y 轴加速度
        label="ay"                                    # 设置当前曲线图例名称
    )                                                 # Y 轴加速度绘制结束

    plt.plot(                                         # 绘制 Z 轴加速度曲线
        time_s,                                       # 设置横轴为相对时间
        df["az"],                                     # 设置纵轴为 Z 轴加速度
        label="az"                                    # 设置当前曲线图例名称
    )                                                 # Z 轴加速度绘制结束

    plt.xlabel("Time (s)")                            # 设置横坐标名称为时间，单位为秒
    plt.ylabel("Acceleration (g)")                    # 设置纵坐标名称为加速度，单位为 g

    plt.title(                                        # 设置当前加速度图标题
        f"{label} - Raw Accelerometer Signal"         # 标题中显示当前手势类别
    )                                                 # 图标题设置结束

    plt.legend()                                      # 显示 ax、ay、az 三条曲线的图例
    plt.grid()                                        # 显示网格，便于观察波形变化
    plt.tight_layout()                                # 自动调整边距，避免标题和坐标轴文字被遮挡

    acc_save_path = (                                 # 构造当前加速度图片保存路径
        OUTPUT_DIR                                    # 使用统一的图片保存目录
        / f"{label}_acc.png"                          # 图片名称，例如 left_acc.png
    )                                                 # 加速度图片路径构造结束

    plt.savefig(                                      # 将当前加速度波形图保存为 PNG 图片
        acc_save_path,                                # 指定图片保存路径
        dpi=200,                                      # 设置保存分辨率为 200 dpi
        bbox_inches="tight"                           # 自动裁剪图片周围多余空白区域
    )                                                 # 加速度图片保存结束

    print(                                            # 在终端输出图片保存结果
        f"Saved: {acc_save_path}"                     # 显示当前加速度图片实际保存位置
    )                                                 # 输出结束


    # =========================                     # 分隔说明
    # 陀螺仪原始波形                               # 当前部分用于绘制三轴角速度
    # =========================                     # 分隔说明

    plt.figure(                                       # 创建新的绘图窗口
        figsize=(10, 5)                               # 设置图像尺寸为 10 × 5 英寸
    )                                                 # 绘图窗口创建结束

    plt.plot(                                         # 绘制 X 轴角速度曲线
        time_s,                                       # 设置横轴为相对时间
        df["gx"],                                     # 设置纵轴为 X 轴角速度
        label="gx"                                    # 设置当前曲线图例名称
    )                                                 # X 轴角速度绘制结束

    plt.plot(                                         # 绘制 Y 轴角速度曲线
        time_s,                                       # 设置横轴为相对时间
        df["gy"],                                     # 设置纵轴为 Y 轴角速度
        label="gy"                                    # 设置当前曲线图例名称
    )                                                 # Y 轴角速度绘制结束

    plt.plot(                                         # 绘制 Z 轴角速度曲线
        time_s,                                       # 设置横轴为相对时间
        df["gz"],                                     # 设置纵轴为 Z 轴角速度
        label="gz"                                    # 设置当前曲线图例名称
    )                                                 # Z 轴角速度绘制结束

    plt.xlabel("Time (s)")                            # 设置横坐标名称为时间，单位为秒
    plt.ylabel("Angular Velocity (deg/s)")            # 设置纵坐标名称为角速度，单位为度每秒

    plt.title(                                        # 设置当前陀螺仪图标题
        f"{label} - Raw Gyroscope Signal"             # 标题中显示当前手势类别
    )                                                 # 图标题设置结束

    plt.legend()                                      # 显示 gx、gy、gz 三条曲线的图例
    plt.grid()                                        # 显示网格，便于观察波形变化
    plt.tight_layout()                                # 自动调整布局，避免文字被裁剪

    gyro_save_path = (                                # 构造当前陀螺仪图片保存路径
        OUTPUT_DIR                                    # 使用统一的图片保存目录
        / f"{label}_gyro.png"                         # 图片名称，例如 left_gyro.png
    )                                                 # 陀螺仪图片路径构造结束

    plt.savefig(                                      # 将当前陀螺仪波形图保存为 PNG 图片
        gyro_save_path,                               # 指定图片保存路径
        dpi=200,                                      # 设置保存分辨率为 200 dpi
        bbox_inches="tight"                           # 自动裁剪图片周围多余空白区域
    )                                                 # 陀螺仪图片保存结束

    print(                                            # 在终端输出图片保存结果
        f"Saved: {gyro_save_path}"                    # 显示当前陀螺仪图片实际保存位置
    )                                                 # 输出结束


print()                                               # 输出空行，使终端结果更加清晰

print(                                                # 输出全部图片保存完成提示
    f"All raw signal figures saved to: {OUTPUT_DIR}"  # 显示所有图片统一保存目录
)                                                     # 输出结束

plt.show()                                            # 在全部五类图像创建完成后一次性显示所有绘图窗口