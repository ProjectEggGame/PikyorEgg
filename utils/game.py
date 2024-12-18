"""
这里相当于游戏资源管理器。所有的游戏资源（列表）都在这里。
"""
from interact import interact
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
		self.window: Union['Window', None] = None
		self.floatWindow: Union['FloatWindow', None] = None  # 在主程序中初始化

	def tick(self) -> None:
		if self.window is not None:
			self.window.tick()
		if self.mainWorld is not None:
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
		renderer.begin(delta)
		if self.mainWorld is not None:
			self.mainWorld.passRender(delta)
		renderer.push()
		renderer.setScale(8)
		if self.window is not None:
			self.window.passRender(delta)
		renderer.pop()
		renderer.end()
	
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
