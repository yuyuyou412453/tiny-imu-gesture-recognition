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
│   │   └── serial_collector.py
│   ├── preprocessing/
│   ├── training/
│   ├── inference/
│   └── deployment/
├── assets/
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
手持 MPU6050 完成指定手势
        ↓
MPU6050 采集 ax、ay、az、gx、gy、gz 六轴数据
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
MPU6050 实时采集
        ↓
ESP32 端侧推理
        ↓
输出手势识别结果
```

## 3. 开发环境配置

ESP32 端主要负责：

- 初始化 MPU6050
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

ESP32 负责通过 I²C 读取 MPU6050 数据，并通过 USB 串口发送至 PC，因此除了 PC 端的 Python 环境外，还需要配置 ESP32 固件开发环境。

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

MPU6050 输出三轴加速度和三轴角速度，共六个主要运动量：

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

当 MPU6050 静止放置时，加速度计仍会受到重力影响，因此三个加速度轴中通常会有一个方向接近 `1 g`，具体取决于传感器当前的放置方向。

在手势执行过程中，六个通道会随时间连续变化，因此一次手势可以表示为一段六通道时序数据：

```text
t1 → ax1, ay1, az1, gx1, gy1, gz1
t2 → ax2, ay2, az2, gx2, gy2, gz2
t3 → ax3, ay3, az3, gx3, gy3, gz3
...
tn → axn, ayn, azn, gxn, gyn, gzn
```

后续将利用这六路时序信号之间的变化规律区分不同手势。

### 4.3 MPU6050 与 ESP32 硬件连接

| MPU6050 | ESP32 开发板 | 功能 |
| --- | --- | --- | --- |
| `VCC` | `3V3` | 模块供电 |
| `GND` | `GND` | 公共地 |
| `SDA` | `D21` | I²C 数据线 |
| `SCL` | `D22` | I²C 时钟线 |

### 4.4 ESP32 读取 MPU6050 数据



### 4.5 串口数据格式

### 4.6 Python 串口接收数据

### 4.7 手势类别定义

### 4.8 原始数据采集与保存


## 5. IMU 数据预处理

### 5.1 原始数据读取

### 5.2 原始六轴波形可视化

### 5.3 数据异常与噪声分析

### 5.4 滤波处理

### 5.5 数据归一化

### 5.6 滑动窗口分割

### 5.7 数据集划分


## 6. IMU 时域与频域特征分析

### 6.1 时域信号分析

### 6.2 时域特征提取

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

