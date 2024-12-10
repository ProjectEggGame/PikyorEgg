from item.item import Item
from render.resource import Resource
from text import Description


class Egg(Item):
	def __init__(self, name: str, description: Description, texture: Resource):
		super().__init__(name, description, texture)
		

class A:
	def __init__(self, a: int):
		self.i = a


class B(A):
	def __init__(self, b: int):
