import os.path
from typing import Union

import pygame
from pygame import Surface

from entity.manager import entityManager
from interact import interact
from render import font
from render.renderer import renderer
from save.save import Archive
from utils.game import game
from utils.text import RenderableString, Description
from utils.vector import Vector, BlockVector
from render.renderable import Renderable
from render.resource import Texture, resourceManager
from window.widget import Widget, Button, Location, ColorSet
from world.world import World, DynamicWorld, WitchWorld


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
		self.backgroundColor: int = 0x88000000
		self.lastOpen: Union['Window', None] = None
		self._backgroundPosition = Vector()
		self._backgroundLocation = Location.LEFT_TOP
	
	def setLastOpen(self, last: 'Window') -> 'Window':
		"""
		:param last: 上一次打开的窗口
		:return: 自身
		"""
		self.lastOpen = last
		return self
	
	def renderBackground(self, delta: float, at: BlockVector = BlockVector()) -> None:
		"""
		渲染背景。可以重写
		"""
		if self._texture is not None:
			w, h = renderer.getCanvas().get_size()
			pos = BlockVector()
			match self._backgroundLocation:
				case Location.LEFT_TOP:
					pos = BlockVector(int(w * self._backgroundPosition.x), int(h * self._backgroundPosition.y))
				case Location.LEFT:
					pos = BlockVector(int(w * self._backgroundPosition.x), int(h * self._backgroundPosition.y + (h - self._texture.getUiScaledSurface().get_size()[1] >> 1)))
				case Location.LEFT_BOTTOM:
					pos = BlockVector(int(w * self._backgroundPosition.x), int(h * self._backgroundPosition.y - self._texture.getUiScaledSurface().get_size()[1]))
				case Location.TOP:
					pos = BlockVector(int(w * self._backgroundPosition.x + (w - self._texture.getUiScaledSurface().get_size()[0] >> 1)), int(h * self._backgroundPosition.y))
				case Location.CENTER:
					pos = BlockVector(int(w * self._backgroundPosition.x + (w - self._texture.getUiScaledSurface().get_size()[0] >> 1)), int(h * self._backgroundPosition.y + (h - self._texture.getUiScaledSurface().get_size()[1] >> 1)))
				case Location.BOTTOM:
					pos = BlockVector(int(w * self._backgroundPosition.x + (w - self._texture.getUiScaledSurface().get_size()[0] >> 1)), int(h * self._backgroundPosition.y - self._texture.getUiScaledSurface().get_size()[1]))
				case Location.RIGHT:
					pos = BlockVector(int(w * self._backgroundPosition.x - self._texture.getUiScaledSurface().get_size()[0]), int(h * self._backgroundPosition.y))
				case Location.RIGHT_TOP:
					pos = BlockVector(int(w * self._backgroundPosition.x - self._texture.getUiScaledSurface().get_size()[0]), int(h * self._backgroundPosition.y + (h - self._texture.getUiScaledSurface().get_size()[1] >> 1)))
				case Location.RIGHT_BOTTOM:
					pos = BlockVector(int(w * self._backgroundPosition.x - self._texture.getUiScaledSurface().get_size()[0]), int(h * self._backgroundPosition.y - self._texture.getUiScaledSurface().get_size()[1]))
			self._texture.renderAtInterface(pos)
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
	
	def passMouseMove(self, x: int, y: int, buttons: tuple[int, int, int]) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(x, y):
				widget.passHover(x, y, buttons)
	
	def passMouseDown(self, x: int, y: int, buttons: tuple[int, int, int]) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(x, y):
				widget.passMouseDown(x, y, buttons)
	
	def passMouseUp(self, x: int, y: int, buttons: tuple[int, int, int]) -> None:
		for widget in self._widgets:
			if widget.isMouseIn(x, y):
				widget.passMouseUp(x, y, buttons)
	
	def passTick(self) -> None:
		for widget in self._widgets:
			widget.tick()
		self.tick()
	
	def tick(self) -> None:
		"""
		窗口的tick函数。可以重写。默认情况下，ESC会关闭当前窗口
		"""
		if interact.keys[pygame.K_ESCAPE].deal():
			game.setWindow(self.lastOpen)
	
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
		self._rendering: list[Description | None] = []
	
	def submit(self, contents: list[Description] | Description | None) -> None:
		"""
		把要显示的东西提交给FloatWindow
		:param contents: 要显示的RenderableString，每一行一个元素，每个RenderableString不要包含换行符
		"""
		if isinstance(contents, list):
			self._rendering = self._rendering + contents
		else:
			self._rendering.append(contents)
	
	def change(self, contents: list[Description] | Description | None) -> None:
		if contents is None:
			self._rendering = []
		elif isinstance(contents, list):
			self._rendering = contents
		else:
			self._rendering = [contents]
	
	def clear(self) -> None:
		self._rendering = []
	
	def empty(self) -> bool:
		return len(self._rendering) == 0
	
	def render(self, delta: float, at=None) -> None:
		if self._rendering is None:
			return
		info = []
		maximum = 0
		for r in self._rendering:
			for i in r.generate():
				present = i.lengthSmall()
				info.append((i, present))
				if present > maximum:
					maximum = present
		s = Surface((maximum, len(info) * font.realHalfHeight))
		s.fill((0x33, 0x33, 0x33))
		for i in range(len(info)):
			info[i][0].renderSmall(s, 0, i * font.realHalfHeight, 0xffffffff, 0x333333)
		x, y = interact.mouse.clone().subtract(0, len(info) * font.realHalfHeight).getTuple()
		if x < 0:
			x = 0
		elif x + maximum > renderer.getCanvas().get_width():
			x = renderer.getCanvas().get_width() - maximum
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
	exitColor = ColorSet()
	exitText = ColorSet()
	exitColor.active = 0xffee0000
	exitColor.hovering = 0xffee6666
	exitColor.inactive = 0xff660000
	exitColor.click = 0xffeeaaaa
	exitText.active = 0xff000000
	exitText.hovering = 0xff000000
	exitText.inactive = 0xff000000
	exitText.click = 0xff000000


