import pygame
from utils import utils
from utils.error import InvalidOperationException


class Point:
	def __init__(self, x: int | float = 0, y: int | float = 0):
		"""
		屏幕上的点，或世界上的点。方块采用整数，其余采用浮点
		:param x: 横坐标，相对左上角。
		:param y: 纵坐标，相对左上角
		"""
		self.x = x
		self.y = y
	
	def set(self, x_or_pos: tuple[int, int] | int, y_or_None: int = None) -> None:
		"""
		重设坐标。可以直接传入一个唯一参数set((x, y))元组，也可以传入两个参数set(x, y)
		"""
		if x_or_pos is tuple:
			self.x = x_or_pos[0]
			self.y = x_or_pos[1]
		else:
			self.x = x_or_pos
			self.y = y_or_None


class Status:
	def __init__(self, name: str):
		"""
		:param name: 监视状态的名称
		"""
		self.name = name
		self._presentStatus = False
		self._shouldDeal = False
	
	def set(self, status: bool) -> None:
		"""
		设置状态。应当仅在main.py的mainThread中调用。用于激活事件
		:param status: 设置为的值
		"""
		self._presentStatus = status
		if status:
			self._shouldDeal = True
	
	def deal(self) -> bool:
		"""
		查看是否需要处理时调用
		:returns 如果需要处理，则返回True，随后将状态置为False
		"""
		if self._shouldDeal:
			self._shouldDeal = False
			return True
		else:
			return False
	
	def peek(self) -> bool:
		"""
		需要处理时调用。
		:returns 如果需要处理，则返回True，但是不重置状态
		"""
		return self._shouldDeal
	
	def __str__(self) -> str:
		return f'{self.name}: {self._presentStatus}'


class ScrollStatus(Status):
	def __init__(self):
		super().__init__('MouseScroll')
		self._shouldDeal = 0
	
	def scroll(self, scr: int) -> None:
		"""
		向下为正
		"""
		self._shouldDeal += scr
	
	def peekScroll(self) -> int:
		"""
		需要处理时调用。
		:returns 如果需要处理，则返回True，但是不重置状态
		"""
		return self._shouldDeal
	
	def resetScroll(self) -> None:
		"""
		重置滚动量
		"""
		self._shouldDeal = 0
	
	def dealScroll(self) -> int:
		if self._shouldDeal != 0:
			ret = self._shouldDeal
			self._shouldDeal = 0
			return ret
		else:
			return 0
	
	def deal(self) -> bool:
		raise InvalidOperationException('ScrollStatus.deal() should not be called')
	
	def peek(self) -> bool:
		raise InvalidOperationException('ScrollStatus.peek() should not be called')
	
	def set(self, status: bool) -> None:
		raise InvalidOperationException('ScrollStatus.set() should not be called')
	
	def __str__(self) -> str:
		return f'{self.name}: {self._shouldDeal}'


class GameSettings:
	def __init__(self):
		self.fps = 60
		self.screenWidth = 800
		self.screenHeight = 600
		self.fullScreen = False
		self.showFPS = False
		self.showMouse = True
		self.showCursor = True
		self.showDebug = False
		self.showLog = False
		self.showInfo = False
		self.showWarning = False
		self.showError = False
		self.showException = False
		self.showTraceback = False


KEY_COUNT = 256
mouse: Point = Point(0, 0)
left: Status = Status('MouseLeft')
middle: Status = Status('MouseMiddle')
right: Status = Status('MouseRight')
scroll: ScrollStatus = ScrollStatus()
keys: list[Status | None] = [Status('')] * KEY_COUNT
specialKeys: list[Status | None] = [Status('')] * KEY_COUNT
for i in pygame.__dict__:
	if not i.startswith('K_'):
		continue
	j = getattr(pygame, i)
	if j <= KEY_COUNT:
		keys[j].name = i[2:]
	else:
		specialKeys[j & (KEY_COUNT - 1)].name = i[2:]
utils.debug(f'keys长度{len(keys)}')

print(f'break {hex(pygame.K_BREAK)} pause {hex(pygame.K_PAUSE)}')


def onKey(event) -> None:
	if event.type == pygame.KEYDOWN:
		if event.key <= KEY_COUNT:
			keys[event.key].set(True)
		else:
			specialKeys[event.key & (KEY_COUNT - 1)].set(True)
	elif event.type == pygame.KEYUP:
		if event.key <= KEY_COUNT:
			keys[event.key].set(False)
		else:
			specialKeys[event.key & (KEY_COUNT - 1)].set(False)


def onMouse(event) -> None:
	if event.type == pygame.MOUSEMOTION:
		mouse.set(event.pos)
	elif event.type == pygame.MOUSEBUTTONDOWN:
		if event.button == 1:
			left.set(True)
		elif event.button == 2:
			right.set(True)
		elif event.button == 3:
			middle.set(True)
		elif event.button == 4:
			scroll.scroll(-1)
		elif event.button == 5:
			scroll.scroll(1)
		else:
			utils.warn(f'onMouse: unknown button {event.button}')
	elif event.type == pygame.MOUSEBUTTONUP:
		if event.button == 1:
			left.set(True)
		elif event.button == 2:
			right.set(True)
		elif event.button == 3:
			middle.set(True)
		elif event.button == 4:
			scroll.scroll(-1)
		elif event.button == 5:
			scroll.scroll(1)
		else:
			utils.warn(f'onMouse: unknown button {event.button}')
