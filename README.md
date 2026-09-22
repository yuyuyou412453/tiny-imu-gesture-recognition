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

## 2. 建立 Python 虚拟环境并配置项目依赖

### 2.1 为什么使用虚拟环境

不同 Python 项目可能依赖不同版本的软件包，如果将所有依赖都直接安装到系统 Python 中，随着项目数量的增加，可能出现版本冲突。因此为不同的项目创建独属于该项目的 Python 虚拟环境，使项目依赖相互隔离。

当前项目的本地路径：

```text
D:\GitHub\tiny-imu-gesture-recognition
```

首先进入项目目录：

```text
cd D:\GitHub\tiny-imu-gesture-recognition
```

### 2.2 创建虚拟环境

执行：

```text
python -m venv .venv
```

其中：

- python：调用当前 Python 解释器
- -m venv：运行 Python 自带的 venv 模块
- .venv：虚拟环境目录名称

执行后，项目根目录中会生成`.venv/`

该目录保存当前项目独立的 Python 解释器和第三方依赖。

### 2.3 激活虚拟环境

Windows PowerShell 下执行：
```text
.\.venv\Scripts\Activate.ps1
```

激活成功后，终端前通常会出现：`(.venv)`

此后通过 pip 安装的软件包都会安装到当前项目的虚拟环境中。

### 2.4 安装所需 Python 库
