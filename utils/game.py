"""
这里相当于游戏资源管理器。所有的游戏资源（列表）都在这里。
"""
import pygame

from interact import interact
from render.renderer import renderer
from utils.error import NullPointerException
from typing import TYPE_CHECKING, Union

from utils.sync import SynchronizedStorage
from utils.text import RenderableString
from utils.vector import Vector

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
		self.processMouse()  # 此处以下是额外键盘功能
		if interact.keys[pygame.K_ESCAPE].deal():
			from window.window import PauseWindow
			self.setWindow(PauseWindow())
		if interact.keys[pygame.K_SPACE].deal() and self._mainWorld is not None:
			if renderer.getCameraAt() is None:
				renderer.cameraAt(self._mainWorld.getPlayer())
				self.hud.sendMessage(RenderableString('\\#cc66ccee视角锁定'))
			elif renderer.cameraOffset.lengthManhattan() == 0:
				self.hud.sendMessage(RenderableString('\\#cc00cc00视角解锁'))
				renderer.cameraAt(None)
			else:
				self.hud.sendMessage(RenderableString('\\#cc7755ee居中锁定'))
				renderer.cameraOffset.set(0, 0)
		if interact.keys[pygame.K_e].deal():
			if self._mainWorld.getPlayer() is not None:
				from window.ingame import StatusWindow
				self.setWindow(StatusWindow())
		self.tickCount += 1
	
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
		self.hud.lastDisplayHealth = 0
		self.hud.lastDisplayHunger = 0
		renderer.cameraAt(None if world is None else world.getPlayer())
	
	def getWorld(self) -> Union['World', None]:
		return self._mainWorld
	
	def quit(self) -> None:
		self.running = False
	
	def processMouse(self, event: pygame.event.Event | None = None):
		if self._mainWorld is not None and self._window.get() is None:
			self.floatWindow.clear()
			loc = interact.mouse.clone().subtract(renderer.getCenter()).getVector().divide(renderer.getMapScale()).add(renderer.getCamera().get())
			target1, target2 = None, None
			targetDist1, targetDist2 = 1, 1
			for e in (self._mainWorld.getEntities() + [self._mainWorld.getPlayer()]):
				if (dist := e.getPosition().add(e.getTexture().getOffset()).distanceManhattan(loc)) < 0.5 and dist < targetDist2:
					if dist < targetDist1:
						target1, target2 = e, target1
						targetDist1, targetDist2 = dist, targetDist1
					else:
						target2 = e
						targetDist2 = dist
			if target2 is not None:
				self.floatWindow.submit(target1.description)
				self.floatWindow.submit(target2.description)
			elif target1 is not None:
				self.floatWindow.submit(target1.description)
			block = self._mainWorld.getBlockAt(loc.getBlockVector())
			if block is not None:
				self.floatWindow.submit(block.getDescription())
		if event is not None:
			if event.buttons[2] == 1 and self._window.get() is None:
				renderer.cameraOffset.subtract(Vector(event.rel[0], event.rel[1]).divide(renderer.getMapScale()))


game = Game()
