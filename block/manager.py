from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from block.block import Block


class BlockManager:
	def __init__(self):
		self._dic = {}
		
	def register(self, blockID: str, block: type):
		if blockID in self._dic:
			raise ValueError(f"注册一个已存在的方块ID: {blockID}")
		self._dic[blockID] = block
	
	def get(self, blockID: str) -> 'Block':
		return self._dic[blockID]


blockManager: BlockManager = BlockManager()
