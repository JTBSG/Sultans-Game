import os
import json5
import pandas as pd


def read_json_files_to_dataframe(folder_path):
    """
    读取文件夹中的所有 JSON 文件，并转换为 DataFrame。
    将 extra 数组中的每个元素展开为新行，保留原始字段。
    空列表/字典存储为 ""。
    """
    data = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_content = json5.load(file)

                # 处理基础字段（extra 除外），将空列表/字典设为 ""
                base_fields = {}
                for k, v in json_content.items():
                    if k == 'extra':
                        continue
                    if isinstance(v, (list, dict)) and not v:
                        base_fields[k] = ""
                    else:
                        base_fields[k] = v

                # 处理 extra 数组
                if 'extra' in json_content and isinstance(json_content['extra'], list):
                    for extra_item in json_content['extra']:
                        # 处理 extra 中的每个元素，将空列表/字典设为 ""
                        processed_extra = {}
                        for ek, ev in extra_item.items():
                            if isinstance(ev, (list, dict)) and not ev:
                                processed_extra[f'extra_{ek}'] = ""
                            else:
                                processed_extra[f'extra_{ek}'] = ev

                        row = {
                            'filename': filename,
                            ** base_fields,
                            ** processed_extra
                        }
                        data.append(row)
                else:
                    # 如果没有 extra 字段，直接添加基础数据
                    row = {
                        'filename': filename,
                        ** base_fields
                    }
                    data.append(row)

            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    folder_path = r"E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config\after_story"
    df = read_json_files_to_dataframe(folder_path)

    # 保存到 Excel
    df.to_excel("F:\\SaTansGame\\info\\after_story.xlsx", index=False, engine="openpyxl")
    print('处理完成，结果已保存')