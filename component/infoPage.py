import json
import os
import sys

from PyQt6.QtCore import QFileSystemWatcher
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QApplication, QHBoxLayout, QLineEdit, QPushButton, \
    QFileDialog, QMessageBox, QGridLayout, QScrollArea


class InfoPage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.is_progressing = False  # 状态锁
        self.initUI()
        self.file_watcher = QFileSystemWatcher()  # 增加文件监视器
        self.file_watcher.fileChanged.connect(self.on_archive_changed)
        self.is_self_saving = False



    def _init_save_file(self):
        # 初始化默认存档路径
        temp_path = os.path.join(os.path.dirname(os.environ.get('APPDATA')), 'LocalLow')
        default_auto_save_file = os.path.join(temp_path, 'DoubleCross', 'SultansGame', 'SAVEDATA', '76561199041269113', 'auto_save.json')
        # 尝试加载默认存档路径
        try:
            self.load_archive(default_auto_save_file)
            # 更新存档文件展示框
            self.archive_path_edit.setText(default_auto_save_file)
        except Exception as e:
            QMessageBox.warning(self, "初始化错误", f"默认文件路径加载失败: {str(e)}")

    def initUI(self):
        layout = QVBoxLayout()

        # 存档路径选择区域
        archive_layout = QHBoxLayout()
        self.archive_path_edit = QLineEdit()
        self.archive_path_edit.setReadOnly(True)
        archive_btn = QPushButton("选择存档")
        archive_layout.addWidget(QLabel("存档文件："))
        archive_layout.addWidget(self.archive_path_edit)
        archive_layout.addWidget(archive_btn)
        archive_btn.clicked.connect(self._select_auto_save_file)
        layout.addLayout(archive_layout)

        # 增加手动刷新按钮
        self.refresh_btn = QPushButton("手动刷新")
        self.refresh_btn.setToolTip("强制重新加载当前存档文件")
        self.refresh_btn.clicked.connect(self.manual_refresh)
        layout.addWidget(self.refresh_btn)

        # 基本信息区域
        self.info_container = QWidget()
        self.info_layout = QGridLayout(self.info_container)
        self.info_layout.setColumnStretch(1, 1)  # 第二列可伸缩

        # 添加滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.info_container)

        # 字段显示配置（字段名: 显示名称）
        self.field_map = {
            "configId": "configId",
            "configVersion": "版本",
            "name": "主角名",
            "difficulty": "难度等级",
            "round": "回合数",
            "saveTime": "保存时间",
            "card_uid_index": "卡牌uid索引",
            "rite_uid_index": "仪式uid索引",
            "sudan_box_show": "左上角是否展示女术士的小盒子",
            "after_round_auto_sort": "回合后自动排序",
            "sudan_card_init_life": "苏丹卡持续回合",
            "sudan_redraw_count": "sudan_redraw_count(苏丹卡还剩几张的时候禁止交换)",
            "sudan_redraw_times_per_round": "重抽次数",
            "sudan_redraw_times": "已用重抽次数",
            "sudan_redraw_times_recovery_round": "重抽次数恢复回合",
            "wizard_first_show": "wizard_first_show",
            "success": "游戏是否达成结局",
            "over_reason": "游戏结局",
            "ithink_card": "俺寻思",
            "pins": "pins",
            "sudan_pool_cards": "sudan_pool_cards(进度展示里面的苏丹卡，增加或者删除都不会影响游戏进度)",
            "sudan_pool": "sudan_pool",
            "sudan_card_pool": "sudan_card_pool",
            "sudan_pool_pos": "sudan_pool_pos",
            "sudan_pool_init_count": "苏丹卡池初始数量",
            "sudan_card_show_times": "sudan_card_show_times",
            "sudan_remove_count": "sudan_remove_count",
            "counter": "counter",
            "random_cache": "random_cache",
            "only_cards": "only_cards",
            "only_rites": "only_rites",
            "event_status": "event_status",
            "delay_ops": "delay_ops",
            "end_rites": "各仪式完成的次数",
            "gen_cards": "卡牌生成次数",
            "gen_tags": "gen_tags",
            "timing_rounds": "timing_rounds",
            "auto_result_rites": "auto_result_rites",
            "notes": "notes",
            "once_new_rites_is_show": "once_new_rites_is_show",
            "cached_event": "cached_event",
            "BagIndex": "当前手牌页",
            "last_round_rite_data": "上回合仪式数据，方便一键上人",
            "rite_auto_result": "下一天的时候是否自动播放",
            "disable_auto_gen_sudan_card": "disable_auto_gen_sudan_card",
            "custom_rite_name": "custom_rite_name",
            "end_open": "进入结局，其实就是变成毛毯燃烧效果",
            "is_armageddon": "是否世界末日，世界末日就是大决战了",
            "armageddon_rite_id": "世界末日的时候剩下的那个仪式"
        }

        layout.insertWidget(2, scroll)  # 插入到路径选择区域下方

        # 添加保存按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存配置", self)
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    # 加载存档文件
    def load_archive(self, path: str):
        try:
            # 先移除旧监视（如果有）
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())

            with open(path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)
            # 调用主界面的更新方法
            self.main_window.update_config(new_config)
            # 添加新监视
            self.file_watcher.addPath(path)
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"无法加载存档文件: {str(e)}")

    # 选择存档文件
    def _select_auto_save_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择存档文件", "", "JSON文件 (*.json)"
        )
        if path:
            self.archive_path_edit.setText(path)
            self.load_archive(path)

    # 手动刷新按钮的点击处理
    def manual_refresh(self):
        current_path = self.archive_path_edit.text()
        if current_path:
            self.load_archive(current_path)
        else:
            QMessageBox.warning(self, "警告", "当前没有已加载的存档文件")

    # 更新基本信息
    def update_info(self):
        # 清空旧内容
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        config = self.main_window.config
        if not config:
            return

        row = 0
        for field, display_name in self.field_map.items():
            value = config.get(field, None)

            # 创建标签
            label = QLabel(f"{display_name}:")
            label.setStyleSheet("font-weight: bold;")

            display_value = str(value)

            value_label = QLabel(display_value)
            value_label.setStyleSheet("border: 1px solid #ddd; padding: 2px;")

            # 添加到布局
            self.info_layout.addWidget(label, row, 0)
            self.info_layout.addWidget(value_label, row, 1)
            row += 1

        # 添加弹性空间
        self.info_layout.setRowStretch(row, 1)

    # 当检测到文件变化时的处理
    def on_archive_changed(self, path):
        if self.is_self_saving:
            return

        # 检查状态锁
        if self.is_progressing:
            return
        # 由于某些编辑器保存时会先删后建，需要重新添加监视
        if not os.path.exists(path):
            self.file_watcher.addPath(path)
            return

        # 加锁
        self.is_progressing = True

        reply = QMessageBox.question(
            self,
            '文件已修改',
            '检测到存档文件已被外部修改，是否重新加载？\n（未保存的更改将会丢失）',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 添加小延迟确保文件写入完成
                QApplication.processEvents()
                self.load_archive(path)
                self.archive_path_edit.setText(path)
            except Exception as e:
                QMessageBox.critical(self, "刷新失败", f"重新加载失败: {str(e)}")

            finally:
                self.is_progressing = False  # 释放状态锁

    # 保存配置到原始文件
    def save_config(self):
        auto_save_path = self.archive_path_edit.text()
        if not auto_save_path:
            QMessageBox.warning(self, "错误", "请先选择存档文件路径")
            return

        try:
            self.is_self_saving = True
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())  # 临时移除文件监视
            # 创建确认对话框
            confirm_box = QMessageBox(self)
            confirm_box.setWindowTitle("确认保存")
            confirm_box.setText("此操作将覆盖原始文件，且不可恢复！\n ⚠️  确定要保存当前配置吗？")
            confirm_box.setIcon(QMessageBox.Icon.Question)

            # 添加按钮（确认+取消）
            confirm_button = confirm_box.addButton("确认", QMessageBox.ButtonRole.YesRole)
            cancel_button = confirm_box.addButton("取消", QMessageBox.ButtonRole.NoRole)
            confirm_box.setDefaultButton(confirm_button)

            # 显示对话框并等待用户选择
            confirm_box.exec()

            if confirm_box.clickedButton() == confirm_button:
                try:
                    with open(auto_save_path, 'w', encoding='utf-8') as asf:
                        json.dump(self.main_window.config, asf, indent=4, ensure_ascii=False)
                    # 显示保存成功提示
                    self.show_message("保存成功", "配置文件已成功保存！")
                except Exception as e:
                    self.show_message("保存失败", f"保存过程中发生错误：\n{str(e)}")
            else:
                print("用户取消保存操作")
        finally:
            self.is_self_saving = False
            if auto_save_path:
                self.file_watcher.addPath(auto_save_path)

    # 显示消息弹窗
    def show_message(self, title, content):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(content)
        msg.exec()

