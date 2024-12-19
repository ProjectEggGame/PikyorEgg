from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from entity.entity import Entity


class EntityManager:
	def __init__(self):
		self._dic = {}
	
	def register(self, entityID: str, block: type):
		if entityID in self._dic:
			raise ValueError(f"注册一个已存在的实体ID: {entityID}")
		self._dic[entityID] = block
	
	def get(self, entityID: str) -> 'Entity':
		return self._dic[entityID]


entityManager: EntityManager = EntityManager()
