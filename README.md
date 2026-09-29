# 基于六轴 IMU 时序信号的轻量手势识别与端侧部署

## 1. 项目目标

- 读取六轴 IMU 数据
- 对原始时序信号进行预处理
- 分析时域与频域特征
- 建立传统机器学习 baseline
- 训练轻量 1D CNN
- 进行模型量化
- 完成实时推理
- 部署到 MCU / 边缘端

## 2. 项目框架与数据链路

### 2.1 项目框架

```text
tiny-imu-gesture-recognition/
├── data/
│   └── raw/
│       ├── left/
│       ├── right/
│       ├── up/
│       ├── down/
│       └── still/
│
├── src/
│   ├── acquisition/
│   │   └── serial_receiver.py
|   |   └── serial_collector.py
│   ├── preprocessing/
|   |   └── load_raw_data.py
│   ├── training/
│   ├── inference/
│   └── deployment/
├── assets/
|   └── raw_signals/
|       ├── left_acc.png
|       ├── left_gyro.png
|       ├── right_acc.png
|       ├── right_gyro.png
|       ├── up_acc.png
|       ├── up_gyro.png
|       ├── down_acc.png
|       ├── down_gyro.png
|       ├── still_acc.png
|       └── still_gyro.png
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

| 路径 | 主要用途 |
| --- | --- |
| `data/` | 保存项目使用的数据 |
| `data/raw/` | 保存未经处理的原始 IMU 数据 |
| `src/` | 保存项目主要源代码 |
| `src/acquisition/` | ESP32 串口数据接收与原始 IMU 数据采集 |
| `src/preprocessing/` | 数据读取、滤波、归一化、滑动窗口和特征处理 |
| `src/training/` | 传统机器学习模型及 1D CNN 的训练代码 |
| `src/inference/` | 模型加载、测试和实时推理代码 |
| `src/deployment/` | 模型导出、量化以及后续端侧部署相关代码 |
| `assets/` | 保存 README 中使用的波形图、频谱图、实验结果图等 |
| `docs/` | 保存补充学习笔记、实验记录和项目文档 |
| `requirements.txt` | 记录 Python 环境中的项目依赖及版本 |
| `.gitignore` | 指定 Git 不需要跟踪的本地文件和目录 |
| `README.md` | 记录项目目标、实现过程、学习笔记和实验结果 |

### 2.2 数据链路

```text
手持 MPU6500 完成指定手势
        ↓
MPU6500 采集 ax、ay、az、gx、gy、gz 六轴数据
        ↓ I²C
ESP32 开发板读取六轴数据
        ↓ USB 串口
Python 接收并保存为带手势标签的 CSV 数据
        ↓
滤波、归一化与滑动窗口分割
        ↓
时域 / 频域特征分析
        ↓
传统机器学习 baseline
        ↓
轻量 1D CNN 训练
        ↓
模型量化与导出
        ↓
部署至 ESP32
        ↓
MPU6500 实时采集
        ↓
ESP32 端侧推理
        ↓
