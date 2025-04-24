import os
import time

import json5
import json
from typing import Dict, Any
import sys
from functools import partial, lru_cache
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QTextEdit, QFileDialog, QDialog, QProgressDialog)
from PyQt6.QtCore import Qt
from ijson import items


# 仪式元数据管理器
class RiteDataManager:
    # 初始化对象，包括定义未知仪式信息、加载仪式数据、定义仪式id和仪式数据的映射
    def __init__(self, rite_db_path: str):
        self.unknown_rite = {
            "id": -1,
            "name": "未知仪式",
            "text": "未知仪式",
            "tips": "",
            "mapping_id": -1,
            "once_new": -1,
            "round_number": -1,
            "waiting_round": -1,
            "waiting_round_end_action": [],
            "method_settlement": "",
            "auto_begin": -1,
            "auto_result": -1,
            "location": "",
            "icon": "",
            "tag_tips": [],
            "tag_tips_up": {},
            "tips_text": [],
            "open_conditions": [],
            "random_text": {},
            "random_text_up": {},
            "settlement_prior": [],
            "settlement": [],
            "settlement_extre": [],
            "cards_slot": {}
        }
        self.rite_dir = rite_db_path
        # 元数据索引：#键: 仪式ID  值: 仪式名
        self.metadata_index: Dict[str, str] = {}

        def resource_path(relative_path):
            if hasattr(sys, '_MEIPASS'):
                print(sys._MEIPASS)
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)

        default_rite_db = resource_path('rite_map_info.json')
        self._build_metadata_index(default_rite_db)

    def _build_metadata_index(self, default_rite_db):
        with open(default_rite_db, 'r', encoding='utf-8') as f:
            self.metadata_index = json5.load(f)

    def get_rite_name(self, rite_id: int) -> str:
        if str(rite_id) not in self.metadata_index:
            return '未知仪式'
        else:
            return self.metadata_index[str(rite_id)]

    def get_rite_details(self, rite_id: int) -> Dict[str, Any]:
        if str(rite_id) not in self.metadata_index:
            return self.unknown_rite

        filename = str(rite_id) + '.json'
        file_path = os.path.join(self.rite_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            full_data = json5.load(f)

        return full_data


if __name__ == "__main__":
    riteDataManager = RiteDataManager("E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config\\rite")

    print('OK')