import os.path

import pygame
from pygame import Surface

from entity.entity import Player
from interact import interact
from render import font
from render.renderer import renderer
from save.save import Archive
from utils.game import game
from utils.text import RenderableString, Description
from utils.vector import Vector
from render.renderable import Renderable
from render.resource import Texture, resourceManager
from window.widget import Widget, Button, Location, ColorSet
from world.world import World


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
		self.render(delta)
		for widget in reversed(self._widgets):
			widget.passRender(delta)
	
	def passMouseMove(self, x: int, y: int) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(x, y):
				widget.passHover(x, y)
	
	def passMouseDown(self, x: int, y: int) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(x, y):
				widget.passMouseDown(x, y)
	
	def passMouseUp(self, x: int, y: int) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(x, y):
				widget.passMouseUp(x, y)
	
	def passTick(self) -> None:
		if self._catches is not None:
			self._catches.tick()
		for widget in self._widgets:
			widget.tick()
		self.tick()
	
	def tick(self) -> None:
		"""
		窗口的tick函数。可以重写。默认情况下，ESC会关闭当前窗口
		"""
		if interact.keys[pygame.K_ESCAPE].deal():
			game.setWindow(None)
	
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


class FloatWindow(Renderable):
	"""
	浮动窗口。窗口会根据鼠标位置自动移动。不用继承，想显示什么直接game.floatWindow.submit()就行了，目前只支持Text
	"""
	
	def __init__(self):
		super().__init__(None)
		self._rendering: Description | None = None
	
	def submit(self, contents: Description | None) -> None:
		"""
		把要显示的东西提交给FloatWindow
		:param contents: 要显示的RenderableString，每一行一个元素，每个RenderableString不要包含换行符
		"""
		self._rendering = contents
	
	def render(self, delta: float, at=None) -> None:
		if self._rendering is None:
			return
		info = []
		maximum = 0
		for i in self._rendering.generate():
			present = i.lengthSmall()
			info.append((i, present))
			if present > maximum:
				maximum = present
		s = Surface((maximum, len(info) * font.fontHeight >> 1))
		s.fill((60, 60, 60))
		for i in range(len(info)):
			info[i][0].renderSmall(s, 0, i * font.fontHeight >> 1, 0xffffffff)
		x, y = interact.mouse.clone().subtract(0, len(info) * font.fontHeight >> 1).getTuple()
		if x < 0:
			x = 0
		if y < 0:
			y = 0
		renderer.getCanvas().blit(s, (x, y))


class PresetColors:
	color = ColorSet()
	textColor = ColorSet()
	textColor.active = 0xff000000
	textColor.hovering = 0xffFCE8AD
	textColor.inactive = 0xff666666
	textColor.click = 0xff000000
	color.active = 0
	color.hovering = 0xff000000
	color.inactive = 0
	color.click = 0


class StartWindow(Window):
	def __init__(self):
		super().__init__("Start")
		self._texture = resourceManager.getOrNew('window/start')
		self._texture.adaptsMap(False)
		self._texture.adaptsUI(False)
		self._texture.adaptsSystem(True)
		
		def _0(*_) -> bool:
			game.setWindow(None)
			game.setWorld(World.generateDefaultWorld())
			game.getWorld().addPlayer(Player('Test'))
			return True
		
		self._widgets.append(Button(Location.CENTER, 0, 0.05, 0.4, 0.08, RenderableString("\\.00FCE8AD\\01LINK START"), Description([RenderableString("开始游戏")]), textLocation=Location.CENTER))
		self._widgets[0].onMouseDown = _0
		self._widgets.append(Button(Location.CENTER, 0, 0.15, 0.4, 0.08, RenderableString("\\.00FCE8AD\\01LOAD"), Description([RenderableString("加载存档")]), textLocation=Location.CENTER))
		self._widgets[1].onMouseDown = lambda x, y: game.setWindow(LoadWindow()) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.25, 0.4, 0.08, RenderableString("\\.00FCE8AD\\01SHUT DOWN"), Description([RenderableString("结束游戏")]), textLocation=Location.CENTER))
		self._widgets[2].onMouseDown = lambda x, y: game.quit() or True
		self._widgets[0].color = PresetColors.color
		self._widgets[1].color = PresetColors.color
		self._widgets[2].color = PresetColors.color
		self._widgets[0].textColor = PresetColors.textColor
		self._widgets[1].textColor = PresetColors.textColor
		self._widgets[2].textColor = PresetColors.textColor
	
	def render(self, delta: float, at=None) -> None:
		super().render(delta)
		size: Vector = renderer.getSize()
		renderer.renderString(RenderableString('\\.00FCE8AD\\00捡 蛋'), int(size.x / 2), int(size.y / 4), 0xff000000, Location.CENTER)
		renderer.renderString(RenderableString('\\.00FCE8AD\\02Pikyor Egg!'), int(size.x / 2), int(size.y / 4) + font.fontHeight + 2, 0xff000000, Location.CENTER)
		renderer.renderString(RenderableString('\\.00FCE8AD\\02卵を拾って'), int(size.x / 2), int(size.y / 4) + font.fontHeight + font.fontHeight + 4, 0xff000000, Location.CENTER)
	
	def tick(self) -> None:
		interact.keys[pygame.K_ESCAPE].deal()  # 舍弃ESC消息