class StartWindow(Window):
	def __init__(self):
		super().__init__("Start")
		self._texture = resourceManager.getOrNew('window/start')
		self._texture.adaptsMap(False)
		self._texture.adaptsUI(False)
		self._texture.adaptsSystem(True)
		
		def _0(x, y, b) -> bool:
			if b[0] == 1:
				game.setWindow(None)
				game.setWorld(DynamicWorld(0, 'DynamicWorld'))
			return True
		
		def _1(x, y, b) -> bool:
			if b[0] == 1:
				game.setWindow(None)
				game.setWorld(WitchWorld(0, 'WitchWorld'))
			return True
		
		self._widgets.append(Button(Location.CENTER, 0, 0.05, 0.4, 0.08, RenderableString("\\.00FCE8AD\\01LINK START"), Description([RenderableString("开始游戏")]), textLocation=Location.CENTER))
		self._widgets[0].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(PlotWindow().setLastOpen(self)) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.15, 0.4, 0.08, RenderableString("\\.00FCE8AD\\01LOAD"), Description([RenderableString("加载存档")]), textLocation=Location.CENTER))
		self._widgets[1].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(LoadWindow().setLastOpen(self)) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.25, 0.4, 0.08, RenderableString("\\.00FCE8AD\\01OPTIONS"), Description([RenderableString("设置")]), textLocation=Location.CENTER))
		self._widgets[2].onMouseDown = _1
		# self._widgets[2].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(SettingsWindow().setLastOpen(self)) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.35, 0.4, 0.08, RenderableString("\\.00FCE8AD\\01SHUT DOWN"), Description([RenderableString("结束游戏")]), textLocation=Location.CENTER))
		self._widgets[3].onMouseDown = lambda x, y, b: b[0] == 1 and game.quit() or True
		self._widgets[0].color = PresetColors.color
		self._widgets[1].color = PresetColors.color
		self._widgets[2].color = PresetColors.color
		self._widgets[3].color = PresetColors.color.clone()
		self._widgets[3].color.hovering = 0xffee0000
		self._widgets[0].textColor = PresetColors.textColor
		self._widgets[1].textColor = PresetColors.textColor
		self._widgets[2].textColor = PresetColors.textColor
		self._widgets[3].textColor = PresetColors.textColor.clone()
		self._widgets[3].textColor.hovering = 0xffeeeeee
	
	def render(self, delta: float, at=None) -> None:
		super().render(delta)
		size: BlockVector = renderer.getSize()
		renderer.renderString(RenderableString('\\.00FCE8AD\\00捡 蛋'), int(size.x / 2), int(size.y / 4), 0xff000000, Location.CENTER)
		renderer.renderString(RenderableString('\\.00FCE8AD\\02Pikyor Egg!'), int(size.x / 2), int(size.y / 4) + font.realFontHeight + 2, 0xff000000, Location.CENTER)
		renderer.renderString(RenderableString('\\.00FCE8AD\\02卵を拾って'), int(size.x / 2), int(size.y / 4) + font.realFontHeight + font.realFontHeight + 4, 0xff000000, Location.CENTER)
	
	def tick(self) -> None:
		interact.keys[pygame.K_ESCAPE].deal()  # 舍弃ESC消息


