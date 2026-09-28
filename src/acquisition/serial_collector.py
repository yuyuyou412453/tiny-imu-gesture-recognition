import serial                              # 导入 pyserial 库，用于 Python 与 ESP32 之间进行串口通信
import time                                # 导入 time 模块，用于延时和计时
import csv                                 # 导入 csv 模块，用于将采集数据写入 CSV 文件
from pathlib import Path                   # 导入 Path，用于处理文件夹和文件路径
from datetime import datetime              # 导入 datetime，用于生成包含日期和时间的文件名

PORT = "COM7"                              # 设置 ESP32 当前使用的串口号
BAUD_RATE = 115200                         # 设置串口波特率，与 ESP32 端保持一致

DURATION = 2.0                             # 设置每个手势样本的采集时间，单位为秒
DEFAULT_NUM_SAMPLES = 20                   # 设置默认连续采集的样本数量
REST_TIME = 2.0                            # 设置两次样本采集之间的休息时间，单位为秒

VALID_LABELS = [                           # 定义程序允许输入的手势类别列表
    "left",                                # 向左手势类别
    "right",                               # 向右手势类别
    "up",                                  # 向上手势类别
    "down",                                # 向下手势类别
    "still"                                # 静止类别
]                                          # 手势类别列表定义结束

label = input(                             # 获取用户输入的当前手势类别
    "Input label (left/right/up/down/still): "  # 在终端显示输入提示
).strip().lower()                          # 去除首尾空格，并统一转换为小写

if label not in VALID_LABELS:              # 判断输入的手势类别是否合法
    raise ValueError(                      # 如果类别不合法，则抛出异常并停止程序
        f"Invalid label: {label}\n"        # 输出当前输入的非法类别
        f"Valid labels: {VALID_LABELS}"    # 输出允许使用的合法类别
    )                                      # 异常信息定义结束

num_input = input(                         # 获取用户输入的样本采集数量
    f"Number of samples [{DEFAULT_NUM_SAMPLES}]: "  # 显示默认采集数量
).strip()                                  # 去除输入字符串首尾空格

if num_input == "":                        # 判断用户是否直接按下回车
    num_samples = DEFAULT_NUM_SAMPLES      # 如果未输入数字，则使用默认样本数量
else:                                      # 如果用户输入了具体数量
    num_samples = int(num_input)           # 将输入字符串转换为整数

    if num_samples <= 0:                   # 判断样本数量是否小于或等于 0
        raise ValueError(                  # 如果数量不合法，则抛出异常
            "Number of samples must be greater than 0."  # 提示样本数量必须大于 0
        )                                  # 异常信息定义结束

save_dir = Path("data/raw") / label        # 构造当前手势类别的数据保存路径
save_dir.mkdir(                            # 创建数据保存目录
    parents=True,                          # 如果上级目录不存在，则自动一并创建
    exist_ok=True                          # 如果目录已经存在，则不报错
)                                          # 目录创建操作结束

print()                                    # 输出空行，使终端显示更加清晰
print(f"Opening serial port {PORT}...")     # 提示正在打开指定串口

ser = serial.Serial(                       # 创建串口连接对象
    PORT,                                  # 指定串口号
    BAUD_RATE,                             # 指定串口通信波特率
    timeout=1                              # 设置串口读取超时时间为 1 秒
)                                          # 串口对象创建结束

time.sleep(2)                              # 等待 ESP32 串口初始化和可能的自动复位完成

print(f"Connected to {PORT}")              # 提示已经成功连接串口
print()                                    # 输出空行

print("==============================")       # 输出分隔线
print(f"Label: {label}")                   # 输出当前采集的手势类别
print(f"Samples: {num_samples}")           # 输出本次计划采集的样本数量
print(f"Duration: {DURATION} s")           # 输出每个样本的采集时长
print("==============================")       # 输出分隔线
print()                                    # 输出空行

print("Keep the MPU6500 orientation consistent.")  # 提醒采集时保持 MPU6500 基本朝向一致
print("Perform ONE gesture during each recording.")  # 提醒每个样本中只完成一次手势
print()                                    # 输出空行

