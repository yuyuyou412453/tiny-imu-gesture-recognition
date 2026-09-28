import serial                              # 导入 PySerial，用于与 ESP32 进行串口通信
import time                                # 导入 time 模块，用于等待串口初始化

PORT = "COM7"                              # 设置 ESP32 当前对应的串口号
BAUD_RATE = 115200                         # 设置串口波特率，与 ESP32 程序保持一致

ser = serial.Serial(                       # 创建串口连接对象
    PORT,                                  # 指定需要打开的串口
    BAUD_RATE,                             # 指定串口通信波特率
    timeout=1                              # 设置串口读取超时时间为 1 s
)

time.sleep(2)                              # 等待 ESP32 串口初始化完成

print(f"Connected to {PORT}")              # 输出当前已经连接的串口
print("Receiving IMU data...")             # 提示开始接收 IMU 数据

try:                                       # 开始执行串口持续读取
    while True:                            # 不断循环读取 ESP32 发送的数据
        line = ser.readline()              # 从串口中读取一整行字节数据

        line = line.decode(                # 将串口收到的字节数据转换为字符串
            "utf-8",                       # 使用 UTF-8 编码方式进行解析
            errors="ignore"                # 如果存在异常字节，则直接忽略
        ).strip()                          # 去除字符串首尾的空格和换行符

        if not line:                       # 判断当前是否读取到有效内容
            continue                       # 如果为空，则跳过当前循环

        parts = line.split(",")            # 使用逗号将一行数据拆分为多个字段

        if len(parts) != 7:                # 判断是否包含时间戳和六轴数据共 7 个字段
            continue                       # 如果字段数量不正确，则跳过当前数据

        timestamp = int(parts[0])          # 将第 1 个字段转换为整数时间戳
        ax = float(parts[1])               # 将第 2 个字段转换为 X 轴加速度
        ay = float(parts[2])               # 将第 3 个字段转换为 Y 轴加速度
        az = float(parts[3])               # 将第 4 个字段转换为 Z 轴加速度
        gx = float(parts[4])               # 将第 5 个字段转换为 X 轴角速度
        gy = float(parts[5])               # 将第 6 个字段转换为 Y 轴角速度
        gz = float(parts[6])               # 将第 7 个字段转换为 Z 轴角速度

        print(                              # 在终端中输出解析后的数据
            timestamp,                     # 输出时间戳
            ax,                            # 输出 X 轴加速度
            ay,                            # 输出 Y 轴加速度
            az,                            # 输出 Z 轴加速度
            gx,                            # 输出 X 轴角速度
            gy,                            # 输出 Y 轴角速度
            gz                             # 输出 Z 轴角速度
        )

except KeyboardInterrupt:                  # 捕获用户按下 Ctrl+C 的操作
    print("\nStopped.")                    # 提示串口数据接收已经停止

finally:                                   # 无论程序正常还是异常结束都会执行
    ser.close()                            # 关闭串口连接
    print("Serial port closed.")           # 提示串口已经关闭