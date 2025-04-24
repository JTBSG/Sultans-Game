# 卡片槽位展示组件
# --------------------------
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from component.SlotCard import SlotCard


class SlotDisplayWidget(QWidget):
    def __init__(self, cards_slot_data, parent=None):
        super().__init__(parent)
        self.cards_slot = cards_slot_data
        self.init_ui()

    def init_ui(self):
        # 横向布局容器
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(20)

        # 生成卡片组件
        for slot_id, slot_data in self.cards_slot.items():
            card = SlotCard(slot_id, slot_data)
            layout.addWidget(card)

        self.setLayout(layout)