from typing import TYPE_CHECKING, Union

from block.manager import blockManager
from render.resource import resourceManager
from utils.element import Element
from utils.error import InvalidOperationException, neverCall
from utils.text import Description, RenderableString
from utils.vector import Vector, BlockVector

if TYPE_CHECKING:
	from entity.entity import Entity
	from render.resource import Texture


class Block(Element):
	def __init__(self, blockID: str, name: str, description: 'Description', position: 'BlockVector', texture: 'Texture'):
		super().__init__(name, description, texture)
		self._position: 'BlockVector' = position.clone()
		self._blockID: str = blockID
		self._holding: list[Element] = []
	
	def tick(self) -> None:
		pass
	
	def passTick(self) -> None:
		self.tick()
		pass
	
	def render(self, delta: float, at: 'Vector | None') -> None:
		self.getTexture().renderAsBlock(self._position.getVector())
	
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
	
	def tryHold(self, block: Element) -> bool:
		"""
		可重写。尝试让该方块叠加一个新的元素
		:param block: 要叠加的元素
		:return: True - 能, False - 否
		"""
		return False
	
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
	
	def save(self) -> dict:
		return {
			'position': {
				'x': self._position.x,
				'y': self._position.y
			},
			'id': self._blockID,
			'holding': [b.save() for b in self._holding]
		}
	
	@classmethod
	def load(cls, d: dict, block: Union['Block', None] = None) -> 'Block':
		"""
		可以用来加载最基本的方块内容，主要是叠加方块
		:param d: 方块字典
		:param block: 默认None，用于识别手动或自动调用。手动调用必须传入方块
		"""
		if block is None:
			raise InvalidOperationException("Block类不应被直接加载。")
		block._holding = [blockManager.get(b['id']).load(b) for b in d['holding']]
		return block
	
	def __str__(self):
		return f"{type(self).__name__}({self.name})"
	
	def __repr__(self):
		return self.__str__()


class Ground(Block):
	"""
	类地面方块
	"""
	
	def __init__(self, blockID: str, name: str, description: 'Description', position: 'BlockVector', texture: 'Texture'):
		super().__init__(blockID, name, description, position, texture)
	
	def canPass(self, entity: Union['Entity', None] = None) -> bool:
		return True


class Wall(Block):
	"""
	类墙方块
	"""
	
	def __init__(self, blockID: str, name: str, description: 'Description', position: 'BlockVector', texture: 'Texture'):
		super().__init__(blockID, name, description, position, texture)

	def canPass(self, entity: Union['Entity', None] = None) -> bool:
		return False


class GrassBlock(Ground):
	def __init__(self, position: 'BlockVector'):
		super().__init__('nature.grass', "草地", Description([RenderableString("\\#FF4BAB25青色的草地")]), position, resourceManager.getOrNew('block/grass'))
	
	@classmethod
	def load(cls, d: dict, block=None) -> 'GrassBlock':
		ret = GrassBlock(BlockVector.load(d['position']))
		super().load(d, ret)
		return ret


class PathBlock(Ground):
	def __init__(self, position: 'BlockVector'):
		super().__init__('nature.path', "草径", Description([RenderableString("\\#FF4BAB25土黄色的道路")]), position, resourceManager.getOrNew('block/path'))
	
	@classmethod
	def load(cls, d: dict, block=None) -> 'PathBlock':
		ret = PathBlock(BlockVector.load(d['position']))
		super().load(d, ret)
		return ret


class FarmlandBlock(Ground):
	def __init__(self, position: 'BlockVector'):
		super().__init__('nature.farmland', "耕地", Description([RenderableString("\\#FF733706肥沃的泥土")]), position, resourceManager.getOrNew('block/farmland'))
	
	@classmethod
	def load(cls, d: dict, block=None) -> 'FarmlandBlock':
		ret = FarmlandBlock(BlockVector.load(d['position']))
		super().load(d, ret)
		return ret


class ErrorBlock(Ground):
	def __init__(self, position: 'BlockVector'):
		super().__init__('system.error', "错误方块", Description([RenderableString("\\#FFEE0000错误方块")]), position, resourceManager.getOrNew('no_texture'))
	
	@classmethod
	def load(cls, d: dict, block=None) -> 'ErrorBlock':
		ret = ErrorBlock(BlockVector.load(d['position']))
		super().load(d, ret)
		return ret


blockManager.register('nature.grass', GrassBlock)
blockManager.register('nature.path', PathBlock)
blockManager.register('nature.farmland', FarmlandBlock)
blockManager.register('system.error', ErrorBlock)
