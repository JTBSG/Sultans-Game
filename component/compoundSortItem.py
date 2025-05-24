from PyQt6.QtCore import QCollator
from PyQt6.QtWidgets import QTableWidgetItem


class CompoundSortItem(QTableWidgetItem):
    def __lt__(self, other):
        row = self.row()
        primary_col = 11  # 第11列
        secondary_col = 12  # 第12列

        # 获取当前行两列数据
        primary_item = self.tableWidget().item(row, primary_col)
        other_primary = other.tableWidget().item(other.row(), primary_col)

        # 主列比较
        try:
            if float(primary_item.text()) != float(other_primary.text()):
                return float(primary_item.text()) < float(other_primary.text())
        except ValueError:
            pass

        # 次列比较
        secondary_item = self.tableWidget().item(row, secondary_col)
        other_secondary = other.tableWidget().item(other.row(), secondary_col)
        try:
            return float(secondary_item.text()) < float(other_secondary.text())
        except ValueError:
            return secondary_item.text() < other_secondary.text()


