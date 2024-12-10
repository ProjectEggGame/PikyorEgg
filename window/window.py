from pygame import Surface

from interact.interact import Point
from render.renderable import Renderable
from render.resource import Resource
from window.widget import Widget


class Window(Renderable):
	def __init__(self, width: float, height: float, title: str, texture: Resource | None = None):
		super().__init__(texture)
		self._width: float = width
		self._height: float = height
		self._title: str = title
		self._widgets: list[Widget] = []
		
	def renderBackground(self, screen: Surface, delta: float) -> None:
		"""
		渲染背景。可以重写
		"""
		if self._texture is not None:
			self._texture.render(screen, delta, (1 - self._width) / 2, (1 - self._height) / 2, self._width, self._height)
		
	def passRender(self, screen: Surface, delta: float, at: Point | None = None) -> None:
		self.renderBackground(screen, delta)
		for widget in self._widgets:
			widget.passRender(screen, delta)
	

mainWindow: Window = Window(1.0, 1.0, '捡蛋')
