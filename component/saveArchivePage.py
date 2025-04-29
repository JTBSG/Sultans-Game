import os

import json5
import json
from typing import Dict, List, Union
import sys
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QTextEdit, QFileDialog, QDialog, QProgressDialog, QInputDialog,
                             QScrollArea)
from PyQt6.QtCore import Qt, QFileSystemWatcher, QTimer
from datetime import datetime


class SaveArchivePage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.config = self.main_window.config
        self.archive_data: List[Union[dict, None]] = [None] * 10
        self.initUI()
        self.file_watcher = QFileSystemWatcher()  # 增加文件监视器
        self.file_watcher.fileChanged.connect(self.on_archive_changed)

    def initUI(self):
        layout = QVBoxLayout()

        # 说明标签
        self.info_label = QLabel("点击存档位进行保存（位置1-10）")
        layout.addWidget(self.info_label)

        # 创建滚动区域以容纳多个存档位
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll_layout = QVBoxLayout(content)

        # 设置按钮样式
        button_style = """
                    QPushButton {
                        min-width: 400px;
                        min-height: 200px;
                        padding: 10px;
                        font-size: 14px;
                        border: 1px solid #BBDEFB;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #E3F2FD;
                    }
                """

        self.slots = []
        for i in range(10):
            btn = QPushButton()
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # 添加按钮和间距
            scroll_layout.addWidget(btn)
            scroll_layout.addSpacing(10)
            self.slots.append(btn)
            btn.clicked.connect(partial(self.save_archive, i))

        # 添加底部弹性空间
        scroll_layout.addStretch(1)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)

    # 处理保存时间的格式转换
    def format_iso_time(self, iso_str):
        try:
            # 处理微秒位数问题（最多支持6位）
            if '.' in iso_str:
                main_part, fractional = iso_str.split('.', 1)
                fractional = fractional[:6]  # 截断到6位微秒
                iso_str = f"{main_part}.{fractional}"
            # 处理时区格式
            iso_str = iso_str.replace('Z', '+00:00')
            # 解析时间
            dt = datetime.fromisoformat(iso_str)
            # 格式化为指定字符串
            return "{}/{:d}/{:d} {:02d}:{:02d}:{:02d}".format(
                dt.year,
                dt.month,  # 自动去除前导零
                dt.day,  # 自动去除前导零
                dt.hour,
                dt.minute,
                dt.second
            )
        except (TypeError, ValueError) as e:
            print(f"时间格式转换失败: {str(e)}")
            return iso_str  # 返回原始值

    # 联动主界面信息更新
    def update_info(self):
        self.config = self.main_window.config
        self.load_archive_data()

    # 加载user_archive.json文件
    def load_archive_data(self):
        try:
            save_dir = os.path.dirname(self.main_window.save_dir)  # 从文件路径提取目录
            archive_path = os.path.normpath(os.path.join(save_dir, "user_archive.json"))

            # 添加文件监视（先移除旧路径再添加新路径）
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            self.file_watcher.addPath(archive_path)

            # 处理文件不存在的情况
            if not os.path.exists(archive_path):
                try:
                    # 写入初始化文件
                    with open(archive_path, 'w', encoding='utf-8') as f:
                        json.dump(self.archive_data, f, indent=2, ensure_ascii=False)
                    return  # 直接返回初始化数据
                except PermissionError as pe:
                    QMessageBox.critical(
                        self,
                        "权限错误",
                        f"没有权限创建存档文件:\n{archive_path}\n{str(pe)}"
                    )
                    return
                except Exception as init_e:
                    QMessageBox.critical(
                        self,
                        "初始化错误",
                        f"创建初始存档文件失败:\n{str(init_e)}"
                    )
                    return
            # user_archive.json文件存在
            with open(archive_path, 'r', encoding='utf-8') as f:
                self.archive_data = json.load(f)
                # 确保总是10个存档位
                if len(self.archive_data) < 10:
                    self.archive_data += [None] * (10 - len(self.archive_data))

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载存档数据失败: {str(e)}")
            self.archive_data = [None] * 10
        finally:
            self.update_slot_display()

    # 更新存档信息
    def update_slot_display(self):
        for i in range(10):
            btn = self.slots[i]
            archive = self.archive_data[i]
            if archive and isinstance(archive, dict):
                # 构建展示文本（严格对应图片布局）
                line1 = f"{i + 1:03d} {archive.get('name', '未命名存档')}"
                line2 = " | ".join([
                    f"存活天数：{archive.get('live_days', 0)}天",
                    f"苏丹卡剩余：{archive.get('left_sudan', 32)}",
                    f"处刑日残余：{archive.get('execution_day', 0)}天"
                ]) + " " * 10 + self.format_iso_time(archive.get('save_time', ''))
                # 按图片布局拼接文本
                display_text = f"{line1}\n{line2}"
                btn.setStyleSheet("background-color: #E1F5FE;")
            else:
                display_text = f"{i + 1:03d}\n （空）"
                btn.setStyleSheet("background-color: #F5F5F5;")
            btn.setText(display_text)

    # 当监视文件发生变化时触发
    def on_archive_changed(self, path):
        QApplication.processEvents()  # 确保UI线程响应
        try:
            if os.path.exists(path):
                # 延时100ms避免文件被其他程序占用
                QTimer.singleShot(100, self.delayed_reload)
            else:
                print(f"文件 {path} 已被删除")
        except Exception as e:
            print(f"文件变化处理异常: {str(e)}")

    # 延时重新加载
    def delayed_reload(self):
        try:
            self.load_archive_data()
            print("存档文件变化，已重新加载数据")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"自动更新失败: {str(e)}")

    # 创建新存档
    def save_archive(self, index):
        # 获取存档名称
        name, ok = QInputDialog.getText(self, '存档设置', '请输入存档名称:', text='未命名存档')
        if not ok:
            return
        # 计算苏丹卡总数
        # 创建卡牌类型缓存（提升性能）
        card_type_cache = {}
        sudan_count = 0
        max_life = -10000000000000
        for card in self.config.get('cards', []):
            card_id = card.get('id')
            # 优先使用缓存避免重复查询
            if card_id not in card_type_cache:
                card_data = self.main_window.card_mgr.get_card_data(card_id)
                card_type_cache[card_id] = card_data.get('type', '') if card_data else ''

            if card_type_cache[card_id] == 'sudan':
                sudan_count += 1
                current_life = card.get('life', 0)
                if current_life > max_life:
                    max_life = current_life
        total_sudan = sudan_count + len(self.config.get('sudan_card_pool', []))
        execution_day = 7 - max_life if sudan_count > 0 else 7

        archive = {
            "name": name,
            "live_days": self.config.get("round", -1),
            "left_sudan": total_sudan,
            "execution_day": execution_day,
            "save_time": self.config.get("saveTime", "2000-01-01T00:00:00.0000000+08:00"),
            "path": f"USERARCHIVE\\{index:03d}.json"
        }

        # 确认覆盖
        if self.archive_data[index] is not None:
            reply = QMessageBox.question(
                self, '确认覆盖', f"存档 {index + 1} 已存在，确定覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # 保存到系统
        try:
            # 保存操作前临时移除监视
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            # 创建存档目录
            save_dir = os.path.dirname(self.main_window.save_dir)
            archive_dir = os.path.join(save_dir, "USERARCHIVE")
            # 先检查目录是否存在
            if not os.path.exists(archive_dir):
                # 创建目录（包含所有中间目录）
                os.makedirs(archive_dir)
                print(f"已创建存档目录：{archive_dir}")  # 调试用，正式版可移除

            # 保存具体存档文件
            with open(os.path.join(archive_dir, f"{index:03d}.json"), 'w', encoding='utf-8') as f:
                json.dump(self.main_window.config, f, ensure_ascii=False, indent=2)

            # 更新存档列表
            self.archive_data[index] = archive
            archive_path = os.path.join(save_dir, "user_archive.json")
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(self.archive_data, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "成功", f"存档位 {index + 1} 保存成功！")
            self.update_slot_display()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存存档失败: {str(e)}")
        finally:
            # 保存完成后重新添加监视
            self.load_archive_data()


if __name__ == "__main__":
    # 模拟主窗口类
    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.config = {}
            self.save_dir = ""

        def update_config(self, new_config):
            self.config = new_config
            print("配置已更新，字段数:", len(new_config))


    # 初始化应用
    app = QApplication(sys.argv)
    # 创建模拟主窗口
    main_window = MockMainWindow()
    main_window.save_dir = r"C:\Users\25285\AppData\LocalLow\DoubleCross\SultansGame\SAVEDATA\76561199041269113\auto_save.json"
    # 创建并显示界面
    info_page = SaveArchivePage(main_window)
    info_page.show()
    # 运行测试循环
    sys.exit(app.exec())
