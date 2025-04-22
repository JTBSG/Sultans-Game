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

# 卡牌元数据管理器
class CardDataManager:
    # 初始化对象，包括定义未知卡牌信息、加载卡牌数据、定义卡牌id和卡牌数据的映射
    def __init__(self, card_db_path: str):
        self.unknown_card = {
            "id": -1,
            "name": "未知卡牌",
            "title": "cards文件中不存在的卡牌",
            "text": "疑惑？？？？？？",
            "pops": [],
            "card_favour": "",
            "type": "",
            "tips": "",
            "rare": -1,
            "resource": "",
            "tag": {},
            "card_vanishing": -1,
            "vanish": {},
            "equips": [],
            "is_only": -1
        }
        self.card_db = self._load_card_db(card_db_path)
        self.card_data_mapping = self._build_card_data_mapping()

    # 加载卡牌数据
    @staticmethod
    def _load_card_db(path: str) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as card_db_path:
                return json5.load(card_db_path)
        except FileNotFoundError:
            print(f"卡牌数据库文件 {path} 未找到")
            return {}
        except Exception as e:
            print(f"加载卡牌数据库时发生错误: {e}")
            return {}

    # 创建ID到卡牌数据的映射
    def _build_card_data_mapping(self) -> Dict[int, dict]:
        return {
            int(cid): data
            for cid, data in self.card_db.items()
        }

    # 根据id获取卡牌初始数据
    def get_card_data(self, card_id: int) -> dict:
        return self.card_data_mapping.get(card_id, self.unknown_card)