输出手势识别结果
```

## 3. 开发环境配置

ESP32 端主要负责：

- 初始化 MPU6500
- 通过 I²C 读取六轴数据
- 按固定采样频率采集数据
- 通过 USB 串口向 PC 发送数据

PC 端 Python 主要负责：

- 接收串口数据
- 保存原始 CSV 数据
- 信号预处理与特征分析
- 模型训练与评估
- 后续模型转换与部署

### 3.1 ESP32 开发环境

ESP32 负责通过 I²C 读取 MPU6500 数据，并通过 USB 串口发送至 PC，因此除了 PC 端的 Python 环境外，还需要配置 ESP32 固件开发环境。

本项目使用 Arduino IDE 编写、编译并烧录 ESP32 固件。

### 3.2 Python 虚拟环境

不同 Python 项目可能依赖不同版本的软件包，如果将所有依赖都直接安装到系统 Python 中，随着项目数量的增加，可能出现版本冲突。因此为不同的项目创建独属于该项目的 Python 虚拟环境，使项目依赖相互隔离。

当前项目的本地路径：

```powershell
D:\GitHub\tiny-imu-gesture-recognition
```

首先进入项目目录：

```powershell
cd D:\GitHub\tiny-imu-gesture-recognition
```

### 3.3 创建虚拟环境

执行：

```powershell
python -m venv .venv
```

其中：

- python：调用当前 Python 解释器
- -m venv：运行 Python 自带的 venv 模块
- .venv：虚拟环境目录名称

执行后，项目根目录中会生成 `.venv/`，该目录保存当前项目独立的 Python 解释器和第三方依赖。

### 3.4 激活虚拟环境

Windows PowerShell 下执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

激活成功后，终端前通常会出现 `(.venv)`，此后通过 pip 安装的软件包都会安装到当前项目的虚拟环境中。

### 3.5 安装所需 Python 库

项目第一阶段主要进行 IMU 数据读取、数值计算、信号处理与可视化，因此先安装以下 Python 库：

```powershell
pip install numpy pandas matplotlib scipy pyserial
```

各库的主要用途如下：

| 库 | 主要用途 |
| --- | --- |
| NumPy | 数组、矩阵以及数值计算 |
| Pandas | CSV 等结构化数据的读取与处理 |
| Matplotlib | 绘制 IMU 时序波形、频谱和实验结果 |
| SciPy | 滤波、FFT 等信号处理操作 |
| PySerial | 接收 ESP32 通过串口发送的 IMU 数据 |

后续进入传统机器学习、1D CNN、模型导出和端侧通信阶段时，再根据实际需要继续安装：

- `scikit-learn`
- `PyTorch`
- `ONNX`
- `ONNX Runtime`

### 3.6 保存项目依赖

为了记录当前项目使用的软件包及其版本，执行：

```powershell
pip freeze > requirements.txt
```

该命令会在项目根目录生成 `requirements.txt`，其中记录当前虚拟环境中已经安装的 Python 软件包及对应版本。

以后如果需要在新的 Python 环境中恢复项目依赖，可以执行：

```powershell
pip install -r requirements.txt
```

从而按照 requirements.txt 中记录的版本重新安装所需的软件包。

## 4. IMU 信号获取与初步认识

### 4.1 什么是六轴 IMU

六轴 IMU（Inertial Measurement Unit，惯性测量单元）通常由三轴加速度计 `Accelerometer` 和三轴陀螺仪 `Gyroscope` 组成。

### 4.2 六轴数据的含义

MPU6500 输出三轴加速度和三轴角速度，共六个主要运动量：

| 数据 | 含义 | 典型单位 |
| --- | --- | --- |
| `ax` | X 轴方向加速度 | g 或 m/s² |
| `ay` | Y 轴方向加速度 | g 或 m/s² |
| `az` | Z 轴方向加速度 | g 或 m/s² |
| `gx` | 绕 X 轴旋转的角速度 | °/s |
| `gy` | 绕 Y 轴旋转的角速度 | °/s |
| `gz` | 绕 Z 轴旋转的角速度 | °/s |

其中：

- `ax`、`ay`、`az` 主要反映传感器的平移运动、振动以及重力在各坐标轴方向上的分量。
- `gx`、`gy`、`gz` 主要反映传感器绕三个坐标轴旋转时的角速度变化。

当 MPU6500 静止放置时，加速度计仍会受到重力影响，因此三个加速度轴中通常会有一个方向接近 `1 g`，具体取决于传感器当前的放置方向。

在手势执行过程中，六个通道会随时间连续变化，因此一次手势可以表示为一段六通道时序数据：

```text
t1 → ax1, ay1, az1, gx1, gy1, gz1
t2 → ax2, ay2, az2, gx2, gy2, gz2
t3 → ax3, ay3, az3, gx3, gy3, gz3
...
tn → axn, ayn, azn, gxn, gyn, gzn
```

后续将利用这六路时序信号之间的变化规律区分不同手势。

### 4.3 MPU6500 与 ESP32 硬件连接

| MPU6500 | ESP32 开发板 | 功能 |
| --- | --- | --- |
| `VCC` | `3V3` | 模块供电 |
| `GND` | `GND` | 公共地 |
| `SDA` | `D21` | I²C 数据线 |
| `SCL` | `D22` | I²C 时钟线 |

### 4.4 ESP32 读取 MPU6500 数据

在读取 MPU6500 数据之前，需要先在 Arduino IDE 中配置 ESP32 开发环境。

首先在 Arduino IDE 的开发板管理器 `Boards Manager` 中搜索：

```text
esp32
```

安装：

```text
esp32 by Espressif Systems
```

本项目当前使用的 ESP32 Arduino Core 版本为：

```text
3.3.11
```

安装完成后，将开发板选择为：

```text
ESP32 Dev Module
```

MPU6500 的寄存器读写通过 Arduino 自带的 Wire 库完成，不额外依赖第三方驱动库。

#### 4.4.1 检测 MPU6500 的 I²C 地址

首先使用 I²C 扫描程序确认 ESP32 能够正常检测到 MPU6500。

在 Arduino IDE 中新建程序：

```cpp
#include <Wire.h>  // 引入 Wire 库，用于 ESP32 的 I²C 通信

