"""
这里相当于游戏资源管理器。所有的游戏资源（列表）都在这里。
"""
from render.renderer import renderer
from utils.error import NullPointerException
from typing import TYPE_CHECKING, Union

from utils.sync import SynchronizedStorage

if TYPE_CHECKING:
	from world.world import World
	from window.window import Window, FloatWindow
	from window.hud import Hud


class Game:
	def __init__(self):
		self._mainWorld: Union['World', None] = None
		self.running: bool = True
		self.tickCount: int = 0
		self._window: SynchronizedStorage[Union['Window', None]] = SynchronizedStorage[Union['Window', None]](None)
		self.floatWindow: Union['FloatWindow', None] = None  # 在主程序中初始化
		self.hud: Union['Hud', None] = None

	def tick(self) -> None:
		notPause: bool = True
		if self._window.get() is not None:
			self._window.get().passTick()
			notPause = not self._window.get().pauseGame()
		self._window.apply(self._window.getNew())
		if self._mainWorld is not None and notPause:
			self._mainWorld.tick()
		self.processMouse()
	
	def render(self, delta: float) -> None:
		"""
		渲染所有内容。
		"""
		if not renderer.ready():
			raise NullPointerException('当前screen为None。')
		if delta > 1:
			delta = 1
		elif delta < 0:
			delta = 0
		elif self._window.get() is not None and self._window.get().pauseGame():
			delta = 1
		renderer.begin(delta, self._window.get() is None)
		if self._mainWorld is not None:
			self._mainWorld.passRender(delta)
		self.hud.render(delta)
		if self._window.get() is not None:
			self._window.get().passRender(delta)
		if self.floatWindow is not None:
			self.floatWindow.render(delta)
		renderer.end()
	
	def setWindow(self, window: Union['Window', None]) -> None:
		self._window.set(window)
		if window is not None:
			window.onResize()
		
	def getWindow(self) -> Union['Window', None]:
		return self._window.getNew()
	
	def setWorld(self, world: Union['World', None]) -> None:
		self._mainWorld = world
		renderer.cameraAt(None)
	
	def getWorld(self) -> Union['World', None]:
		return self._mainWorld
		
	def quit(self) -> None:
		self.running = False
	
	def readConfig(self, config: dict[str, any]) -> None:
		"""
		读取配置文件。
		"""
		pass
	
	@staticmethod
	def writeConfig() -> dict[str, any]:
		return {}
	
	def processMouse(self):
		pass


game = Game()
