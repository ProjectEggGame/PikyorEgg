from pygame import Surface

from utils.vector import Vector
from render.renderable import Renderable
from render.resource import Texture
from window.widget import Widget


class Window(Renderable):
	"""
	窗口。窗口始终占据整个屏幕，且默认同时只会显示game.window这一个窗口。
	请注意，渲染期间不可以改编Windows._widgets的元素个数，否则会导致循环迭代器失效。更改元素没有关系。
	self._catches是捕捉控件。如果它不是None，那么所有的消息都会最先传给它，然后再根据返回值传给其他控件。
	"""
	def __init__(self, title: str, texture: Texture | None = None):
		"""
		:param title: 窗口标题
		:param texture: 窗口背景纹理，默认None
		"""
		super().__init__(texture)
		self._title: str = title
		self._widgets: list[Widget] = []
		self._catches: Widget | None = None
		
	def renderBackground(self, screen: Surface, delta: float) -> None:
		"""
		渲染背景。可以重写
		"""
		if self._texture is not None:
			self._texture.renderAtInterface(screen, Vector(0, 0))
		
	def passRender(self, screen: Surface, delta: float, at: Vector | None = None) -> None:
		self.renderBackground(screen, delta)
		for widget in self._widgets:
			widget.passRender(screen, delta)
			
	def tick(self) -> None:
		"""
		窗口的tick函数。可以重写，但是不要忘了令所有widgets和catches也tick一下
		"""
		if self._catches is not None:
			self._catches.tick()
		for widget in self._widgets:
			widget.tick()
	
	def onResize(self) -> None:
		"""
		窗口大小改变时的回调。可以重写，但是不要忘了令所有widgets也onResize一下
		"""
		for widget in self._widgets:
			widget.onResize()
