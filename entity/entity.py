import item.item as item
from render.resource import Resource
from utils.element import Element
from text import Description


class Entity(Element):
	def __init__(self, name: str, description: Description, texture: Resource | None, speed: float = 0):
		"""
		:param name: 实体名称
		:param description: 实体描述，字符串列表
		"""
		super().__init__(name, description, texture)
		self._x: float = 0
		self._y: float = 0
		self._speed: float = speed
	
	def passTick(self) -> None:
		"""
		内置函数，不应当额外调用，不应当随意重写。
		重写时必须注意调用父类的同名函数，防止遗漏逻辑。
		"""
		pass
	
	def tick(self) -> None:
		"""
		交由具体类重写
		"""
		pass
	
	def getX(self) -> float:
		"""
		:return: x坐标
		"""
		return self._x
	
	def getY(self) -> float:
		"""
		:return: y坐标
		"""
		return self._y


class Player(Entity):
	def __init__(self):
		"""
		创建玩家
		"""
		super().__init__("player", Description(), None)
		self.health = 100
		self.maxHealth = 100
		self.name = 'Player'
		self.inventory = item.BackPack()

	