class LoadWindow(Window):
	def __init__(self):
		super().__init__("Load")
		self._widgets.append(Button(Location.LEFT_TOP, 0, 0, 0.09, 0.12, RenderableString('\\01Back'), Description([RenderableString("返回")]), Location.CENTER))
		self._widgets[0].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(self.lastOpen) or True
		if os.path.exists('user') and os.path.exists('user/archive'):
			def packer(s: str):
				string = s
				
				def _func(x, y, b):
					if b[0] == 1:
						archive = Archive(string)
						archive.read()
						game.setWorld(World.load(archive.dic))
						game.setWindow(None)
						archive.close()
					return True
				
				return _func
			
			dl = os.listdir('user/archive')
			for i in range(len(dl)):
				button = Button(Location.CENTER, 0, -0.4 + i * 0.1, 0.4, 0.08, RenderableString('\\10' + dl[i][:-5]), Description([RenderableString("加载此存档")]), Location.CENTER)
				button.onMouseDown = packer(dl[i][:-5])
				self._widgets.append(button)
	
	def tick(self) -> None:
		if interact.keys[pygame.K_ESCAPE].deal():
			game.setWindow(self.lastOpen or StartWindow())
	
	def setLastOpen(self, last: 'Window') -> 'Window':
		self.lastOpen = last
		if isinstance(last, StartWindow):
			self._texture = resourceManager.getOrNew('window/start')
			for w in self._widgets:
				w.color = PresetColors.color
				w.textColor = PresetColors.textColor
		return self


