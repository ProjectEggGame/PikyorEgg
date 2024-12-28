import random

import pygame
from typing import TYPE_CHECKING, Union, Callable

from entity.manager import entityManager, skillManager
from entity.skill import Skill
from utils import utils
from window.window import DeathWindow

if TYPE_CHECKING:
	from block.block import Block

from item.item import BackPack
from interact import interact
from utils.vector import Vector, BlockVector, Matrices
from render.resource import resourceManager
from utils.game import game
from utils.text import RenderableString, EntityDescription
from render.resource import Texture
from utils.element import Element


class Entity(Element):
	def __init__(self, entityID: str, name: str, description: EntityDescription, texture: list[Texture], position: Vector, speed: float = 0):
		"""
		:param name: 实体名称
		:param description: 实体描述，字符串列表
		:param texture: 纹理列表，一般认为[0][1]是前面，[2][3]是后，[4][5]是左，[6][7]是右。可以参考class Player的构造函数
		"""
		super().__init__(name, description, texture[0])
		self.__renderInterval: int = 6
		self.__velocity: Vector = Vector(0, 0)
		self._position: Vector = position
		self.basicMaxSpeed: float = speed
		self._maxSpeed: float = speed
		self._setVelocity: Vector = Vector(0, 0)
		self._textureSet: list[Texture] = texture
		self._id: str = entityID
	
	def __processMove(self) -> None:
		if (vLength := self._setVelocity.length()) == 0:
			self.__velocity.set(0, 0)
			return
		rayTraceResult: list[tuple[Union['Block', BlockVector], Vector]] = game.getWorld().rayTraceBlock(self._position, self._setVelocity, vLength)
		for block, vector in rayTraceResult:
			block: Union['Block', BlockVector]  # 命中方块，或者命中方块坐标
			vector: Vector  # 起始点->命中点
			if not isinstance(block, BlockVector):
				if block.canPass(self):  # 可通过方块，跳过
					continue
				block = block.getBlockPosition()
			block: BlockVector
			newPosition: Vector = self._position + vector
			newVelocity: Vector = self._setVelocity - vector
			rel: list[tuple[BlockVector, Vector]] | BlockVector | None = block.getRelativeBlock(newPosition, newVelocity)
			if rel is None:  # 在中间
				continue
			elif isinstance(rel, BlockVector):  # 撞边不撞角
				vel2: Vector = (Matrices.xOnly if rel.x == 0 else Matrices.yOnly) @ newVelocity
				for b, v in game.getWorld().rayTraceBlock(newPosition, vel2, vel2.length()):
					if not isinstance(b, BlockVector):
						if b.canPass(self):
							continue
						# 还得判断钻缝的问题
						b = b.getBlockPosition()
					grb = b.getRelativeBlock(newPosition + v, v)
					if not isinstance(grb, list) or len(grb) == 0:
						continue
					b2 = game.getWorld().getBlockAt(grb[0][0])
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
					relativeBlock: Union['Block', None] = game.getWorld().getBlockAt(rel[0][0])
					if relativeBlock is None or not relativeBlock.canPass(self):  # 碰一边，然后恰好撞墙
						self.__velocity.set(vector)
					else:
						self.__velocity.set(vector + rel[0][1])
					return
				# 碰一边处理结束，顶角处理开始
				# 都能过的话，无脑，0优先。
				# 然后这里好像还要再trace一次新的方向看看
				relativeBlock: Union['Block', None] = game.getWorld().getBlockAt(rel[0][0])
				if relativeBlock is not None and relativeBlock.canPass(self):  # 0能过，trace新方向
					for b, v in game.getWorld().rayTraceBlock(newPosition, rel[0][1], rel[0][1].length()):
						if not isinstance(b, BlockVector):
							if b.canPass(self):
								continue
							# 还得判断钻缝的问题
							b = b.getBlockPosition()
						grb = b.getRelativeBlock(newPosition + v, v)
						if not isinstance(grb, list) or len(grb) == 0:
							continue
						b2 = game.getWorld().getBlockAt(grb[0][0])
						if b2 is None or not b2.canPass(self):
							self.__velocity.set(vector + v)
							return
					# 钻缝问题处理结束
					# 退出for循环，说明全部通过
					self.__velocity.set(vector + rel[0][1])
					return
				relativeBlock = game.getWorld().getBlockAt(rel[1][0])
				if relativeBlock is not None and relativeBlock.canPass(self):  # 1能过，trace新方向
					for b, v in game.getWorld().rayTraceBlock(newPosition, rel[1][1], rel[1][1].length()):
						if not isinstance(b, BlockVector):
							if b.canPass(self):
								continue
							# 还得判断钻缝的问题
							b = b.getBlockPosition()
						grb = b.getRelativeBlock(newPosition + v, v)
						if not isinstance(grb, list) or len(grb) == 0:
							continue
						b2 = game.getWorld().getBlockAt(grb[0][0])
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
		if abs(self.__velocity.x) >= abs(self.__velocity.y):
			if self.__velocity.x < 0:
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
					self._texture = self._textureSet[4]
			elif self.__velocity.x > 0:
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
					self._texture = self._textureSet[6]
		else:
			if self.__velocity.y < 0:
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
					self._texture = self._textureSet[2]
			elif self.__velocity.y > 0:
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
					self._texture = self._textureSet[0]
		self.tick()
	
	def tick(self) -> None:
		"""
		交由具体类重写
		"""
		pass
	
	def render(self, delta: float, at: Vector | None) -> None:
		self._texture.renderAtMap(self._position + self.__velocity * delta)
	
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
	
	def save(self) -> dict:
		return {
			"id": self._id,
			"position": self._position.save(),
			"velocity": self.__velocity.save(),
			"name": self.name,
			"maxSpeed": self._maxSpeed,
		}
	
	@classmethod
	def load(cls, d: dict, entity: Union['Entity', None] = None) -> Union['Entity', None]:
		"""
		:param d: 加载字典
		:param entity: 默认None，用于区分手动调用和自动调用。手动调用必须传入，理论上不允许自动调用
		:return: 返回entity
		"""
		entity._id = d["id"]
		entity.__velocity = Vector.load(d["velocity"])
		entity.name = d["name"]
		entity._maxSpeed = d["maxSpeed"]
		entity._position = Vector.load(d["position"])
		return entity


