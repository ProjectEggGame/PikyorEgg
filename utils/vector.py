from typing import Union

from utils import utils
from utils.error import InvalidOperationException


class Vector:
	def __init__(self, x: float = 0, y: float = 0):
		"""
		屏幕上的点，或世界上的点。方块采用整数，其余采用浮点
		:param x: 横坐标，相对左上角。
		:param y: 纵坐标，相对左上角
		"""
		self.x = x
		self.y = y
	
	def set(self, x_or_pos: Union[float, tuple[float, float], 'Vector'], y_or_None: float | None = None) -> None:
		"""
		重设坐标。可以直接传入一个唯一参数set((x, y))元组，也可以传入两个参数set(x, y)
		"""
		if x_or_pos is tuple:
			self.x = x_or_pos[0]
			self.y = x_or_pos[1]
		elif type(x_or_pos) == type(self):
			self.x = x_or_pos.x
			self.y = x_or_pos.y
		else:
			self.x = x_or_pos
			self.y = y_or_None
	
	def add(self, x: Union[float, tuple[float, float], 'Vector'], y: float | None = None) -> 'Vector':
		if x is tuple:
			x, y = x
		elif type(x) == type(self):
			x, y = x.x, x.y
		self.x += x
		self.y += y
		return self
	
	def subtract(self, x: Union[float, tuple[float, float], 'Vector'], y: float | None = None) -> 'Vector':
		if x is tuple:
			x, y = x
		elif type(x) == type(self):
			x, y = x.x, x.y
		self.x -= x
		self.y -= y
		return self
	
	def multiply(self, mul) -> 'Vector':
		self.x *= mul
		self.y *= mul
		return self
	
	def dot(self, other: 'Vector') -> float:
		return self.x * other.x + self.y * other.y
	
	def clone(self) -> 'Vector':
		return Vector(self.x, self.y)
	
	def length(self) -> float:
		return float(self.x ** 2 + self.y ** 2) ** 0.5
	
	def normalize(self) -> 'Vector':
		if self.x == 0 and self.y == 0:
			return self
		selfLength = self.length()
		self.x /= selfLength
		self.y /= selfLength
		return self
	
	def floor(self) -> 'Vector':
		self.x = int(self.x)
		self.y = int(self.y)
		return self
	
	def reverse(self) -> 'Vector':
		self.x = -self.x
		self.y = -self.y
		return self
	
	def distance(self, other: 'Vector') -> float:
		return float((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
	
	def distanceManhattan(self, other: 'Vector') -> float:
		return abs(self.x - other.x) + abs(self.y - other.y)
	
	def getTuple(self) -> tuple[float, float]:
		return self.x, self.y
	
	def getBlockVector(self) -> 'BlockVector':
		return BlockVector(int(self.x), int(self.y))
	
	def directionalCloneBlock(self) -> 'BlockVector':
		"""
		查看方向性。对于x和y，如果大于0，修改为1；如果小于0，修改为-1；否则修改为0
		:return:
		"""
		return BlockVector(0 if self.x == 0 else 1 if self.x > 0 else -1, 0 if self.y == 0 else 1 if self.y > 0 else -1)
	
	def directionalClone(self) -> 'Vector':
		"""
		查看方向性。对于x和y，如果大于0，修改为1；如果小于0，修改为-1；否则修改为0
		:return:
		"""
		return Vector(0 if self.x == 0 else 1 if self.x > 0 else -1, 0 if self.y == 0 else 1 if self.y > 0 else -1)
	
	def pointVerticalTo(self, line: 'Vector') -> 'Vector':
		"""
		将本坐标视为坐标点，求该点到直线的垂线向量，包含长度。
		:param line: 目标直线
		:return: 垂线
		"""
		d = line.clone().normalize()
		length = d.x * self.y - d.y * self.x
		if length == 0:
			return Vector(0, 0)
		d.x, d.y = d.y, -d.x
		return d.multiply(length)
	
	def __len__(self) -> float:
		return float(self.x ** 2 + self.y ** 2) ** 0.5
	
	def __add__(self, other: 'Vector') -> 'Vector':
		return Vector(self.x + other.x, self.y + other.y)
	
	def __sub__(self, other: 'Vector') -> 'Vector':
		return Vector(self.x - other.x, self.y - other.y)
	
	def __mul__(self, val: float) -> 'Vector':
		return Vector(self.x * val, self.y * val)
	
	def __truediv__(self, other: float) -> 'Vector':
		return Vector(self.x / other, self.y / other)
	
	def __eq__(self, other: 'Vector') -> bool:
		return self.x == other.x and self.y == other.y
	
	def __str__(self) -> str:
		return f'Vector({self.x:.2f}, {self.y:.2f})'
	
	def __repr__(self) -> str:
		return f'Vector({self.x:.2f}, {self.y:.2f})'


class BlockVector:
	def __init__(self, x: int = 0, y: int = 0):
		"""
		屏幕上的点，或世界上的点。方块采用整数，其余采用浮点
		:param x: 横坐标，相对左上角。
		:param y: 纵坐标，相对左上角
		"""
		if x >= 0x1_0000_0000 or y >= 0x1_0000_0000:
			raise ValueError('BlockVector out of range')
		self.x = x
		self.y = y
	
	def set(self, x_or_pos: Union[int, tuple[int, int], 'BlockVector'], y_or_None: int | None = None) -> None:
		"""
		重设坐标。可以直接传入一个唯一参数set((x, y))元组，也可以传入两个参数set(x, y)
		"""
		if x_or_pos is tuple:
			self.x = x_or_pos[0]
			self.y = x_or_pos[1]
		elif type(x_or_pos) == type(self):
			self.x = x_or_pos.x
			self.y = x_or_pos.y
		else:
			self.x = x_or_pos
			self.y = y_or_None
	
	def add(self, x: Union[int, tuple[int, int], 'BlockVector'], y: int | None = None) -> 'BlockVector':
		if x is tuple:
			x, y = x
		elif type(x) == type(self):
			x, y = x.x, x.y
		self.x += x
		self.y += y
		return self
	
	def subtract(self, x: Union[int, tuple[int, int], 'BlockVector'], y: int | None = None) -> 'BlockVector':
		if x is tuple:
			x, y = x
		elif type(x) == type(self):
			x, y = x.x, x.y
		self.x -= x
		self.y -= y
		return self
	
	def multiply(self, mul: int | float) -> 'BlockVector':
		self.x = (self.x * mul)
		self.y = (self.y * mul)
		return self
	
	def dot(self, other: 'BlockVector') -> int:
		return self.x * other.x + self.y * other.y
	
	def clone(self) -> 'BlockVector':
		return BlockVector(self.x, self.y)
	
	def length(self) -> float:
		return float(self.x ** 2 + self.y ** 2) ** 0.5
	
	def distance(self, other: 'BlockVector') -> float:
		return float((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
	
	def distanceManhattan(self, other: 'BlockVector') -> float:
		return abs(self.x - other.x) + abs(self.y - other.y)
	
	def normalizeClone(self) -> 'Vector':
		if self.x == 0 and self.y == 0:
			return Vector()
		selfLength = self.length()
		return Vector(self.x / selfLength, self.y / selfLength)
	
	def reverse(self) -> 'BlockVector':
		self.x = -self.x
		self.y = -self.y
		return self
	
	def floor(self) -> 'BlockVector':
		self.x = int(self.x)
		self.y = int(self.y)
		return self
	
	def getTuple(self) -> tuple[int, int]:
		return self.x, self.y
	
	def getVector(self) -> Vector:
		return Vector(self.x, self.y)
	
	def directionalCloneBlock(self) -> 'BlockVector':
		"""
		查看方向性。对于x和y，如果大于0，修改为1；如果小于0，修改为-1；否则修改为0
		:return:
		"""
		return BlockVector(0 if self.x == 0 else 1 if self.x > 0 else -1, 0 if self.y == 0 else 1 if self.y > 0 else -1)
	
	def directionalClone(self) -> 'Vector':
		"""
		查看方向性。对于x和y，如果大于0，修改为1；如果小于0，修改为-1；否则修改为0
		:return:
		"""
		return Vector(0 if self.x == 0 else 1 if self.x > 0 else -1, 0 if self.y == 0 else 1 if self.y > 0 else -1)
	
	def pointVerticalTo(self, line: Vector) -> Vector:
		"""
		将本坐标视为坐标点，求该点到直线的垂线向量，包含长度。
		:param line: 目标直线
		:return: 垂线
		"""
		d = line.clone().normalize()
		length = d.x * self.y - d.y * self.x
		if length == 0:
			return Vector(0, 0)
		d.x, d.y = d.y, -d.x
		return d.multiply(length)
	
	def contains(self, point: Vector) -> bool:
		"""
		检查方块是否包含目标点
		:param point: 目标点
		"""
		return self.x <= point.x <= self.x + 1 and self.y <= point.y <= self.y + 1
	
	def getHitPoint(self, start: Vector, direction: Vector) -> Vector | None:
		"""
		获取从start射出的射线direction会碰到方块表面位置，返回start点到该位置的向量
		:param start: 起始点
		:param direction: 方向
		:returns: 如果start不经过direction，返回None
		"""
		if direction.x == 0 and direction.y == 0:
			return None
		start: Vector = start.clone()
		direction: Vector = direction.clone().normalize()
		relative: Vector = ((self.getVector() - start).subtract(0.5, 0.5))
		dc: BlockVector = direction.directionalCloneBlock()
		if self.contains(start):
			if dc.x != 0:
				result: Vector = direction.clone().multiply(0.5 / abs(relative.x))
				if -0.5 < result.y < 0.5:
					return result
			if dc.y != 0:
				result: Vector = direction.clone().multiply(0.5 / abs(relative.y))
				if -0.5 < result.x < 0.5:
					return result
			raise InvalidOperationException(f'不应当运行到此处，请检查代码问题。{start = }, {direction = }, {relative = }, {dc = }')
		else:
			if -0.5 < relative.x < 0.5:  # 在上下方
				if dc.y == -1 and relative.y > 0:
					return None
				if dc.y == 1 and relative.y < 0:
					return None
				result = direction.multiply(abs(relative.y) - 0.5)
				if -0.5 < result.x < 0.5:
					return result
				return None
			if -0.5 < relative.y < 0.5:  # 在左右方
				if dc.x == -1 and relative.x > 0:
					return None
				if dc.x == 1 and relative.x < 0:
					return None
				result = direction.multiply(abs(relative.x) - 0.5)
				if -0.5 < result.y < 0.5:
					return result
				return None
			if dc.x == 0 or dc.y == 0:  # 斜角
				return None
			x_extend = direction.multiply(abs(relative.x) - 0.5).subtract(relative)
			y_extend = direction.multiply(abs(relative.y) - 0.5).subtract(relative)
			if -0.5 < x_extend.y < 0.5:
				return x_extend
			if -0.5 < y_extend.x < 0.5:
				return y_extend
			return None
	
	def __len__(self) -> float:
		return float(self.x ** 2 + self.y ** 2) ** 0.5
	
	def __add__(self, other: 'BlockVector') -> 'BlockVector':
		return BlockVector(self.x + other.x, self.y + other.y)
	
	def __sub__(self, other: 'BlockVector') -> 'BlockVector':
		return BlockVector(self.x - other.x, self.y - other.y)
	
	def __mul__(self, val: int | float) -> 'BlockVector':
		return BlockVector(self.x * val, self.y * val)
	
	def __truediv__(self, other: int | float) -> 'BlockVector':
		return BlockVector(int(self.x / other), int(self.y / other))
	
	def __eq__(self, other: 'BlockVector') -> bool:
		return self.x == other.x and self.y == other.y
	
	def __str__(self) -> str:
		return f'Block({self.x}, {self.y})'
	
	def __repr__(self) -> str:
		return f'Block({self.x}, {self.y})'
	
	def __hash__(self) -> int:
		return self.x << 32 + self.y
