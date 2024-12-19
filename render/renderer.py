from collections import deque
from enum import Enum
from typing import Union, TYPE_CHECKING

from interact import interact
from render import font
from save import configs
from utils import utils
from utils.text import RenderableString

if TYPE_CHECKING:
	from entity.entity import Entity

import pygame
from pygame import Surface
from utils.vector import Vector, BlockVector
from utils.error import IllegalStatusException, InvalidOperationException
from utils.sync import SynchronizedStorage


# from utils.game import game
# 不可以import game，否则会导致循环导入


class Location(Enum):
	LEFT_TOP = 0
	"""
	左上角
	"""
	LEFT = 1
	"""
	左居中
	"""
	LEFT_BOTTOM = 2
	"""
	左下角
	"""
	TOP = 3
	"""
	上居中
	"""
	CENTER = 4
	"""
	正中心
	"""
	BOTTOM = 5
	"""
	下居中
	"""
	RIGHT_TOP = 6
	"""
	右上角
	"""
	RIGHT = 7
	"""
	右居中
	"""
	RIGHT_BOTTOM = 8
	"""
	右下角
	"""


class RenderStack:
	def __init__(self, other: 'RenderStack | None' = None):
		if other is None:
			self.offset: BlockVector = BlockVector(0, 0)
			self.scale: float = 1
			self.padding: int = 10
		else:
			self.offset = other.offset
			self.scale = other.scale
			self.padding = other.padding