class Damageable:
	"""
	所有有血条的实体都要额外继承这个类
	"""
	
	def __init__(self, maxHealth: float = 100, health: float | None = None):
		self._health: float = health or maxHealth
		self._maxHealth: float = maxHealth
		self._isAlive: bool = True
	
	def onDeath(self) -> None:
		"""
		死亡时调用，可重写
		"""
		game.getWorld().removeEntity(self)
	
	def onHeal(self, amount: float) -> float:
		"""
		被治疗时调用，并且在这里实际应用回复。如果已经死亡，则即便恢复了也不会调用这个函数。可重写
		:param amount: 治疗量
		:return: 实际治疗量
		"""
		if amount <= 0:
			return 0
		delta: float = self._maxHealth - self._health
		if amount >= delta:
			self._health = self._maxHealth
			return delta
		else:
			self._health += amount
			return amount
	
	def onDamage(self, amount: float, src: Entity) -> float:
		"""
		被伤害时调用，并且在这里实际应用伤害。如果已经死亡，则即便伤害了也不会调用这个函数。返回时，可以忽略负血量的问题直接返回原始伤害值。可重写
		:param amount: 伤害量
		:param src: 伤害来源
		:return: 实际伤害量
		"""
		if amount < 0:
			return 0
		if amount >= self._health:
			self._health = 0
			self._isAlive = False
			self.onDeath()
			return amount
		else:
			self._health -= amount
			return amount
	
	def setHealth(self, health: float) -> None:
		"""
		设置生命值
		"""
		if health <= 0:
			self._health = 0
			return
		if health >= self._maxHealth:
			self._health = self._maxHealth
			return
		self._health = health
	
	def setMaxHealth(self, maxHealth: float) -> None:
		self._maxHealth = maxHealth
	
	def getHealth(self) -> float:
		return self._health
	
	def getMaxHealth(self) -> float:
		return self._maxHealth
	
	def heal(self, amount: float) -> float:
		"""
		执行治疗
		:param amount: 治疗量
		:return: 实际治疗值
		"""
		if not self._isAlive:
			return 0
		return self.onHeal(amount)
	
	def damage(self, amount: float, src: 'Entity') -> float:
		"""
		执行伤害
		:param amount: 伤害量
		:param src: 伤害来源
		:return: 实际伤害量
		"""
		if not self._isAlive:
			return 0
		return self.onDamage(amount, src)
	
	def save(self) -> dict:
		return {
			"health": self._health,
			"maxHealth": self._maxHealth,
			"isAlive": self._isAlive
		}
	
	@classmethod
	def load(cls, d: dict, entity: Union['Damageable', None]) -> 'Damageable':
		entity._health = d["health"]
		entity._maxHealth = d["maxHealth"]
		entity._isAlive = d["isAlive"]
		return entity


