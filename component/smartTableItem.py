from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import QCollator


class SmartTableItem(QTableWidgetItem):
    def __lt__(self, other):
        # 数值列智能比较（如第5列count）
        if self.column() in [2, 3, 5, 6, 7, 11, 12]:
            try:
                return int(self.text()) < int(other.text())
            except ValueError:
                return self.text() < other.text()  # 异常时退回文本比较

        # 混合数字文本智能排序（如名称列）
        collator = QCollator()
        collator.setNumericMode(True)
        return collator.compare(self.text(), other.text()) < 0