import pygame
from pygame import Surface
from typing import TYPE_CHECKING, Union

from utils import utils

if TYPE_CHECKING:
	from block.block import Block

from item.item import BackPack
from interact import interact
from utils.vector import Vector, BlockVector
from render.renderer import renderer
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
		:param texture: 纹理列表，一般认为[0][1]是前面，[2][3]是后，[4][5]是左，[6][7]是右
		"""
		super().__init__(name, description, texture[0])
		self._position: Vector = Vector(0, 0)
		self._maxSpeed: float = speed
		self._velocity: Vector = Vector(0, 0)
		self._setVelocity: Vector = Vector(0, 0)
		self.__renderInterval: int = 6
		self._textureSet: list[Texture] = texture
	
	def passTick(self) -> None:
		"""
		内置函数，不应当额外调用，不应当随意重写。
		重写时必须注意调用父类的同名函数，防止遗漏逻辑。
		"""
		self._position.add(self._velocity)
		if (vLength := self._setVelocity.length()) != 0:
			rayTraceResult: list[tuple[Union['Block', BlockVector], Vector]] = game.mainWorld.rayTraceBlock(self._position, self._setVelocity, vLength)
			for block, vector in rayTraceResult:
				if isinstance(block, BlockVector):  # None block
					if vector.length() < vLength:
						self._velocity.set(vector)
					break
				elif not block.canPass(self):
					if vector.length() < vLength:
						self._velocity.set(vector)
					break
		self._velocity.set(self._setVelocity)
		vcb: BlockVector = self._velocity.directionalCloneBlock()
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
					self._texture = self._textureSet[1]
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
		self._texture.renderAtMap(screen, self._position + self._velocity * delta)
	
	def setVelocity(self, v: Vector) -> None:
		"""
		设置速度
		:param v: 目标值
		"""
		self._setVelocity.set(v)
	
	def getPosition(self) -> Vector:
		return self._position.clone()
	
	def getVelocity(self) -> Vector:
		return self._velocity.clone()


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
		
