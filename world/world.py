import random

from pygame import Surface

from block.block import Block, GrassBlock
from entity.entity import Entity
from interact.interact import Vector
from render.renderable import Renderable


class World(Renderable):
	def __init__(self, worldID: int):
		super().__init__(None)
		self._id: int = worldID
		self._entityList: list[Entity] = []
		self._ground: list[list[Block | None]] = [[None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20, [None] * 20]
	
	def tick(self) -> None:
		for e in self._entityList:
			e.tick()
		for bl in self._ground:
			for b in bl:
				if b is None:
					continue
				b.tick()
	
	def render(self, screen: Surface, delta: float, at: Vector | None) -> None:
		for bl in self._ground:
			for b in bl:
				if b is None:
					continue
				b.render(screen, delta, at)
		for e in self._entityList:
			e.render(screen, delta, at)
	
	def generateDefaultWorld() -> 'World':
		w: World = World(-1)
		for i in range(len(w._ground)):
			for j in range(len(w._ground[0])):
				w._ground[i][j] = GrassBlock(Vector(i, j))
		return w


def generateRandom(seed_or_random=None) -> random.Random:
	if seed_or_random is None:
		r = random.Random()
	elif isinstance(seed_or_random, random.Random):
		r = seed_or_random
	else:
		r = random.Random(seed_or_random)
	return r
