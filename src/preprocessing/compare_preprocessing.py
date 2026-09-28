from pathlib import Path                                  # 导入 Path，用于处理文件夹和文件路径
import pandas as pd                                       # 导入 pandas，用于读取 CSV 数据
import matplotlib.pyplot as plt                          # 导入 matplotlib，用于绘制波形


LABELS = [                                                # 定义需要进行对比的四类动态手势
    "left",                                               # 向左手势
    "right",                                              # 向右手势
    "up",                                                 # 向上手势
    "down"                                                # 向下手势
]                                                         # 动态手势类别定义结束


OUTPUT_DIR = Path(                                        # 定义对比图保存目录
    "assets/preprocessing_comparison"
)                                                         # 图片保存目录定义结束

OUTPUT_DIR.mkdir(                                         # 创建图片保存目录
    parents=True,                                         # 如果上级目录不存在则自动创建
    exist_ok=True                                         # 如果目录已经存在则不会报错
)                                                         # 图片保存目录创建结束


for label in LABELS:                                      # 依次处理四类动态手势

    raw_dir = Path("data/raw") / label                    # 设置当前类别的原始数据目录

    processed_dir = Path("data/processed") / label        # 设置当前类别处理后的数据目录

    raw_files = sorted(                                   # 获取当前类别全部原始 CSV 文件
        raw_dir.glob("*.csv")                             # 查找目录中的全部 CSV 文件
    )                                                     # 原始 CSV 文件列表获取结束

    if len(raw_files) == 0:                               # 判断当前类别是否存在原始数据
        print(f"No raw files found for {label}")          # 如果不存在则输出提示
        continue                                          # 跳过当前类别

    raw_path = raw_files[0]                               # 选择当前类别第一个 CSV 作为代表样本

    processed_path = (                                    # 构造对应的预处理后 CSV 文件路径
        processed_dir                                     # 使用处理后数据目录
        / raw_path.name                                   # 保持原始文件名不变
    )                                                     # 处理后文件路径构造结束

    raw_df = pd.read_csv(raw_path)                        # 读取原始 CSV 数据

    processed_df = pd.read_csv(processed_path)            # 读取预处理后的 CSV 数据

    time_s = (                                            # 计算当前样本的相对时间
        raw_df["timestamp"]                               # 获取时间戳
        - raw_df["timestamp"].iloc[0]                     # 减去第一个时间戳，使时间从 0 开始
    ) / 1000.0                                            # 将时间单位从毫秒转换为秒


    plt.figure(figsize=(10, 5))                           # 创建加速度对比图

    plt.plot(                                             # 绘制原始 X 轴加速度
        time_s,                                           # 横坐标使用时间
        raw_df["ax"],                                     # 纵坐标使用原始 ax
        label="Raw ax"                                    # 设置图例名称
    )                                                     # 原始加速度绘制结束

    plt.plot(                                             # 绘制处理后的 X 轴加速度
        time_s,                                           # 横坐标使用时间
        processed_df["ax"],                               # 纵坐标使用处理后的 ax
        label="Processed ax"                              # 设置图例名称
    )                                                     # 处理后加速度绘制结束

    plt.xlabel("Time (s)")                                # 设置横坐标名称
    plt.ylabel("Acceleration (g)")                        # 设置纵坐标名称

    plt.title(                                            # 设置加速度图标题
        f"{label} - Raw vs Processed Accelerometer"
    )                                                     # 加速度图标题设置结束

    plt.legend()                                          # 显示图例
    plt.grid()                                            # 显示网格
    plt.tight_layout()                                    # 自动调整图像布局

    acc_output_path = (                                   # 构造加速度对比图保存路径
        OUTPUT_DIR                                        # 使用统一图片目录
        / f"{label}_acc_comparison.png"                   # 设置图片文件名
    )                                                     # 保存路径构造结束

    plt.savefig(                                          # 保存加速度对比图
        acc_output_path,                                  # 指定保存路径
        dpi=200,                                          # 设置图片分辨率
        bbox_inches="tight"                               # 自动裁剪多余空白区域
    )                                                     # 加速度图片保存结束

    plt.close()                                           # 关闭当前图像，避免同时打开大量窗口


    plt.figure(figsize=(10, 5))                           # 创建陀螺仪对比图

    plt.plot(                                             # 绘制原始 X 轴角速度
        time_s,                                           # 横坐标使用时间
        raw_df["gx"],                                     # 纵坐标使用原始 gx
        label="Raw gx"                                    # 设置图例名称
    )                                                     # 原始角速度绘制结束

    plt.plot(                                             # 绘制处理后的 X 轴角速度
        time_s,                                           # 横坐标使用时间
        processed_df["gx"],                               # 纵坐标使用处理后的 gx
        label="Processed gx"                              # 设置图例名称
    )                                                     # 处理后角速度绘制结束

    plt.xlabel("Time (s)")                                # 设置横坐标名称
    plt.ylabel("Angular Velocity (deg/s)")                # 设置纵坐标名称

    plt.title(                                            # 设置陀螺仪图标题
        f"{label} - Raw vs Processed Gyroscope"
    )                                                     # 陀螺仪图标题设置结束

    plt.legend()                                          # 显示图例
    plt.grid()                                            # 显示网格
    plt.tight_layout()                                    # 自动调整图像布局

    gyro_output_path = (                                  # 构造陀螺仪对比图保存路径
        OUTPUT_DIR                                        # 使用统一图片目录
        / f"{label}_gyro_comparison.png"                  # 设置图片文件名
    )                                                     # 保存路径构造结束

    plt.savefig(                                          # 保存陀螺仪对比图
        gyro_output_path,                                 # 指定保存路径
        dpi=200,                                          # 设置图片分辨率
        bbox_inches="tight"                               # 自动裁剪多余空白区域
    )                                                     # 陀螺仪图片保存结束

    plt.close()                                           # 关闭当前图像

    print(                                                # 输出当前类别保存完成提示
        f"Saved comparison figures for {label}"
    )                                                     # 输出结束


print()                                                   # 输出空行

print(                                                    # 输出全部图片保存完成提示
    f"All comparison figures saved to: {OUTPUT_DIR}"
)                                                         # 输出结束