import ast
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

from manager.cardDataManager import CardDataManager
from manager.tagDataManager import TagDataManager


# 软件主界面
class CardTablePage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.config = self.main_window.config
        self.initUI()
        self._connect_signals()  # 初始化时连接信号

    # 连接表格数据变更信号
    def _connect_signals(self):
        self.table.itemChanged.connect(self.update_card_data)

    # 断开表格数据变更信号
    def _disconnect_signals(self):
        try:
            self.table.itemChanged.disconnect(self.update_card_data)
        except TypeError:
            pass  # 忽略未连接时的错误

    # 界面初始化
    def initUI(self):
        # 创建主控件和布局
        main_layout = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入卡片名字进行搜索...")
        self.search_input.returnPressed.connect(self.filter_cards)  # 添加回车事件绑定
        search_button = QPushButton("搜索")
        search_button.clicked.connect(self.filter_cards)
        search_layout.addWidget(QLabel("快速搜索："))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        # 添加过滤按钮
        filter_btn_layout = QHBoxLayout()
        self.btn_show_all = QPushButton("查看全部")
        self.btn_show_hand = QPushButton("查看手牌")
        self.btn_show_hidden = QPushButton("查看隐藏")

        # 添加新增卡牌按钮
        self.add_new_card_btn = QPushButton("新增卡牌")

        # 设置按钮样式
        for btn in [self.btn_show_all, self.btn_show_hand, self.btn_show_hidden, self.add_new_card_btn]:
            btn.setFixedSize(100, 30)

        # 绑定点击事件
        self.btn_show_all.clicked.connect(lambda: self.filter_by_pos_mode('all'))
        self.btn_show_hand.clicked.connect(lambda: self.filter_by_pos_mode('hand'))
        self.btn_show_hidden.clicked.connect(lambda: self.filter_by_pos_mode('hidden'))
        self.add_new_card_btn.clicked.connect(self.add_new_card)

        filter_btn_layout.addWidget(self.btn_show_all)
        filter_btn_layout.addWidget(self.btn_show_hand)
        filter_btn_layout.addWidget(self.btn_show_hidden)
        filter_btn_layout.addWidget(self.add_new_card_btn)

        # 卡片表格
        self.table = QTableWidget()
        self.table.setColumnCount(16)  # TODO:记得要修改卡片表格的列数
        self.table.setHorizontalHeaderLabels([
            "查看", "删除", "UID", "ID", "名称", "数量", "存在回合", "强化次数", "标签",
            "装备槽", "装备", "背包", "背包位置", "自定义名称", "描述", "查看"
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

    # 加载卡片数据到表格
    def load_data(self):
        # 加载数据的时候断开信号连接
        self._disconnect_signals()

        self.table.setRowCount(len(self.config.get('cards', {})))

        for row, card in enumerate(self.config.get('cards', {})):
            # 添加查看卡片初始信息按钮
            front_btn = QPushButton("查看详情")
            front_btn.clicked.connect(partial(self.show_detail, row))
            self.table.setCellWidget(row, 0, front_btn)

            # 添加删除按钮到列1
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(partial(self.delete_card, row))
            self.table.setCellWidget(row, 1, delete_btn)

            # 创建不可编辑的UID项和id项
            uid_item = QTableWidgetItem(str(card.get('uid')))
            uid_item.setFlags(uid_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            id_item = QTableWidgetItem(str(card.get('id')))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 获取卡牌id对应的名称
            card_name = QTableWidgetItem(self.main_window.card_mgr.get_card_data(card.get('id')).get('name'))
            card_name.setFlags(card_name.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.table.setItem(row, 2, QTableWidgetItem(uid_item))
            self.table.setItem(row, 3, QTableWidgetItem(id_item))
            self.table.setItem(row, 4, QTableWidgetItem(card_name))
            self.table.setItem(row, 5, QTableWidgetItem(str(card.get('count'))))
            self.table.setItem(row, 6, QTableWidgetItem(str(card.get('life'))))
            self.table.setItem(row, 7, QTableWidgetItem(str(card.get('rareup'))))
            self.table.setItem(row, 8, QTableWidgetItem(str(card.get('tag'))))
            self.table.setItem(row, 9, QTableWidgetItem(str(card.get('equip_slots'))))
            self.table.setItem(row, 10, QTableWidgetItem(str(card.get('equips'))))
            self.table.setItem(row, 11, QTableWidgetItem(str(card.get('bag'))))
            self.table.setItem(row, 12, QTableWidgetItem(str(card.get('bagpos'))))
            self.table.setItem(row, 13, QTableWidgetItem(card.get('custom_name')))
            self.table.setItem(row, 14, QTableWidgetItem(card.get('custom_text')))

            # 添加末端操作按钮
            end_btn = QPushButton("查看详情")
            end_btn.clicked.connect(partial(self.show_detail, row))
            self.table.setCellWidget(row, 15, end_btn)

        # 重新连接信号
        self._connect_signals()

        self.table.resizeColumnsToContents()  # 自动调整列宽
        # 标签、装备栏和装备太长了，设置一个列宽最大值
        self.table.setColumnWidth(8, min(self.table.columnWidth(8), 200))
        self.table.setColumnWidth(9, min(self.table.columnWidth(9), 200))
        self.table.setColumnWidth(10, min(self.table.columnWidth(10), 200))
        self.table.resizeRowsToContents()  # 自动调整行高
        self.table.setAlternatingRowColors(True)  # 设置隔行颜色区分

    # 根据名字搜索卡片
    def filter_cards(self):
        search_id = self.search_input.text().strip()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 4)  # 名字列
            match = search_id.lower() in item.text().lower()
            self.table.setRowHidden(row, not match)

    # 根据卡牌在背包中的未知过滤卡牌
    # TODO 这里如果位置为(0,0)或者(0,1)则不显示在手牌中，除了背包中真正在(0,1)位置的那一张牌
    # TODO tag中如果存在“own:-1”说明此卡牌在手牌中存在过但已经被使用，此处未加筛选
    def filter_by_pos_mode(self, mode):
        for row in range(self.table.rowCount()):
            bag = int(self.table.item(row, 11).text())
            bagpos = int(self.table.item(row, 12).text())

            # 判断是否为(0,0)或者(0,1)
            invisible = (bag == 0 and bagpos == 0) or (bag == 0 and bagpos == 1)

            if invisible:
                pass
            else:
                # 解析第8列字段
                item_text = self.table.item(row, 8).text().strip()
                try:
                    data_dict = ast.literal_eval(item_text)

                    if not isinstance(data_dict, dict):
                        raise Exception

                    if data_dict.get('own', None) == -1:
                        invisible = True
                except Exception as e:
                    self.show_message("错误", f"解析错误：{str(e)}")

            # 根据模式设置行可见性
            if mode == 'all':
                self.table.setRowHidden(row, False)
            elif mode == 'hand':
                self.table.setRowHidden(row, invisible)
            elif mode == 'hidden':
                self.table.setRowHidden(row, not invisible)

        # 清除搜索框内容
        self.search_input.clear()

    # 新增一张卡牌
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

    # 更新卡片数据到配置对象
    # TODO 只更新了卡片数据到子界面的config中，未同步到主界面的config
    def update_card_data(self, item):
        row = item.row()
        column = item.column()
        card = self.config.get('cards')[row]

        print("更新前数据为")
        print(self.config.get('cards')[row])

        try:
            # 保存旧值用于错误恢复
            old_value = None
            if column in (5, 6, 7, 11, 12):  # 数值型字段
                old_value = str(card.get(self._get_field_name(column), ''))
            elif column == 8:  # 标签
                old_value = str(card.get('tag', {}))
            elif column == 9:  # 装备槽位
                old_value = str(card.get('equip_slots', []))
            elif column == 10:  # 装备列表
                old_value = str(card.get('equips', []))
            elif column in (13, 14):  # 字符串字段
                old_value = card.get(self._get_field_name(column), '')

            # 处理字段更新
            if column == 5:  # 数量
                card_id = int(card.get('id'))  # 获取ID列的文本
                card_data = self.main_window.card_mgr.get_card_data(card_id)
                tags = card_data.get('tag', {})
                stackable = '可堆叠' in tags
                new_count = int(item.text())
                if not stackable and new_count != 1:
                    raise ValueError("不可堆叠卡牌数量必须保持为1")
                card['count'] = new_count  # 只有验证通过才更新

            elif column == 6:  # 存在回合
                card['life'] = int(item.text())
            elif column == 7:  # 强化等级
                card['rareup'] = int(item.text())
            elif column == 8:  # 标签
                new_value = json.loads(json.dumps(eval(item.text())))
                if not isinstance(new_value, dict):
                    raise ValueError("检查标签格式，必须为字典格式")
                else:
                    card['tag'] = new_value
            elif column == 9:  # 装备槽
                new_value = json.loads(json.dumps(eval(item.text())))
                if not isinstance(new_value, list):
                    raise ValueError("检查装备槽格式，必须为列表格式")
                card['equip_slots'] = new_value
            elif column == 10:  # 装备
                new_value = json.loads(json.dumps(eval(item.text())))
                if not isinstance(new_value, list):
                    raise ValueError("检查装备格式，必须为列表格式")
                card['equips'] = new_value
            elif column == 11:  # 背包
                if item.text() not in ('0', '1', '2', '3'):
                    card['bag'] = int("bag的值必须为0/1/2/3")
                else:
                    card['bag'] = int(item.text())
            elif column == 12:  # 背包位置
                card['bagpos'] = int(item.text())
            elif column == 13:  # 自定义名称
                card['custom_name'] = item.text()
            elif column == 14:  # 描述
                card['custom_text'] = item.text()

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
            5: 'count',
            6: 'life',
            7: 'rareup',
            8: 'tag',
            9: 'equip_slots',
            10: 'equips',
            11: 'bag',
            12: 'bagpos',
            13: 'custom_name',
            14: 'custom_text'
        }
        return mapping.get(column, '')

    # 显示卡牌详细信息
    def show_detail(self, row):
        try:
            card_id = int(self.table.item(row, 3).text())  # 获取ID列的文本
            card_data = self.main_window.card_mgr.get_card_data(card_id)
            detail_window = CardDetailWindow(card_data, self)
            detail_window.show()
        except Exception as e:
            self.show_message("错误", f"无法显示详细信息：{str(e)}")

    # 新增delete_card方法处理删除操作
    def delete_card(self, row):
        # 确认对话框
        reply = QMessageBox.question(
            self,
            '确认删除',
            '确定要删除该卡片吗？此操作不可恢复！',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if 0 <= row < len(self.config['cards']):
                # 判断要删除的卡牌是否是苏丹卡
                card_id = self.config['cards'][row].get('id', 0)
                card_data = self.main_window.card_mgr.get_card_data(card_id)
                card_type = card_data.get('type', "")
                # 如果新增卡牌为苏丹卡,在苏丹卡池中添加新苏丹卡的id
                if card_type == "sudan":
                    self.config['sudan_pool_cards'].pop(self.config['cards'][row].get('tag').get('sudan_pool_index')-1)
                # 删除数据
                del self.config['cards'][row]
                # 调用主界面更新方法
                self.main_window.update_config(self.config)
                # 重新加载表格
                self.load_data()

    # 显示消息弹窗
    def show_message(self, title, content):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(content)
        msg.exec()