class Renderer:
	def __init__(self):
		super().__init__()
		self._screen: Surface | None = None  # 屏幕
		self._size: tuple[float, float] = (0, 0)
		
		self._canvas: Surface | None = None  # 用于预绘制的画布
		self._canvasSize: Vector = Vector()
		self._canvasCenter: BlockVector = BlockVector()
		
		self._isRendering: bool = False
		
		self._renderStack: deque[RenderStack] = deque[RenderStack]()
		self._renderStack.append(RenderStack())
		
		self._camera: SynchronizedStorage[Vector] = SynchronizedStorage[Vector](Vector(10.0, 10.0))
		self._cameraAt: Union['Entity', None] = None
		
		self._systemScale: int = 16  # 方块基本是16px
		self._customMapScale: int = 16
		self._mapScaleChanged: bool = True
		
		self._offset: BlockVector = BlockVector(0, 0)
		self._presentOffset: BlockVector = BlockVector(0, 0)
		
		self._customScale: float = 1.0
		self._is4to3: SynchronizedStorage[bool] = SynchronizedStorage[bool](True)
	
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
				self._offset = BlockVector(int(self._size[0] - self._size[1] * 4 / 3) >> 1, 0)
			elif self._size[0] / self._size[1] < 4 / 3:
				self._offset = BlockVector(0, int(self._size[1] - self._size[0] / 4 * 3) >> 1)
			else:
				self._offset = BlockVector(0, 0)
			self.setSystemScale(min(self._size[0] // 12, self._size[1] // 9))
		else:
			if self._size[0] / self._size[1] > 16 / 9:
				self._offset = BlockVector(int(self._size[0] - self._size[1] * 16 / 9) >> 1, 0)
			elif self._size[0] / self._size[1] < 16 / 9:
				self._offset = BlockVector(0, int(self._size[1] - self._size[0] / 16 * 9) >> 1)
			else:
				self._offset = BlockVector(0, 0)
			self.setSystemScale(min(self._size[0] // 16, self._size[1] // 9))
		self._canvasSize = BlockVector(self._size[0], self._size[1]).subtract(self._offset).subtract(self._offset)
		self._canvas = Surface(self._canvasSize.getTuple())
		self._canvasCenter.set(int(self._canvasSize.x / 2), int(self._canvasSize.y / 2))
		self._updateOffset()
	
	def cameraAt(self, entity: 'Entity') -> 'Entity':
		e = self._cameraAt
		self._cameraAt = entity
		return e
	
	def begin(self, delta: float, noWindow: bool) -> None:
		"""
		仅在game.render中调用
		"""
		if self._isRendering:
			raise IllegalStatusException("尝试开始绘制，但是绘制已经开始。")
		if noWindow and interact.scroll.peekScroll() != 0:
			newScale = self._customScale * (0.8 ** interact.scroll.dealScroll())
			newScale = utils.frange(newScale, 0.5, 8)
			if newScale != self._customScale:
				self._customScale = newScale
				self._mapScaleChanged = True
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
	
	def getOffset(self) -> BlockVector:
		return self._offset.clone()
	
	def render(self, src: Surface, sx: int | float, sy: int | float, sw: int | float, sh: int | float, dx: int | float, dy: int | float, dw: int | float | None = None, dh: int | float | None = None) -> None:
		"""
		渲染目标。以下全部是int类型的px单位。请尽量避免使用这个方法，因为这个方法的效率比较低下。
		:param src: 源Surface
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
			self._canvas.blit(scaled, (self._presentOffset.x + dx, self._presentOffset.y + dy), (sx, sy, sw, sh))
		else:
			scaled = pygame.transform.scale(src, (dw * self._renderStack[-1].scale, dh * self._renderStack[-1].scale))
			self._canvas.blit(scaled, (self._presentOffset.x + dx, self._presentOffset.y + dy))
	
	def renderAtMap(self, src: Surface, mapPoint: Vector, fromPos: Vector | None = None, fromSize: Vector | None = None) -> None:
		"""
		按地图的方式渲染目标，会忽略margin，会考虑camera
		"""
		self.assertRendering()
		dst = self._canvas
		if fromPos is None or fromSize is None:
			dst.blit(src, self._canvasCenter.clone().add((mapPoint - self._camera.get()).subtract(0.5, 0.5).multiply(self._customMapScale).getBlockVector()).getTuple())
		else:
			dst.blit(src, self._canvasCenter.clone().add((mapPoint + fromPos - self._camera.get()).subtract(0.5, 0.5).multiply(self._customMapScale).getBlockVector()).getTuple(), (fromPos.x, fromPos.y, fromSize.x, fromSize.y))
	
	def renderAsBlock(self, src: Surface, mapPoint: Vector, fromPos: Vector | None = None, fromSize: Vector | None = None):
		self.assertRendering()
		if fromPos is None or fromSize is None:
			self._canvas.blit(src, self._canvasCenter.clone().add((mapPoint - self._camera.get()).multiply(self._customMapScale).getBlockVector()).getTuple())
		else:
			self._canvas.blit(src, self._canvasCenter.clone().add((mapPoint + fromPos - self._camera.get()).multiply(self._customMapScale).getBlockVector()).getTuple(), (fromPos.x, fromPos.y, fromSize.x, fromSize.y))
	
	def renderString(self, text: RenderableString, x: int, y: int, defaultColor: int, location: Location = Location.LEFT_TOP) -> None:
		"""
		:param text: 要显示的文本
		:param x: 参考坐标
		:param y: 参考坐标
		:param defaultColor: 默认颜色
		:param location: 渲染位置，默认左上角
		"""
		self.assertRendering()
		if len(text.set) == 0:
			return
		height = font.fontHeight if text.set[0].font < 10 else (font.fontHeight >> 1)
		match location:
			case Location.LEFT_TOP:
				text.renderAt(self._canvas, x, y, defaultColor)
			case Location.LEFT:
				text.renderAt(self._canvas, x, y - (height >> 1), defaultColor)
			case Location.LEFT_BOTTOM:
				text.renderAt(self._canvas, x, y - height, defaultColor)
			case Location.TOP:
				l: int = text.length()
				text.renderAt(self._canvas, x - (l >> 1), y, defaultColor)
			case Location.CENTER:
				l: int = text.length()
				text.renderAt(self._canvas, x - (l >> 1), y - (height >> 1), defaultColor)
			case Location.BOTTOM:
				l: int = text.length()
				text.renderAt(self._canvas, x - (l >> 1), y - height, defaultColor)
			case Location.RIGHT_TOP:
				l: int = text.length()
				text.renderAt(self._canvas, x - l, y, defaultColor)
			case Location.RIGHT:
				l: int = text.length()
				text.renderAt(self._canvas, x - l, y - (height >> 1), defaultColor)
			case Location.RIGHT_BOTTOM:
				l: int = text.length()
				text.renderAt(self._canvas, x - l, y - height, defaultColor)
	
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
	
	def setSystemScale(self, scl: int) -> None:
		self._systemScale = int(scl)
		self._mapScaleChanged = True
	
	def getSystemScale(self) -> float:
		return self._systemScale
	
	def setCustomScale(self, scl: float) -> None:
		self._customScale = scl
		self._mapScaleChanged = True
	
	def getCustomScale(self) -> float:
		return self._customScale
	
	def getMapScale(self) -> float:
		return self._customMapScale
	
	def dealMapScaleChange(self) -> bool:
		"""
		应当仅在main.py, renderThread中调用
		:return:
		"""
		if self._mapScaleChanged:
			self._customMapScale = int(self._customScale * self._systemScale)
			map_size = self._canvasSize.clone().multiply(1 / self._customMapScale)
			self._mapScaleChanged = False
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
			self._customMapScale if size_x is None else (self._customMapScale * size_x) // 16,
			self._customMapScale if size_y is None else (self._customMapScale * size_y) // 16
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
		self._is4to3.set(configs.readElseDefault(config, "screenSize", False, {"4:3": True, "16:9": False}, "screenSize: {} is not supported. Using 4:3."))
		self._is4to3.apply(self._is4to3.getNew())
		self.setCustomScale(configs.readElseDefault(config, "customScale", 1, lambda f: utils.frange(f, 0.5, 8)))
		
	def writeConfig(self) -> dict[str, any]:
		return {
			"screenSize": "4:3" if self._is4to3.get() else "16:9",
			"customScale": self._customScale,
		}


renderer: Renderer = Renderer()
