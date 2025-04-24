import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QApplication, QDialog, QScrollArea, QWidget, QTextEdit


class SlotCard(QFrame):
    COLOR_MAP = {
        '任务': '#FFE6EE',  # 角色-粉色
        '物品': '#E6F4FF',  # 物品-浅蓝
        '苏丹卡': '#E8FFEA',  # 苏丹卡-浅绿
        '其他': '#FFFFFF'  # 默认白色
    }

    RARE_MAP = {'0': '石', '1': '铜', '2': '银', '3': '金'}

    clicked = pyqtSignal()  # 新增点击信号

    def __init__(self, slot_id, slot_data):
        super().__init__()
        self.slot_id = slot_id
        self.data = slot_data
        self.setup_card()


    # 基础样式
    def setup_card(self):
        self.setFixedSize(160, 200)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(1)

        # 动态设置颜色
        condition_type = self.get_condition_type()
        bg_color = self.COLOR_MAP.get(condition_type, self.COLOR_MAP['其他'])
        self.setStyleSheet(f"""
            background-color: {bg_color};
            border-radius: 8px;
            padding: 8px;
        """)

        # 内容布局
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # 槽位编号
        lbl_id = QLabel(f"<b>{self.slot_id.upper()}</b>")
        lbl_id.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_id.setStyleSheet("font-size: 14px; color: #444;")
        layout.addWidget(lbl_id)

        # 槽位的type要求
        type_text = self.get_condition_type()
        lbl_type = QLabel(f"类型：{type_text}")
        lbl_type.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(lbl_type)

        # 描述文本
        lbl_desc = QLabel(f"「{self.data['text']}」")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #333; font-style: italic; font-size: 12px;")
        layout.addWidget(lbl_desc)

        # 添加点击事件
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mousePressEvent = self._on_click

        self.setLayout(layout)

    def _on_click(self, event):
        self.clicked.emit()
        DetailDialog(self.data).exec()


    # 解析条件类型用于颜色标记
    def get_condition_type(self):
        condition = self.data['condition']
        if 'type' in condition:
            condition_type = condition['type']
            if condition_type == 'item':
                return '物品'
            elif condition_type == 'char':
                return '人物'
            elif condition_type == 'sudan':
                return '苏丹卡'
            else:
                return '其他'


class DetailDialog(QDialog):
    def __init__(self, slot_data):
        super().__init__()
        self.setWindowTitle("详细条件")
        self.setMinimumSize(300, 400)

        # 滚动区域
        scroll = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout()

        # 格式化详细条件
        text = self._format_details(slot_data['condition'])
        text_edit = QTextEdit()
        text_edit.setText(text)
        text_edit.setReadOnly(True)

        layout.addWidget(text_edit)
        content.setLayout(layout)
        scroll.setWidget(content)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)

    def _format_details(self, condition, indent=0):
        """递归格式化嵌套条件"""
        spaces = '  ' * indent
        text = []

        if isinstance(condition, dict):
            for k, v in condition.items():
                if isinstance(v, dict):
                    text.append(f"{spaces}{k}:")
                    text.append(self._format_details(v, indent + 1))
                elif isinstance(v, list):
                    text.append(f"{spaces}{k}:")
                    for item in v:
                        text.append(self._format_details(item, indent + 1))
                else:
                    text.append(f"{spaces}{k}: {v}")
        else:
            text.append(f"{spaces}{condition}")

        return '\n'.join(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 启动主窗口
    main_window = SlotCard("s1", {
                    "condition":
                    {
                        "type":"item",
                        "!金币":1,
                        "any":{
                            "cost.消耗品=": 1,
                            "is":2000364,
                            "is":2000365,
                            "is":2000366,
                            "空屋":1,
                            "is":2000680,
                            "is":2000700,
                            "is":2000853,
                            "is":2000760
                        },
                    },
                    "open_adsorb":0,
                    "is_key":0,
                    "is_empty":1,
                    "is_enemy":0,
                    "text":"可以尝试置入道具或地点，也许会有些用处"
                })
    main_window.show()
    sys.exit(app.exec())

