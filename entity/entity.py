import pygame
from pygame import Surface
from typing import TYPE_CHECKING, Union

from utils import utils

if TYPE_CHECKING:
	from block.block import Block

from item.item import BackPack
from interact import interact
from utils.vector import Vector, BlockVector, Matrices
from render.resource import resourceManager
from utils.game import game
from utils.text import Description
from render.resource import Texture
from utils.element import Element


class Entity(Element):
	def __init__(self, name: str, description: Description, texture: list[Texture], speed: float = 0):
		"""
		:param name: 实体名称
		:param description: 实体描述，字符串列表
		:param texture: 纹理列表，一般认为[0][1]是前面，[2][3]是后，[4][5]是左，[6][7]是右。可以参考class Player的构造函数
		"""
		super().__init__(name, description, texture[0])
		self._position: Vector = Vector(0, 0)
		self._maxSpeed: float = speed
		self.__velocity: Vector = Vector(0, 0)
		self._setVelocity: Vector = Vector(0, 0)
		self.__renderInterval: int = 6
		self._textureSet: list[Texture] = texture
		
	def __processMove(self) -> None:
		if (vLength := self._setVelocity.length()) == 0:
			self.__velocity.set(0, 0)
			return
		rayTraceResult: list[tuple[Union['Block', BlockVector], Vector]] = game.mainWorld.rayTraceBlock(self._position, self._setVelocity, vLength)
		for block, vector in rayTraceResult:
			block: Union['Block', BlockVector]  # 命中方块，或者命中方块坐标
			vector: Vector  # 起始点->命中点
			if type(block) != BlockVector:
				if block.canPass(self):  # 可通过方块，跳过
					continue
				block = block.getBlockPosition()
			block: BlockVector
			newPosition: Vector = self._position + vector
			newVelocity: Vector = self._setVelocity - vector
			rel: list[tuple[BlockVector, Vector]] | BlockVector | None = block.getRelativeBlock(newPosition, newVelocity)
			if rel is None:  # 在中间
				continue
			elif type(rel) == BlockVector:  # 撞边不撞角
				vel2: Vector = (Matrices.xOnly if rel.x == 0 else Matrices.yOnly) @ newVelocity
				for b, v in game.mainWorld.rayTraceBlock(newPosition, vel2, vel2.length()):
					if type(b) != BlockVector:
						if b.canPass(self):
							continue
					# 还得判断钻缝的问题
						b = b.getBlockPosition()
					grb = b.getRelativeBlock(newPosition + v, v)
					if type(grb) != list or len(grb) == 0:
						continue
					b2 = game.mainWorld.getBlockAt(grb[0][0])
					if b2 is None or not b2.canPass(self):
						self.__velocity.set(vector + v)
						return
					# 钻缝问题处理结束
				# 退出for循环，说明全部通过
				self.__velocity.set(vector + vel2)
				return
			elif not rel:  # 空列表
				continue  # 不影响移动
			else:  # 撞角
				if len(rel) == 1:  # 碰一边
					relativeBlock: Union['Block', None] = game.mainWorld.getBlockAt(rel[0][0])
					if relativeBlock is None or not relativeBlock.canPass(self):  # 碰一边，然后恰好撞墙
						self.__velocity.set(vector)
					else:
						self.__velocity.set(vector + rel[0][1])
					return
				# 碰一边处理结束，顶角处理开始
				# 都能过的话，无脑，0优先。
				# 然后这里好像还要再trace一次新的方向看看
				relativeBlock: Union['Block', None] = game.mainWorld.getBlockAt(rel[0][0])
				if relativeBlock is not None and relativeBlock.canPass(self):  # 0能过，trace新方向
					for b, v in game.mainWorld.rayTraceBlock(newPosition, rel[0][1], rel[0][1].length()):
						if type(b) != BlockVector:
							if b.canPass(self):
								continue
						# 还得判断钻缝的问题
							b = b.getBlockPosition()
						grb = b.getRelativeBlock(newPosition + v, v)
						if type(grb) != list or len(grb) == 0:
							continue
						b2 = game.mainWorld.getBlockAt(grb[0][0])
						if b2 is None or not b2.canPass(self):
							self.__velocity.set(vector + v)
							return
						# 钻缝问题处理结束
					# 退出for循环，说明全部通过
					self.__velocity.set(vector + rel[0][1])
					return
				relativeBlock = game.mainWorld.getBlockAt(rel[1][0])
				if relativeBlock is not None and relativeBlock.canPass(self):  # 1能过，trace新方向
					for b, v in game.mainWorld.rayTraceBlock(newPosition, rel[1][1], rel[1][1].length()):
						if type(b) != BlockVector:
							if b.canPass(self):
								continue
						# 还得判断钻缝的问题
							b = b.getBlockPosition()
						grb = b.getRelativeBlock(newPosition + v, v)
						if type(grb) != list or len(grb) == 0:
							continue
						b2 = game.mainWorld.getBlockAt(grb[0][0])
						if b2 is None or not b2.canPass(self):
							self.__velocity.set(vector + v)
							return
						# 钻缝问题处理结束
					# 退出for循环，说明全部通过
					self.__velocity.set(vector + rel[1][1])
					return
				# 都不能过
				self.__velocity.set(vector)
				return
		self.__velocity.set(self._setVelocity)
		return
	
	def passTick(self) -> None:
		"""
		内置函数，不应当额外调用，不应当随意重写。
		重写时必须注意调用父类的同名函数，防止遗漏逻辑。
		除非你一定要覆写当中的代码，否则尽量不要重写这个函数。
		"""
		self._position.add(self.__velocity)
		self.__processMove()
		vcb: BlockVector = self.__velocity.directionalCloneBlock()
		if vcb.x < 0:
			self.__renderInterval -= 1
			if self._texture is self._textureSet[4]:
				if self.__renderInterval <= 0:
					self.__renderInterval = 6
					self._texture = self._textureSet[5]
			elif self._texture is self._textureSet[5]:
				if self.__renderInterval <= 0:
					self.__renderInterval = 6
					self._texture = self._textureSet[4]
			else:
				self.__renderInterval = 6
				self._texture = self._textureSet[4]
		elif vcb.x > 0:
			self.__renderInterval -= 1
			if self._texture is self._textureSet[6]:
				if self.__renderInterval <= 0:
					self.__renderInterval = 6
					self._texture = self._textureSet[7]
			elif self._texture is self._textureSet[7]:
				if self.__renderInterval <= 0:
					self.__renderInterval = 6
					self._texture = self._textureSet[6]
			else:
				self.__renderInterval = 6
				self._texture = self._textureSet[6]
		elif vcb.y < 0:
			self.__renderInterval -= 1
			if self._texture is self._textureSet[2]:
				if self.__renderInterval <= 0:
					self.__renderInterval = 6
					self._texture = self._textureSet[3]
			elif self._texture is self._textureSet[3]:
				if self.__renderInterval <= 0:
					self.__renderInterval = 6
					self._texture = self._textureSet[2]
			else:
				self.__renderInterval = 6
				self._texture = self._textureSet[2]
		elif vcb.y > 0:
			self.__renderInterval -= 1
			if self._texture is self._textureSet[0]:
				if self.__renderInterval <= 0:
					self.__renderInterval = 6
					self._texture = self._textureSet[1]
			elif self._texture is self._textureSet[1]:
				if self.__renderInterval <= 0:
					self.__renderInterval = 6
					self._texture = self._textureSet[0]
			else:
				self.__renderInterval = 6
				self._texture = self._textureSet[0]
		self.tick()
	
	def tick(self) -> None:
		"""
		交由具体类重写
		"""
		pass
	
	def render(self, screen: 'Surface', delta: float, at: Vector | None) -> None:
		self._texture.renderAtMap(screen, self._position + self.__velocity * delta)
	
	def setVelocity(self, v: Vector) -> None:
		"""
		设置速度
		:param v: 目标值
		"""
		self._setVelocity.set(v)
	
	def getPosition(self) -> Vector:
		return self._position.clone()
	
	def getVelocity(self) -> Vector:
		return self.__velocity.clone()


