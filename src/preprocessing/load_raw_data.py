from pathlib import Path                  # 导入 Path，用于处理文件夹和文件路径
import pandas as pd                       # 导入 pandas，用于读取和处理 CSV 数据


DATA_DIR = Path("data/raw")               # 设置正式原始数据所在目录

LABELS = [                                # 定义需要读取的五类手势
    "left",                               # 向左手势
    "right",                              # 向右手势
    "up",                                 # 向上手势
    "down",                               # 向下手势
    "still"                               # 静止类别
]


all_samples = []                          # 创建列表，用于保存所有读取到的样本信息


for label in LABELS:                      # 依次遍历五个手势类别

    label_dir = DATA_DIR / label          # 构造当前类别对应的文件夹路径

    csv_files = sorted(                   # 获取当前类别中的全部 CSV 文件并按照文件名排序
        label_dir.glob("*.csv")           # 查找当前文件夹下所有扩展名为 .csv 的文件
    )

    print(                                # 输出当前类别的文件数量
        f"{label}: {len(csv_files)} files"
    )

    for csv_path in csv_files:            # 依次遍历当前类别中的每一个 CSV 文件

        df = pd.read_csv(csv_path)         # 使用 pandas 读取当前 CSV 文件

        sample = {                         # 创建字典，记录当前样本的信息
            "label": label,                # 保存当前样本所属的手势类别
            "path": csv_path,              # 保存当前 CSV 文件路径
            "data": df                     # 保存读取到的 DataFrame 数据
        }

        all_samples.append(sample)         # 将当前样本加入总样本列表


print()                                    # 输出空行

print(                                     # 输出最终读取到的样本总数
    f"Total samples: {len(all_samples)}"
)


for sample in all_samples[:5]:             # 取前 5 个样本进行简单检查

    print()                                # 输出空行

    print(                                 # 输出当前样本的类别
        f"Label: {sample['label']}"
    )

    print(                                 # 输出当前样本的文件路径
        f"File: {sample['path']}"
    )

    print(                                 # 输出当前样本的数据点数量
        f"Points: {len(sample['data'])}"
    )

    print(                                 # 输出当前 CSV 的前 5 行数据
        sample["data"].head()
    )