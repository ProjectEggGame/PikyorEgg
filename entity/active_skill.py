import pygame
from pygame import Surface

from entity.manager import skillManager
from entity.skill import Skill
from render.renderer import renderer, Location
from utils.game import game
from utils.text import SkillDescription, RenderableString, toRomanNumeral
from utils.vector import Vector, BlockVector


def renderSkill(distance: float, halfWidth: float, direction: Vector, color: int) -> None:
	pos: Vector = game.getWorld().getPlayer().updatePosition()
	basis = renderer.getMapBasis()
	canvas: Surface = renderer.getCanvas()
	scale = renderer.getMapScale()
	ver = Vector(direction.y, -direction.x)
	ver.normalize().multiply(halfWidth)
	d = direction.clone().normalize().multiply(scale)
	rightDirection = pos + ver
	rightDirection.multiply(scale)
	leftDirection = pos - ver
	leftDirection.multiply(scale)
	pts = [
		rightDirection.getBlockVector(),
		(rightDirection + (dh := d * (distance - halfWidth))).getBlockVector(),
		(pos * scale + d * distance).getBlockVector(),
		(leftDirection + dh).getBlockVector(),
		leftDirection.getBlockVector(),
	]
	minX = min(pts, key=lambda x: x.x).x
	minY = min(pts, key=lambda x: x.y).y
	maxX = max(pts, key=lambda x: x.x).x
	maxY = max(pts, key=lambda x: x.y).y
	width = int(scale * 0.05)
	offset = BlockVector(minX - width, minY - width)
	size = (maxX - minX + width + width, maxY - minY + width + width)
	pygame.draw.lines(canvas, ((color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff), False, [(i.x + basis.x, i.y + basis.y) for i in pts], width)
	pts[0] = pts[0].subtract(offset).getTuple()
	pts[1] = pts[1].subtract(offset).getTuple()
	pts[2] = pts[2].subtract(offset).getTuple()
	pts[3] = pts[3].subtract(offset).getTuple()
	pts[4] = pts[4].subtract(offset).getTuple()
	sfc = Surface(size)
	sfc.set_alpha(color >> 24)
	sfc.set_colorkey((0, 0, 0))
	pygame.draw.polygon(sfc, ((color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff), pts)
	canvas.blit(sfc, (basis + offset).getTuple())


def renderSkillRange(r: float, color: int) -> None:
	pos: Vector | BlockVector = game.getWorld().getPlayer().updatePosition()
	basis = renderer.getMapBasis()
	canvas: Surface = renderer.getCanvas()
	scale = renderer.getMapScale()
	pos = pos.multiply(scale).getBlockVector().add(basis)
	r = int(r * scale)
	sfc = Surface((r << 1, r << 1))
	pygame.draw.circle(sfc, ((color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff), (r, r), r)
	sfc.set_alpha(color >> 24)
	sfc.set_colorkey((0, 0, 0))
	canvas.blit(sfc, (pos - BlockVector(r, r)).getTuple())
	pygame.draw.circle(canvas, ((color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff), (pos.x, pos.y), r, int(scale * 0.05))


class Active(Skill):
	def __init__(self, skillID: int, description: SkillDescription):
		super().__init__(skillID, description)
	
	def onUse(self, mouseAtMap: Vector) -> None:
		pass
	
	def onTick(self) -> None:
		if self.coolDown > 0:
			self.coolDown -= 1
	
	def render(self, delta: float, mouseAtMap: Vector | BlockVector, chosen: bool = False, isRenderIcon: bool = False) -> int | None:
		"""
		渲染效果。不管是技能释放预览，还是技能最终释放，都执行这个函数
		:param delta: tick偏移
		:param mouseAtMap: BlockVector屏幕图标，或者Vector鼠标在地图上的地图坐标，一般用于确定技能释放位置或方向
		:param chosen: 如果选中，则需要渲染技能预览
		:param isRenderIcon: 指示是否是在渲染技能图标
		:return: int在渲染技能图标后返回；非渲染技能图标时无需返回
		"""
		return super().render(delta, mouseAtMap)


class ActiveFlash(Active):
	def __init__(self):
		super().__init__(101, SkillDescription(self, [RenderableString('\\10\\#ff44aaee闪现'), RenderableString('    \\#ffaa4499向前方闪现一段距离')]))
		self.maxCoolDown = 1200
		self.shouldSetPosition: Vector | None | tuple[Vector, float] = None
	
	def init(self, player) -> None:
		super().init(player)
		self.player.preTick.append(self.onTick)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ff44aaee闪现')
		else:
			return RenderableString('\\10\\#ff44aaee闪现' + (toRomanNumeral(self._level) if self._level < 5 else "(MAX)"))
	
	def getMaxLevel(self) -> int:
		return 5
	
	def upgrade(self) -> bool:
		if self._level < 5 and super().upgrade():
			self.description.d[0] = self.getName()
			self.maxCoolDown = 1300 - self._level * 100
			return True
		return False
	
	def upgradeCost(self) -> int:
		return 10
	
	def onTick(self) -> None:
		if self.coolDown > 0:
			self.coolDown -= 1
		if self.shouldSetPosition is not None:
			if isinstance(self.shouldSetPosition, tuple):
				self.player.basicMaxSpeed += self.shouldSetPosition[1]
				self.player.setPosition(self.shouldSetPosition[0])
				self.shouldSetPosition = None
			elif isinstance(self.shouldSetPosition, Vector):
				self.shouldSetPosition = (self.shouldSetPosition, self.player.basicMaxSpeed)
				self.player.basicMaxSpeed = 0
	
	def render(self, delta: float, at: Vector | BlockVector, chosen: bool = False, isRenderIcon: bool = False) -> None:
		if isRenderIcon:
			ret = super().render(delta, at)
			if self.coolDown > 0:
				s = Surface(self.texture.getUiScaledSurface().get_size())
				s.set_alpha(0xaa)
				renderer.getCanvas().blit(s, at.getTuple())
				renderer.renderString(RenderableString(f'\\11{int(self.coolDown / 20)}'), at.x + (s.get_width() >> 1), at.y + (s.get_height() >> 1), 0xffffffff, Location.CENTER)
			return ret
		elif chosen:
			renderSkill(3, 0.2, at - self.player.getPosition(), 0x554499ee if self.coolDown <= 0 else 0x55ee4444)
	
	def onUse(self, mouseAtMap: Vector) -> None:
		if self.coolDown > 0:
			return
		direction = (mouseAtMap - (pos := self.player.getPosition())).normalize().multiply(3)
		from block.block import Block
		block: Block = game.getWorld().getBlockAt((tar := pos + direction).getBlockVector())
		if block is not None and block.canPass(self.player):
			self.shouldSetPosition = tar
		else:
			res = game.getWorld().rayTraceBlock(tar, direction.reverse(), direction.length())
			if res is None:
				return
			for b, v in res:
				b: Block | BlockVector
				v: Vector
				if isinstance(b, BlockVector):
					continue
				if b.canPass(self.player):
					self.shouldSetPosition = tar + v
					break
		self.coolDown = self.maxCoolDown


class ActiveAdrenalin(Active):
	def __init__(self):
		super().__init__(102, SkillDescription(self, [RenderableString('\\10\\#ffaa0000肾上腺素'), RenderableString('    \\#ffaa4499短时间内不受伤害'), RenderableString(f'    \\#ffaa0000持续0.00秒')]))
		self.timeCount = 0
		self.maxCoolDown = 1200
	
	def init(self, player) -> None:
		super().init(player)
		self.player.preTick.append(self.onTick)
		self.player.preDamage.append(self.onDamage)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffaa0000肾上腺素')
		else:
			return RenderableString('\\10\\#ffaa0000肾上腺素' + (toRomanNumeral(self._level) if self._level < 5 else "(MAX)"))
	
	def getMaxLevel(self) -> int:
		return 5
	
	def upgrade(self) -> bool:
		if self._level < 5 and super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[2] = RenderableString(f'    \\#ffaa0000持续{(60 + self._level * 8) / 20:.2f}秒')
			self.maxCoolDown = 900 - self._level * 60
			return True
		return False
	
	def render(self, delta: float, at: Vector | BlockVector, chosen: bool = False, isRenderIcon: bool = False) -> int | None:
		if isRenderIcon:
			ret = super().render(delta, at)
			if self.coolDown > 0:
				s = Surface(self.texture.getUiScaledSurface().get_size())
				s.set_alpha(0xaa)
				renderer.getCanvas().blit(s, at.getTuple())
				renderer.renderString(RenderableString(f'\\11{int(self.coolDown / 20)}'), at.x + (s.get_width() >> 1), at.y + (s.get_height() >> 1), 0xffffffff, Location.CENTER)
			return ret
		elif chosen:
			renderSkillRange(2, 0x554499ee if self.coolDown <= 0 else 0x55ee4444)
	
	def onTick(self) -> None:
		if self.coolDown > 0:
			self.coolDown -= 1
		if self.timeCount > 0:
			self.timeCount -= 1
	
	def onUse(self, mouseAtMap: Vector) -> None:
		if self.coolDown > 0:
			return
		self.timeCount = 60 + self._level * 8
		self.coolDown = self.maxCoolDown
	
	def onDamage(self, damage: float, entity) -> float:
		if self.timeCount > 0 and entity is not self.player and not isinstance(entity, str):
			return 0
		else:
			return damage


class ActiveAttack(Active):
	def __init__(self):
		super().__init__(103, SkillDescription(self, [RenderableString('\\10\\#ffeeee00猛啄'), RenderableString('    \\#ffaa4499向狐狸发起进攻！'), RenderableString(f'    \\#ffaa4499攻击范围 1.5L 2W'), RenderableString(f'    \\#ffeeee00对范围内狐狸造成0点伤害')]))
	
	def init(self, player) -> None:
		super().init(player)
		self.player.preTick.append(self.onTick)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffeeee00猛啄')
		else:
			return RenderableString('\\10\\#ffeeee00猛啄' + (toRomanNumeral(self._level) if self._level < 10 else "(MAX)"))
	
	def upgrade(self) -> bool:
		if self._level < 10 and super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[3] = RenderableString(f'    \\#ffeeee00对范围内狐狸造成{10 + self._level}点伤害')
			return True
		return False
	
	def render(self, delta: float, mouseAtMap: Vector | BlockVector, chosen: bool = False, isRenderIcon: bool = False) -> int | None:
		if isRenderIcon:
			ret = super().render(delta, mouseAtMap)
			return ret
		elif chosen:
			renderSkill(1.5, 1, mouseAtMap - self.player.getPosition(), 0x55eeee00 if self.coolDown <= 0 else 0x55ee4444)
	
	def onUse(self, mouseAtMap: Vector) -> None:
		if self.coolDown > 0:
			return
		pos = self.player.getPosition()
		direction = mouseAtMap - pos
		direction.normalize()
		from entity.entity import Damageable
		from entity.entity import Entity
		for e in game.getWorld().getEntities():
			if not isinstance(e, Damageable):
				continue
			assert isinstance(e, Entity) and isinstance(e, Damageable)
			pe = e.getPosition()
			rel = pe - pos
			if rel.lengthManhattan() > 2.2:
				continue
			cross = abs(rel.x * direction.y - rel.y * direction.x)
			if cross > 1:
				continue
			if rel.dot(direction) > 1.5:
				continue
			e.damage(10 + self._level, self.player)


class ActiveSwift(Active):
	def __init__(self):
		super().__init__(104, SkillDescription(self, [RenderableString('\\10\\#ff0088cc疾跑'), RenderableString('    \\#ffaa4499快，快，快……我不行了')]))
		self.timeCount = 0
		self.maxCoolDown = 800
	
	def init(self, player) -> None:
		super().init(player)
		self.player.preTick.append(self.onTick)
	
	def onTick(self) -> None:
		if self.coolDown > 0:
			self.coolDown -= 1
		if self.timeCount > 0:
			self.timeCount -= 1
			if self.timeCount == 0:
				self.player.basicMaxSpeed -= 0.1
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ff0088cc疾跑')
		else:
			return RenderableString('\\10\\#ff0088cc疾跑' + (toRomanNumeral(self._level) if self._level < 10 else "(MAX)"))
	
	def onUse(self, mouseAtMap: Vector) -> None:
		if self.coolDown > 0:
			return
		self.timeCount = 40 + self._level * 5
		self.coolDown = self.maxCoolDown
		self.player.basicMaxSpeed += 0.1
	
	def upgrade(self) -> bool:
		if self._level < 10 and super().upgrade():
			self.description.d[0] = self.getName()
			return True
		return False
	
	def render(self, delta: float, mouseAtMap: Vector | BlockVector, chosen: bool = False, isRenderIcon: bool = False) -> int | None:
		if isRenderIcon:
			ret = super().render(delta, mouseAtMap)
			if self.coolDown > 0:
				s = Surface(self.texture.getUiScaledSurface().get_size())
				s.set_alpha(0xaa)
				renderer.getCanvas().blit(s, mouseAtMap.getTuple())
				renderer.renderString(RenderableString(f'\\11{int(self.coolDown / 20)}'), mouseAtMap.x + (s.get_width() >> 1), mouseAtMap.y + (s.get_height() >> 1), 0xffffffff, Location.CENTER)
			return ret
		elif chosen:
			renderSkillRange(1.5, 0x550088cc if self.coolDown <= 0 else 0x550088cc)


skillManager.register(101, ActiveFlash)
skillManager.register(102, ActiveAdrenalin)
skillManager.register(103, ActiveAttack)
skillManager.register(104, ActiveSwift)
