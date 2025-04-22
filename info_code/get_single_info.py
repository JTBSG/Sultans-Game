import json5
import pandas as pd


def flatten_json_file(file_path):
    """
    读取单个JSON文件，仅展平一级嵌套字段
    处理主JSON对象中的列表结构
    二级及以上嵌套保持原样（转为JSON字符串）
    空字典/列表存储为""
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json5.load(f)

    rows = []

    # 处理主JSON对象（可能是字典或列表）
    if isinstance(data, list):
        # 如果JSON根是列表，给每个元素分配虚拟key
        for i, item in enumerate(data):
            process_item(item, f"item_{i}", rows)
    elif isinstance(data, dict):
        # 标准情况：JSON根是字典
        for main_key, main_value in data.items():
            process_item(main_value, main_key, rows)
    else:
        raise ValueError("JSON根元素必须是字典或列表")

    return pd.DataFrame(rows)


def process_item(item, key, rows):
    """处理单个JSON项目"""
    row = {'_key': key}

    if isinstance(item, dict):
        # 处理字典项
        for k, v in item.items():
            handle_value(row, k, v)
    elif isinstance(item, list):
        # 处理列表项（作为整体处理）
        handle_value(row, 'value', item)
    else:
        # 处理简单值
        row['value'] = item

    rows.append(row)


def handle_value(row, key, value):
    """统一处理各种类型的值"""
    if isinstance(value, (dict, list)):
        if not value:  # 空字典/列表
            row[key] = ""
        else:
            # 非空嵌套结构转为JSON字符串
            row[key] = json5.dumps(value, ensure_ascii=False)
    else:
        # 简单类型直接存储
        row[key] = value


if __name__ == "__main__":
    # 使用示例
    file_path = r"E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config\upgrade.json"  # 替换为实际文件路径
    df = flatten_json_file(file_path)

    # 保存结果
    df.to_excel("F:\SaTansGame\info\\upgrade.xlsx", index=False, encoding='utf-8-sig')
    print("OK")