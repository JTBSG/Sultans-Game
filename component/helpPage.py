import sys

from PyQt6.QtWidgets import QTextEdit, QApplication


class HelpPage(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setReadOnly(True)
        self.setHtml("""
            <h1 style="color: #2c3e50;">苏丹的游戏存档编辑器 v1.0.0</h1>

            <h2>使用指南</h2>
            <div style="margin-left: 20px;">
                <h3>基本功能</h3>
                <ol>
                    <li>选择存档文件，查看基本信息</li>
                    <li>卡牌编辑界面功能：
                        <ul>
                            <li>展示牌桌上全部卡牌，包括手牌和隐藏的卡牌</li>
                            <li>使用搜索框快速定位卡牌</li>
                            <li>点击"新增卡牌"按钮添加新卡牌，在添加装备类卡牌时请设置其标签为”{'own': 1}“</li>
                            <li>表格直接编辑修改卡牌属性，修改前请确保您知晓卡牌各属性的格式和内容</li>
                            <li>点击查看详情按钮查看卡牌的默认信息</li>
                            <li>点击删除按钮删除对应卡牌</li>
                        </ul>
                    </li>
                </ol>

                <h3>注意事项，仔细阅读</h3>
                <ul>
                    <li>使用本软件前一定备份存档文件</li>
                    <li>默认存档文件路径示例："C:\\Users\\25285\\AppData\\LocalLow\\DoubleCross\\SultansGame\\SAVEDATA\\76561199041269113\\auto_save.json"</li>
                    <li>在游戏中点击”保存并退出按钮“后再使用本软件修改存档信息，否则游戏内会在存档文件中写入新内容导致您的修改无效</li>
                    <li>修改配置后请及时保存</li>        
                </ul>
                
                <h3>bugs/tips</h3>
                <ul>
                    <li>tip:虽然部分卡牌被设置为不可堆叠和唯一，但是依旧可以编辑其数量，只不过游戏会将多张合并为一张，且卡牌属性为多张属性之和</li>
                    <li>bug:目前软件区分是否为手牌的方式是根据其在背包中的位置，(0,0)和(0,1)位置的卡牌是隐藏卡牌，这就导致真正(0,1)位置的卡牌也被划分为了隐藏</li>
                    <li>bug:书籍如果被使用依旧会占用背包位置，导致被筛选为手牌中的卡，需要根据其标签中是否存在{'own': -1}进一步筛选，我这里懒得搞了</li>
                    <li>bug:如果先搜索了卡牌然后新增卡牌，可能导致页面布局改变，点击手动刷新即可恢复页面布局</li>
                    <li>tip:有任何问题欢迎与我联系</li>     
                </ul>
            </div>

            <hr>

            <h2>版权信息</h2>
            <div style="margin-left: 20px;">
                <p>开发者：JTBSG</p>
                <p>联系方式：2528575905@qq.com</p>
                <p>版本号：1.0.0 (2025-04)</p>
                <p>开源协议：MIT License</p>
            </div>

            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                h1 { border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #3498db; margin-top: 25px; }
                h3 { color: #2ecc71; }
                ul, ol { margin: 10px 0; }
                li { margin: 5px 0; }
            </style>
        """)
        self.setStyleSheet("""
            QTextEdit {
                padding: 20px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)


    # 启动主窗口
    main_window = HelpPage()
    main_window.show()
    sys.exit(app.exec())