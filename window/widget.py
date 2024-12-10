from render.renderable import Renderable
from render.resource import Resource
from text import Description


class Widget(Renderable):
	def __init__(self, x: float, y: float, width: float, height: float, name: str, description: Description, texture: Resource):
		super().__init__(texture)
		self.x: float = x
		self.y: float = y
		self.width: float = width
		self.height: height = height
		self.name: str = name
		self.description: Description = description
	
	