class PauseWindow(Window):
	def __init__(self):
		super().__init__("Pause")
		self._widgets.append(Button(Location.CENTER, 0, -0.3, 0.4, 0.08, RenderableString('\\01Continue'), Description([RenderableString("继续游戏")]), Location.CENTER))
		self._widgets[0].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(None) or True
		self._widgets.append(Button(Location.CENTER, 0, -0.2, 0.4, 0.08, RenderableString('\\01Settings'), Description([RenderableString("设置")]), Location.CENTER))
		self._widgets[1].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(SettingsWindow().setLastOpen(self)) or True
		self._widgets.append(Button(Location.CENTER, 0, -0.1, 0.4, 0.08, RenderableString('\\01Load'), Description([RenderableString("\\#ffee0000放弃保存\\r并读取存档")]), Location.CENTER))
		self._widgets[2].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(LoadWindow().setLastOpen(self)) or True
		self._widgets.append(Button(Location.CENTER, 0, 0, 0.4, 0.08, RenderableString('测试按钮'), Description([
			RenderableString("\\#ffee0000蠢蠢的狗"),
			RenderableString("\\#ffee55dd\\/ 只会直线行走"),
			RenderableString("\\#ffee7766 敌对单位"),
			RenderableString(f"\\#ffee6677 基础伤害 {8}"),
			RenderableString(f"\\#ffeedd66 搜索范围 {4}"),
		]), Location.CENTER))
		self._widgets[3].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(TaskWindow(3).setLastOpen(self)) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.1, 0.4, 0.08, RenderableString('\\01Save'), Description([RenderableString("保存游戏")]), Location.CENTER))
		
		def _4(x, y, b) -> bool:
			if b[0] == 1:
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
		
		def _5(x, y, b) -> bool:
			if b[0] == 1:
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
		
		self._widgets[5].color = PresetColors.exitColor
		self._widgets[5].textColor = PresetColors.exitText
		self._widgets[5].onMouseDown = _5
		self._widgets[5].onTick = _5t