void setup() {  // setup() 在 ESP32 上电或复位后只执行一次
    Serial.begin(115200);  // 初始化串口通信，设置波特率为 115200

    // SDA = GPIO21，SCL = GPIO22
    Wire.begin(21, 22);  // 初始化 I²C，总线数据线使用 GPIO21，时钟线使用 GPIO22

    delay(1000);  // 延时 1000 ms，等待系统初始化完成

    Serial.println("I2C Scanner");  // 在串口监视器中输出 I2C Scanner
}

void loop() {  // loop() 中的程序会不断循环执行
    byte error;  // 保存 I²C 通信返回的状态
    byte address;  // 保存当前正在扫描的 I²C 地址
    int deviceCount = 0;  // 记录本轮扫描检测到的 I²C 设备数量

    Serial.println("Scanning...");  // 在串口监视器中提示开始扫描

    for (address = 1; address < 127; address++) {  // 依次扫描 1～126 的 I²C 地址
        Wire.beginTransmission(address);  // 尝试与当前地址上的 I²C 设备建立通信
        error = Wire.endTransmission();  // 结束本次通信，并获取通信返回状态

        if (error == 0) {  // 如果返回值为 0，说明当前地址存在正常响应的 I²C 设备
            Serial.print("I2C device found at address 0x");  // 输出检测到设备的提示信息

            if (address < 16) {  // 如果地址小于 0x10
                Serial.print("0");  // 补一个 0，使地址按照两位十六进制形式显示
            }

            Serial.println(address, HEX);  // 以十六进制形式输出检测到的 I²C 地址
            deviceCount++;  // 检测到的设备数量加 1
        }
    }

    if (deviceCount == 0) {  // 如果本轮扫描没有检测到任何 I²C 设备
        Serial.println("No I2C devices found.");  // 输出未检测到设备的提示信息
    }

    Serial.println();  // 输出空行，方便区分不同轮次的扫描结果

    delay(3000);  // 延时 3000 ms，再开始下一轮扫描
}
```

将程序编译并烧录到 ESP32 后，打开 Arduino IDE 的串口监视器，将波特率设置为：

```text
115200
```

正常情况下可以看到：

```text
Scanning...
I2C device found at address 0x68
```

#### 4.4.2 确认 IMU 芯片型号

I²C 扫描只能确认地址 `0x68` 上存在设备，因此进一步读取 `WHO_AM_I` 寄存器确认芯片型号：

```cpp
#include <Wire.h>                  // I²C 通信库

#define MPU_ADDR 0x68              // IMU 的 I²C 地址
#define WHO_AM_I 0x75              // WHO_AM_I 芯片身份寄存器地址

void setup()
{
    Serial.begin(115200);          // 初始化串口，波特率设置为 115200

    Wire.begin(21, 22);            // 初始化 I²C：SDA = GPIO21，SCL = GPIO22

    delay(1000);                   // 等待传感器上电稳定

    Wire.beginTransmission(MPU_ADDR);  // 开始与地址为 0x68 的设备通信

    Wire.write(WHO_AM_I);          // 指定要读取的 WHO_AM_I 寄存器

    Wire.endTransmission(false);   // 不释放 I²C 总线，准备继续读取数据

    Wire.requestFrom(MPU_ADDR, 1); // 从设备读取 1 个字节

    if (Wire.available())          // 判断是否成功接收到数据
    {
        byte whoAmI = Wire.read(); // 读取 WHO_AM_I 寄存器返回值

        Serial.print("WHO_AM_I = 0x");  // 输出提示信息

        Serial.println(whoAmI, HEX);    // 以十六进制形式输出芯片身份值
    }
    else
    {
        Serial.println("Failed to read WHO_AM_I.");  // 读取失败时输出提示
    }
}

void loop()
{
}
```

实际读取结果为：

```text
WHO_AM_I = 0x70
```

因此本项目使用的模块实际识别为 MPU6500 或 MPU6500 兼容芯片，后续按照 MPU6500 寄存器定义进行数据读取。

### 4.5 串口数据格式

为了方便后续 Python 解析和 CSV 数据保存，本项目采用逗号分隔的串口数据格式，每一行表示一个采样时刻的数据：

```text
timestamp,ax,ay,az,gx,gy,gz
```

各字段含义如下：

| 字段 | 含义 | 单位 |
| --- | --- | --- |
| `timestamp` | ESP32 启动后的时间 | ms |
| `ax` | X 轴加速度 | g |
| `ay` | Y 轴加速度 | g |
| `az` | Z 轴加速度 | g |
| `gx` | 绕 X 轴角速度 | °/s |
| `gy` | 绕 Y 轴角速度 | °/s |
| `gz` | 绕 Z 轴角速度 | °/s |

本项目以约 `50 Hz` 为目标采样频率。程序通过 MPU6500 的采样率分频寄存器配置传感器内部输出频率，并按照约 `20 ms` 的周期读取六轴数据。由于 I²C 读取、数据处理及串口发送本身存在一定耗时，实际串口输出间隔可能略大于 `20 ms`。

ESP32 使用以下程序读取 MPU6500 六轴数据，并按照上述格式通过串口输出：

```cpp
#include <Wire.h>                              // 引入 Wire 库，用于 ESP32 与 MPU6500 之间进行 I²C 通信

