from collections import deque

import pygame.transform
from pygame import Surface

from utils.error import IllegalStatusException, InvalidOperationException
# from utils.game import game
# 不可以import game，否则会导致循环导入


class RenderStack:
	def __init__(self, other: 'RenderStack | None' = None):
		if other is None:
			self.offset: tuple[int, int] = 0, 0
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
		self._size: tuple[int, int] = (0, 0)
		self._is4to3: bool = False
		self._isRendering = False
		self._renderStack: deque[RenderStack] = deque[RenderStack]()
		self._renderStack.append(RenderStack())
	
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
		self._canvas = Surface(screen.get_size())
	
	def begin(self) -> None:
		if self._isRendering:
			raise IllegalStatusException("尝试开始绘制，但是绘制已经开始。")
		self._isRendering = True
		
	def setSize(self, size: tuple[int, int]) -> None:
		self._size = size
		if self._is4to3:
			if size[0] / size[1] > 4 / 3:
				self._renderStack[-1].offset = (size[0] - size[1] * 4 / 3) / 2, 0
			elif size[0] / size[1] < 4 / 3:
				self._renderStack[-1].offset = 0, (size[1] - size[0] / 4 * 3) / 2
			else:
				self._renderStack[-1].offset = 0, 0
		else:
			if size[0] / size[1] > 16 / 9:
				self._renderStack[-1].offset = (size[0] - size[1] * 16 / 9) / 2, 0
			elif size[0] / size[1] < 16 / 9:
				self._renderStack[-1].offset = 0, (size[1] - size[0] / 16 * 9) / 2
			else:
				self._renderStack[-1].offset = 0, 0
				
	def end(self) -> None:
		"""
		只在渲染帧结束时调用
		:return:
		"""
		if not self._isRendering:
			raise IllegalStatusException("尝试结束绘制，但是绘制尚未开始。")
		self._screen.blit(self._canvas, self._renderStack[-1].offset)
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
	
	def getSize(self) -> tuple[int, int]:
		return self._size
	
	def getCanvas(self) -> Surface:
		return self._canvas
	
	def getScreen(self) -> Surface:
		return self._screen
	
	def render(self, src: Surface, dst: Surface, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int = None, dh: int = None) -> None:
		"""
		渲染目标。以下全部是int类型的px单位
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
			dst.blit(scaled, (self._renderStack[-1].offset[0] + dx, self._renderStack[-1].offset[1] + dy), (sx, sy, sw, sh), 0)
		else:
			scaled = pygame.transform.scale(src, (dw * self._renderStack[-1].scale, dh * self._renderStack[-1].scale))
			dst.blit(scaled, (self._renderStack[-1].offset[0] + dx, self._renderStack[-1].offset[1] + dy))
	
	def push(self) -> None:
		self.assertRendering()
		self._renderStack.append(RenderStack(self._renderStack[-1]))
	
	def pop(self) -> None:
		self.assertRendering()
		if len(self._renderStack) == 1:
			raise IllegalStatusException("尝试弹出空栈。renderer.pop()被过多调用。")
		self._renderStack.pop()
	
	def scale(self, scl: float) -> None:
		self.assertRendering()
		self._renderStack[-1].scale = scl
	
	def padding(self, pad: int) -> None:
		self.assertRendering()
		self._renderStack[-1].padding = pad
	
	def offset(self, x: int, y: int) -> None:
		self.assertRendering()
		self._renderStack[-1].offset = x, y
	

renderer: Renderer = Renderer()
