import random
from typing import Union, TYPE_CHECKING

import pygame

from block.manager import blockManager
from entity.manager import entityManager
from interact import interact
from render.renderer import renderer
from render.resource import resourceManager
from save.save import Archive
from utils import utils
from utils.game import game
from utils.text import RenderableString, Description

if TYPE_CHECKING:
	from entity.entity import Entity, Player, Rice, Coop

from render.renderable import Renderable
from utils.vector import Vector, BlockVector
from block.block import Block, FarmlandBlock, GrassBlock
from window.widget import Widget, Button, Location, ColorSet


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
	
	def setLastOpen(self, last: 'World') -> 'World':
		"""
		:param last: 上一次打开的窗口
		:return: 自身
		"""
		self.lastOpen = last
		return self
	
	def tick(self) -> None:
		for e in self._entityList:
			e.passTick()
		for b in self._ground.values():
			if b is None:
				continue
			b.passTick()
		if self._player is not None:
			self._player.passTick()

		if interact.keys[pygame.K_ESCAPE].deal():
			from window.window import PauseWindow
			game.setWindow(PauseWindow())
		if interact.keys[pygame.K_m].deal():
			from window.window import TaskWindow
			game.setWindow(TaskWindow(4))
		if interact.keys[pygame.K_SPACE].deal():
			if renderer.getCameraAt() is None:
				renderer.cameraAt(self.getPlayer())
				game.hud.sendMessage(RenderableString('\\#cc66ccee视角锁定'))
			elif renderer.cameraOffset.lengthManhattan() == 0:
				game.hud.sendMessage(RenderableString('\\#cc00cc00视角解锁'))
				renderer.cameraAt(None)
			else:
				game.hud.sendMessage(RenderableString('\\#cc7755ee居中锁定'))
				renderer.cameraOffset.set(0, 0)
		if interact.keys[pygame.K_e].deal():
			if self.getPlayer() is not None:
				from window.ingame import StatusWindow
				game.setWindow(StatusWindow())
	
	def render(self, delta: float, at: Union[Vector, None]) -> None:
		ct = renderer.getCenter().getVector().divide(renderer.getMapScale())
		block2 = ct.clone().add(renderer.getCamera().get()).getBlockVector().add(1, 1)
		block1 = ct.reverse().add(renderer.getCamera().get()).getBlockVector().subtract(1, 1)
		newList2 = list(self._entityList)
		if self._player is not None:
			newList2.append(self._player)
		newList = []
		for e in newList2:
			p = e.getPosition()
			if p.x < block1.x or p.x > block2.x or p.y < block1.y or p.y > block2.y:
				continue
			newList.append(e)
		newList.sort(key=lambda k: k.getPosition().y)
		e = 0
		for j in range(block1.y, block2.y + 1):
			for i in range(block1.x, block2.x + 1):
				b = self._ground.get(hash(BlockVector(i, j)))
				if b is None:
					continue
				b.render(delta, at)
			j += 1
			while e < len(newList):
				if newList[e].getPosition().y <= j:
					newList[e].render(delta, at)
					e += 1
				else:
					break
	
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
	
	def setBlockAt(self, point: BlockVector, block: Block) -> Block | None:
		"""
		设置方块，返回原来的方块
		"""
		b = self._ground[hash(point)]
		self._ground[hash(point)] = block
		return b
	
	def getRandom(self) -> random.Random:
		return self._seed
	
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
	def __init__(self, worldID: int, name: str, seed: int | None = None):
		super().__init__(worldID, name, seed)
		self._camera_position: Vector = Vector(0, 0)
		self._lay_egg_button: Button | None = None
		self._chicken_growth = 0  # 小鸡的成长值
		self._chicken_nest_position = BlockVector(-49, 49)  # 鸡窝位置
		self.generate_map()  # 初始化地图
		player = entityManager.get('player')(Vector(0, 0))
		self.setPlayer(player)
		for i in range(200):
			self.addEntity(entityManager.get('entity.rice')(Vector(self._seed.random() * 100 - 50, self._seed.random() * 100 - 50)))
		for i in range(40):
			self.addEntity(entityManager.get('entity.stick')(Vector(self._seed.random() * 100 - 50, self._seed.random() * 100 - 50)))
		for i in range(-50, -39):
			self.getBlockAt(BlockVector(i, 3)).holdAppend(blockManager.get('hold.fence')(BlockVector(i, 3)))
			self.getBlockAt(BlockVector(i, -3)).holdAppend(blockManager.get('hold.fence')(BlockVector(i, -3)))
		for i in range(-2, 3):
			self.getBlockAt(BlockVector(-50, i)).holdAppend(blockManager.get('hold.fence')(BlockVector(-50, i)))
			self.getBlockAt(BlockVector(-40, i)).holdAppend(blockManager.get('hold.safety_line')(BlockVector(-40, i)))
		self.addEntity(entityManager.get('entity.coop')(Vector(4, 4)))
		for i in range(10):
			self.addEntity(entityManager.get('enemy.dog')(Vector(self._seed.random() * 100 - 50, self._seed.random() * 100 - 50)))
		
		#w = int(self._seed.random() * 100 - 51)
		#m = int(self._seed.random() * 100 - 51)
		w = 0
		m = 0
		for i in range(w,w+2):
			for j in range(m,m+2):
				self.getBlockAt(BlockVector(i,j)).holdAppend(blockManager.get('hold.door')(BlockVector(i,j)))
	
	def generate_map(self) -> None:
		for i in range(-50, 50):
			for j in range(-50, 50):
				v = BlockVector(i, j)
				block = blockManager.dic.get(self._seed.choice(['nature.grass', 'nature.path', 'nature.farmland']))(v)
				self._ground[hash(v)] = block
	
	def passTick(self) -> None:
		super().tick()
		if self._player:
			self.update_camera_position()
			if self._player.growth_value >= 100 and not self._lay_egg_button:
				self.create_lay_egg_button()
		
	
	def render(self, delta: float, at: Union[Vector, None]) -> None:
		super().render(delta, at)
		if self._lay_egg_button:
			self._lay_egg_button.render(delta, at)
	
	def update_camera_position(self) -> None:
		if self._player:
			# 设置镜头位置为小鸡位置，但限制在地图范围内
			self._camera_position = self._player.getPosition().subtract(Vector(20, 20))  # 假设镜头跟随小鸡并保持20个单位的距离
			self._camera_position = self._camera_position.clamp(Vector(-30, -30), Vector(30, 30))  # 限制镜头位置在合理范围内
	
	def create_lay_egg_button(self) -> None:
		self._lay_egg_button = Button(
			Location.LEFT_TOP,
			0,
			0,
			0.09,
			0.12,
			RenderableString('下蛋'),
			Description([RenderableString("立即下蛋")]),
			Location.CENTER
		)
		self._lay_egg_button.onMouseDown = self.on_lay_egg_button_click
	
		
	def increase_chicken_growth(self, amount: int) -> None:
		self._chicken_growth += amount
		if self._chicken_growth >= 100:
			self.create_lay_egg_button()
		if self._chicken and self._chicken.growth_value >= 50 and self._chicken.texture.path == 'else/chicken_small':
			self._chicken.texture = resourceManager.getOrNew('else/chicken_big')  # 更改小鸡图片为大图片
	
	def getCameraPosition(self) -> Vector:
		return self._camera_position
	
	def getLayEggButton(self) -> Button | None:
		return self._lay_egg_button
	
	def getChickenGrowth(self) -> int:
		return self._chicken_growth
	
	def getChickenNestPosition(self) -> BlockVector:
		return self._chicken_nest_position


