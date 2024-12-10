from item.item import Item
from render.resource import Resource
from text import Description


class Egg(Item):
	def __init__(self, name: str, description: Description, texture: Resource):
		super().__init__(name, description, texture)