class Player(Entity):
	def __init__(self):
		"""
		创建玩家
		"""
		super().__init__("player", Description(), [
			resourceManager.getOrNew('player/no_player_1'),
			resourceManager.getOrNew('player/no_player_2'),
			resourceManager.getOrNew('player/no_player_b1'),
			resourceManager.getOrNew('player/no_player_b2'),
			resourceManager.getOrNew('player/no_player_l1'),
			resourceManager.getOrNew('player/no_player_l2'),
			resourceManager.getOrNew('player/no_player_r1'),
			resourceManager.getOrNew('player/no_player_r2'),
		], 0.16)
		self.health = 100
		self.maxHealth = 100
		self.inventory = BackPack()
		for t in self._textureSet:
			t.getSurface().set_colorkey((0, 0, 0))
			t.getMapScaledSurface().set_colorkey((0, 0, 0))
			t.setOffset(Vector(0, -6))
	
	def tick(self) -> None:
		v: Vector = Vector()
		if interact.keys[pygame.K_w].peek():
			v.add(0, -1)
		if interact.keys[pygame.K_a].peek():
			v.add(-1, 0)
		if interact.keys[pygame.K_s].peek():
			v.add(0, 1)
		if interact.keys[pygame.K_d].peek():
			v.add(1, 0)
		self.setVelocity(v.normalize().multiply(self._maxSpeed))
		if interact.keys[pygame.K_q].deal():
			utils.info(self.getPosition().toString())
