import math
import random
from typing import Union, TYPE_CHECKING

from utils import utils

if TYPE_CHECKING:
	from entity.entity import Entity, Player

from pygame import Surface
from render.renderable import Renderable
from utils.vector import Vector, BlockVector
from block.block import Block, GrassBlock, PathBlock, ErrorBlock


class World(Renderable):
	def __init__(self, worldID: int, seed: int | None = None):
		super().__init__(None)
		self._player: Union['Player', None] = None
		self._id: int = worldID
		self._entityList: set['Entity'] = set['Entity']()
		self._ground: dict[int, Block] = dict[int, Block]()
		self._seed: random.Random
	
	def generateDefaultWorld() -> 'World':
		w: World = World(-1)
		for i in range(-3, 3):
			for j in range(-3, 3):
				if j == 1 and i == 1:
					continue
				v = BlockVector(i, j)
				w._ground[hash(v)] = GrassBlock(v) if j != 0 or i != 0 else PathBlock(v)
		return w
	
	def tick(self) -> None:
		for e in self._entityList:
			e.passTick()
		for b in self._ground.values():
			if b is None:
				continue
			b.passTick()
		if self._player is not None:
			self._player.passTick()
	
	def render(self, screen: Surface, delta: float, at: Union[Vector, None]) -> None:
		for b in self._ground.values():
			if b is None:
				continue
			b.render(screen, delta, at)
		for e in self._entityList:
			e.render(screen, delta, at)
		if self._player is not None:
			self._player.render(screen, delta, at)
	
	def addPlayer(self, player: 'Player') -> None:
		self._player = player
	
	def getPlayer(self) -> Union['Player', None]:
		return self._player
	
	def addEntity(self, entity: 'Entity') -> None:
		self._entityList.add(entity)
	
	def removeEntity(self, entity: 'Entity') -> None:
		self._entityList.remove(entity)
	
	def getBlockAt(self, point: Vector | BlockVector) -> None:
		return self._ground.get(hash(point if isinstance(point, BlockVector) else point.clone().getBlockVector()))
	
	def setBlockAt(self, point: BlockVector, block: Block) -> Block | None:
		"""
		设置方块，返回原来的方块
		"""
		b = self._ground[hash(point)]
		self._ground[hash(point)] = block
		return b
	
	def rayTraceBlock(self, start: Vector, direction: Vector, length: float, width: float = 0) -> list[tuple[Block | BlockVector, Vector]]:
		"""
		平面上查找某一起点、射线、长度范围内的所有方块
		:param start: 起始点
		:param direction: 射线方向
		:param length: 追踪长度
		:param width: 循迹宽度，默认0
		:return: 元组列表，距离小到大排序。如果方块为None，则第一个参数为方块向量，否则为方块；第二个参数是起始点方向向的命中点（没有宽度偏移）
		"""
		if utils.fequal(direction.x, 0) and utils.fequal(direction.y, 0):
			return []
		result: list[tuple[Block | BlockVector, Vector]] = []
		dcb: BlockVector = direction.directionalCloneBlock()
		if dcb.x == 0 and start.xInteger():
			dcb.x = 1
		if dcb.y == 0 and start.yInteger():
			dcb.y = 1
		directionFix: Vector = direction.directionalClone().multiply(width + 1)
		checkEnd: BlockVector = start.clone().add(direction.normalize().multiply(length)).add(directionFix).getBlockVector()
		checkStart: BlockVector = start.clone().subtract(directionFix).getBlockVector()
		for i in [checkStart.x] if dcb.x == 0 else range(checkStart.x - dcb.x, checkEnd.x + dcb.x, dcb.x):
			for j in [checkStart.y] if dcb.y == 0 else range(checkStart.y - dcb.y, checkEnd.y + dcb.y, dcb.y):
				if i == 3 and j == -3:
					pass
				blockPos: BlockVector = BlockVector(i, j)
				hitResult: Vector | None = blockPos.getHitPoint(start, direction)
				if hitResult is not None and hitResult.length() < length:
					result.append((self._ground[hash(blockPos)] if hash(blockPos) in self._ground.keys() else blockPos.clone(), hitResult.clone()))
		return result
	
	def __str__(self) -> str:
		return f'World(blocks = {len(self._ground)}, {self._ground})'


def generateRandom(seed_or_random=None) -> random.Random:
	if seed_or_random is None:
		r = random.Random()
	elif isinstance(seed_or_random, random.Random):
		r = seed_or_random
	else:
		r = random.Random(seed_or_random)
	return r