try:                                       # 开始异常处理，用于捕获用户中断

    for sample_index in range(             # 使用循环连续采集多个样本
        1,                                 # 从第 1 个样本开始
        num_samples + 1                    # 循环到指定样本数量
    ):                                     # for 循环定义结束

        print()                            # 输出空行
        print(                             # 输出当前样本采集进度
            f"Sample {sample_index}/{num_samples}"  # 显示当前第几个样本
        )                                  # 输出语句结束

        for i in range(3, 0, -1):          # 生成 3、2、1 倒计时
            print(i)                       # 输出当前倒计时数字
            time.sleep(1)                  # 每个数字之间等待 1 秒

        ser.reset_input_buffer()           # 清空串口接收缓冲区，避免保存倒计时期间的数据

        print("Start!")                    # 提示正式开始本次采集

        rows = []                          # 创建空列表，用于保存当前样本的所有数据行
        start_time = time.time()           # 记录当前样本开始采集的时间

        while (                            # 在指定采集时长内持续读取串口数据
            time.time() - start_time       # 计算当前已经采集的时间
            < DURATION                     # 判断是否仍小于设定采集时长
        ):                                 # while 条件定义结束

            line = (                       # 读取并处理一行串口数据
                ser.readline()             # 从串口读取一整行字节数据
                .decode(                   # 将字节数据转换为字符串
                    "utf-8",               # 使用 UTF-8 编码方式解码
                    errors="ignore"        # 遇到异常字节时直接忽略
                )                          # decode 操作结束
                .strip()                   # 去除字符串首尾空格和换行符
            )                              # 当前串口数据行读取结束

            if not line:                   # 判断当前读取的数据是否为空
                continue                   # 如果为空，则跳过本轮循环

            parts = line.split(",")        # 按逗号将一行数据拆分成多个字段

            if len(parts) != 7:            # 判断数据是否包含时间戳和六轴共 7 个字段
                continue                   # 如果字段数量不正确，则跳过该行

            try:                           # 尝试将字符串字段转换为数值

                row = [                    # 创建当前采样时刻的数据列表
                    int(parts[0]),          # 将第 1 个字段转换为整数时间戳
                    float(parts[1]),        # 将第 2 个字段转换为 X 轴加速度
                    float(parts[2]),        # 将第 3 个字段转换为 Y 轴加速度
                    float(parts[3]),        # 将第 4 个字段转换为 Z 轴加速度
                    float(parts[4]),        # 将第 5 个字段转换为 X 轴角速度
                    float(parts[5]),        # 将第 6 个字段转换为 Y 轴角速度
                    float(parts[6])         # 将第 7 个字段转换为 Z 轴角速度
                ]                          # 当前数据列表定义结束

                rows.append(row)           # 将当前数据行加入本次样本的数据列表

            except ValueError:             # 捕获字段无法正确转换为数值的情况
                continue                   # 出现异常时跳过当前数据行

        print("Stop!")                     # 提示当前样本采集结束

        timestamp_string = (               # 生成用于文件命名的时间字符串
            datetime.now()                 # 获取当前日期和时间
            .strftime(                     # 将日期时间按照指定格式转换为字符串
                "%Y%m%d_%H%M%S_%f"         # 设置文件名中的日期时间格式
            )                              # strftime 操作结束
        )                                  # 时间字符串生成结束

        filename = f"{timestamp_string}.csv"  # 使用时间字符串生成 CSV 文件名
        save_path = save_dir / filename    # 拼接得到完整的文件保存路径

        with open(                         # 打开 CSV 文件准备写入数据
            save_path,                     # 指定文件保存路径
            "w",                           # 以写入模式打开文件
            newline="",                    # 防止 Windows 下产生额外空行
            encoding="utf-8"               # 设置文件编码为 UTF-8
        ) as f:                            # 将打开的文件对象命名为 f

            writer = csv.writer(f)         # 创建 CSV 写入对象

            writer.writerow([              # 写入 CSV 文件表头
                "timestamp",               # 第 1 列为时间戳
                "ax",                      # 第 2 列为 X 轴加速度
                "ay",                      # 第 3 列为 Y 轴加速度
                "az",                      # 第 4 列为 Z 轴加速度
                "gx",                      # 第 5 列为 X 轴角速度
                "gy",                      # 第 6 列为 Y 轴角速度
                "gz"                       # 第 7 列为 Z 轴角速度
            ])                             # 表头写入结束

            writer.writerows(rows)         # 将本次采集到的所有数据行写入 CSV 文件

        print(f"Saved: {save_path}")       # 输出当前样本的文件保存路径
        print(f"Samples received: {len(rows)}")  # 输出本次成功采集的数据点数量

        if len(rows) < 70:                 # 判断当前样本的数据点数量是否过少
            print(                         # 输出数据点数量过少的警告
                "WARNING: "                # 警告信息前半部分
                "Too few data points."     # 提示当前采样点数量不足
            )                              # 警告输出结束

        if sample_index < num_samples:     # 判断当前是否还有后续样本需要采集

            print(                         # 输出休息时间提示
                f"Rest for {REST_TIME} s..."  # 提示两次采集之间的等待时间
            )                              # 提示输出结束

            time.sleep(                    # 暂停程序，让用户准备下一次手势
                REST_TIME                  # 等待设定的休息时间
            )                              # 休息结束

except KeyboardInterrupt:                  # 捕获用户按下 Ctrl+C 主动中断程序

    print()                                # 输出空行
    print(                                 # 输出中断提示
        "Collection interrupted by user."  # 提示数据采集已被用户中断
    )                                      # 中断提示输出结束

finally:                                   # 无论程序如何结束都执行以下代码

    ser.close()                            # 关闭串口连接并释放串口资源

    print()                                # 输出空行
    print("Serial port closed.")           # 提示串口已经关闭

print()                                    # 输出空行
print("==============================")       # 输出分隔线
print("Collection finished.")              # 提示整个数据采集过程结束
print(f"Label: {label}")                   # 输出本次采集的手势类别
print(f"Target samples: {num_samples}")    # 输出计划采集的样本数量
print(f"Save directory: {save_dir}")       # 输出数据实际保存目录
print("==============================")       # 输出结束分隔线