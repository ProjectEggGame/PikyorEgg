from typing import overload, TYPE_CHECKING, Union

from pygame import Surface
from render.resource import resourceManager
from utils.element import Element
from utils.game import game
from utils.error import InvalidOperationException, neverCall
from utils.text import Description

if TYPE_CHECKING:
	from entity.entity import Entity
	from utils.vector import Vector, BlockVector
	from render.resource import Texture


class Block(Element):
	def __init__(self, name: str, description: 'Description', position: 'BlockVector', texture: 'Texture'):
		super().__init__(name, description, texture)
		self._position: 'BlockVector' = position.clone()
	
	def tick(self) -> None:
		pass
	
	def passTick(self) -> None:
		self.tick()
		pass
	
	def render(self, screen: Surface, delta: float, at: 'Vector | None') -> None:
		self.getTexture().renderAsBlock(screen, self._position.getVector())
	
	def canPass(self, entity: Union['Entity', None] = None) -> bool:
		"""
		必须重写。标志当前挡块是否允许特定实体通过
		:param entity: 要检测的实体
		"""
		neverCall(f"{type(self)}.canPass未重写")
		return True
	
	def getPosition(self) -> 'Vector':
		return self._position.getVector()
	
	def getBlockPosition(self) -> 'BlockVector':
		return self._position.clone()


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
	
	def __init__(self, name: str, description: 'Description', position: 'BlockVector', texture: 'Texture'):
		super().__init__(name, description, position, texture)
	
	def canPass(self, entity: Union['Entity', None] = None) -> bool:
		return True


class Wall(Block, ElementHolder):
	"""
	类墙方块
	"""
	
	def __init__(self, name: str, description: 'Description', position: 'BlockVector', texture: 'Texture'):
		super().__init__(name, description, position, texture)
	
	def canPass(self, entity: Union['Entity', None] = None) -> bool:
		return False


class GrassBlock(Ground, ElementHolder):
	def __init__(self, position: 'BlockVector'):
		super().__init__("草地", Description(["\\#FF4BAB25青色的草地"]), position, resourceManager.getOrNew('block/grass'))


class PathBlock(Ground, ElementHolder):
	def __init__(self, position: 'BlockVector'):
		super().__init__("草陉", Description(["\\#FF4BAB25土黄色的道路"]), position, resourceManager.getOrNew('block/path'))
	
	def render(self, screen: Surface, delta: float, at: 'Vector | None') -> None:
		if game.mainWorld is not None:
			pass
		self.getTexture().renderAsBlock(screen, self._position.getVector())


class ErrorBlock(Ground):
	def __init__(self, position: 'BlockVector'):
		super().__init__("错误方块", Description(["\\#FFEE0000错误方块"]), position, resourceManager.getOrNew('no_texture'))
