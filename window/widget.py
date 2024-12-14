from typing import Callable

from render.renderable import Renderable
from render.renderer import renderer
from render.resource import Texture
from utils.text import Description, RenderableString
from enum import Enum

from utils.vector import BlockVector


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


class Widget(Renderable):
	"""
	你可以为控件定义很多属性。属性中，所有带on前缀的都应当是函数类型的事件响应器。\n
	以下所有的事件都可以置None，或者传入回调函数。\n
	大多数事件回调类型都是(x: int, y: int) -> bool，返回true则表示阻断事件传递。\n
	onHover，鼠标浮游在控件上时调用。\n
	onClick，鼠标点击时触发。指的是，鼠标按下，且抬起时触发。\n
	onMouseDown，鼠标按下。\n
	onMouseUp，鼠标抬起。\n
	onTick，每tick调用。\n
	_x, _y, _w, _h与公开的x, y, width, height不同。前者的单位是屏幕像素；后者的单位是窗口，例如x=0.5意味着x坐标位于屏幕的一半。
	"""
	def __init__(self, location: Location, x: float, y: float, width: float, height: float, name: RenderableString, description: Description, texture: Texture):
		"""
		创建控件。注意，位置取屏幕的相对位置。如果取LEFT_TOP，则x, y指代控件左上角与窗口左上角的相对位置；如果取RIGHT，则x, y分别指代控件右边与窗口右边的相对位置，和控件正中央与屏幕纵向正中央的相对位置
		:param location: 位置
		:param x: 横坐标，一般取-1~1，表示窗口占比
		:param y: 纵坐标，一般取-1~1，表示窗口占比
		:param width: 宽度
		:param height: 高度
		:param name: 控件显示名称
		:param description: 控件描述
		:param texture: 控件背景纹理
		"""
		super().__init__(texture)
		self.location: Location = location
		self.x: float = x
		self.y: float = y
		self.width: float = width
		self.height: height = height
		self.name: RenderableString = name
		self.description: Description = description
		self._x: int = 0
		self._y: int = 0
		self._w: int = 0
		self._h: int = 0
		self.onHover: Callable[[int, int], bool] | None = None
		self.onClick: Callable[[int, int], bool] | None = None
		self.onMouseUp: Callable[[int, int], bool] | None = None
		self.onMouseDown: Callable[[int, int], bool] | None = None
		self.onTick: Callable[[], int] | None = None
		

	def onResize(self) -> None:
		"""
		根据预设调整具体位置
		"""
		renderer.getSize()
		
	def isMouseIn(self, x: int, y: int):
		pass
	
	def tick(self) -> None:
		"""
		可以重写，默认为调用self.onTick
		:return:
		"""
		if self.onTick is not None:
			self.onTick()
	
	def click(self, x: int, y: int) -> bool:
		if self.onClick is not None:
			return self.onClick(x, y)