class SettingsWindow(Window):
	def __init__(self):
		super().__init__("Settings")
		
		class Des(Description):
			def __init__(self):
				super().__init__()
			
			def generate(self) -> list['RenderableString']:
				return [
					RenderableString('\\#ff66ccee使用4:3屏幕比例 <'),
					RenderableString('\\#ff666666使用16:9屏幕比例')
				] if renderer.is4to3.get() else [
					RenderableString('\\#ff666666使用4:3屏幕比例'),
					RenderableString('\\#ff66ccee使用16:9屏幕比例 <')
				]
		
		self._widgets.append(Button(Location.LEFT_TOP, 0, 0, 0.09, 0.12, RenderableString('\\01Back'), Description([RenderableString("返回")]), Location.CENTER))
		self._widgets[0].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(self.lastOpen or (StartWindow() if game.getWorld() is None else None)) or True
		self._widgets.append(Button(Location.CENTER, 0, -0.3, 0.4, 0.08, RenderableString('\\01Screen \\#ff66ccee4:3\\r\\01 | 16:9' if renderer.is4to3.get() else '\\01Screen 4:3 | \\#ff66ccee16:9'), Des(), Location.CENTER))
		
		def _1(x, y, b):
			if b[0] == 1:
				renderer.is4to3.set(not renderer.is4to3.get())
				self._widgets[1].name = RenderableString('\\01Screen \\#ff66ccee4:3\\r\\01 | 16:9' if renderer.is4to3.getNew() else '\\01Screen 4:3 | \\#ff66ccee16:9')
			return True
		
		self._widgets[1].onMouseDown = _1
		from utils import utils
		
		class Des2(Description):
			def __init__(self):
				super().__init__()
				self._color = 0
			
			def generate(self) -> list['RenderableString']:
				return [
					RenderableString('\\#ff66cceeTRACE <' if utils.logLevel == 0 else 'Trace'),
					RenderableString('\\#ff66cceeDEBUG <' if utils.logLevel == 1 else 'Debug'),
					RenderableString('\\#ff66cceeINFO <' if utils.logLevel == 2 else 'Info'),
					RenderableString('\\#ff66cceeWARN <' if utils.logLevel == 3 else 'Warn'),
					RenderableString('\\#ff66cceeERROR <' if utils.logLevel == 4 else 'Error')
				]
		
		def _2(x, y, b):
			if b[0] == 1:
				if utils.logLevel == 4:
					utils.logLevel = 0
				else:
					utils.logLevel += 1
			elif b[2] == 1:
				if utils.logLevel == 0:
					utils.logLevel = 4
				else:
					utils.logLevel -= 1
			else:
				return True
			self._widgets[2].name = RenderableString(['\\01LogLevel \\#ff66cceeT\\r\\01|D|I|W|E', '\\01LogLevel T|\\#ff66cceeD\\r\\01|I|W|E', '\\01LogLevel T|D|\\#ff66cceeI\\r\\01|W|E', '\\01LogLevel T|D|I|\\#ff66cceeW\\r\\01|E', '\\01LogLevel T|D|I|W|\\#ff66cceeE'][utils.logLevel])
			return True
		
		self._widgets.append(Button(Location.CENTER, 0, -0.2, 0.4, 0.08, RenderableString(['\\01LogLevel \\#ff66cceeT\\r\\01|D|I|W|E', '\\01LogLevel T|\\#ff66cceeD\\r\\01|I|W|E', '\\01LogLevel T|D|\\#ff66cceeI\\r\\01|W|E', '\\01LogLevel T|D|I|\\#ff66cceeW\\r\\01|E', '\\01LogLevel T|D|I|W|\\#ff66cceeE'][utils.logLevel]), Des2()))
		self._widgets[2].onMouseDown = _2
		self._widgets.append(Button(Location.CENTER, -0.1, -0.1, 0.2, 0.08, RenderableString('\\01Show FPS' if renderer.displayFPS else '\\01Hide FPS'), Description([RenderableString("是否显示FPS")]), Location.CENTER))
		
		def _3(x, y, b):
			if b[0] == 1:
				renderer.displayFPS = not renderer.displayFPS
				self._widgets[3].name = RenderableString('\\01Show FPS' if renderer.displayFPS else '\\01Hide FPS')
			return True
		
		self._widgets[3].onMouseDown = _3
		self._widgets.append(Button(Location.CENTER, 0.1, -0.1, 0.2, 0.08, RenderableString('\\01Show TPS' if renderer.displayFPS else '\\01Hide TPS'), Description([RenderableString("是否显示TPS")]), Location.CENTER))
		
		def _4(x, y, b):
			if b[0] == 1:
				renderer.displayTPS = not renderer.displayTPS
				self._widgets[4].name = RenderableString('\\01Show TPS' if renderer.displayTPS else '\\01Hide TPS')
			return True
		
		self._widgets[4].onMouseDown = _4
		self._widgets.append(Button(Location.CENTER, -0.1, 0, 0.2, 0.08, RenderableString('\\01ScrollLock' if renderer.lockScroll else '\\01ScrollRelease'), Description([RenderableString("地图缩放锁定" if renderer.lockScroll else '滚动滚轮以改变地图缩放')]), Location.CENTER))
		
		def _5(x, y, b):
			if b[0] == 1:
				renderer.lockScroll = not renderer.lockScroll
				self._widgets[5].description = Description([RenderableString('地图缩放锁定' if renderer.lockScroll else '滚动滚轮以改变地图缩放')])
				self._widgets[5].name = RenderableString('\\01ScrollLock' if renderer.lockScroll else '\\01ScrollRelease')
			return True
		
		self._widgets[5].onMouseDown = _5
	
	def setLastOpen(self, last: 'Window') -> 'Window':
		self.lastOpen = last
		if isinstance(last, StartWindow):
			self._texture = resourceManager.getOrNew('window/start')
			for w in self._widgets:
				w.color = PresetColors.color
				w.textColor = PresetColors.textColor
		return self


