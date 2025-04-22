import os

import json5
import json
from typing import Dict
import sys
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QTextEdit, QFileDialog, QDialog, QProgressDialog)
from PyQt6.QtCore import Qt


# 标签元数据管理器
class TagDataManager:
    # 初始化对象，包括定义未知标签信息、加载标签数据、定义标签名和标签数据的映射
    def __init__(self, tag_db_path: str):
        self.unknown_tag = {
            "id": -1,
            "name": "未知标签",
            "code": "",
            "type": "",
            "text": "",
            "tips": "",
            "resource": "",
            "can_add": -1,
            "can_visible": -1,
            "can_inherit": -1,
            "can_nagative_and_zero": -1,
            "fail_tag": [],
            "tag_vanishing": -1,
            "tag_sfx": "",
            "tag_rank": -1,
            "attributes": {}
        }
        self.tag_db = self._load_tag_db(tag_db_path)
        self.tag_data_mapping = self._build_tag_data_mapping()

    # 加载标签数据
    def _load_tag_db(self, path: str) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as tag_db_path:
                return json5.load(tag_db_path)
        except FileNotFoundError:
            print(f"标签数据库文件 {path} 未找到")
            return {}
        except Exception as e:
            print(f"加载标签数据库时发生错误: {e}")
            return {}

    # 创建名字到标签数据的映射
    # TODO 现在是根据标签的code映射标签信息，但是实际存档文件中的标签是中文名，还没适配
    def _build_tag_data_mapping(self) -> Dict[str, dict]:
        return {
            code: data
            for code, data in self.tag_db.items()
        }

    # 根据标签名字获取标签信息
    def get_tag_data(self, tag_name: str) -> dict:
        return self.tag_data_mapping.get(tag_name, self.unknown_tag)