import os

import json5
import json
from typing import Dict
import sys
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QTextEdit, QFileDialog, QDialog, QProgressDialog, QScrollArea)
from PyQt6.QtCore import Qt

from component.slotDisplayWidget import SlotDisplayWidget
from manager.cardDataManager import CardDataManager
from manager.riteDataManager import RiteDataManager


# 仪式初始信息窗口
class RiteDetailWindow(QWidget):
    def __init__(self, rite_data, parent=None):
        super().__init__(parent)
        self.rite_data = rite_data
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)  # 确保标题栏存在
        self.initUI()
        self.setMinimumSize(800, 300)  # 窗口最小尺寸

    # 初始化UI界面
    def initUI(self):
        self.setWindowTitle('仪式初始信息')

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # 使用文本区域显示格式化信息
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(self.format_rite_info())
        layout.addWidget(self.text_area)

        # 卡牌槽位展示
        layout.addWidget(QLabel("卡片槽位配置："))
        slots_widget = self.create_slots_display()
        layout.addWidget(slots_widget)


        self.setLayout(layout)

    # 窗口显示时自动调整大小
    def showEvent(self, event):
        if self.parent():
            # 自动居中
            self.resize(self.parent().width() // 4, self.parent().height() // 4)
            self.move(self.parent().geometry().center() - self.rect().center())
        super().showEvent(event)

    # 使用独立组件展示卡片槽位
    def create_slots_display(self):
        if not self.rite_data.get('cards_slot'):
            return QLabel("无卡片槽位配置")

        slots_widget = SlotDisplayWidget(
            self.rite_data['cards_slot']
        )
        # 添加横向滚动支持
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(slots_widget)
        return scroll_area

    # 格式化仪式信息为可读文本
    def format_rite_info(self):
        try:
            formatted = []
            # 基本信息
            formatted.append(f"id：{self.rite_data['id']}")
            formatted.append(f"名称：{self.rite_data['name']}")
            formatted.append(f"描述：{self.rite_data['text']}")
            # tips-提示
            if self.rite_data['tips'] != "":
                formatted.append(f"提示：{self.rite_data['tips']}")
            else:
                formatted.append(f"提示：无")
            # mapping_id-仪式背景图
            if self.rite_data['mapping_id']:
                formatted.append(f"仪式背景图：{self.rite_data['mapping_id']}")
            else:
                formatted.append(f"仪式背景图：无")
            # once_new-这个仪式出现在场上时，是否每次都打上“新”的标识
            formatted.append(f"once_new：{self.rite_data['once_new']}")
            formatted.append(f"仪式进行回合：{self.rite_data['round_number']}")
            formatted.append(f"仪式等待回合：{self.rite_data['waiting_round']}")
            formatted.append(f"仪式等待时间到了后的处理：{self.rite_data['waiting_round_end_action']}")
            # method_settlement-没用
            formatted.append(f"method_settlement：{self.rite_data['method_settlement']}")
            formatted.append(f"是否自动执行仪式：{self.rite_data['auto_begin']}")
            formatted.append(f"结算界面是否自动执行：{self.rite_data['auto_result']}")
            formatted.append(f"仪式出现位置：{self.rite_data['location']}")
            formatted.append(f"仪式图标：{self.rite_data['icon']}")
            # tag_tips-废弃了
            formatted.append(f"tag_tips：{self.rite_data['tag_tips']}")
            # tag_tips_up-仪式所需数值
            formatted.append("仪式所需数值：")
            if self.rite_data['tag_tips_up']:
                for key, value in self.rite_data['tag_tips_up'].items():
                    formatted.append(f"   {key}：{value}")
            else:
                formatted.append(f"   无")
            # tips_text-提示信息
            formatted.append(f"提示信息：{self.rite_data['tips_text']}")
            # open_conditions-开启条件
            formatted.append(f"开启条件：{self.rite_data['open_conditions']}")
            # random_text-随机文本-已弃用
            formatted.append(f"random_text：{self.rite_data['random_text']}")
            # random_text_up-随机文本
            formatted.append(f"random_text_up：{self.rite_data['random_text_up']}")
            # settlement_prior-优先结算
            formatted.append(f"settlement_prior：{self.rite_data['settlement_prior']}")
            # settlement-结算
            formatted.append("settlement：")
            if self.rite_data['settlement']:
                formatted.append(f"{self.rite_data['settlement']}")
            else:
                formatted.append(f"   无")
            # settlement_extre-额外结算
            formatted.append(f"settlement_extre：{self.rite_data['settlement_extre']}")
            # cards_slot-卡牌槽
            formatted.append(f"cards_slot：{self.rite_data['cards_slot']}")











            # 详细配置
            formatted.append("\n详细配置：")
            formatted.append(json.dumps(self.rite_data, indent=2, ensure_ascii=False))

            return "\n".join(formatted)
        except Exception as e:
            return f"信息格式化失败：{str(e)}"


if __name__ == "__main__":
    rites_path = "E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config\\rite"
    rite_id = 5000001
    rite_mgr = RiteDataManager(rites_path)
    rite_data = rite_mgr.get_rite_details(rite_id)


    app = QApplication(sys.argv)
    # 启动主窗口
    main_window = RiteDetailWindow(rite_data)
    main_window.show()
    sys.exit(app.exec())