class DeathWindow(Window):
	def __init__(self):
		super().__init__("You Died!")
		self._widgets.append(Button(Location.CENTER, 0, 0.1, 0.4, 0.08, RenderableString('\\01Restart'), Description([RenderableString("复活")]), Location.CENTER))
		self._widgets[0].onMouseDown = lambda x, y, b: b[0] == 1 and (game.setWindow(None) or game.getWorld().setPlayer(entityManager.get('player')(Vector()))) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.2, 0.4, 0.08, RenderableString('\\01Load'), Description([RenderableString("加载存档")]), Location.CENTER))
		self._widgets[1].onMouseDown = lambda x, y, b: b[0] == 1 and game.setWindow(LoadWindow().setLastOpen(self)) or True
		self._widgets.append(Button(Location.CENTER, 0, 0.3, 0.4, 0.08, RenderableString('\\01Exit'), Description([RenderableString('退出游戏')]), Location.CENTER))
		self._widgets[2].color = PresetColors.exitColor
		self._widgets[2].textColor = PresetColors.exitText
		self._widgets[2].onMouseDown = lambda x, y, b: b[0] == 1 and (game.setWorld(None) or game.setWindow(StartWindow())) or True
	
	def render(self, delta: float, at=None) -> None:
		w, h = renderer.getSize().getTuple()
		renderer.fill(0xffee0000, int(0.3 * w), int(0.3 * h), int(0.4 * w), int(0.2 * h))
		renderer.renderString(RenderableString("\\01\\#ff000000You are dead"), int(0.5 * w), int(0.4 * h), 0xff000000, Location.CENTER)
	
	def tick(self) -> None:
		interact.keys[pygame.K_ESCAPE].deal()