#define MPU6500_ADDR 0x68                      // 定义 MPU6500 的 I²C 从机地址为 0x68

#define SMPLRT_DIV 0x19                        // 定义采样率分频寄存器地址为 0x19
#define CONFIG 0x1A                            // 定义陀螺仪数字低通滤波配置寄存器地址为 0x1A
#define GYRO_CONFIG 0x1B                       // 定义陀螺仪量程配置寄存器地址为 0x1B
#define ACCEL_CONFIG 0x1C                      // 定义加速度计量程配置寄存器地址为 0x1C
#define ACCEL_CONFIG2 0x1D                     // 定义加速度计数字低通滤波配置寄存器地址为 0x1D
#define ACCEL_XOUT_H 0x3B                      // 定义加速度计 X 轴高 8 位数据寄存器地址为 0x3B
#define PWR_MGMT_1 0x6B                        // 定义电源管理寄存器地址为 0x6B
#define WHO_AM_I 0x75                          // 定义芯片身份识别寄存器地址为 0x75

void writeRegister(byte reg, byte value)       // 定义寄存器写入函数，reg 为寄存器地址，value 为写入的数据
{                                              // writeRegister() 函数开始
    Wire.beginTransmission(MPU6500_ADDR);      // 开始与 I²C 地址为 0x68 的 MPU6500 通信
    Wire.write(reg);                           // 将需要写入的目标寄存器地址发送给 MPU6500
    Wire.write(value);                         // 将需要写入目标寄存器的配置值发送给 MPU6500
    Wire.endTransmission();                    // 结束本次 I²C 写操作并释放总线
}                                              // writeRegister() 函数结束

byte readRegister(byte reg)                    // 定义寄存器读取函数，读取指定寄存器中的 1 个字节
{                                              // readRegister() 函数开始
    Wire.beginTransmission(MPU6500_ADDR);      // 开始与 MPU6500 通信
    Wire.write(reg);                           // 指定需要读取的寄存器地址
    Wire.endTransmission(false);               // 结束写地址阶段，但不释放 I²C 总线，准备继续读取
    Wire.requestFrom(MPU6500_ADDR, 1);         // 向 MPU6500 请求读取 1 个字节的数据

    if (Wire.available())                      // 判断 I²C 接收缓冲区中是否已经存在可读取的数据
    {                                          // 如果存在数据，则进入该代码块
        return Wire.read();                    // 从 I²C 缓冲区读取 1 个字节并返回
    }                                          // if 判断结束

    return 0xFF;                               // 如果读取失败，则返回 0xFF 作为错误标志
}                                              // readRegister() 函数结束

void setup()                                   // setup() 在 ESP32 上电或复位后只执行一次
{                                              // setup() 函数开始
    Serial.begin(115200);                      // 初始化串口通信，并将波特率设置为 115200

    Wire.begin(21, 22);                        // 初始化 I²C，总线 SDA 使用 GPIO21，SCL 使用 GPIO22

    delay(1000);                               // 延时 1000 ms，等待 MPU6500 上电并稳定

    byte whoAmI = readRegister(WHO_AM_I);      // 读取 WHO_AM_I 寄存器，用于确认传感器芯片身份

    Serial.print("WHO_AM_I = 0x");             // 在串口中输出 WHO_AM_I 提示信息
    Serial.println(whoAmI, HEX);               // 将读取到的芯片身份值以十六进制形式输出并换行

    if (whoAmI != 0x70)                        // 判断芯片身份值是否为 MPU6500 对应的 0x70
    {                                          // 如果身份值不是 0x70，则进入错误处理
        Serial.println("MPU6500 identification failed."); // 在串口中输出 MPU6500 身份识别失败提示

        while (1)                              // 进入无限循环，使程序停止继续执行
        {                                      // while 循环开始
            delay(10);                         // 每次循环延时 10 ms，避免高速空循环
        }                                      // while 循环结束
    }                                          // 芯片身份判断结束

    writeRegister(PWR_MGMT_1, 0x01);           // 向电源管理寄存器写入 0x01，唤醒 MPU6500 并选择时钟源

    delay(100);                                // 延时 100 ms，等待 MPU6500 完成唤醒

    writeRegister(CONFIG, 0x04);               // 配置陀螺仪数字低通滤波器，带宽约为 20 Hz

    writeRegister(ACCEL_CONFIG2, 0x04);        // 配置加速度计数字低通滤波器，带宽约为 20 Hz

    writeRegister(GYRO_CONFIG, 0x08);          // 设置陀螺仪量程为 ±500 °/s

    writeRegister(ACCEL_CONFIG, 0x08);         // 设置加速度计量程为 ±4 g

    writeRegister(SMPLRT_DIV, 19);             // 设置采样率分频值，使传感器内部输出频率约为 50 Hz

    Serial.println("MPU6500 initialized successfully."); // 在串口中输出 MPU6500 初始化成功提示

    delay(1000);                               // 延时 1000 ms，等待传感器输出数据稳定
}                                              // setup() 函数结束

