import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from render.resource import Texture
	from utils.text import Description
from utils.element import Element


class Breakable:
	def __init__(self, durability: int, maxDurability: int = -1):
		"""
		:param durability: 耐久
		:param maxDurability: 最大耐久。默认-1。为-1时，视为maxDurability = durability
		"""
		self.durability = durability
		self.maxDurability = durability if maxDurability == -1 else maxDurability
	
	def fix(self, amount: int) -> None:
		"""
		维修一个工具，不需要额外判断是否超过了最大耐久。
		:param amount: 修复的耐久
		"""
		self.durability += amount
		if self.maxDurability > 0:
			self.durability = min(self.durability, self.maxDurability)


class WeaponLike(Breakable):
	def __init__(self, damage: float, durability: int, maxDurability: int = -1):
		"""
		WeaponLike已经继承了Breakable，不需要额外继承Breakable
		:param damage: 武器的基础伤害
		:param durability: 武器耐久
		:param maxDurability: 武器最大耐久，默认-1
		"""
		super().__init__(durability, maxDurability)
		self._damage = damage
	
	def getDamage(self) -> float:
		"""
		获取基础伤害
		"""
		return self._damage
	
	def onDamage(self) -> None:
		"""
		造成伤害时执行函数
		"""
		pass
	
	def onBreak(self) -> None:
		"""
		消耗耐久时执行函数
		"""
		pass


class FoodQuality(enum.Enum):
	F__KING_AWFUL = (-50, '原地去世')
	TERRIBLE = (-10, '难以下咽')
	POOR = (-2, '勉强能吃')
	AVERAGE = (0, '一般一般')
	GOOD = (3, '味道还行')
	GREAT = (5, '好吃爱吃')
	EXCELLENT = (8, '美味佳肴')
	PERFECT = (12, '完美无瑕！')
	SUPERIOR = (18, '百年难遇！')
	SUPREME = (25, '千载难逢！！')
	INSANE = (32, '万世孤独！！！')


class FoodLike:
	def __init__(self, saturation: float, quality: FoodQuality, extraRegeneration: float = 0):
		"""
		:param saturation: 能填充的饱食度
		:param quality: 食物质量
		:param extraRegeneration: 除了质量提供的生命恢复以外，物品提供的额外回复。默认0
		"""
		self._saturation = saturation
		self._quality = quality
		self._regeneration = extraRegeneration
	
	def getSaturation(self) -> float:
		"""
		:returns: 食物能够填充的饱食度
		"""
		return self._saturation
	
	def getRegeneration(self) -> float:
		"""
		:returns: 食物带来的总生命恢复
		"""
		return self._regeneration + self._quality.value[0]
	
	def getQuality(self) -> FoodQuality:
		"""
		:returns: 食物品质
		"""
		return self._quality
	
	def getExtraRegeneration(self) -> float:
		"""
		:returns: 食物额外回复属性
		"""
		return self._quality.value[0]


class Item(Element):
	def __init__(self, name: str, description: 'Description', texture: 'Texture'):
		"""
		:param name: 物品名称
		:param description: 物品描述，字符串列表
		"""
		super().__init__(name, description, texture)
		self.name = name
		self.description = description


class Weapon(Item, WeaponLike):
	def __init__(self, name: str, description: 'Description', texture: 'Texture'):
		"""
		:param name: 武器名称
		:param description: 武器描述，字符串列表
		"""
		super().__init__(name, description, texture)


class ItemStack:
	def __init__(self, item: Item, count: int = 1):
		"""
		物品堆。“物品”是抽象概念、描述，没有“数量”一说；
		游戏中持有的只能是“物品堆”，物品堆有“数量”一说
		:param item: 描述物品
		:param count: 数量，不超过64，不小于1
		:raises ValueError
		"""
		if count < 1:
			raise ValueError("正在创建总和小于1的物品堆。")
		if count > 64:
			raise ValueError("正在创建总和超过64的物品堆。")
		self.item = item
		self.count = count


class Inventory:
	def __init__(self, count: int):
		"""
		物品栏，相当于能够表示count个“物品堆”槽位
		:param count: 能容纳的物品堆的数量，不小于1
		:raises ValueError
		"""
		if count < 1:
			raise ValueError("正在创建容量小于1的物品栏。")
		self._items = [None for _ in range(count)]
		self._count = count
	
	def get(self, offset: int) -> ItemStack | None:
		"""
		获取对应位置的物品
		:param offset: 相当于list[offset]
		:returns: 对应的物品，有可能是None
		"""
		if self._count <= offset:
			raise IndexError(f"尝试获取容纳{self._count}个物品的容器的第{offset}偏移的物品")
		return self._items[offset]


class BackPack(Inventory):
	def __init__(self):
		"""
		玩家物品栏。一般不会用到，因为在Player里面已经进行了初始化。
		这个构造函数不应当被调用。
		"""
		super().__init__(32)