class TaskWindow(Window):
	def __init__(self, progress_X):
		super().__init__("Task")
		self._texture = resourceManager.getOrNew('window/task')
		self._texture.adaptsMap(False)
		self._texture.systemScaleOffset = 0.02
		self._texture.adaptsSystem(True)
		self._texture.renderAtInterface(BlockVector(30, 30))
		self.progress = progress_X
		self.looking = 2
		
		X = ["暂未解锁"] * 5
		for i in range(self.progress):
			X[i] = "解锁"
		
		self._widgets.append(Button(Location.CENTER, -0.25, -0.2, 0.12, 0.08, RenderableString("\\.00FCE8AD\\01TASK 1"), Description([RenderableString(X[0])]), textLocation=Location.CENTER))
		self._widgets.append(Button(Location.CENTER, -0.25, -0.1, 0.12, 0.08, RenderableString("\\.00FCE8AD\\01TASK 2"), Description([RenderableString(X[1])]), textLocation=Location.CENTER))
		self._widgets.append(Button(Location.CENTER, -0.25, 0, 0.12, 0.08, RenderableString("\\.00FCE8AD\\01TASK 3"), Description([RenderableString(X[2])]), textLocation=Location.CENTER))
		self._widgets.append(Button(Location.CENTER, -0.25, 0.1, 0.12, 0.08, RenderableString("\\.00FCE8AD\\01TASK 4"), Description([RenderableString(X[3])]), textLocation=Location.CENTER))
		self._widgets.append(Button(Location.CENTER, -0.25, 0.2, 0.12, 0.08, RenderableString("\\.00FCE8AD\\01TASK 5"), Description([RenderableString(X[4])]), textLocation=Location.CENTER))
		
		self._backgroundLocation = Location.CENTER
		color = PresetColors.color.clone()
		color.hovering = 0
		textColor = PresetColors.color.clone()
		textColor.hovering = 0xff777700
		textColor.active = 0xff000000
		self._widgets[0].color = color
		self._widgets[1].color = color
		self._widgets[2].color = color
		self._widgets[3].color = color
		self._widgets[4].color = color
		self._widgets[0].textColor = textColor
		self._widgets[1].textColor = textColor
		self._widgets[2].textColor = textColor
		self._widgets[3].textColor = textColor
		self._widgets[4].textColor = textColor
		
		def _1(x, y, b) -> bool:
			self.looking = 1
			return True
		
		def _2(x, y, b) -> bool:
			self.looking = 2
			return True
		
		def _3(x, y, b) -> bool:
			self.looking = 3
			return True
		
		def _4(x, y, b) -> bool:
			self.looking = 4
			return True
		
		def _5(x, y, b) -> bool:
			self.looking = 5
			return True
		
		if self.progress == 5:
			self._widgets[4].onMouseDown = _5
		if self.progress >= 4:
			self._widgets[3].onMouseDown = _4
		if self.progress >= 3:
			self._widgets[2].onMouseDown = _3
		if self.progress >= 2:
			self._widgets[1].onMouseDown = _2
		if self.progress >= 1:
			self._widgets[0].onMouseDown = _1
	
	def onResize(self) -> None:
		if renderer.is4to3.get():
			self._widgets[0].x = -0.33
			self._widgets[1].x = -0.33
			self._widgets[2].x = -0.33
			self._widgets[3].x = -0.33
			self._widgets[4].x = -0.33
		else:
			self._widgets[0].x = -0.25
			self._widgets[1].x = -0.25
			self._widgets[2].x = -0.25
			self._widgets[3].x = -0.25
			self._widgets[4].x = -0.25
		super().onResize()
	
	def render(self, delta: float, at=None) -> None:
		super().render(delta)
		if self.looking == 1:
			size: BlockVector = renderer.getSize()
			renderer.renderString(RenderableString('\\.00FCE8AD\\00任务1：'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), (size.y >> 1) - font.realFontHeight, 0xff000000, Location.BOTTOM)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00\\#ffee0000胸有大志，吃100颗米粒！'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), size.y >> 1, 0xff000000, Location.TOP)
		
		if self.looking == 2:
			size: BlockVector = renderer.getSize()
			renderer.renderString(RenderableString('\\.00FCE8AD\\00任务2：'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), (size.y >> 1) - font.realFontHeight, 0xff000000, Location.BOTTOM)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00\\#ffee0000年少有为，织鸡窝！'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), size.y >> 1, 0xff000000, Location.TOP)
		
		if self.looking == 3:
			size: BlockVector = renderer.getSize()
			renderer.renderString(RenderableString('\\.00FCE8AD\\00任务3：'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), (size.y >> 1) - font.realFontHeight, 0xff000000, Location.BOTTOM)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00老巫婆鸡，指点迷津！'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), size.y >> 1, 0xff000000, Location.BOTTOM)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00\\#ffee0000找到老巫婆鸡'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), size.y >> 1, 0xff000000, Location.TOP)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00并躲避狐狸的攻击'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), (size.y >> 1) + font.realFontHeight, 0xff000000, Location.TOP)
		
		if self.looking == 4:
			size: BlockVector = renderer.getSize()
			renderer.renderString(RenderableString('\\.00FCE8AD\\00任务4：'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), (size.y >> 1) - font.realFontHeight, 0xff000000, Location.BOTTOM)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00你需要获得公鸡的受精！'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), size.y >> 1, 0xff000000, Location.BOTTOM)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00所以你需要和别的母鸡斗争'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), size.y >> 1, 0xff000000, Location.TOP)
		
		if self.looking == 5:
			size: BlockVector = renderer.getSize()
			renderer.renderString(RenderableString('\\.00FCE8AD\\00任务5：'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), (size.y >> 1) - font.realFontHeight, 0xff000000, Location.BOTTOM)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00下蛋是一个漫长而艰辛的过程'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), size.y >> 1, 0xff000000, Location.BOTTOM)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00你要陪她聊天'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), size.y >> 1, 0xff000000, Location.TOP)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00让它开心起来'), int((0.58 if renderer.is4to3.get() else 0.56) * size.x), (size.y >> 1) + font.realFontHeight, 0xff000000, Location.TOP)
	
	def passRender(self, delta: float, at: Vector | None = None) -> None:
		s = Surface(renderer.getCanvas().get_size())
		s.fill(self.backgroundColor & 0xffffff)
		s.set_alpha(self.backgroundColor >> 24)
		renderer.getCanvas().blit(s, (0, 0))
		super().passRender(delta, at)
	
	def tick(self) -> None:
		super().tick()
		if interact.keys[pygame.K_m].deal():
			game.setWindow(self.lastOpen)