void loop()                                    // loop() 在 ESP32 运行过程中不断循环执行
{                                              // loop() 函数开始
    Wire.beginTransmission(MPU6500_ADDR);      // 开始与 MPU6500 进行 I²C 通信

    Wire.write(ACCEL_XOUT_H);                  // 指定从 ACCEL_XOUT_H 寄存器开始连续读取传感器数据

    Wire.endTransmission(false);               // 不释放 I²C 总线，准备继续执行连续读取

    Wire.requestFrom(MPU6500_ADDR, 14);        // 连续请求读取 14 个字节的加速度、温度和陀螺仪原始数据

    if (Wire.available() == 14)                // 判断是否完整接收到 14 个字节的数据
    {                                          // 如果接收到完整数据，则进入数据解析过程
        int16_t rawAx = (Wire.read() << 8) | Wire.read(); // 读取 X 轴加速度高低两个字节并合成为 16 位有符号数据
        int16_t rawAy = (Wire.read() << 8) | Wire.read(); // 读取 Y 轴加速度高低两个字节并合成为 16 位有符号数据
        int16_t rawAz = (Wire.read() << 8) | Wire.read(); // 读取 Z 轴加速度高低两个字节并合成为 16 位有符号数据

        int16_t rawTemp = (Wire.read() << 8) | Wire.read(); // 读取温度高低两个字节并合成为 16 位原始温度数据

        int16_t rawGx = (Wire.read() << 8) | Wire.read(); // 读取 X 轴陀螺仪高低两个字节并合成为 16 位有符号数据
        int16_t rawGy = (Wire.read() << 8) | Wire.read(); // 读取 Y 轴陀螺仪高低两个字节并合成为 16 位有符号数据
        int16_t rawGz = (Wire.read() << 8) | Wire.read(); // 读取 Z 轴陀螺仪高低两个字节并合成为 16 位有符号数据

        float ax = rawAx / 8192.0;              // ±4 g 量程下以 8192 LSB/g 将 X 轴原始数据转换为 g
        float ay = rawAy / 8192.0;              // ±4 g 量程下以 8192 LSB/g 将 Y 轴原始数据转换为 g
        float az = rawAz / 8192.0;              // ±4 g 量程下以 8192 LSB/g 将 Z 轴原始数据转换为 g

        float gx = rawGx / 65.5;                // ±500 °/s 量程下以 65.5 LSB/(°/s) 将 X 轴原始数据转换为 °/s
        float gy = rawGy / 65.5;                // ±500 °/s 量程下以 65.5 LSB/(°/s) 将 Y 轴原始数据转换为 °/s
        float gz = rawGz / 65.5;                // ±500 °/s 量程下以 65.5 LSB/(°/s) 将 Z 轴原始数据转换为 °/s

        unsigned long timestamp = millis();     // 获取 ESP32 启动至当前时刻经过的时间，单位为 ms

        Serial.print(timestamp);                // 通过串口输出当前时间戳
        Serial.print(",");                      // 输出逗号，用于分隔时间戳和 X 轴加速度

        Serial.print(ax, 4);                    // 输出 X 轴加速度，并保留 4 位小数
        Serial.print(",");                      // 输出逗号，用于分隔不同数据字段

        Serial.print(ay, 4);                    // 输出 Y 轴加速度，并保留 4 位小数
        Serial.print(",");                      // 输出逗号，用于分隔不同数据字段

        Serial.print(az, 4);                    // 输出 Z 轴加速度，并保留 4 位小数
        Serial.print(",");                      // 输出逗号，用于分隔不同数据字段

        Serial.print(gx, 4);                    // 输出 X 轴角速度，并保留 4 位小数
        Serial.print(",");                      // 输出逗号，用于分隔不同数据字段

        Serial.print(gy, 4);                    // 输出 Y 轴角速度，并保留 4 位小数
        Serial.print(",");                      // 输出逗号，用于分隔不同数据字段

        Serial.println(gz, 4);                  // 输出 Z 轴角速度，保留 4 位小数并在本组数据结束后换行
    }                                          // 六轴数据读取与输出结束

    delay(20);                                 // 延时约 20 ms，再进行下一轮数据读取，使采样频率接近 50 Hz
}                                              // loop() 函数结束
```

将程序烧录到 ESP32 后，在串口监视器中可以连续观察到类似：

```text
1520,0.0123,-0.0184,0.9981,0.4271,-0.1924,0.0613
1540,0.0131,-0.0179,0.9976,0.4018,-0.2057,0.0526
1560,0.0147,-0.0201,1.0023,0.3894,-0.1812,0.0741
```

串口中只传输时间戳和六轴传感器数据，不直接传输手势标签。手势标签将在 PC 端采集数据时由 Python 程序根据当前指定的手势类别添加。

这种格式便于 Python 使用逗号直接拆分各字段，并进一步保存为 CSV 文件。

### 4.6 Python 串口接收数据

Python 接收 ESP32 已经格式化后的串口文本，并按照逗号分隔符提取时间戳和六轴数值，将字符串转换为后续数据处理所需的数值类型。

首先确认 ESP32 当前使用的串口。

执行：

```powershell
python -m serial.tools.list_ports
```

当前 ESP32 对应的串口为：

```text
COM7
```

在运行 Python 串口程序之前，需要关闭 Arduino IDE 的 Serial Monitor，避免 Arduino IDE 和 Python 同时占用同一个串口。

在项目根目录运行：

```powershell
python src\acquisition\serial_receiver.py
```

程序成功连接 ESP32 后，可以在终端中连续观察到类似：

```text
Connected to COM7
Receiving IMU data...
5867 -0.9681 0.0811 0.1072 4.0611 2.2595 1.4962
5889 -0.9669 0.0775 0.1152 3.6947 -0.5649 -1.9237
5911 -0.9738 0.0707 0.1113 4.9008 1.1298 -2.6718
```

按下：

```text
Ctrl + C
```

可以停止数据接收，并关闭串口连接：

```text
Stopped.
Serial port closed.
```

至此，已经完成：

```text
MPU6500
    ↓ I²C
