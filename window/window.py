from pygame import Surface
from pygame.event import Event

from render.renderer import renderer
from utils import utils
from utils.game import game
from utils.text import RenderableString, Description
from utils.vector import Vector
from render.renderable import Renderable
from render.resource import Texture
from window.widget import Widget, Button, Location


class Window(Renderable):
	"""
	窗口。窗口始终占据整个屏幕，且默认同时只会显示game.window这一个窗口。
	请注意，渲染期间不可以改变Windows._widgets的元素个数，否则会导致循环迭代器失效。更改元素没有关系。
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
		self.backgroundColor: int = 0x88000000
	
	def renderBackground(self, delta: float) -> None:
		"""
		渲染背景。可以重写
		"""
		if self._texture is not None:
			self._texture.renderAtInterface(Vector(0, 0))
		else:
			head = self.backgroundColor & 0xff000000
			if head == 0:
				renderer.getCanvas().fill(0)
			else:
				color = self.backgroundColor & 0xffffff
				s = Surface(renderer.getCanvas().get_size())
				s.fill(color)
				s.set_alpha(head >> 24)
				renderer.getCanvas().blit(s, (0, 0))
	
	def render(self, delta: float, at=None) -> None:
		pass
	
	def passRender(self, delta: float, at: Vector | None = None) -> None:
		self.renderBackground(delta)
		for widget in self._widgets:
			widget.passRender(delta)
		self.render(delta)
	
	def passMouseMove(self, event: Event) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(event.pos[0], event.pos[1]):
				widget.passHover(event.pos[0], event.pos[1])
	
	def passMouseDown(self, event: Event) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(event.pos[0], event.pos[1]):
				widget.passMouseDown(event.pos[0], event.pos[1])
	
	def passMouseUp(self, event: Event) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(event.pos[0], event.pos[1]):
				widget.passMouseUp(event.pos[0], event.pos[1])
	
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
	
	def pauseGame(self) -> bool:
		"""
		可重写。有些窗口不需要暂停游戏，重写改False就行
		"""
		return True


class FloatWindow(Window):
	"""
	浮动窗口。窗口会根据鼠标位置自动移动。不用继承，想显示什么直接game.floatWindow.submit()就行了，目前只支持Text
	"""
	
	def __init__(self):
		super().__init__("Floater")
		self._rendering: list[RenderableString] = []
	
	def submit(self, contents: list[RenderableString]) -> None:
		"""
		把要显示的东西提交给FloatWindow
		:param contents: 要显示的RenderableString，每一行一个元素，每个RenderableString不要包含换行符
		"""
		self._rendering = contents


class StartWindow(Window):
	def __init__(self):
		super().__init__("Start")
		self._widgets.append(Button(Location.CENTER, 0, 0.05, 0.4, 0.08, RenderableString("\\2LINK START"), Description([RenderableString("开始游戏")]), textLocation=Location.CENTER))
		self._widgets[0].onMouseDown = lambda x, y: game.setWindow(None) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.15, 0.4, 0.08, RenderableString("\\2SHUT DOWN"), Description([RenderableString("结束游戏")]), textLocation=Location.CENTER))
		self._widgets[1].onMouseDown = lambda x, y: game.quit() or True
	
	def render(self, delta: float, at=None) -> None:
		super().render(delta)
		utils.trace('hello')
		size: Vector = renderer.getSize()
		renderer.renderString(RenderableString('\\0P\\1i\\3k\\4y\\0o\\1r \\3E\\4g\\0g\\1!'), int(size.x / 2), int(size.y / 4), 0xeeeeee00, Location.CENTER)
