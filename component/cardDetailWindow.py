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

# 卡牌初始信息窗口
class CardDetailWindow(QWidget):
    def __init__(self, card_data, parent=None):
        super().__init__(parent)
        self.card_data = card_data
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)  # 确保标题栏存在
        self.initUI()
        self.setMinimumSize(400, 500)  # 窗口最小尺寸

    # 初始化UI界面
    def initUI(self):
        self.setWindowTitle('卡牌初始信息')

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # 使用文本区域显示格式化信息
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(self.format_card_info())

        layout.addWidget(self.text_area)
        self.setLayout(layout)

    # 窗口显示时自动调整大小
    def showEvent(self, event):
        if self.parent():
            # 自动居中
            self.resize(self.parent().width() // 4, self.parent().height() // 4)
            self.move(self.parent().geometry().center() - self.rect().center())
        super().showEvent(event)

    # 格式化卡牌信息为可读文本
    def format_card_info(self):
        try:
            formatted = []
            # 基本信息
            formatted.append(f"id：{self.card_data['id']}")
            formatted.append(f"名称：{self.card_data['name']}")
            formatted.append(f"称号：{self.card_data['title']}")
            formatted.append(f"描述：{self.card_data['text']}")
            formatted.append(f"类型：{self.card_data['type']}")
            formatted.append(f"稀有度：{self.card_data['rare']}星")
            formatted.append(f"唯一卡牌：{'是' if self.card_data['is_only'] else '否'}")
            # 标签信息
            formatted.append("标签属性：")
            if self.card_data['tag']:
                for tag, value in self.card_data['tag'].items():
                    formatted.append(f"   {tag}：{value}")
            else:
                formatted.append(f"   无")
            # 装备信息
            formatted.append("可装备槽位：")
            if self.card_data['equips']:
                formatted.append(", ".join(self.card_data['equips']))
            else:
                formatted.append(f"   无")
            # 详细配置
            formatted.append("\n详细配置：")
            formatted.append(json.dumps(self.card_data, indent=2, ensure_ascii=False))

            return "\n".join(formatted)
        except Exception as e:
            return f"信息格式化失败：{str(e)}"