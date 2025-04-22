import json
import json5
from datetime import datetime
from typing import Any, List, Dict, Optional

from datetime import datetime, timedelta, timezone
from dateutil import parser  # 需要安装python-dateutil包


def convert_datetime(iso_str: str) -> datetime:
    """增强型日期转换函数"""
    # 预处理微秒位数
    if '.' in iso_str:
        date_part, time_part = iso_str.split('.', 1)
        time_part, tz_part = time_part.split('+', 1) if '+' in time_part else (
            time_part.split('-', 1) if '-' in time_part else (time_part, '')
        )

        # 处理7位微秒（保留6位，第7位四舍五入）
        microseconds = time_part[:7].ljust(7, '0')[:7]
        rounded = str(round(int(microseconds) / 10)).zfill(6)
        iso_str = f"{date_part}.{rounded[:6]}+{tz_part}"

    # 使用dateutil的宽松解析器
    return parser.isoparse(iso_str)

class Card:
    """卡牌对象的封装"""

    def __init__(self, data: Dict[str, Any]):
        self.uid = data['uid']
        self.id = data['id']
        self.count = data['count']  # 卡牌数量
        self.life = data['life']  # 卡牌在游戏中已存在的回合数
        self.rareup = data['rareup']

        # 容器类型
        self.tag = data['tag']
        self.equip_slots = data['equip_slots']
        self.equips = data['equips']

        # 背包配置
        self.bag = data['bag']  # 该卡牌在背包中的第几行
        self.bagpos = data['bagpos']  # 该卡牌在背包中的位置

        # 自定义内容
        self.custom_name = data['custom_name']
        self.custom_text = data['custom_text']

    def to_dict(self):
        return {
            "uid": self.uid,
            "id": self.id,
            "count": self.count,
            "life": self.life,
            "rareup": self.rareup,
            "tag": self.tag,
            "equip_slots": self.equip_slots,
            "equips": self.equips,
            "bag": self.bag,
            "bagpos": self.bagpos,
            "custom_name": self.custom_name,
            "custom_text": self.custom_text
        }


class Rite:
    """仪式对象的封装"""

    def __init__(self, data: Dict[str, Any]):

        # 保留原始数据
        self.raw_data = data

        # 基础标识字段
        self.uid = data['uid']
        self.id = data['id']  # 避免与内置id冲突

        # 布尔状态字段
        self.new_born = data.get('new_born', False)
        self.is_show = data.get('is_show', True)
        self.start = data.get('start', False)

        # 数值型配置
        self.start_round = data.get('start_round', 0)
        self.start_life = data.get('start_life', 0)
        self.life = data.get('life', 0)

        # 嵌套卡片引用（处理null值）
        self.related_cards = [
            Card(card_data) if card_data else None
            for card_data in data.get('cards', [])
        ]

        # 自定义内容
        self.custom_name = data.get('custom_name', '')

    def to_dict(self):
        return {
            "uid": self.uid,
            "id": self.id,
            "new_born": self.new_born,
            "is_show": self.is_show,
            "start": self.start,
            "start_round": self.start_round,
            "start_life": self.start_life,
            "life": self.life,
            "cards": self.related_cards,
            "custom_name": self.custom_name
        }

class NoteItem:
    """笔记项数据结构"""
    def __init__(self,
                 type: int,
                 id: int,
                 uid: int,
                 count: int):
        self.type = type       # 类型标识
        self.id = id           # 关联ID
        self.uid = uid         # 唯一标识
        self.count = count     # 计数

    @classmethod
    def from_dict(cls, data: dict) -> 'NoteItem':
        return cls(
            type=data['type'],
            id=data['id'],
            uid=data['uid'],
            count=data['count']
        )

    def to_dict(self):
        return {
            "type": self.type,
            "id": self.id,
            "uid": self.uid,
            "count": self.count
        }


