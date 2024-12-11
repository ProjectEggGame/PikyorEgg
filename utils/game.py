"""
这里相当于游戏资源管理器。所有的游戏资源（列表）都在这里。
"""

from render.renderer import renderer
from utils.error import NullPointerException
from window.window import Window
from world.world import World


class Game:
	def __init__(self):
		self.mainWorld: World | None = World.generateDefaultWorld()
		self.running: bool = True
		self.tickCount: int = 0
		self.window: Window | None = None
	
	def tick(self) -> None:
		if self.mainWorld is not None:
			self.mainWorld.tick()
	
	def render(self, delta: float) -> None:
		"""
		渲染所有内容。
		"""
		if not renderer.ready():
			raise NullPointerException('当前screen为None。')
		renderer.begin()
		if self.mainWorld is not None:
			self.mainWorld.passRender(renderer.getCanvas(), delta)
		renderer.push()
		renderer.setScale(8)
		if self.window is not None:
			self.window.passRender(renderer.getCanvas(), delta)
		renderer.pop()
		renderer.end()


game = Game()
