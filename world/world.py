import random
from typing import Union, TYPE_CHECKING

import pygame

from block.manager import blockManager
from entity.manager import entityManager
from interact.interacts import interact
from render.renderer import renderer
from save.save import Archive
from utils.util import utils
from utils.game import game
from utils.text import RenderableString

if TYPE_CHECKING:
	from entity.entity import Entity, Player

from render.renderable import Renderable
from utils.vector import Vector, BlockVector
from block.block import Block, BrickWallBlock, BrickGroundBlock
from music.music import Music_player


class World(Renderable):
	def __init__(self, worldID: int, name: str, seed: int | None = None):
		super().__init__(None)
		self._name: str = name
		self._player: Union['Player', None] = None
		self._id: int = worldID
		self._entityList: set['Entity'] = set['Entity']()
		self._ground: dict[int, Block] = dict[int, Block]()
		self._seed: random.Random = random.Random(seed or 0)
	
	@staticmethod
	def generateDefaultWorld(seed: int | None = None) -> 'World':
		w: World = World(-1, "__DEFAULT_WORLD__")
		rd = random.Random(seed or 0)
		for i in range(-10, 10):
			for j in range(-10, 10):
				v = BlockVector(i, j)
				w._ground[hash(v)] = blockManager.dic[rd.sample(blockManager.dic.keys(), 1)[0]](v)
		w.addEntity(entityManager.get('enemy.dog')())
		return w
	
	def tick(self) -> None:
		for e in self._entityList.copy():
			e.passTick()
		for b in self._ground.values():
			if b is None:
				continue
			b.passTick()
		if self._player is not None:
			self._player.passTick()
		if game.getWindow() is None:
			if interact.keys[pygame.K_ESCAPE].deals():
				from window.window import PauseWindow
				game.setWindow(PauseWindow())
			if interact.keys[pygame.K_TAB].deals():
				from window.ingame import TaskWindow
				game.setWindow(TaskWindow())
			if interact.keys[pygame.K_SPACE].deals():
				if renderer.getCameraAt() is None:
					renderer.cameraAt(self.getPlayer())
					game.hud.sendMessage(RenderableString('\\#cc66ccee视角锁定'))
				elif renderer.cameraOffset.lengthManhattan() == 0:
					game.hud.sendMessage(RenderableString('\\#cc00cc00视角解锁'))
					renderer.cameraAt(None)
				else:
					game.hud.sendMessage(RenderableString('\\#cc7755ee居中锁定'))
					renderer.cameraOffset.set(0, 0)
	
	def render(self, delta: float) -> None:
		ct = renderer.getCenter().getVector().divide(renderer.getMapScale())
		block2 = ct.clone().add(renderer.getCamera().get()).getBlockVector().add(0, 1)
		block1 = ct.reverse().add(renderer.getCamera().get()).getBlockVector()
		newList = []
		y2 = block2.y + 2
		for e in iter(self._entityList.copy()):
			p = e.getPosition()
			if p.x < block1.x or p.x > block2.x or p.y < block1.y or p.y > y2:
				continue
			if renderer.getCameraAt() is not e:
				e.updatePosition(delta)
			newList.append(e)
		p = self._player.getPosition()
		if block1.x <= p.x <= block2.x and block1.y <= p.y <= y2:
			newList.append(self._player)
			if renderer.getCameraAt() is not self._player:
				self._player.updatePosition(delta)
		newList.sort(key=lambda k: k.getPosition().y)
		newListLength = len(newList)
		e = 0
		j = block1.y
		while j <= block2.y:
			i = block1.x
			while i <= block2.x:
				b = self._ground.get(hash(BlockVector(i, j)))
				if b is None:
					i += 1
					continue
				b.render(delta)
				i += 1
			j += 1
			while e < newListLength:
				if newList[e].updatePosition().y <= j:
					newList[e].render(delta)
					e += 1
				else:
					break
		self._player.renderSkill(delta)
	
	def setPlayer(self, player: 'Player') -> None:
		self._player = player
		if player is not None:
			renderer.cameraAt(player)
	
	def getPlayer(self) -> Union['Player', None]:
		return self._player
	
	def addEntity(self, entity: 'Entity') -> None:
		self._entityList.add(entity)
	
	def removeEntity(self, entity: 'Entity') -> None:
		self._entityList.remove(entity)
	
	def getEntities(self) -> list['Entity']:
		return list(self._entityList)
	
	def getBlockAt(self, point: Vector | BlockVector) -> Block | None:
		return self._ground.get(hash(point if isinstance(point, BlockVector) else point.clone().getBlockVector()))
	
	def setBlockAt(self, point: BlockVector, block: Block) -> None:
		"""
		设置方块
		"""
		# b = self._ground[hash(point)]
		self._ground[hash(point)] = block
	
	def getRandom(self) -> random.Random:
		return self._seed
	
	def getID(self) -> int:
		return self._id
	
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
	
	def save(self) -> None:
		archive: Archive = Archive(self._name)
		w = archive.dic['world'] = {}
		e = archive.dic['entity'] = []
		archive.dic['name'] = self._name
		archive.dic['id'] = self._id
		archive.dic['player'] = self._player.save()
		for p, b in self._ground.items():
			w[p] = b.save()
		for f in self._entityList:
			e.append(f.save())
		archive.write()
	
	@classmethod
	def load(cls, d: dict) -> 'World':
		world = cls(d['id'], d['name'])
		world._player = entityManager.get('player').load(d['player'])
		for i in (dictWorld := d['world']):
			dictBlock = dictWorld[i]
			block = blockManager.get(dictBlock['id']).load(dictBlock)
			world._ground[hash(block.getBlockPosition())] = block
		for e in d['entity']:
			world._entityList.add(entityManager.get(e['id']).load(e))
		return world
	
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