class JSONConfig:
    """JSON配置的面向对象封装"""

    def __init__(self, data: Dict[str, Any]):
        # 基础字段
        self.config_id = data['configId']
        self.config_version = data['configVersion']
        self.name = data['name']
        self.difficulty = data['difficulty']
        self.round = data['round']  # 回合数

        # 日期字段转换
        self.save_time = convert_datetime(data['saveTime'])  # 文件保存时间

        # 索引配置
        self.card_uid_index = data['card_uid_index']
        self.rite_uid_index = data['rite_uid_index']

        self.sudan_box_show = data['sudan_box_show']
        self.after_round_auto_sort = data['after_round_auto_sort']
        self.sudan_card_init_life = data['sudan_card_init_life']

        self.sudan_redraw_count = data['sudan_redraw_count'],
        self.sudan_redraw_times_per_round = data['sudan_redraw_times_per_round'],
        self.sudan_redraw_times = data['sudan_redraw_times'],
        self.sudan_redraw_times_recovery_round = data['sudan_redraw_times_recovery_round']

        self.wizard_first_show = data['wizard_first_show']
        self.success = data['success']

        self.over_reason = data['over_reason']
        self.ithink_card = data['ithink_card']

        # cards列表，每回合的所有牌都会出现在cards中
        self.cards = [Card(card_data) for card_data in data['cards']]

        # 转换rites列表
        self.rites = [Rite(rite_data) for rite_data in data.get('rites', [])]

        # pins字段
        self.pins = data.get('pins', [])

        # sudan_pool_cards字段
        self.sudan_pool_cards = data.get('sudan_pool_cards', [])

        # sudan_pool字段
        self.sudan_pool = data.get('sudan_pool', "")

        # sudan_card_pool字段
        self.sudan_card_pool = [Card(pool_data) for pool_data in data.get('sudan_card_pool', [])]

        # sudan_pool_pos字段
        self.sudan_pool_pos = data.get('sudan_pool_pos', [])

        # sudan_pool_init_count字段
        self.sudan_pool_init_count = data['sudan_pool_init_count']

        # sudan_card_show_times字段
        self.sudan_card_show_times = data.get('sudan_card_show_times', {})

        # sudan_remove_count字段
        self.sudan_remove_count = data.get('sudan_remove_count')

        # 新增计数器系统，其中7000060表示回合数，7000008表示治理家业的时候放入空置宅邸的回合数，每三个回合获得五金币并清零，7100005是灵视，7000559是新月是否升级过的计数器
        self.counter = data.get('counter', {})  # 类型: Dict[str, int] (格式: {计数器ID: 计数值})

        self.global_counter_cacher = data.get('global_counter_cacher', {})

        # 随机数缓存
        self.random_cache = data.get('random_cache', {})  # 类型: Dict (具体结构根据业务逻辑定)

        # 唯一卡牌限制列表
        self.only_cards = data.get('only_cards', [])  # 类型: List[int] (卡牌ID数组)

        # 唯一仪式限制列表
        self.only_rites = data.get('only_rites', [])  # 类型: List[int] (仪式ID数组)

        # 事件状态字典（事件ID: 是否完成），true则表示事件已经完成，可以再次触发，false表示事件还没有完成，不能再次触发
        self.event_status = data.get('event_status', {})
        # 类型: Dict[str, bool] (格式: {"事件ID": 布尔状态})

        # 延迟操作队列
        self.delay_ops = data.get('delay_ops', [])
        # 类型: List (具体操作结构需根据业务逻辑定义)

        # 结束仪式数据（仪式ID: 关联数值）
        self.end_rites = data.get('end_rites', {})
        # 类型: Dict[str, int] (格式: {"仪式ID": 数值})

        # 生成卡牌记录（卡牌ID: 生成次数）
        self.gen_cards = data.get('gen_cards', {})
        # 类型: Dict[str, int] (格式: {"卡牌ID": 生成次数})

        # 生成标签统计（标签名: 数值），统计标签数量
        self.gen_tags = data.get('gen_tags', {})
        # 类型: Dict[str, int] 示例: {"physique": 176}

        # 定时回合配置（事件ID: 触发回合）
        self.timing_rounds = data.get('timing_rounds', {})
        # 类型: Dict[str, int] 示例: {"530001100": 105}

        # 自动完成仪式列表
        self.auto_result_rites = data.get('auto_result_rites', [])
        # 类型: List (具体元素结构需根据业务定义)

        # 嵌套笔记系统（二维结构）
        self.notes = [
            [NoteItem.from_dict(item) for item in sublist]
            for sublist in data.get('notes', [[]])
        ]  # 类型: List[List[NoteItem]]

        # 一次性新仪式展示状态
        self.once_new_rites_is_show = data.get('once_new_rites_is_show', {})
        # 类型: Dict[str, bool] (格式: {"仪式ID": 是否展示})

        # 事件缓存队列
        self.cached_event = data.get('cached_event', [])
        # 类型: List (具体元素结构根据业务逻辑定义)

        # 背包索引标识
        self.BagIndex = data.get('BagIndex', 0)
        # 类型: int (默认值0)

        # 上回合仪式数据（嵌套字典结构）
        self.last_round_rite_data = data.get('last_round_rite_data', {})
        # 类型: Dict[str, Dict[str, Dict[str, Any]]]
        # 格式: {"仪式ID": {"阶段标识": {"id": 卡牌ID, "count": 数量}}}

        # 自动化配置标志
        self.rite_auto_result = data.get('rite_auto_result', False)  # 类型: bool
        self.disable_auto_gen_sudan_card = data.get('disable_auto_gen_sudan_card', False)  # 类型: bool

        # 自定义内容
        self.custom_rite_name = data.get('custom_rite_name', {})  # 类型: Dict[str, str]
        self.end_open = data.get('end_open', False)  # 类型: bool
        self.is_armageddon = data.get('is_armageddon', False)  # 类型: bool
        self.armageddon_rite_id = data.get('armageddon_rite_id', 0)  # 类型: int

    def to_dict(self):
        return {
            # 基础字段
            "configId": self.config_id,
            "configVersion": self.config_version,
            "name": self.name,
            "difficulty": self.difficulty,
            "round": self.round,
            "saveTime": self.save_time,
            "card_uid_index": self.card_uid_index,
            "rite_uid_index": self.rite_uid_index,
            "sudan_box_show": self.sudan_box_show,
            "after_round_auto_sort": self.after_round_auto_sort,
            "sudan_card_init_life": self.sudan_card_init_life,
            "sudan_redraw_count": self.sudan_redraw_count,
            "sudan_redraw_times_per_round": self.sudan_redraw_times_per_round,
            "sudan_redraw_times": self.sudan_redraw_times,
            "sudan_redraw_times_recovery_round": self.sudan_redraw_times_recovery_round,
            "wizard_first_show": self.wizard_first_show,
            "success": self.success,
            "over_reason": self.over_reason,
            "ithink_card": self.ithink_card,
            "cards": [card.to_dict() for card in self.cards],
            "rites": [rite.to_dict() for rite in self.rites],
            "pins": self.pins,
            "sudan_pool_cards": self.sudan_pool_cards,
            "sudan_pool": self.sudan_pool,
            "sudan_card_pool": self.sudan_card_pool,
            "sudan_pool_pos": self.sudan_pool_pos,
            "sudan_pool_init_count": self.sudan_pool_init_count,
            "sudan_card_show_times": self.sudan_card_show_times,
            "sudan_remove_count": self.sudan_remove_count,
            "counter": self.counter,
            "global_counter_cacher": self.global_counter_cacher,
            "random_cache": self.random_cache,
            "only_cards": self.only_cards,
            "only_rites": self.only_rites,
            "event_status": self.event_status,
            "delay_ops": self.delay_ops,
            "end_rites": self.end_rites,
            "gen_cards": self.gen_cards,
            "gen_tags": self.gen_tags,
            "timing_rounds": self.timing_rounds,
            "auto_result_rites": self.auto_result_rites,
            "notes": [
                [item.to_dict() for item in sublist]
                for sublist in self.notes
            ],
            "once_new_rites_is_show": self.once_new_rites_is_show,
            "cached_event": self.cached_event,
            "BagIndex": self.BagIndex,
            "last_round_rite_data": self.last_round_rite_data,
            "rite_auto_result": self.rite_auto_result,
            "disable_auto_gen_sudan_card": self.disable_auto_gen_sudan_card,
            "custom_rite_name": self.custom_rite_name,
            "end_open": self.end_open,
            "is_armageddon": self.is_armageddon,
            "armageddon_rite_id": self.armageddon_rite_id
        }


