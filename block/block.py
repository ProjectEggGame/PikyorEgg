from pygame import Surface

from interact.interact import Point
from render.renderer import renderer
from render.resource import Resource, resourceManager
from utils.element import Element
from text import Description


class Block(Element):
	def __init__(self, name: str, description: Description, position, texture: Resource):
		super().__init__(name, description, texture)
		self._position: Point = position
	
	def tick(self) -> None:
		pass
	
	def render(self, screen: Surface, delta: float, at: Point | None) -> None:
		renderer.push()
		renderer.offset(20, 20)
		self.getTexture().renderCenter(screen, self._position)
		renderer.pop()


class GrassBlock(Block):
	def __init__(self, position: Point):
		super().__init__("Grass Block", Description(["\\#FF4BAB25青色的草地"]), position, resourceManager.getOrNew('block/grass'))
	
