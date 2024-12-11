from typing import overload

from pygame import Surface

from entity.entity import Entity
from interact.interact import Vector
from item.item import Item
from render.renderer import renderer
from render.resource import Resource, resourceManager
from utils.element import Element
from text import Description
from utils.error import InvalidOperationException, CodeBasedException


class Block(Element):
	def __init__(self, name: str, description: Description, position: Vector, texture: Resource):
		super().__init__(name, description, texture)
		self._position: Vector = position
	
	def tick(self) -> None:
		pass
	
	def render(self, screen: Surface, delta: float, at: Vector | None) -> None:
		renderer.push()
		renderer.offset(20, 20)
		self.getTexture().renderAtMap(screen, self._position)
		renderer.pop()
	
	@overload
	def canPass(self) -> bool:
		"""
		必须重写。志当前方块上是否允许实体经过
		"""
		raise CodeBasedException(f"{type(self)}.canPass未重写")
	
	@overload
	def canPass(self, entity: Entity) -> bool:
		"""
		必须重写。标志当前挡块是否允许特定实体通过
		:param entity: 要检测的实体
		"""
		return self.canPass()
	
	def canPass(self, *args) -> None:
		"""
		如果你调用了这个函数，请检查参数类型是否正确
		"""
		raise InvalidOperationException(f"canPass调用类型错误。接受到的类型：{type(args)}")


class ElementHolder:
	"""
	方块上如果可以叠加其他的方块，那么继承这个类。注意，叠加元素可能还可以继续层叠元素
	"""
	
	def __init__(self):
		self._holding: list[Element] = []
	
	def tryHold(self, block: Element) -> bool:
		"""
		可重写。尝试让该方块叠加一个新的元素
		:param block: 要叠加的元素
		:return: True - 能, False - 否
		"""
		if len(self._holding) > 0:
			return False
		else:
			return True
	
	def holdAppend(self, element: Element) -> None:
		"""
		可重写。强行叠加一个元素。失败的时候可能会直接抛错
		:param element: 要叠加的元素
		"""
		if not self.tryHold(element):
			raise InvalidOperationException("无法叠加元素")
		self._holding.append(element)
	
	def getHolding(self) -> list[Element]:
		"""
		获取当前方块上叠加的元素
		"""
		return self._holding
	
	def holdRemove(self, element: Element) -> bool:
		"""
		删除一个叠加的方块
		:param element: 对象本身
		:return: 是否成功删除了方块
		"""
		if self._holding.__contains__(element):
			self._holding.remove(element)
			return True
		else:
			return False
		
		
class Ground(Block):
	"""
	类地面方块
	"""
	def __init__(self, name: str, description: Description, position: Vector, texture: Resource):
		super().__init__(name, description, position, texture)
	
	def canPass(self) -> bool:
		return True


class Wall(Block, ElementHolder):
	"""
	类墙方块
	"""
	def __init__(self, name: str, description: Description, position: Vector, texture: Resource):
		super().__init__(name, description, position, texture)
	
	def canPass(self) -> bool:
		return False


class GrassBlock(Ground, ElementHolder):
	def __init__(self, position: Vector):
		super().__init__("Grass Block", Description(["\\#FF4BAB25青色的草地"]), position, resourceManager.getOrNew('block/grass'))