def load_config(file_path: str) -> JSONConfig:
    """
    加载并解析JSON配置文件
    :param file_path: JSON文件路径
    :return: 结构化配置对象
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        return JSONConfig(raw_data)

def save_config(config, file_path):
    """保存配置到原始文件"""
    try:
        config_dict = config.to_dict()

        # 转换datetime格式（如果需要）
        if hasattr(config, 'save_time'):
            config_dict["saveTime"] = str(config.save_time)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)

        # 显示保存成功提示
        print("保存成功", "配置文件已更新")
    except Exception as e:
        print("保存失败", f"错误信息：{str(e)}")

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    for row, card in enumerate(raw_data.get('cards')):
        print(row)
        print(card)
        print('OK')

class TagDataManager:
    """标签元数据管理器"""

    def __init__(self, tag_db_path: str):
        self.tag_db = self._load_tag_db(tag_db_path)
        self.tag_data_mapping = self._build_tag_data_mapping()
        self.unknown_tag = {
            "id": -1,
            "name": "未知标签",
            "code": "",
            "type": "",
            "text": "",
            "tips": "",
            "resource": "",
            "can_add": -1,
            "can_visible": -1,
            "can_inherit": -1,
            "can_nagative_and_zero": -1,
            "fail_tag": [],
            "tag_vanishing": -1,
            "tag_sfx": "",
            "tag_rank": -1,
            "attributes": {}
        }

    def _load_tag_db(self, path: str) -> Dict:
        """加载标签数据库"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json5.load(f)
        except FileNotFoundError:
            print(f"标签数据库文件 {path} 未找到")
            return {}
        except Exception as e:
            print(f"加载标签数据库时发生错误: {e}")
            return {}

    def _build_tag_data_mapping(self) -> Dict[str, dict]:
        """构建标签名字到标签数据的映射"""
        return {
            name: data
            for name, data in self.tag_db.items()
        }

    def get_tag_data(self, tag_name: str) -> dict:
        return self.tag_data_mapping.get(tag_name, self.unknown_tag)



# 使用示例
if __name__ == "__main__":
    tag_mgr = TagDataManager(
        "E:\\SteamLibrary\\steamapps\\common\\Sultan's Game\\Sultan's Game_Data\\StreamingAssets\\config\\tag.json")

    load_data("C:\\Users\\25285\\AppData\\LocalLow\\DoubleCross\\SultansGame\\SAVEDATA\\76561199041269113"
                         "\\auto_save.json")

    config = load_config("C:\\Users\\25285\\AppData\\LocalLow\\DoubleCross\\SultansGame\\SAVEDATA\\76561199041269113"
                         "\\auto_save.json")

    # 访问示例
    print('OK')
    print(f"配置名称: {config.name}")
    print(f"保存时间: {config.save_time.isoformat()}")

    save_config(config, "C:\\Users\\25285\\Desktop\\新建文件夹 (2)\\1auto_save.json")