class DeprecatedPlayer(Entity, Damageable):
	def __init__(self, name: str):
		"""
		创建玩家
		"""
		Entity.__init__(self, "player", name, EntityDescription(self), [
			resourceManager.getOrNew('player/no_player_1'),
			resourceManager.getOrNew('player/no_player_2'),
			resourceManager.getOrNew('player/no_player_b1'),
			resourceManager.getOrNew('player/no_player_b2'),
			resourceManager.getOrNew('player/no_player_l1'),
			resourceManager.getOrNew('player/no_player_l2'),
			resourceManager.getOrNew('player/no_player_r1'),
			resourceManager.getOrNew('player/no_player_r2'),
		], Vector(), 0.16)
		Damageable.__init__(self, 100)
		self.inventory = BackPack()
		self.hunger = 0
	
	def onDeath(self) -> None:
		utils.info('死亡')
	
	def tick(self) -> None:
		v: Vector = Vector()
		if game.getWindow() is None:
			if interact.keys[pygame.K_w].peek():
				v.add(0, -1)
			if interact.keys[pygame.K_a].peek():
				v.add(-1, 0)
			if interact.keys[pygame.K_s].peek():
				v.add(0, 1)
			if interact.keys[pygame.K_d].peek():
				v.add(1, 0)
		self.setVelocity(v.normalize().multiply(self._maxSpeed))
	
	@classmethod
	def load(cls, d: dict, entity=None) -> 'DeprecatedPlayer':
		p = DeprecatedPlayer(d['name'])
		super().load(d, p)
		return p


class Rice(Entity):
	def __init__(self, position: Vector):
		super().__init__('entity.rice', '米粒', EntityDescription(self, [RenderableString("\\#FFFFD700黄色的米粒")]), [resourceManager.getOrNew('entity/rice')], position, 0)
	
	def tick(self) -> None:
		player = game.getWorld().getPlayer()
		if player is not None and player.getPosition().distanceManhattan(self.getPosition()) <= 0.6:
			player.grow(2, self)
			game.getWorld().removeEntity(self)
			game.getWorld().addEntity(Rice(Vector(game.getWorld().getRandom().uniform(-50, 50), game.getWorld().getRandom().uniform(-50, 50))))
	
	@classmethod
	def load(cls, d: dict, entity: Union['Entity', None] = None) -> Union['Entity', None]:
		e = Rice(Vector.load(d['position']))
		return Entity.load(d, e)


class Stick(Entity):
	def __init__(self, position: Vector):
		super().__init__('entity.stick', '树枝', EntityDescription(self, [RenderableString("\\#FFFFD700坚硬的树枝")]), [resourceManager.getOrNew('entity/stick')], position, 0)
	
	def tick(self) -> None:
		player = game.getWorld().getPlayer()
		if player is not None and player.getPosition().distanceManhattan(self.getPosition()) <= 0.6:
			player.grow(2, self)
			game.getWorld().removeEntity(self)
			game.getWorld().addEntity(Stick(Vector(game.getWorld().getRandom().uniform(-50, 50), game.getWorld().getRandom().uniform(-50, 50))))
	
	@classmethod
	def load(cls, d: dict, entity: Union['Entity', None] = None) -> Union['Entity', None]:
		e = Stick(Vector.load(d['position']))
		return Entity.load(d, e)


