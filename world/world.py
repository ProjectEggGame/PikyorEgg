import random

from pygame import Surface

from block.block import Block, GrassBlock
from entity.entity import Entity
from interact.interact import Point
from render.renderable import Renderable


class World(Renderable):
	def __init__(self, worldID: int):
		super().__init__(None)
		self._id: int = worldID
		self._entityList: list[Entity] = []
		self._ground: list[Block] = [GrassBlock(Point(0, 0))]  # test code
	
	def tick(self) -> None:
		for e in self._entityList:
			e.tick()
		for b in self._ground:
			b.tick()
	
	def render(self, screen: Surface, delta: float, at: Point | None) -> None:
		for b in self._ground:
			b.render(screen, delta, at)
		for e in self._entityList:
			e.render(screen, delta, at)


def generateRandom(seed_or_random=None) -> random.Random:
	if seed_or_random is None:
		r = random.Random()
	elif isinstance(seed_or_random, random.Random):
		r = seed_or_random
	else:
		r = random.Random(seed_or_random)
	return r
