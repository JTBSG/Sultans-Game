import json
import sys

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
                             QPushButton, QLabel, QFormLayout, QSpinBox, QTextEdit, QApplication, QMessageBox)
from manager.cardDataManager import CardDataManager


class AddCardDialog(QDialog):
    def __init__(self, card_mgr, parent=None, base_uid=0, base_sudan_pool_cards_length=0):
        super().__init__(parent)
        self.parent = parent
        self.card_mgr = card_mgr
        self.selected_card = None
        self.base_uid = base_uid
        self.base_sudan_pool_cards_length = base_sudan_pool_cards_length
        self.new_card_data = {
            'uid': self.base_uid,
            'id': -1,  # 默认未知卡牌
            'count': 1,
            'life': 0,
            'rareup': 0,
            'tag': {},
            'equip_slots': [],
            'equips': [],
            'bag': 0,
            'bagpos': 2,
            'custom_name': "",
            'custom_text': ""
        }
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("选择卡牌")
        self.setMinimumSize(800, 500)

        main_layout = QHBoxLayout()

        # 左侧搜索面板
        left_panel = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入卡牌名称搜索...")
        self.search_input.textChanged.connect(self.update_card_list)
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.update_card_list)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)

        # 卡牌列表
        self.card_list = QListWidget()
        self.card_list.itemClicked.connect(self.show_card_details)

        left_panel.addLayout(search_layout)
        left_panel.addWidget(self.card_list)

        # 右侧信息面板
        right_panel = QVBoxLayout()

        # 卡牌详细信息
        self.info_label = QLabel("卡牌默认信息")
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)

        # 可编辑字段
        form_layout = QFormLayout()
        self.id_spin = QSpinBox()
        self.id_spin.setRange(-1, 9999999)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 999)
        self.life_spin = QSpinBox()
        self.rareup_spin = QSpinBox()
        self.rareup_spin.setRange(0, 3)
        self.tag_edit = QLineEdit()
        self.equip_slots_edit = QLineEdit()
        self.equips_edit = QLineEdit()
        self.bag_spin = QSpinBox()
        self.bag_spin.setRange(0, 3)
        self.bagpos_spin = QSpinBox()
        self.bagpos_spin.setRange(2, 99)
        self.name_edit = QLineEdit()
        self.text_edit = QLineEdit()

        form_layout.addRow("id:", self.id_spin)  # 不可编辑
        self.id_spin.setReadOnly(True)  # 新增设置不可编辑
        self.id_spin.setStyleSheet("background-color: #f0f0f0;")  # 设置灰色背景
        form_layout.addRow("数量:", self.count_spin)
        form_layout.addRow("存在回合:", self.life_spin)  # 不可编辑
        self.life_spin.setReadOnly(True)  # 新增设置不可编辑
        self.life_spin.setStyleSheet("background-color: #f0f0f0;")  # 设置灰色背景
        form_layout.addRow("强化次数:", self.rareup_spin)
        form_layout.addRow("标签:", self.tag_edit)
        form_layout.addRow("装备槽位:", self.equip_slots_edit)
        form_layout.addRow("装备:", self.equips_edit)  # 不可编辑
        self.equips_edit.setReadOnly(True)  # 新增设置不可编辑
        self.equips_edit.setStyleSheet("background-color: #f0f0f0;")  # 设置灰色背景
        form_layout.addRow("背包:", self.bag_spin)
        form_layout.addRow("背包槽位:", self.bagpos_spin)
        form_layout.addRow("自定义名称:", self.name_edit)
        form_layout.addRow("自定义描述:", self.text_edit)

        # 操作按钮
        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("确认")
        confirm_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)

        right_panel.addWidget(self.info_label)
        right_panel.addWidget(self.info_text)
        right_panel.addLayout(form_layout)
        right_panel.addLayout(btn_layout)

        main_layout.addLayout(left_panel, 40)
        main_layout.addLayout(right_panel, 60)
        self.setLayout(main_layout)

        # 初始化列表
        self.update_card_list()
        self.init_data_binding()
        self.set_default_values()

    def set_default_values(self):
        """将默认值设置到表单控件"""
        # 数值类型控件
        self.id_spin.setValue(self.new_card_data['id'])
        self.count_spin.setValue(self.new_card_data['count'])
        self.life_spin.setValue(self.new_card_data['life'])
        self.rareup_spin.setValue(self.new_card_data['rareup'])
        self.bag_spin.setValue(self.new_card_data['bag'])
        self.bagpos_spin.setValue(self.new_card_data['bagpos'])

        # 字符串类型控件
        self.name_edit.setText(self.new_card_data['custom_name'])
        self.text_edit.setText(self.new_card_data['custom_text'])

        # 复杂数据结构控件（字典/列表）
        self.tag_edit.setText(str(self.new_card_data['tag']))
        self.equip_slots_edit.setText(str(self.new_card_data['equip_slots']))
        self.equips_edit.setText(str(self.new_card_data['equips']))

    def init_data_binding(self):
        # 绑定数据到控件
        self.count_spin.valueChanged.connect(lambda v: self._update_field('count', v))
        self.rareup_spin.valueChanged.connect(lambda v: self._update_field('rareup', v))
        self.bag_spin.valueChanged.connect(lambda v: self._update_field('bag', v))
        self.bagpos_spin.valueChanged.connect(lambda v: self._update_field('bagpos', v))
        self.name_edit.textChanged.connect(lambda t: self._update_field('custom_name', t))
        self.text_edit.textChanged.connect(lambda t: self._update_field('custom_text', t))

    def _update_field(self, field, value):
        self.new_card_data[field] = value

    # 更新卡牌列表
    def update_card_list(self):
        search_text = self.search_input.text().lower()
        self.card_list.clear()

        # 获取所有卡牌数据并按ID排序
        cards = sorted(self.card_mgr.card_data_mapping.values(),
                       key=lambda x: x['id'],
                       reverse=False)

        for card in cards:
            if search_text in card['name'].lower():
                item_text = f"{card['id']} - {card['name']}"
                self.card_list.addItem(item_text)

    # 展示卡牌详细信息
    def show_card_details(self, item):
        # 解析选择的卡牌ID
        card_id = int(item.text().split(' - ')[0])
        card_data = self.card_mgr.get_card_data(card_id)

        # 将选择的卡牌id赋值给新卡牌
        self.id_spin.setValue(card_id)  # 更新显示
        self.new_card_data['id'] = card_id
        # 判断新增卡牌类型，如果是苏丹卡则标签中增加苏丹卡池索引，如果是人物卡标签中增加追随者标签，如果是物品卡用户需自己添加拥有标签
        if card_data.get('type', '') == "sudan":
            self.new_card_data['tag'] = f"{{'sudan_pool_index': {self.base_sudan_pool_cards_length+1}}}"
        elif card_data.get('type', '') == "char":
            self.new_card_data['tag'] = "{'adherent': 1}"
        self.tag_edit.setText(self.new_card_data['tag'])  # 更新显示
        # 显示卡牌信息
        info = (
            f"ID: {card_data['id']}\n"
            f"名称: {card_data['name']}\n"
            f"称号: {card_data['title']}\n"
            f"类型: {card_data['type']}\n"
            f"稀有度: {card_data['rare']}星\n"
            f"是否唯一: {'是' if card_data['is_only'] else '否'}\n"
            f"默认装备槽: {card_data['equips']}\n"
            f"默认标签: {card_data['tag']}\n"
            f"描述: {card_data['text']}"
        )

        self.info_text.setPlainText(info)
        self.selected_card = card_data

    # 向主界面中传递新生成的卡片信息
    def get_new_card_data(self):
        if not self.selected_card:
            return None
        return self.new_card_data

    def accept(self):
        # 校验tag和equip_slots格式是否正确
        # 此处优化了json.loads无法处理单引号的问题
        if self.selected_card is None:
            QMessageBox.warning(self, "错误", "请先选择卡牌类型")
            return

        try:
            if 'tag' in self.new_card_data:
                self.new_card_data['tag'] = json.loads(json.dumps(eval(self.tag_edit.text())))
                if not isinstance(self.new_card_data['tag'], dict):
                    raise ValueError("检查标签格式，必须为字典格式")

            if 'equip_slots' in self.new_card_data:
                self.new_card_data['equip_slots'] = json.loads(json.dumps(eval(self.equip_slots_edit.text())))
                if not isinstance(self.new_card_data['equip_slots'], list):
                    raise ValueError("检查装备槽格式，必须为列表格式")
            super().accept()

        except ValueError as e:
            QMessageBox.critical(self, "错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "格式错误",
                                 f"JSON格式解析失败：{str(e)}\n"
                                 f"请检查以下输入：\n"
                                 f"标签应类似：{{\"support\":2,\"survival\":3}}\n"
                                 f"装备槽位应类似：[\"weapon\",\"cloth\"]")


if __name__ == "__main__":
    card_manager = CardDataManager(
        "E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config\cards.json")

    app = QApplication(sys.argv)

    window = AddCardDialog(card_manager)
    window.show()
    sys.exit(app.exec())