class LoadWindow(Window):
	def __init__(self):
		super().__init__("Load")
		self._texture = resourceManager.getOrNew('window/start')
		self._widgets.append(Button(Location.LEFT_TOP, 0, 0, 0.09, 0.12, RenderableString('Back'), Description([RenderableString("返回")]), Location.CENTER))
		self._widgets[0].onMouseDown = lambda x, y: game.setWindow(StartWindow()) or True
		self._widgets[0].color = PresetColors.color
		self._widgets[0].textColor = PresetColors.textColor
		if os.path.exists('user') and os.path.exists('user/archive'):
			dl = os.listdir('user/archive')
			for i in range(len(dl)):
				button = Button(Location.CENTER, 0, -0.4 + i * 0.1, 0.4, 0.08, RenderableString('\\10' + dl[i][:-5]), Description([RenderableString("加载此存档")]), Location.CENTER)
				button.color = PresetColors.color
				button.textColor = PresetColors.textColor
				
				def _func(*_):
					archive = Archive(dl[i][:-5])
					archive.read()
					game.setWorld(World.load(archive.dic))
					game.setWindow(None)
					archive.close()
					return True
				
				button.onMouseDown = _func
				self._widgets.append(button)
	
	def tick(self) -> None:
		if interact.keys[pygame.K_ESCAPE].deal():
			game.setWindow(StartWindow())


class PauseWindow(Window):
	def __init__(self):
		super().__init__("Pause")
		self._widgets.append(Button(Location.CENTER, 0, -0.3, 0.4, 0.08, RenderableString('\\01Continue'), Description([RenderableString("继续游戏")]), Location.CENTER))
		self._widgets[0].onMouseDown = lambda x, y: game.setWindow(None) or True
		self._widgets.append(Button(Location.CENTER, 0, -0.2, 0.4, 0.08, RenderableString('\\01Settings'), Description([RenderableString("设置")]), Location.CENTER))
		self._widgets[1].onMouseDown = lambda x, y: game.setWindow(None) or True
		self._widgets.append(Button(Location.CENTER, 0, -0.1, 0.4, 0.08, RenderableString('\\01???'), Description([RenderableString("？？？")]), Location.CENTER))
		self._widgets[2].onMouseDown = lambda x, y: game.setWindow(None) or True
		self._widgets.append(Button(Location.CENTER, 0, 0, 0.4, 0.08, RenderableString('\\01???'), Description([RenderableString("？？？")]), Location.CENTER))
		self._widgets[3].onMouseDown = lambda x, y: game.setWindow(None) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.1, 0.4, 0.08, RenderableString('\\01Save'), Description([RenderableString("保存游戏")]), Location.CENTER))
		
		def _4(*_) -> bool:
			self._widgets[4].description = Description([RenderableString("\\#ffFCE8AD保存中……")])
			game.getWorld().save()
			self._widgets[4].description = Description([RenderableString("\\#ffFCE8AD保存完成")])
			return True
		
		self._widgets[4].onMouseDown = _4
		
		class Des(Description):
			def __init__(self):
				super().__init__()
				self.exitClick = 0
				self.exitTime = 0
				self.content = [[RenderableString('\\.ffee0000退出游戏'), RenderableString('\\#ffee0000\\.00ff0000不要忘了保存！')], [RenderableString('\\#ffee0000\\.00ff0000再按一次退出游戏'), RenderableString('\\#ffee0000\\.00ff0000不要忘了保存！！！')]]
			
			def generate(self) -> list['RenderableString']:
				return self.content[self.exitClick]
		
		des = Des()
		self._widgets.append(Button(Location.CENTER, 0, 0.2, 0.4, 0.08, RenderableString('\\01Exit'), des, Location.CENTER))
		
		def _5(*_) -> bool:
			if des.exitClick == 1:
				game.setWorld(None)
				game.setWindow(StartWindow())
				return True
			des.exitTime = 20
			des.exitClick = 1
			return True
		
		def _5t():
			if des.exitTime == 1:
				des.exitClick = 0
			des.exitTime -= 1
		
		self._widgets[5].color.active = 0xffee0000
		self._widgets[5].color.hovering = 0xffee6666
		self._widgets[5].color.inactive = 0xff660000
		self._widgets[5].color.click = 0xffeeaaaa
		self._widgets[5].textColor.active = 0xff000000
		self._widgets[5].textColor.hovering = 0xff000000
		self._widgets[5].textColor.inactive = 0xff000000
		self._widgets[5].textColor.click = 0xff000000
		self._widgets[5].onMouseDown = _5
		self._widgets[5].onTick = _5t