class WitchWorld(World):
	def __init__(self, worldID: int, name: str, seed: int | None = None):
		super().__init__(worldID, name, seed)
		self._camera_position: Vector = Vector(0, 0)
		self._lay_egg_button: Button | None = None
		self._chicken_growth = 0  # 小鸡的成长值
		self._chicken_nest_position = BlockVector(-4, 0)  # 鸡窝位置
		self.generate_map()  # 初始化地图
		player = entityManager.get('player')(Vector(0, 0))
		self.setPlayer(player)
		'''
		for i in range(-50, -39):
			self.getBlockAt(BlockVector(i, 3)).holdAppend(blockManager.get('hold.fence')(BlockVector(i, 3)))
			self.getBlockAt(BlockVector(i, -3)).holdAppend(blockManager.get('hold.fence')(BlockVector(i, -3)))
		for i in range(-2, 3):
			self.getBlockAt(BlockVector(-50, i)).holdAppend(blockManager.get('hold.fence')(BlockVector(-50, i)))
			self.getBlockAt(BlockVector(-40, i)).holdAppend(blockManager.get('hold.safety_line')(BlockVector(-40, i)))
		self.addEntity(entityManager.get('entity.coop')(Vector(4, 4)))

		'''
		for i in range(10):
			self.addEntity(entityManager.get('enemy.dog')(Vector(self._seed.random() * 10 - 5, self._seed.random() * 10 - 5)))
		
		self.addEntity(entityManager.get('entity.witch')(Vector(-4, 0)))

	def generate_map(self) -> None:
		for i in range(-5, 5):
			for j in range(-5, 5):
				v = BlockVector(i, j)
				block = blockManager.dic.get('witch.blue')(v)
				self._ground[hash(v)] = block
	
	
	
	