class Player(Entity, Damageable):
	def __init__(self, position: Vector):
		Entity.__init__(self, 'player', 'Chick', EntityDescription(self, [RenderableString("\\#FFFFD700黄色的小鸡"), RenderableString('\\/    也就是你')]), [
			resourceManager.getOrNew('player/chick_1'),
			resourceManager.getOrNew('player/chick_1'),
			resourceManager.getOrNew('player/chick_b1'),
			resourceManager.getOrNew('player/chick_b1'),
			resourceManager.getOrNew('player/chick_l1'),
			resourceManager.getOrNew('player/chick_l1'),
			resourceManager.getOrNew('player/chick_r1'),
			resourceManager.getOrNew('player/chick_r1'),
		], position, 0.16)
		Damageable.__init__(self, 100)
		self.growth_value: float = 0  # 成长值初始化为0
		self.backpack_stick: float = 0  # 背包里树枝数量初始化为0
		self.preDeath: list[Callable[[], bool]] = []  # () -> bool是否取消
		self.preDamage: list[Callable[[float, Entity], float]] = []  # (float值, Entity来源) -> float更改后的值
		self.postDamage: list[Callable[[float, Entity], None]] = []  # (float值, Entity来源) -> None
		self.preTick: list[Callable[[], None]] = []
		self.postTick: list[Callable[[], None]] = []
		self.preGrow: list[Callable[[int, Entity | str], int]] = []
		self.postGrow: list[Callable[[int, Entity | str], None]] = []
		self.prePick: list[Callable[[int, Entity | str], None]] = []
		self.postPick: list[Callable[[int, Entity | str], None]] = []
		self.skills: dict[int, Skill] = {}
		self.__allSkills: dict[int, Skill] = skillManager.dic.copy()
		self.__allSkills.pop(0)

	def onDeath(self) -> None:
		flag = True
		for i in self.preDeath:
			if i():
				flag = False
		if flag:
			utils.info('死亡')
			game.setWindow(DeathWindow())
		else:
			self._isAlive = True
			
	def onDamage(self, amount: float, src: Entity) -> float:
		for i in self.preDamage:
			amount = i(amount, src)
		amount = Damageable.onDamage(self, amount, src)
		for i in self.postDamage:
			i(amount, src)
		return amount
	
	def save(self) -> dict:
		data = Entity.save(self)
		data.update(Damageable.save(self))
		data['growth_value'] = self.growth_value
		return data
	
	@classmethod
	def load(cls, d: dict, entity: Union['Player', None] = None) -> 'Player':
		chicken = Player(Vector.load(d['position']))
		chicken.growth_value = d['growth_value']
		Entity.load(d, chicken)
		Damageable.load(d, chicken)
		return chicken
	
	def grow(self, amount: float, src: Entity | str) -> float:
		for i in self.preGrow:
			amount = i(amount, src)
		if self.growth_value == 100:
			return 0
		val = self.growth_value + amount
		if val > 100:
			self.growth_value = 100
			ret = amount + 100 - self.growth_value
		else:
			self.growth_value = val
			ret = amount
		for i in self.postGrow:
			i(ret, src)
		return ret
	
	def pick(self, amount: int, src: Entity | str) -> int:
		for i in self.prePick:
			amount = i(amount, src)
		if self.backpack_stick == 100:
			return 0
		val = self.backpack_stick + amount
		if val > 100:
			self.backpack_stick = 100
			ret = amount + 100 - self.backpack_stick
		else:
			self.backpack_stick = val
			ret = amount
		for i in self.postPick:
			i(ret, src)
		return ret
	
	def tick(self) -> None:
		for i in self.preTick:
			i()
		v: Vector = Vector()
		if game.getWindow() is None:
			if interact.keys[pygame.K_w].peek():
				v.add(0, -1)
			if interact.keys[pygame.K_a].peek():
				v.add(-1, 0)
			if interact.keys[pygame.K_s].peek():
				v.add(0, 1)
			if interact.keys[pygame.K_d].peek():
				v.add(1, 0)
			if interact.specialKeys[pygame.K_LSHIFT & interact.KEY_COUNT].peek():
				self._maxSpeed = self.basicMaxSpeed * 0.5
			elif interact.specialKeys[pygame.K_LCTRL & interact.KEY_COUNT].peek():
				self._maxSpeed = self.basicMaxSpeed * 2
			else:
				self._maxSpeed = self.basicMaxSpeed
			## debug
			if interact.keys[pygame.K_q].deal():
				self.grow(100, self)
			## debug
			if interact.keys[pygame.K_r].deal():
				if self.growth_value < 100:
					game.hud.sendMessage(RenderableString('\\#ffee0000你还没长大，不能下蛋~'))
				else:
					self.growth_value -= 100
					game.hud.sendMessage(RenderableString('你成功下了一个蛋~'))
					game.getWorld().addEntity(BlueEgg(self._position.clone()))
					if len(self.__allSkills) > 0:
						k = game.getWorld().getRandom().sample(sorted(self.__allSkills), 1)
						self.skills[k[0]] = self.__allSkills.pop(k[0])()
						self.skills[k[0]].upgrade()
						game.hud.sendMessage(RenderableString('你获得了新的技能：') + self.skills[k[0]].getName())
		self.setVelocity(v.normalize().multiply(self._maxSpeed))
		for i in self.postTick:
			i()


