from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
	from entity.entity import Entity


class EntityManager:
	def __init__(self):
		self.dic = {}
	
	def register(self, entityID: str, block: type):
		if entityID in self.dic:
			raise ValueError(f"注册一个已存在的实体ID: {entityID}")
		self.dic[entityID] = block
	
	def get(self, entityID: str):
		return self.dic[entityID]


entityManager: EntityManager = EntityManager()

