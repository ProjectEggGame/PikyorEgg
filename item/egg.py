from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from render.resource import Texture
	from utils.text import Description

from item.item import Item


class Egg(Item):
	def __init__(self, name: str, description: 'Description', texture: 'Texture'):
		super().__init__(name, description, texture)
