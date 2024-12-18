"""
这里相当于游戏资源管理器。所有的游戏资源（列表）都在这里。
"""
from render.renderer import renderer
from utils.error import NullPointerException
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
	from world.world import World
	from window.window import Window, FloatWindow


class Game:
	def __init__(self):
		self.mainWorld: Union['World', None] = None
		self.running: bool = True
		self.tickCount: int = 0
		self._window: Union['Window', None] = None
		self.floatWindow: Union['FloatWindow', None] = None  # 在主程序中初始化

	def tick(self) -> None:
		notPause: bool = True
		if self._window is not None:
			self._window.tick()
			notPause = not self._window.pauseGame()
		if self.mainWorld is not None and notPause:
			self.mainWorld.tick()
		self.processMouse()
	
	def render(self, delta: float) -> None:
		"""
		渲染所有内容。
		"""
		if not renderer.ready():
			raise NullPointerException('当前screen为None。')
		if delta > 1:
			# utils.warn(f'{delta = :.3f}')
			delta = 1
		if delta < 0:
			delta = 0
		renderer.begin(delta, self._window is None)
		if self.mainWorld is not None:
			self.mainWorld.passRender(delta)
		renderer.push()
		renderer.setScale(8)
		if self._window is not None:
			self._window.passRender(delta)
		renderer.pop()
		renderer.end()
	
	def setWindow(self, window: Union['Window', None]) -> None:
		self._window = window
		if window is not None:
			window.onResize()
		
	def getWindow(self) -> Union['Window', None]:
		return self._window
	
	def quit(self) -> None:
		self.running = False
	
	def readConfig(self, config: dict[str, any]) -> None:
		"""
		读取配置文件。
		"""
		pass
	
	def writeConfig(self) -> dict[str, any]:
		return {}
	
	def processMouse(self):
		pass


game = Game()
