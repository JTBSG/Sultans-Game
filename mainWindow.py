import gc
import os

import json5
import json
from typing import Dict
import sys
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QTextEdit, QFileDialog, QDialog, QProgressDialog, QInputDialog,
                             QTabWidget)
from PyQt6.QtCore import Qt, QFileSystemWatcher
from component.startupDialog import StartupDialog
from component.cardDetailWindow import CardDetailWindow
from component.addCardDialog import AddCardDialog

from manager.cardDataManager import CardDataManager
from manager.tagDataManager import TagDataManager
from manager.riteDataManager import RiteDataManager
from component.cardTablePage import CardTablePage
from component.riteTablePage import RiteTablePage
from component.infoPage import InfoPage
from component.helpPage import HelpPage


class MainWindow(QMainWindow):
    def __init__(self, data_dir: str):
        super().__init__()
        self.config = {}  # 统一管理配置数据
        self.card_mgr = None
        self.rite_mgr = None
        self.default_data_dir = data_dir
        self.data_dir = data_dir
        self.info_page = InfoPage(self)
        self.table_page = CardTablePage(self)
        self.rite_page = RiteTablePage(self)


        self.initUI()

        # 尝试加载默认manager数据
        self._init_managers(self.default_data_dir)
        self.info_page._init_save_file()
        self.info_page.update_info()
        self.table_page.update_info()
        self.rite_page.update_info()

    # 初始化卡牌和标签管理器
    def _init_managers(self, data_dir: str):
        self.show_loading()
        try:
            cards_path = os.path.join(data_dir, "cards.json")
            tags_path = os.path.join(data_dir, "tag.json")
            rites_path = os.path.join(data_dir, "rite")
            try:
                self.card_mgr = CardDataManager(cards_path)
                # self.tag_mgr = TagDataManager(tags_path)
                self.rite_mgr = RiteDataManager(rites_path)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载默认游戏数据失败: {str(e)}")
        finally:
            self.hide_loading()

    def initUI(self):
        self.setWindowTitle('苏丹')
        self.setGeometry(300, 300, 1200, 600)

        # 创建选项卡容器
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 初始化页面
        self.tabs.addTab(self.info_page, "基本信息")
        self.tabs.addTab(self.table_page, "卡牌编辑")
        self.tabs.addTab(self.rite_page, "仪式编辑")
        help_page = HelpPage()
        self.tabs.addTab(help_page, "帮助信息")

    # 显示加载提示对话框
    def show_loading(self):
        self.loading_dialog = QProgressDialog("正在加载数据，请稍候...", None, 0, 0, self)
        self.loading_dialog.setWindowTitle("加载中")
        self.loading_dialog.setCancelButton(None)
        self.loading_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.loading_dialog.setMinimumDuration(0)
        self.loading_dialog.show()
        QApplication.processEvents()  # 强制刷新界面

    # 隐藏加载提示对话框
    def hide_loading(self):
        if hasattr(self, 'loading_dialog') and self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None

    # 添加配置更新方法
    def update_config(self, new_config):
        self.config = new_config
        self.info_page.update_info()
        self.table_page.update_info()
        self.rite_page.update_info()

    # 在关闭窗口时增加
    def closeEvent(self, event):
        self.info_page.file_watcher.deleteLater()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    startup_dialog = StartupDialog()
    if startup_dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    # 启动主窗口
    main_window = MainWindow(startup_dialog.data_dir)
    main_window.show()
    sys.exit(app.exec())