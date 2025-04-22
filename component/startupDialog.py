import os
import sys

from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class StartupDialog(QDialog):
    DEFAULT_PATHS = [
        r"E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config",
        r"C:\Program Files (x86)\Steam\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config"
    ]

    def __init__(self):
        super().__init__()
        self.data_dir = None
        self.init_ui()
        self.setWindowTitle("配置游戏默认数据")
        self.setAcceptDrops(True)  # 启用拖放功能

    def init_ui(self):
        layout = QVBoxLayout()

        # 说明文本
        info = QLabel(
            "请选择或输入游戏数据目录\n"
            "示例路径：\n"
            r"C:\Program Files (x86)\Steam\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config"
            "\n"
            r"E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(info)

        # 路径输入框
        self.path_edit = QLineEdit()
        layout.addWidget(self.path_edit)

        # 按钮容器
        btn_layout = QHBoxLayout()
        # 选择目录按钮
        select_btn = QPushButton("浏览目录")
        select_btn.clicked.connect(self.select_data_dir)
        select_btn.setStyleSheet("padding: 6px 12px;")
        btn_layout.addWidget(select_btn)
        # 确认按钮
        self.confirm_btn = QPushButton("进入主界面")
        self.confirm_btn.clicked.connect(self.validate_and_accept)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 4px;
                    }
                    QPushButton:disabled {
                        background-color: #BDBDBD;
                    }
                """)
        btn_layout.addWidget(self.confirm_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.resize(600, 180)

        # 设置默认路径
        self.path_edit.setPlaceholderText("点击按钮选择或直接输入数据目录...")
        self.path_edit.textChanged.connect(self.validate_path)
        self._set_smart_default_path()
        self.path_edit.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }
                    QLineEdit[valid="true"] {
                        border-color: #4CAF50;
                    }
                    QLineEdit[valid="false"] {
                        border-color: #F44336;
                    }
                """)

    # 设置智能默认路径
    def _set_smart_default_path(self):
        for path in self.DEFAULT_PATHS:
            if os.path.exists(path) and self.is_valid_data_dir(path):
                self.path_edit.setText(path)
                self.path_edit.setToolTip(path)
                break

    # 拖放功能实现
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.path_edit.setText(path)
                break

    def select_data_dir(self):
        path = QFileDialog.getExistingDirectory(self, "选择游戏数据目录")
        if path:
            self.path_edit.setText(path)

    # 在手动输入文件目录时实时验证路径有效性，并且在选择/拖放/输入文件目录后改变输入框和按钮样式
    def validate_path(self):
        path = self.path_edit.text()
        is_valid = False
        if path:
            exists = os.path.exists(path)
            valid_data = self.is_valid_data_dir(path) if exists else False
            is_valid = exists and valid_data

            # 更新样式和提示
            status = "true" if is_valid else "false"
            self.path_edit.setProperty("valid", status)
            self.path_edit.setToolTip(path if exists else "路径不存在")
            self.path_edit.style().unpolish(self.path_edit)
            self.path_edit.style().polish(self.path_edit)

            # 自动补全路径分隔符
            if len(path) > 3 and not path.endswith(os.sep):
                self.path_edit.setText(path + os.sep)
        self.confirm_btn.setEnabled(is_valid)

    # 增强型路径验证
    @staticmethod
    def is_valid_data_dir(path):
        required_files = {'cards.json'}
        try:
            return required_files.issubset(set(os.listdir(path)))
        except Exception:
            return False

    def validate_and_accept(self):
        self.data_dir = self.path_edit.text()
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartupDialog()
    window.show()
    sys.exit(app.exec())