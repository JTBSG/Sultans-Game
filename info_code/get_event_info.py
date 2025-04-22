import os
import json
import pandas as pd
import json5


import os
import json5
import pandas as pd

import os
import json5
import pandas as pd

def read_json_files_to_dataframe(folder_path):
    """
    读取文件夹中的所有 JSON 文件，并转换为 DataFrame。
    仅展平一级嵌套字段，二级及更深嵌套的字段保留为 JSON 字符串。
    如果一级嵌套字段是空字典或空列表，则存储为空字符串 ""。
    """
    data = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_content = json5.load(file)

                row = {'filename': filename}

                # 遍历 JSON 的顶级字段
                for key, value in json_content.items():
                    if isinstance(value, dict):
                        # 如果是字典（一级嵌套）
                        if not value:  # 检查是否为空字典 {}
                            row[key] = ""  # 存储为空字符串
                        else:
                            # 非空字典转为 JSON 字符串
                            row[key] = json5.dumps(value, ensure_ascii=False)
                    elif isinstance(value, list):
                        # 如果是列表
                        if not value:  # 检查是否为空列表 []
                            row[key] = ""  # 存储为空字符串
                        else:
                            # 非空列表，检查每个元素是否是字典
                            processed_list = []
                            for item in value:
                                if isinstance(item, dict):
                                    if not item:  # 空字典 {}
                                        processed_list.append("")
                                    else:
                                        # 非空字典转为 JSON 字符串
                                        processed_list.append(json5.dumps(item, ensure_ascii=False))
                                else:
                                    processed_list.append(item)
                            row[key] = processed_list
                    else:
                        # 其他类型（str, int, bool 等）直接存储
                        row[key] = value

                data.append(row)

            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    folder_path = r"E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config\init"
    df = read_json_files_to_dataframe(folder_path)
    df.to_excel("F:\\SaTansGame\\info\\init.xlsx", index=False, engine="openpyxl")
    print('OK')