class Coop(Entity):
	def __init__(self, position: Vector):
		super().__init__('entity.coop', '鸡窝', EntityDescription(self, [RenderableString('鸡舍')]), [resourceManager.getOrNew('entity/coop')], position, 0)
	
	@classmethod
	def load(cls, d: dict, entity: Union['Entity', None] = None) -> Union['Entity', None]:
		e = Coop(Vector.load(d['position']))
		return Entity.load(d, e)


class BlueEgg(Entity):
	def __init__(self, position: Vector):
		super().__init__('entity.egg.blue', '蓝色的蛋', EntityDescription(self, [RenderableString('\\#FF00D7FF蓝色的蛋'), RenderableString('\\#ff999999\\/  你别管为什么这么大')]), [a := resourceManager.getOrNew('egg/blue_egg'), a, a, a, a, a, a, a], position, 0)
	
	@classmethod
	def load(cls, d: dict, entity: Union['Entity', None] = None) -> Union['Entity', None]:
		e = BlueEgg(Vector.load(d['position']))
		return Entity.load(d, e)


# 注册实体
entityManager.register('entity.rice', Rice)
entityManager.register('entity.stick', Stick)
entityManager.register('player', Player)
entityManager.register('entity.coop', Coop)
entityManager.register('entity.egg.blue', BlueEgg)
entityManager.register('deprecated', DeprecatedPlayer)

for t in [
	resourceManager.getOrNew('player/no_player_1'),
	resourceManager.getOrNew('player/no_player_2'),
	resourceManager.getOrNew('player/no_player_b1'),
	resourceManager.getOrNew('player/no_player_b2'),
	resourceManager.getOrNew('player/no_player_l1'),
	resourceManager.getOrNew('player/no_player_l2'),
	resourceManager.getOrNew('player/no_player_r1'),
	resourceManager.getOrNew('player/no_player_r2'),
]:
	t.getSurface().set_colorkey((0, 0, 0))
	t.getMapScaledSurface().set_colorkey((0, 0, 0))
	t.setOffset(Vector(0, -6))
for t in [
	resourceManager.getOrNew('entity/rice'),
	resourceManager.getOrNew('entity/stick'),
	resourceManager.getOrNew('entity/coop')
]:
	t.getSurface().set_colorkey((0, 0, 0))
	t.getMapScaledSurface().set_colorkey((0, 0, 0))
	t.setOffset(Vector(0, -2))
resourceManager.getOrNew('entity/coop').setOffset(Vector(0, -5))
for t in [
	resourceManager.getOrNew('player/chick_1'),
	resourceManager.getOrNew('player/chick_b1'),
	resourceManager.getOrNew('player/chick_l1'),
	resourceManager.getOrNew('player/chick_r1'),
]:
	t.systemScaleOffset *= 10
	t.adaptsSystem()
	t.getSurface().set_colorkey((1, 1, 1))
	t.getMapScaledSurface().set_colorkey((1, 1, 1))
	t.setOffset(Vector(0, -4))
for t in [
	resourceManager.getOrNew('egg/blue_egg')
]:
	t.getSurface().set_colorkey((0xff, 0xff, 0xff))
	t.getMapScaledSurface().set_colorkey((0xff, 0xff, 0xff))
	t.setOffset(Vector(0, -7))
del t
