import os

import json5
import json
from typing import Dict
import sys
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QTextEdit, QFileDialog, QDialog, QProgressDialog, QInputDialog)
from PyQt6.QtCore import Qt, QFileSystemWatcher
from component.startupDialog import StartupDialog
from component.cardDetailWindow import CardDetailWindow
from component.addCardDialog import AddCardDialog
from component.riteDetailWindow import RiteDetailWindow

from manager.cardDataManager import CardDataManager
from manager.tagDataManager import TagDataManager


# 软件主界面
class RiteTablePage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.config = self.main_window.config
        self.initUI()
        self._connect_signals()  # 初始化时连接信号

    # 连接表格数据变更信号
    def _connect_signals(self):
        self.table.itemChanged.connect(self.update_rite_data)

    # 断开表格数据变更信号
    def _disconnect_signals(self):
        try:
            self.table.itemChanged.disconnect(self.update_rite_data)
        except TypeError:
            pass  # 忽略未连接时的错误

    # 界面初始化
    def initUI(self):
        # 创建主控件和布局
        main_layout = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入仪式名字进行搜索...")
        self.search_input.returnPressed.connect(self.filter_rites)  # 添加回车事件绑定
        search_button = QPushButton("搜索")
        search_button.clicked.connect(self.filter_rites)
        search_layout.addWidget(QLabel("快速搜索："))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        # 添加过滤按钮
        filter_btn_layout = QHBoxLayout()

        # # 添加新增仪式按钮
        # self.add_new_card_btn = QPushButton("新增仪式")
        #
        # # 设置按钮样式
        # for btn in [self.add_new_card_btn]:
        #     btn.setFixedSize(100, 30)
        #
        # # 绑定点击事件
        # self.add_new_card_btn.clicked.connect(self.add_new_card)
        #
        # filter_btn_layout.addWidget(self.add_new_card_btn)

        # 卡片表格
        self.table = QTableWidget()
        self.table.setColumnCount(13)  # TODO:记得要修改卡片表格的列数
        self.table.setHorizontalHeaderLabels([
            "查看", "UID", "ID", "名称", "new_born", "is_show", "start", "start_round",
            "start_life", "life", "cards", "自定义名称", "查看"
        ])



        # 将控件加入主布局
        main_layout.addLayout(search_layout)
        main_layout.addLayout(filter_btn_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

    # 初始化从主界面中获取config信息
    def update_info(self):
        self.config = self.main_window.config
        self.load_data()

    # 加载仪式数据到表格
    def load_data(self):
        # 加载数据的时候断开信号连接
        self._disconnect_signals()

        self.table.setRowCount(len(self.config.get('rites', {})))

        for row, rite in enumerate(self.config.get('rites', {})):
            # 添加查看卡片初始信息按钮
            front_btn = QPushButton("查看详情")
            front_btn.clicked.connect(partial(self.show_detail, row))
            self.table.setCellWidget(row, 0, front_btn)

            # 创建不可编辑的UID项和id项
            uid_item = QTableWidgetItem(str(rite.get('uid')))
            uid_item.setFlags(uid_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            id_item = QTableWidgetItem(str(rite.get('id')))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 获取仪式id对应的名称
            rite_name = QTableWidgetItem(self.main_window.rite_mgr.get_rite_name(rite.get('id')))
            rite_name.setFlags(rite_name.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.table.setItem(row, 1, QTableWidgetItem(uid_item))
            self.table.setItem(row, 2, QTableWidgetItem(id_item))
            self.table.setItem(row, 3, QTableWidgetItem(rite_name))
            self.table.setItem(row, 4, QTableWidgetItem(str(rite.get('new_born'))))
            self.table.setItem(row, 5, QTableWidgetItem(str(rite.get('is_show'))))
            self.table.setItem(row, 6, QTableWidgetItem(str(rite.get('start'))))
            self.table.setItem(row, 7, QTableWidgetItem(str(rite.get('start_round'))))
            self.table.setItem(row, 8, QTableWidgetItem(str(rite.get('start_life'))))
            self.table.setItem(row, 9, QTableWidgetItem(str(rite.get('life'))))
            self.table.setItem(row, 10, QTableWidgetItem(str(rite.get('cards'))))
            self.table.setItem(row, 11, QTableWidgetItem(rite.get('custom_name')))


            # 添加末端操作按钮
            end_btn = QPushButton("查看详情")
            end_btn.clicked.connect(partial(self.show_detail, row))
            self.table.setCellWidget(row, 12, end_btn)

        # 重新连接信号
        self._connect_signals()

        self.table.resizeColumnsToContents()  # 自动调整列宽
        # 卡牌列太长了，设置一个列宽最大值
        self.table.setColumnWidth(10, min(self.table.columnWidth(10), 500))
        self.table.resizeRowsToContents()  # 自动调整行高
        self.table.setAlternatingRowColors(True)  # 设置隔行颜色区分

    # 根据名字搜索仪式
    def filter_rites(self):
        search_id = self.search_input.text().strip()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 3)  # 名字列
            match = search_id.lower() in item.text().lower()
            self.table.setRowHidden(row, not match)

    # 新增仪式
    def add_new_card(self):
        # 获取当前uid指针
        current_uid = self.config.get('card_uid_index', 0)
        # 获取当前苏丹卡池的总卡数量
        current_sudan_pool_cards_length = len(self.config.get('sudan_pool_cards', []))
        dialog = AddCardDialog(card_mgr=self.main_window.card_mgr, parent=self, base_uid=current_uid, base_sudan_pool_cards_length=current_sudan_pool_cards_length)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_card = dialog.get_new_card_data()
            if new_card:
                # 添加新卡牌到数据列表
                self.config['cards'].append(new_card)
                # 获取新卡牌的type
                new_card_id = new_card.get('id', -1)
                new_card_data = self.main_window.card_mgr.get_card_data(new_card_id)
                new_card_type = new_card_data.get('type', "")
                # 如果新增卡牌为苏丹卡,在苏丹卡池中添加新苏丹卡的id
                if new_card_type == "sudan":
                    self.config['sudan_pool_cards'].append(new_card_id)

                # 刷新表格
                self.load_data()
                # uid索引加1
                self.config['card_uid_index'] += 1

                # 调用主界面更新方法
                self.main_window.update_config(self.config)

                # 滚动到新增行
                new_row = self.table.rowCount() - 1
                if new_row >= 0:
                    # 使用第2列（ID列）的项进行定位
                    item = self.table.item(new_row, 3)
                    if item:
                        self.table.scrollToItem(item, QTableWidget.ScrollHint.PositionAtTop)
                        self.table.setCurrentCell(new_row, 0)  # 同时高亮选中该行

    # 更新仪式数据到配置对象
    def update_rite_data(self, item):
        row = item.row()
        column = item.column()
        rite = self.config.get('rites')[row]

        try:
            # 保存旧值用于错误恢复
            old_value = None
            if column in (7, 8, 9):  # 数值型字段
                old_value = str(rite.get(self._get_field_name(column), ''))
            elif column == 10:  # 仪式卡牌
                old_value = str(rite.get('cards', []))
            elif column == 11:  # 字符串字段
                old_value = rite.get(self._get_field_name(column), '')

            # 处理字段更新
            if column == 5:  # 数量
                card_id = int(rite.get('id'))  # 获取ID列的文本
                card_data = self.main_window.card_mgr.get_card_data(card_id)
                tags = card_data.get('tag', {})
                stackable = '可堆叠' in tags
                new_count = int(item.text())
                if not stackable and new_count != 1:
                    raise ValueError("不可堆叠卡牌数量必须保持为1")
                rite['count'] = new_count  # 只有验证通过才更新

            elif column == 6:  # 存在回合
                rite['life'] = int(item.text())
            elif column == 7:  # 强化等级
                rite['rareup'] = int(item.text())
            elif column == 8:  # 标签
                new_value = json.loads(json.dumps(eval(item.text())))
                if not isinstance(new_value, dict):
                    raise ValueError("检查标签格式，必须为字典格式")
                else:
                    rite['tag'] = new_value
            elif column == 9:  # 装备槽
                new_value = json.loads(json.dumps(eval(item.text())))
                if not isinstance(new_value, list):
                    raise ValueError("检查装备槽格式，必须为列表格式")
                rite['equip_slots'] = new_value
            elif column == 10:  # 装备
                new_value = json.loads(json.dumps(eval(item.text())))
                if not isinstance(new_value, list):
                    raise ValueError("检查装备格式，必须为列表格式")
                rite['equips'] = new_value
            elif column == 11:  # 背包
                if item.text() not in ('0', '1', '2', '3'):
                    rite['bag'] = int("bag的值必须为0/1/2/3")
                else:
                    rite['bag'] = int(item.text())
            elif column == 12:  # 背包位置
                rite['bagpos'] = int(item.text())
            elif column == 13:  # 自定义名称
                rite['custom_name'] = item.text()
            elif column == 14:  # 描述
                rite['custom_text'] = item.text()

        except Exception as e:
            # 恢复旧值并提示错误
            self.table.blockSignals(True)
            item.setText(old_value)
            self.table.blockSignals(False)
            self.show_message("输入错误", f"无效输入：{str(e)}，已恢复原值")

        finally:
            print("更新后数据为")
            print(self.config.get('cards')[row])
            print('-----------------------')
            # 调用主界面更新方法
            self.main_window.update_config(self.config)

    # 根据列索引获取字段名称
    def _get_field_name(self, column: int) -> str:
        mapping = {
            4: 'new_born',
            5: 'is_show',
            6: 'start',
            7: 'start_round',
            8: 'start_life',
            9: 'life',
            10: 'cards',
            11: 'custom_name'
        }
        return mapping.get(column, '')

    # 显示卡牌详细信息
    def show_detail(self, row):
        try:
            rite_id = int(self.table.item(row, 2).text())  # 获取ID列的文本
            rite_data = self.main_window.rite_mgr.get_rite_details(rite_id)
            print(rite_data)
            detail_window = RiteDetailWindow(rite_data, self)
            detail_window.show()
        except Exception as e:
            self.show_message("错误", f"无法显示详细信息：{str(e)}")

    # 显示消息弹窗
    def show_message(self, title, content):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(content)
        msg.exec()

