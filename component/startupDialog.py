import json
import os
import sys

from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from pathlib import Path


class StartupDialog(QDialog):
    CONFIG_FILE = "app_config.json"

    def __init__(self):
        super().__init__()
        self.data_dir = None
        self.save_dir = None
        self.config_path = self.get_config_path()
        self.init_ui()
        self.load_config()
        self.setWindowTitle("初始化配置")
        self.setAcceptDrops(True)  # 启用拖放功能

    # 获取跨平台的配置文件路径
    def get_config_path(self):
        config_dir = Path.home() / ".SultansGame_Save_Editor"
        config_dir.mkdir(exist_ok=True)
        return config_dir / self.CONFIG_FILE

    def init_ui(self):
        layout = QVBoxLayout()

        # 说明文本
        info = QLabel(
            "请选择游戏数据文件夹和存档文件\n"
            "游戏数据文件夹示例路径：\n"
            r"C:\Program Files (x86)\Steam\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config"
            "\n"
            r"E:\SteamLibrary\steamapps\common\Sultan's Game\Sultan's Game_Data\StreamingAssets\config"
            "\n"
            "存档文件示例路径：\n"
            r"C:\Users\25285\AppData\LocalLow\DoubleCross\SultansGame\SAVEDATA\76561199041269113\auto_save.json"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(info)

        # 游戏数据相关ui
        data_layout = QHBoxLayout()
        # 路径输入框
        data_label = QLabel("游戏数据文件夹:")
        data_layout.addWidget(data_label)
        # 游戏数据路径输入框
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("点击按钮选择或直接输入游戏数据文件夹...")
        self.path_edit.setStyleSheet("""
                            QLineEdit {
                                padding: 5px;
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
        data_layout.addWidget(self.path_edit)
        # 游戏数据浏览按钮
        data_btn = QPushButton("浏览")
        data_btn.clicked.connect(self.select_data_dir)
        data_layout.addWidget(data_btn)
        layout.addLayout(data_layout)

        # 存档文件相关ui
        save_layout = QHBoxLayout()
        # 存档路径标签
        save_label = QLabel("存档文件:")
        save_layout.addWidget(save_label)
        # 存档路径输入框
        self.save_edit = QLineEdit()
        self.save_edit.setPlaceholderText("点击按钮选择或直接输入存档文件...")
        self.save_edit.setStyleSheet("""
                                    QLineEdit {
                                        padding: 5px;
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
        save_layout.addWidget(self.save_edit)
        # 存档浏览按钮
        save_btn = QPushButton("浏览")
        save_btn.clicked.connect(self.select_save_dir)
        save_layout.addWidget(save_btn)
        layout.addLayout(save_layout)

        # 按钮容器
        btn_layout = QHBoxLayout()
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

        # 连接文本框内容变化信号
        self.path_edit.textChanged.connect(self.validate_path)
        self.save_edit.textChanged.connect(self.validate_path)

        self.setLayout(layout)
        self.resize(700, 180)


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

    def select_save_dir(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择存档文件",
            filter="JSON存档文件 (*.json)"
        )
        if path:
            self.save_edit.setText(path)

    # 在手动输入文件目录时实时验证路径有效性，并且在选择/拖放/输入文件目录后改变输入框和按钮样式
    def validate_path(self):
        data_path = self.path_edit.text()
        save_path = self.save_edit.text()

        data_valid = bool(data_path) and self.is_valid_data_dir(data_path)
        save_valid = bool(save_path) and self.is_valid_save_dir(save_path)

        # 更新样式和提示
        self.update_field_style(self.path_edit, data_valid)
        self.update_field_style(self.save_edit, save_valid)

        # 自动补全路径分隔符
        if data_valid:
            if len(data_path) > 3 and not data_path.endswith(os.sep):
                self.path_edit.setText(data_path + os.sep)

        self.confirm_btn.setEnabled(data_valid and save_valid)

    # 增强型路径验证
    @staticmethod
    def is_valid_data_dir(path):
        required_files = {'cards.json'}
        required_dirs = {'rite'}
        try:
            # 获取目录下所有条目
            entries = set(os.listdir(path))
            # 检查必要文件存在性
            has_required_files = required_files.issubset(entries)
            # 检查必要目录存在性
            has_required_dirs = required_dirs.issubset(entries)
            # 进一步验证文件类型
            cards_valid = os.path.isfile(os.path.join(path, 'cards.json'))
            rite_valid = os.path.isdir(os.path.join(path, 'rite'))
            return has_required_files and has_required_dirs and cards_valid and rite_valid
        except Exception as e:
            print(f"目录验证失败: {str(e)}")
            return False

    @staticmethod
    def is_valid_save_dir(path):
        return (
                os.path.isfile(path) and
                path.lower().endswith('.json') and
                os.path.getsize(path) > 0  # 确保不是空文件
        )

    # 更新输入框样式
    def update_field_style(self, field, valid):
        field.setProperty("valid", "true" if valid else "false")
        field.style().unpolish(field)
        field.style().polish(field)

    # 加载配置文件
    def load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    self.path_edit.setText(config.get("data_dir", ""))
                    self.save_edit.setText(config.get("save_dir", ""))
            except Exception as e:
                QMessageBox.warning(self, "配置错误", f"无法读取配置文件:\n{str(e)}")

    # 保存配置文件
    def save_config(self):
        config = {
            "data_dir": self.path_edit.text(),
            "save_dir": self.save_edit.text()
        }
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存配置:\n{str(e)}")


    def validate_and_accept(self):
        if self.is_valid_data_dir(self.path_edit.text()) and \
                self.is_valid_save_dir(self.save_edit.text()):

            self.data_dir = self.path_edit.text()
            self.save_dir = self.save_edit.text()
            self.save_config()  # 保存配置
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "路径无效",
                "检查游戏数据文件夹和存档文件路径是否正确"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartupDialog()
    window.show()
    sys.exit(app.exec())