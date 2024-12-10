from pygame import Surface

from render.renderable import Renderable
from render.resource import Resource
from text import Description


class Element(Renderable):
	def __init__(self, name: str, description: Description, texture: Resource):
		super().__init__(texture)
		self.name = name
		self.description = description