class DynamicWorld(World):
	def __init__(self, name: str, seed: int | None = None):
		super().__init__(0, name, seed)
		self.generate_map()  # 初始化地图
		player = entityManager.get('player')(Vector(0, 0))
		self.setPlayer(player)
		game.hud.sendMessage(RenderableString('第一个任务有啦！Tab查看任务吧'))
		Music_player.background_play(1)
		Music_player.background_set_volume(0.1)
	
	def generate_map(self) -> None:
		direction = Vector(self._seed.random() - 0.5, self._seed.random() - 0.5)
		while direction.length() < 0.001:
			direction = Vector(self._seed.random() - 0.5, self._seed.random() - 0.5)
		direction.normalize()
		for i in range(-4, 4):
			flag = (i == 3 or i == -4)
			for j in range(-4, 4):
				self._ground[hash(BlockVector(i, j))] = (block := blockManager.dic.get('nature.grass')(BlockVector(i, j)))
				if flag or j == -4 or j == 3:
					block.holdAppend(blockManager.get('hold.fence')(BlockVector(i, j)) if BlockVector(i, j).normalizeClone().subtract(direction).length() > 0.4 else blockManager.get('hold.safety_line')(BlockVector(i, j)))
		## debug
		self.getBlockAt(BlockVector(1, 1)).holdAppend(blockManager.get('hold.door')(BlockVector(1, 1)))
		## debug
		# 第一段生成
		length1 = self._seed.random() * 10 + 20
		ref = direction * length1
		blocks = self.rayTraceBlock(Vector(0, 0), direction, length1)
		for i in blocks:
			if isinstance(i[0], BlockVector):
				self.setBlockAt(i[0], blockManager.dic.get('nature.path' if self._seed.random() < 0.8 else 'nature.grass')(i[0]))
		
		#第二段生成

		def generateBlock(p, rate):
			if rate < 0.4:
				return
			self.setBlockAt(p, blockManager.dic.get('nature.grass' if rate < 0.5 or self._seed.random() > rate else 'nature.path')(p))
			if self.getBlockAt(b := BlockVector(p.x - 1, p.y - 1)) is None:
				generateBlock(b, rate - 0.1)
			if self.getBlockAt(b := BlockVector(p.x - 1, p.y)) is None:
				generateBlock(b, rate - 0.1)
			if self.getBlockAt(b := BlockVector(p.x - 1, p.y + 1)) is None:
				generateBlock(b, rate - 0.1)
			if self.getBlockAt(b := BlockVector(p.x, p.y - 1)) is None:
				generateBlock(b, rate - 0.1)
			if self.getBlockAt(b := BlockVector(p.x, p.y + 1)) is None:
				generateBlock(b, rate - 0.1)
			if self.getBlockAt(b := BlockVector(p.x + 1, p.y - 1)) is None:
				generateBlock(b, rate - 0.1)
			if self.getBlockAt(b := BlockVector(p.x + 1, p.y)) is None:
				generateBlock(b, rate - 0.1)
			if self.getBlockAt(b := BlockVector(p.x + 1, p.y + 1)) is None:
				generateBlock(b, rate - 0.1)
		
		for i in blocks:
			if not isinstance(i[0], BlockVector):
				continue
			pos = i[0]
			if self.getBlockAt(BlockVector(pos.x - 1, pos.y - 1)) is None:
				generateBlock(pos, 0.7)
			if self.getBlockAt(BlockVector(pos.x - 1, pos.y)) is None:
				generateBlock(pos, 0.7)
			if self.getBlockAt(BlockVector(pos.x - 1, pos.y + 1)) is None:
				generateBlock(pos, 0.7)
			if self.getBlockAt(BlockVector(pos.x, pos.y - 1)) is None:
				generateBlock(pos, 0.7)
			if self.getBlockAt(BlockVector(pos.x, pos.y + 1)) is None:
				generateBlock(pos, 0.7)
			if self.getBlockAt(BlockVector(pos.x + 1, pos.y - 1)) is None:
				generateBlock(pos, 0.7)
			if self.getBlockAt(BlockVector(pos.x + 1, pos.y)) is None:
				generateBlock(pos, 0.7)
			if self.getBlockAt(BlockVector(pos.x + 1, pos.y + 1)) is None:
				generateBlock(pos, 0.7)
		for i, j in self._ground.items():
			if j is None:
				continue
			if abs(j.getBlockPosition().x) < 5 and abs(j.getBlockPosition().y) < 5:
				continue
			if self._seed.random() < 0.05:
				self.addEntity(entityManager.get('entity.rice')(Vector(self._seed.random() + j.getBlockPosition().x, self._seed.random() + j.getBlockPosition().y)))
	def tick(self):
		super().tick()
		if game.getWorld().getID() == 0 and game.getWindow() == None and Music_player.musicplaying != 1:
			Music_player.background_play(1)
			Music_player.background_set_volume(0.1)
		

class WitchWorld(World):
	def __init__(self):
		super().__init__(1, '老巫鸡的密室', None)
		self.generate_map()  # 初始化地图
		Music_player.background_play(2)
		Music_player.background_set_volume(0.1)
	
	def generate_map(self) -> None:
		for i in range(0, 15):
			for j in range(-4, 4):
				v = BlockVector(i, j)
				block = blockManager.dic.get('witch.blue')(v)
				self._ground[hash(v)] = block
		player = entityManager.get('player')(Vector(8, 0))
		self.setPlayer(player)
		for i in range(10):
			self.addEntity(entityManager.get('enemy.dog')(Vector(self._seed.random() * 15, self._seed.random() * 8-4)))
		self.addEntity(entityManager.get('entity.witch')(Vector(14, -3)))

# class BabybuiltWorld(World):
