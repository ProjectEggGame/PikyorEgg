from collections import deque
from typing import Union, TYPE_CHECKING

from interact import interact
from utils import utils

if TYPE_CHECKING:
	from entity.entity import Entity

import pygame
from pygame import Surface
from utils.vector import Vector
from utils.error import IllegalStatusException, InvalidOperationException
from utils.sync import SynchronizedStorage, Boolean


# from utils.game import game
# 不可以import game，否则会导致循环导入


class RenderStack:
	def __init__(self, other: 'RenderStack | None' = None):
		if other is None:
			self.offset: Vector = Vector(0, 0)
			self.scale: float = 1
			self.padding: int = 10
		else:
			self.offset = other.offset
			self.scale = other.scale
			self.padding = other.padding


class Renderer:
	def __init__(self):
		super().__init__()
		self._screen: Surface | None = None
		self._canvas: Surface | None = None
		self._size: tuple[float, float] = (0, 0)
		self._canvasSize: Vector = Vector()
		self._is4to3: SynchronizedStorage[bool] = SynchronizedStorage[bool](True)
		self._isRendering: bool = False
		self._renderStack: deque[RenderStack] = deque[RenderStack]()
		self._renderStack.append(RenderStack())
		self._camera: SynchronizedStorage[Vector] = SynchronizedStorage[Vector](Vector(10.0, 10.0))
		self._cameraAt: Union['Entity', None] = None
		self._systemScale: float = 16.0  # 方块基本是16px
		self._customScale: float = 1.0
		self._customMapScale: float = 16.0
		self._scaleChanged: bool = True
		self._offset: Vector = Vector(0, 0)
		self._presentOffset: Vector = Vector(0, 0)
	
	def ready(self) -> bool:
		"""
		检查渲染器状态是否良好
		"""
		return self._canvas is not None and self._screen is not None
	
	def setScreen(self, screen: Surface) -> None:
		"""
		设置屏幕Surface
		"""
		self._screen = screen
		self._size = screen.get_size()
		if self._is4to3.get():
			if self._size[0] / self._size[1] > 4 / 3:
				self._offset = Vector((self._size[0] - float(self._size[1]) * 4 / 3) / 2, 0)
			elif self._size[0] / self._size[1] < 4 / 3:
				self._offset = Vector(0, (self._size[1] - float(self._size[0]) / 4 * 3) / 2)
			else:
				self._offset = Vector(0, 0)
		else:
			if self._size[0] / self._size[1] > 16 / 9:
				self._offset = Vector((self._size[0] - float(self._size[1]) * 16 / 9) / 2, 0)
			elif self._size[0] / self._size[1] < 16 / 9:
				self._offset = Vector(0, (self._size[1] - float(self._size[0]) / 16 * 9) / 2)
			else:
				self._offset = Vector(0, 0)
		self._canvasSize = Vector(self._size[0], self._size[1]).subtract(self._offset).subtract(self._offset)
		self._canvas = Surface(self._canvasSize.getTuple())
		self._updateOffset()
	
	def cameraAt(self, entity: 'Entity') -> 'Entity':
		e = self._cameraAt
		self._cameraAt = entity
		return e
	
	def begin(self, delta: float) -> None:
		"""
		仅在game.render中调用
		"""
		if self._isRendering:
			raise IllegalStatusException("尝试开始绘制，但是绘制已经开始。")
		if interact.scroll.peekScroll() != 0:
			newScale = self._customScale * (0.8 ** interact.scroll.dealScroll())
			if utils.flesseq(newScale, 0.5):
				newScale = 0.5
			elif utils.fgreatereq(newScale, 8):
				newScale = 8
			if newScale != self._customScale:
				self._customScale = newScale
				self._scaleChanged = True
		self._isRendering = True
		# begin apply sync
		if self._cameraAt is None:
			self._camera.apply(self._camera.getNew().clone())
		else:
			self._camera.get().set(self._cameraAt.getPosition() + self._cameraAt.getVelocity() * delta)
			self._camera.getNew().set(self._camera.get().clone())
		self._is4to3.apply(self._is4to3.getNew())
		# end apply sync
		self._screen.fill(0)
		self._canvas.fill(0)
	
	def _updateOffset(self) -> None:
		self._presentOffset = self._offset + self._renderStack[-1].offset
	
	def end(self) -> None:
		"""
		只在渲染帧结束时调用
		:return:
		"""
		if not self._isRendering:
			raise IllegalStatusException("尝试结束绘制，但是绘制尚未开始。")
		self._screen.blit(self._canvas, self._offset.getTuple())
		pygame.display.flip()
		if len(self._renderStack) != 1:
			raise IllegalStatusException("渲染帧结束时有栈没有弹出。请检查是否缺失了renderer.pop()")
		self._isRendering = False
	
	def assertRendering(self) -> None:
		"""
		该函数可能抛出错误。这个错误不应被手动捕捉，因为抛出这个错误说明是代码逻辑上出现了问题。一些操作应当在渲染时进行，但是在非渲染时刻进行了这一操作，就会报错
		:raises: InvalidOperationError
		"""
		if self._isRendering:
			return
		raise InvalidOperationException('操作需要在渲染时进行。当前未进行渲染。')
	
	def assertNotRendering(self) -> None:
		"""
		该函数可能抛出错误。这个错误不应被手动捕捉，因为抛出这个错误说明是代码逻辑上出现了问题。一些操作应当在非渲染时刻进行，但是在渲染时刻进行了这一操作，就会报错
		:raises: InvalidOperationError
		"""
		if not self._isRendering:
			return
		raise InvalidOperationException('操作需要在非渲染时进行。当前正在渲染。')
	
	def getSize(self) -> Vector:
		return self._canvasSize
	
	def getCanvas(self) -> Surface:
		return self._canvas
	
	def getScreen(self) -> Surface:
		return self._screen
	
	def getCamera(self) -> Vector:
		return self._camera.getNew()
	
	def render(self, src: Surface, dst: Surface, sx: int | float, sy: int | float, sw: int | float, sh: int | float, dx: int | float, dy: int | float, dw: int | float | None = None, dh: int | float | None = None) -> None:
		"""
		渲染目标。以下全部是int类型的px单位。请尽量避免使用这个方法，因为这个方法的效率比较低下。
		:param src: 源Surface
		:param dst: 目标Surface
		:param sx: 源截取起始位置
		:param sy: 源截取起始位置
		:param sw: 源截取宽度
		:param sh: 源截取高度
		:param dx: 目标位置
		:param dy: 目标位置
		:param dw: 目标区域宽度
		:param dh: 目标区域高度
		"""
		self.assertRendering()
		if dw is None or dh is None:
			scaled = pygame.transform.scale(src, (self._renderStack[-1].scale * sw, self._renderStack[-1].scale * sw))
			dst.blit(scaled, (self._presentOffset.x + dx, self._presentOffset.y + dy), (sx, sy, sw, sh), 0)
		else:
			scaled = pygame.transform.scale(src, (dw * self._renderStack[-1].scale, dh * self._renderStack[-1].scale))
			dst.blit(scaled, (self._presentOffset.x + dx, self._presentOffset.y + dy))
	
	def renderAtMap(self, src: Surface, dst: Surface, mapPoint: Vector, fromPos: Vector | None = None, fromSize: Vector | None = None) -> None:
		"""
		按地图的方式渲染目标，会忽略margin，会考虑camera
		"""
		self.assertRendering()
		if fromPos is None or fromSize is None:
			dst.blit(src, self._canvasSize.clone().multiply(0.5).add((mapPoint - self._camera.get()).subtract(0.5, 0.5).multiply(self._customMapScale)).getTuple())
		else:
			dst.blit(src, self._canvasSize.clone().multiply(0.5).add((mapPoint + fromPos - self._camera.get()).subtract(0.5, 0.5).multiply(self._customMapScale)).getTuple(), (fromPos.x, fromPos.y, fromSize.x, fromSize.y))
	
	def renderAsBlock(self, src: Surface, dst: Surface, mapPoint: Vector, fromPos: Vector | None = None, fromSize: Vector | None = None):
		self.assertRendering()
		if fromPos is None or fromSize is None:
			dst.blit(src, self._canvasSize.clone().multiply(0.5).add((mapPoint - self._camera.get()).multiply(self._customMapScale)).getBlockTuple())
		else:
			dst.blit(src, self._canvasSize.clone().multiply(0.5).add((mapPoint + fromPos - self._camera.get()).multiply(self._customMapScale)).getBlockTuple(), (fromPos.x, fromPos.y, fromSize.x, fromSize.y))
	
	def push(self) -> None:
		self.assertRendering()
		self._renderStack.append(RenderStack(self._renderStack[-1]))
	
	def pop(self) -> None:
		self.assertRendering()
		if len(self._renderStack) == 1:
			raise IllegalStatusException("尝试弹出空栈。renderer.pop()被过多调用。")
		self._renderStack.pop()
	
	def setScale(self, scl: float) -> None:
		self.assertRendering()
		self._renderStack[-1].scale = scl
		self._updateOffset()
	
	def setSystemScale(self, scl: float) -> None:
		self._systemScale = scl
		self._scaleChanged = True
	
	def setCustomScale(self, scl: float) -> None:
		self._customScale = scl
		self._scaleChanged = True
	
	def getMapScale(self) -> float:
		return self._customMapScale
	
	def dealMapScaleChange(self) -> bool:
		"""
		应当仅在main.py, renderThread中调用
		:return:
		"""
		if self._scaleChanged:
			self._customMapScale = self._customScale * self._systemScale
			self._scaleChanged = False
			return True
		else:
			return False
	
	def mapScaleSurface(self, s: Surface, size_x: int | float | None = None, size_y: int | float | None = None) -> Surface:
		"""
		应用地图缩放
		:param s: 要缩放的surface
		:param size_x: 原图x，置None默认16
		:param size_y: 原图y，置None默认16
		:return: 缩放后的表面
		"""
		return pygame.transform.scale(s, (
			self._customMapScale if size_x is None else self._customMapScale * size_x / 16,
			self._customMapScale if size_y is None else self._customMapScale * size_y / 16
		))
	
	def uiScaleSurface(self, s: Surface) -> Surface:
		return pygame.transform.scale(s, (self._renderStack[-1].scale * s.get_size()[0], self._renderStack[-1].scale * s.get_size()[1]))
	
	def padding(self, pad: int | float) -> None:
		self.assertRendering()
		self._renderStack[-1].padding = pad
	
	def offset(self, x: int | float, y: int | float) -> None:
		self.assertRendering()
		self._renderStack[-1].offset = x, y
	
	def modifyOffset(self, x: int | float, y: int | float) -> None:
		self.assertRendering()
		self._renderStack[-1].offset.add(x, y)
	
	def readConfig(self, config: dict[str, any]) -> None:
		if "screenSize" in config:
			ss = config["screenSize"]
			if ss == "4:3":
				self._is4to3.set(True)
			elif ss == "16:9":
				self._is4to3.set(False)
			else:
				utils.warn(f"screenSize: {ss} is not supported. Using 4:3.")
	
	def writeConfig(self) -> dict[str, any]:
		return {
			"screenSize": "4:3" if self._is4to3.getNew() else "16:9"
		}


renderer: Renderer = Renderer()