ESP32
    ↓ USB 串口
Python / PySerial
    ↓
六轴数据解析
```

PC 端已经能够稳定接收并解析 ESP32 发送的六轴 IMU 数据，后续将在此基础上定义手势类别，并将采集数据保存为带标签的 CSV 文件。

### 4.7 手势类别定义

本项目设置五类手势：

| 标签 | 手势定义 |
| --- | --- |
| `left` | 从初始位置向左平移一次 |
| `right` | 从初始位置向右平移一次 |
| `up` | 从初始位置向上平移一次 |
| `down` | 从初始位置向下平移一次 |
| `still` | 保持传感器基本静止 |

数据采集时保持 MPU6500 的握持方向基本一致，每次动态手势均从相近的初始位置开始，并只完成一次单方向移动。

方向以使用者视角为准：

```text
          up
           ↑
left  ←  初始位置  →  right
           ↓
         down
```

### 4.8 原始数据采集与保存 

在完成串口数据接收后，编写 Python 程序实现手势数据的连续采集与自动保存。

采集程序运行后首先输入当前手势类别和需要采集的样本数量。若不输入样本数量，则默认连续采集 20 个样本。

每次采集前进行 `3、2、1` 倒计时，随后清空串口接收缓冲区并采集约 `2 s` 的六轴 IMU 数据。单次采集结束后，将当前样本自动保存为独立 CSV 文件，并在短暂等待后继续采集下一组数据。

数据采集程序保存在:

```text
src\acquisition\serial_collector.py
```

正式采集过程中，保持 MPU6500 的基本握持方向一致，每个动态样本只完成一次指定方向的运动，同时保留一定的速度和幅度变化。

最终共采集：

```text
5 类 × 20 个样本 = 100 个原始样本
```

每个样本通常包含约 `91～92` 个采样点，相邻采样点时间间隔约为 `22` ms，对应实际采样频率约为 `45.45` Hz。

整体数据传输稳定，未发现明显的大面积丢点或损坏文件。至此完成正式原始数据集采集，后续进入原始数据读取、波形可视化和数据预处理阶段。

## 5. IMU 数据预处理

### 5.1 原始数据读取

为了便于后续进行波形可视化和信号预处理，使用 Pandas 对 `data/raw/` 中的原始 CSV 数据进行批量读取。

数据读取程序保存在：

```text
src/preprocessing/load_raw_data.py
```

最终成功读取，数据无丢失或明显离群特征。

### 5.2 原始六轴波形可视化

为了直观观察不同手势下六轴 IMU 信号的变化规律，使用 Matplotlib 分别绘制三轴加速度和三轴角速度的原始时域波形。

绘图程序保存在：

```text
src/preprocessing/plot_raw_signals.py
```

<p align="center">
  <img src="assets/raw_signals/left_acc.png" width="48%">
  <img src="assets/raw_signals/left_gyro.png" width="48%">
</p>

<p align="center">
  <img src="assets/raw_signals/right_acc.png" width="48%">
  <img src="assets/raw_signals/right_gyro.png" width="48%">
</p>

<p align="center">
  <img src="assets/raw_signals/up_acc.png" width="48%">
  <img src="assets/raw_signals/up_gyro.png" width="48%">
</p>

<p align="center">
  <img src="assets/raw_signals/down_acc.png" width="48%">
  <img src="assets/raw_signals/down_gyro.png" width="48%">
</p>

<p align="center">
  <img src="assets/raw_signals/still_acc.png" width="48%">
  <img src="assets/raw_signals/still_gyro.png" width="48%">
</p>

### 5.3 数据异常与噪声分析

为了检查原始数据质量，对全部 100 个样本进行批量统计分析。

分析程序保存在：

```text
src/preprocessing/analyze_raw_data.py
```

统计结果表明：

```text
缺失值：0
样本长度：91～92 点
典型采样间隔：22 ms
最大采样间隔：44 ms
```

整体数据完整，仅存在极少量偶发采样间隔增大的情况。

此外，不同类别之间存在一定的起始基线差异；`still` 类陀螺仪在静止状态下仍存在非零输出，说明传感器存在一定零偏和随机噪声。

### 5.4 基线校正与滤波

根据前述数据分析结果，对原始六轴 IMU 信号进行基线校正和低通滤波处理。

处理程序保存在：

```text
src/preprocessing/preprocess_signals.py
```

首先使用每个样本前 `10` 个采样点的均值作为初始基线，并从对应通道中减去该基线，以减小初始姿态差异和陀螺仪零偏的影响。

随后采用 `4 阶 Butterworth` 低通滤波器对六轴信号进行平滑处理，截止频率设置为 `8` Hz，用于抑制高频随机噪声。

处理后的数据保存至：

```text
data/processed/
```

处理前后的代表波形对比如下：

<p align="center">
  <img src="assets/preprocessing_comparison/left_acc_comparison.png" width="48%">
  <img src="assets/preprocessing_comparison/left_gyro_comparison.png" width="48%">
</p>

<p align="center">
  <img src="assets/preprocessing_comparison/right_acc_comparison.png" width="48%">
  <img src="assets/preprocessing_comparison/right_gyro_comparison.png" width="48%">
</p>

<p align="center">
  <img src="assets/preprocessing_comparison/up_acc_comparison.png" width="48%">
  <img src="assets/preprocessing_comparison/up_gyro_comparison.png" width="48%">
</p>

<p align="center">
  <img src="assets/preprocessing_comparison/down_acc_comparison.png" width="48%">
  <img src="assets/preprocessing_comparison/down_gyro_comparison.png" width="48%">
</p>

处理结果表明，基线偏移得到明显校正，高频波动得到一定抑制，同时主要手势变化趋势仍能够较好保留。

### 5.5 数据集划分

为了避免同一次手势产生的相似数据同时出现在训练集和测试集中，在滑动窗口分割之前，首先按照完整 CSV 样本划分数据集。

数据集划分程序保存在：

```text
src/preprocessing/split_dataset.py
```

每类包含 20 个样本，按照 70% / 15% / 15% 的比例随机划分为：

```text
Train : 14 × 5 = 70
Val   :  3 × 5 = 15
Test  :  3 × 5 = 15
```

划分后的数据保存至：

```text
data/split/
```

其中训练集用于模型参数学习，验证集用于训练过程中的模型选择和参数调整，测试集仅用于最终性能评估。

### 5.6 固定长度序列构建与数据归一化

由于每个 CSV 对应一次完整手势，且样本长度基本为 `91～92` 个采样点，因此将所有样本统一截取为前 `90` 个采样点，并保留 `ax、ay、az、gx、gy、gz` 六个通道。

数据处理程序保存在：

```text
src/preprocessing/build_model_input.py
```

处理后单个样本尺寸为：

```text
90 × 6
```

最终数据尺寸为：

```text
Train : (70, 90, 6)
Val   : (15, 90, 6)
Test  : (15, 90, 6)
```

随后对六个通道进行标准化:

```text
x' = (x - mean) / std
```

其中均值和标准差仅由训练集计算，并使用同一组参数处理训练集、验证集和测试集，以避免数据泄漏。

最终模型输入及归一化参数保存至：

```text
data/model_input/
```

## 6. IMU 时域与频域特征分析

### 6.1 时域信号分析

为了观察不同手势在时域中的整体变化规律，对训练集中每类 14 个样本的六轴信号分别求平均，并绘制平均时域波形。

分析程序保存在：

```text
src/analysis/time_domain_analysis.py
```

<p align="center">
  <img src="assets/time_domain/left_mean_acc.png" width="48%">
  <img src="assets/time_domain/left_mean_gyro.png" width="48%">
</p>

<p align="center">
  <img src="assets/time_domain/right_mean_acc.png" width="48%">
  <img src="assets/time_domain/right_mean_gyro.png" width="48%">
</p>

<p align="center">
  <img src="assets/time_domain/up_mean_acc.png" width="48%">
  <img src="assets/time_domain/up_mean_gyro.png" width="48%">
</p>

<p align="center">
  <img src="assets/time_domain/down_mean_acc.png" width="48%">
  <img src="assets/time_domain/down_mean_gyro.png" width="48%">
</p>

<p align="center">
  <img src="assets/time_domain/still_mean_acc.png" width="48%">
  <img src="assets/time_domain/still_mean_gyro.png" width="48%">
</p>

平均波形表明，不同方向手势在各加速度轴和角速度轴上的变化趋势存在明显差异。其中 `left/right` 与 `up/down` 均表现出一定的方向相反特征，而 `still` 类六轴信号整体保持在 `0` 附近，为后续时域特征提取和手势分类提供了基础。

### 6.2 时域特征提取

为了将时域波形中的变化规律转换为可用于机器学习的数值特征，对每个完整手势样本的六个 IMU 通道分别提取基础时域统计特征。

特征提取程序保存在：

```text
src/analysis/extract_time_features.py
```

每个通道提取以下 7 个特征：

```text
mean
std
min
max
ptp
rms
energy
```

- mean：均值，表示信号整体偏向哪个水平。对于已经做过基线校正的数据，均值还能反映这一段动作整体更偏正方向还是负方向。
- std：标准差，表示波动有多剧烈。标准差越大，说明这一段动作变化越明显；still 通常会比较小。
- min：最小值，表示这一段信号出现过的最强负向变化。
- max：最大值，表示这一段信号出现过的最强正向变化。
- ptp：峰峰值，`max - min`，表示整段信号的总变化范围。它不关心正负方向，只看“摆动幅度有多大”。
- rms：均方根，Root Mean Square，表示信号的总体有效幅值。相比均值，它不会因为正负相互抵消而变小，所以很适合衡量动作强度。
- energy：能量，通常定义为所有采样点平方和：
                \[
                E=\sum_{n=1}^{N}x[n]^2
                \]
  它表示整段信号总体“活动量”有多大，动作越剧烈，通常能量越大。

因此每个样本最终得到：

```text
6 个通道 × 7 个特征 = 42 个时域特征
```

最终生成：

```text
Train : 70 samples × 42 features
Val   : 15 samples × 42 features
Test  : 15 samples × 42 features
```

提取后的时域特征保存至：

```text
data/features/
```

这些基础时域特征用于描述信号的整体水平、波动范围、极值和能量等特性，并作为后续传统机器学习 Baseline 的基础输入。

### 6.3 频域分析与 FFT

### 6.4 频域特征提取

### 6.5 不同手势信号对比

## 7. 传统机器学习 Baseline

### 7.1 Baseline 的作用

### 7.2 特征数据集构建

### 7.3 模型选择

### 7.4 模型训练

### 7.5 模型测试与评估

### 7.6 混淆矩阵与结果分析


## 8. 轻量 1D CNN 手势识别

### 8.1 为什么使用 1D CNN

### 8.2 模型输入与输出

### 8.3 网络结构设计

### 8.4 数据加载

### 8.5 模型训练

### 8.6 模型验证与测试

### 8.7 训练过程可视化

### 8.8 分类结果分析

### 8.9 与传统机器学习 Baseline 对比


## 9. 模型轻量化与量化

### 9.1 为什么进行模型量化

### 9.2 模型导出

### 9.3 模型量化

### 9.4 量化前后性能对比

### 9.5 模型大小与计算量分析


## 10. ESP32 端侧部署

### 10.1 端侧部署流程

### 10.2 模型转换与集成

### 10.3 ESP32 实时数据缓存

### 10.4 端侧数据预处理

### 10.5 ESP32 模型推理

### 10.6 实时手势识别

### 10.7 串口输出识别结果


## 11. 实验结果与性能分析

### 11.1 手势识别准确率

### 11.2 混淆矩阵

### 11.3 不同模型性能对比

### 11.4 模型大小

### 11.5 单次推理时间

### 11.6 实时识别效果


## 12. 项目总结

### 12.1 项目实现结果

### 12.2 当前存在的问题

### 12.3 后续改进方向

