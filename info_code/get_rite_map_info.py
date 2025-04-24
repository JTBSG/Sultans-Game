import json
import os
from typing import Dict

import json5

rite_dir = "E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config\\rite"
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rite_map_info.json')
index_data: Dict[str, str] = {}
for filename in os.listdir(rite_dir):
    if not filename.endswith('.json'):
        continue
    file_id = os.path.splitext(filename)[0]
    file_path = os.path.join(rite_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json5.load(f)
        if 'name' not in data:
            index_data[file_id] = ""
        else:
            index_data[file_id] = data['name']

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

