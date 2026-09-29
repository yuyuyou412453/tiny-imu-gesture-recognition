from pathlib import Path                                  # 导入 Path，用于处理文件夹和文件路径
import random                                             # 导入 random，用于随机打乱样本顺序
import shutil                                             # 导入 shutil，用于复制文件


SOURCE_DIR = Path("data/processed")                       # 设置预处理后完整手势样本所在目录
OUTPUT_DIR = Path("data/split")                           # 设置划分后数据集的保存目录

LABELS = [                                                # 定义五类手势标签
    "left",                                               # 向左手势
    "right",                                              # 向右手势
    "up",                                                 # 向上手势
    "down",                                               # 向下手势
    "still"                                               # 静止类别
]                                                         # 手势标签列表定义结束

TRAIN_COUNT = 14                                          # 每类分配 14 个样本到训练集
VAL_COUNT = 3                                             # 每类分配 3 个样本到验证集
TEST_COUNT = 3                                            # 每类分配 3 个样本到测试集

RANDOM_SEED = 42                                          # 设置固定随机种子，保证每次划分结果一致


random.seed(RANDOM_SEED)                                  # 初始化随机种子


for split_name in ["train", "val", "test"]:               # 依次创建训练集、验证集和测试集目录

    for label in LABELS:                                  # 依次处理五类手势

        split_label_dir = (                               # 构造当前数据子集和类别对应的目录
            OUTPUT_DIR                                    # 使用数据集划分输出根目录
            / split_name                                  # 添加 train、val 或 test 子目录
            / label                                       # 添加具体手势类别目录
        )                                                 # 当前输出目录构造结束

        split_label_dir.mkdir(                            # 创建当前输出目录
            parents=True,                                 # 如果上级目录不存在则自动创建
            exist_ok=True                                 # 如果目录已经存在则不会报错
        )                                                 # 目录创建结束


for label in LABELS:                                      # 依次处理五类手势

    source_label_dir = SOURCE_DIR / label                 # 构造当前类别对应的源数据目录

    csv_files = sorted(                                   # 获取当前类别中的全部 CSV 文件
        source_label_dir.glob("*.csv")                    # 查找当前目录中的所有 CSV 文件
    )                                                     # CSV 文件列表获取结束

    if len(csv_files) != 20:                              # 检查当前类别是否正好包含 20 个样本

        print(                                            # 输出样本数量异常提示
            f"Warning: {label} contains "
            f"{len(csv_files)} files instead of 20."
        )                                                 # 警告信息输出结束

    random.shuffle(csv_files)                             # 随机打乱当前类别的样本顺序

    train_files = (                                       # 从打乱后的样本中选取训练集
        csv_files[:TRAIN_COUNT]                           # 取前 14 个样本作为训练集
    )                                                     # 训练集文件列表生成结束

    val_files = (                                         # 从剩余样本中选取验证集
        csv_files[                                        # 对样本列表进行切片
            TRAIN_COUNT:                                  # 从第 15 个样本开始
            TRAIN_COUNT + VAL_COUNT                       # 一直到第 17 个样本
        ]
    )                                                     # 验证集文件列表生成结束

    test_files = (                                        # 从最后剩余样本中选取测试集
        csv_files[                                        # 对样本列表进行切片
            TRAIN_COUNT + VAL_COUNT:                      # 从第 18 个样本开始
        ]
    )                                                     # 测试集文件列表生成结束


    for csv_path in train_files:                          # 依次复制训练集中的每个样本

        destination = (                                   # 构造训练集目标路径
            OUTPUT_DIR                                    # 使用划分数据根目录
            / "train"                                     # 指定训练集目录
            / label                                       # 指定当前手势类别
            / csv_path.name                               # 保持原始文件名不变
        )                                                 # 训练集目标路径构造结束

        shutil.copy2(                                     # 复制当前 CSV 文件
            csv_path,                                     # 指定源文件
            destination                                   # 指定目标文件
        )                                                 # 当前训练样本复制结束


    for csv_path in val_files:                            # 依次复制验证集中的每个样本

        destination = (                                   # 构造验证集目标路径
            OUTPUT_DIR                                    # 使用划分数据根目录
            / "val"                                       # 指定验证集目录
            / label                                       # 指定当前手势类别
            / csv_path.name                               # 保持原始文件名不变
        )                                                 # 验证集目标路径构造结束

        shutil.copy2(                                     # 复制当前 CSV 文件
            csv_path,                                     # 指定源文件
            destination                                   # 指定目标文件
        )                                                 # 当前验证样本复制结束


    for csv_path in test_files:                           # 依次复制测试集中的每个样本

        destination = (                                   # 构造测试集目标路径
            OUTPUT_DIR                                    # 使用划分数据根目录
            / "test"                                      # 指定测试集目录
            / label                                       # 指定当前手势类别
            / csv_path.name                               # 保持原始文件名不变
        )                                                 # 测试集目标路径构造结束

        shutil.copy2(                                     # 复制当前 CSV 文件
            csv_path,                                     # 指定源文件
            destination                                   # 指定目标文件
        )                                                 # 当前测试样本复制结束


    print()                                               # 输出空行，便于区分不同类别

    print(                                                # 输出当前类别划分结果
        f"{label}: "
        f"train={len(train_files)}, "
        f"val={len(val_files)}, "
        f"test={len(test_files)}"
    )                                                     # 当前类别划分结果输出结束


print()                                                   # 输出空行

print("Dataset split completed.")                         # 输出数据集划分完成提示