class PlotWindow(Window):
	def __init__(self):
		super().__init__("Plot")
		self._texture = resourceManager.getOrNew('window/plot')
		self._texture.systemScaleOffset = 0.0625
		self._texture.adaptsMap(False)
		self._texture.adaptsSystem(True)
		self.Sentence = 0
		
		def _0(x, y, b) -> bool:
			if self.Sentence < 8:
				self.Sentence += 1
			else:
				game.setWindow(None)
				game.setWorld(DynamicWorld(0, 'DynamicWorld'))
			return True
		
		def _1(x, y, b) -> bool:
			if b[0] == 1:
				game.setWindow(None)
				game.setWorld(DynamicWorld(0, 'DynamicWorld'))
			return True
		
		self._widgets.append(Button(Location.CENTER, 0, 0.05, 0.4, 0.08, RenderableString("\\.00FFFFFF\\01NEXT"), Description([RenderableString("继续")]), textLocation=Location.CENTER))
		self._widgets[0].onMouseDown = _0
		self._widgets.append(Button(Location.CENTER, 0, 0.15, 0.4, 0.08, RenderableString("\\.00FFFFFF\\01SKIP"), Description([RenderableString("跳过剧情")]), textLocation=Location.CENTER))
		self._widgets[1].onMouseDown = _1
		
		self._widgets[0].color = PresetColors.color
		self._widgets[1].color = PresetColors.color
		
		self._widgets[0].textColor = PresetColors.textColor
		self._widgets[1].textColor = PresetColors.textColor
	
	def render(self, delta: float, at=None) -> None:
		super().render(delta)
		size: BlockVector = renderer.getSize()
		if self.Sentence == 0:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00嘿！小家伙，你终于醒啦！'), int(size.x * 0.61), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00别怕，这里很安全。'), int(size.x * 0.61), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
		if self.Sentence == 1:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00你是一直体弱多病的小鸡，'), int(size.x * 0.62), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00没办法生蛋赚钱，'), int(size.x * 0.62), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
		if self.Sentence == 2:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00正因如此，你的主人不仅虐待你'), int(size.x * 0.62), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00还把你无情地抛弃在了荒草丛中。'), int(size.x * 0.62), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
		if self.Sentence == 3:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00当我发现你的时候，你浑身是伤'), int(size.x * 0.62), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00虚弱得连站都站不稳'), int(size.x * 0.62), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
		if self.Sentence == 4:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00咱们现在来到了一个新的村庄'), int(size.x * 0.62), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00这就是你以后生活的地方啦!'), int(size.x * 0.62), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
		if self.Sentence == 5:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00接下来的日子可能不太轻松'), int(size.x * 0.62), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00你要搜集草地上的米粒来填饱肚子'), int(size.x * 0.62), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
		if self.Sentence == 6:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00并尽可能多地收集树枝，'), int(size.x * 0.62), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00为自己建造一个鸡窝'), int(size.x * 0.62), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
		if self.Sentence == 7:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00在这个村庄里有很多邪恶的狐狸，'), int(size.x * 0.62), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00你一定要注意防范他们的攻击!'), int(size.x * 0.62), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
		if self.Sentence == 8:
			renderer.renderString(RenderableString('\\.00FCE8AD\\00你的最终目标是逆天改命，'), int(size.x * 0.62), int(size.y * 0.28), 0xffffffff, Location.CENTER)
			renderer.renderString(RenderableString('\\.00FCE8AD\\00生一个蛋，并孵出一只小鸡!'), int(size.x * 0.62), int(size.y * 0.28 + font.realFontHeight), 0xffffffff, Location.CENTER)
	
	def tick(self) -> None:
		if interact.keys[pygame.K_ESCAPE].deal():
			self.Sentence += 1
