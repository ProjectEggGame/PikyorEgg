import pygame
from typing import TYPE_CHECKING, Union

from entity.manager import entityManager
from utils import utils

if TYPE_CHECKING:
	from block.block import Block

from item.item import BackPack
from interact import interact
from utils.vector import Vector, BlockVector, Matrices
from render.resource import resourceManager
from utils.game import game
from utils.text import RenderableString, Description
from render.resource import Texture
from utils.element import Element


class Entity(Element):
	def __init__(self, entityID: str, name: str, description: Description, texture: list[Texture], speed: float = 0):
		"""
		:param name: 实体名称
		:param description: 实体描述，字符串列表
		:param texture: 纹理列表，一般认为[0][1]是前面，[2][3]是后，[4][5]是左，[6][7]是右。可以参考class Player的构造函数
		"""
		super().__init__(name, description, texture[0])
		self.__renderInterval: int = 6
		self.__velocity: Vector = Vector(0, 0)
		self._position: Vector = Vector(0, 0)
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
	
	def onDamage(self, amount: float) -> float:
		"""
		被伤害时调用，并且在这里实际应用伤害。如果已经死亡，则即便伤害了也不会调用这个函数。返回时，可以忽略负血量的问题直接返回原始伤害值。可重写
		:param amount: 伤害量
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
		if not self._isAlive:
			return
		if health <= 0:
			self._health = 0
			return
		if health >= self._maxHealth:
			self._health = self._maxHealth
			return
	
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
	
	def damage(self, amount: float) -> float:
		"""
		执行伤害
		:param amount: 伤害量
		:return: 实际伤害量
		"""
		if not self._isAlive:
			return 0
		return self.onDamage(amount)


class Player(Entity, Damageable):
	def __init__(self, name: str):
		"""
		创建玩家
		"""
		Entity.__init__(self, "player", name, Description(), [
			resourceManager.getOrNew('player/no_player_1'),
			resourceManager.getOrNew('player/no_player_2'),
			resourceManager.getOrNew('player/no_player_b1'),
			resourceManager.getOrNew('player/no_player_b2'),
			resourceManager.getOrNew('player/no_player_l1'),
			resourceManager.getOrNew('player/no_player_l2'),
			resourceManager.getOrNew('player/no_player_r1'),
			resourceManager.getOrNew('player/no_player_r2'),
		], 0.16)
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
	def load(cls, d: dict, entity=None) -> 'Player':
		p = Player(d['name'])
		super().load(d, p)
		return p


class Rice(Entity):
    def __init__(self, position: Vector):
        super().__init__(position)
        self._id = 'entity.rice'
        self._description = Description([RenderableString("\\#FFFFD700黄色的米粒")])
        self._resource = resourceManager.getOrNew('entity/rice')

    def save(self) -> dict:
        return {
            'id': self._id,
            'position': self._position.save()
        }

    @classmethod
    def load(cls, d: dict) -> 'Rice':
        rice = cls(Vector.load(d['position']))
        return rice

    def render(self, delta: float, at: Vector | None = None) -> None:
        # 实现米粒的渲染逻辑
        pass

    def passTick(self) -> None:
        # 实现米粒的每一帧逻辑
        pass


class Chicken(Entity):
    def __init__(self, position: Vector):
        super().__init__(position)
        self._id = 'entity.chicken'
        self._description = Description([RenderableString("\\#FFD700黄色的小鸡")])
        self.texture = resourceManager.getOrNew('egg/dark_red_birth_egg')
        self.growth_value = 0  # 成长值初始化为0

    def save(self) -> dict:
        data = super().save()
        data['growth_value'] = self.growth_value
        return data

    @classmethod
    def load(cls, d: dict) -> 'Chicken':
        chicken = cls(Vector.load(d['position']))
        chicken.growth_value = d.get('growth_value', 0)
        return chicken

    def render(self, delta: float, at: Vector | None = None) -> None:
        # 实现小鸡的渲染逻辑
        pass

    def passTick(self) -> None:
        # 实现小鸡的每一帧逻辑
        # 检查周围是否有米粒实体
        for entity in self._world._entityList:
            if entity._id == 'entity.rice' and self._position.distanceTo(entity._position) < 1:
                self._world.removeEntity(entity)
                self.growth_value += 10  # 每次吃米粒增加10点成长值
                print(f"小鸡吃掉了一颗米粒，成长值: {self.growth_value}")
                break

    def move(self, direction: Vector)-> None:
        new_position = self._position.clone().add(direction)
        self.setPosition(new_position)

    def moveTo(self, target: Vector) -> None:
        # 简单的移动逻辑，假设每次移动一个单位
        while self._position != target:
            direction = target.subtract(self._position).normalize()
            self.move(direction)
            print(f"小鸡移动到: {self._position}")



# 注册实体
entityManager.register('entity.rice', Rice)
entityManager.register('entity.chicken', Chicken)

entityManager.register('player', Player)

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
	t.adaptsUI()
	t.getSurface().set_colorkey((0, 0, 0))
	t.getMapScaledSurface().set_colorkey((0, 0, 0))
	t.setOffset(Vector(0, -6))
	
