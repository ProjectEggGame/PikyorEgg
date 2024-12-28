from typing import TYPE_CHECKING, Union

from pygame import Surface

from entity.manager import skillManager
from render.renderer import renderer, Location
from render.resource import resourceManager
from utils.game import game
from utils.text import SkillDescription, RenderableString, toRomanNumeral
from utils.vector import BlockVector, Vector

if TYPE_CHECKING:
	from entity.entity import Entity


class Skill:
	def __init__(self, skillID: int, description: SkillDescription):
		self._level: int = 0
		self._id: int = skillID
		from entity.entity import Player
		self._player: Player = game.getWorld().getPlayer()
		self.description: SkillDescription = description
		self.texture = resourceManager.getOrNew(f'skill/{self._id}')
		self.texture.adaptsSystem()
		self.texture.adaptsMap(False)
	
	def getLevel(self) -> int:
		return self._level
	
	def upgradeCost(self) -> int:
		return self._level
	
	def getName(self=None) -> RenderableString:
		return RenderableString('\\00空白技能')
	
	def render(self, delta: float, at: BlockVector) -> int:
		"""
		:return: 宽度
		"""
		self.texture.renderAtInterface(at)
		return self.texture.getSystemScaledSurface().get_width()
	
	def upgrade(self) -> bool:
		"""
		升级这个技能
		:return: True - 成功，False - 失败
		"""
		self._level += 1
		return True


class SkillEasySatisfaction(Skill):
	def __init__(self):
		super().__init__(1, SkillDescription([RenderableString('\\#ffeeee00爱米'), RenderableString('\\#ffee55dd    可以从米粒中获得额外成长')]))
		self._player.preGrow.append(self.onGrow)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffeeee00爱米')
		else:
			return RenderableString('\\10\\#ffeeee00爱米' + toRomanNumeral(self._level))
	
	def upgrade(self) -> bool:
		if super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[1] = RenderableString(f'\\#ffee55dd    从米粒中获得额外{self._level}点成长')
			return True
		return False
	
	def onGrow(self, amount: int, src: Union['Entity', str]) -> int:
		from entity.entity import Rice
		if isinstance(src, Rice):
			amount += self._level
		return amount


class SkillResistance(Skill):
	def __init__(self):
		super().__init__(2, SkillDescription([RenderableString('\\#ffeeee00坚毅'), RenderableString(f'\\#ffee55dd    减少受到的0.00%伤害')]))
		self._player.preDamage.append(self.onDamage)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffeeeedd坚毅')
		else:
			return RenderableString('\\10\\#ffeeeedd坚毅' + toRomanNumeral(self._level))
	
	def upgrade(self) -> bool:
		if super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[1] = RenderableString(f'\\#ffee55dd    减少受到的{float(self._level * 100 / (10 + self._level)):.2f}%伤害')
			return True
		return False
	
	def upgradeCost(self) -> int:
		return 1
	
	def onDamage(self, amount: float, src: 'Entity') -> float:
		return amount * 10 / (10 + self._level)


class SkillFastGrow(Skill):
	def __init__(self):
		super().__init__(3, SkillDescription([RenderableString('\\#ffee8844揠苗'), RenderableString('\\#ffee55dd  每秒获得0.00点成长'), RenderableString('\\#ffee0000    但是每秒受到0.00点伤害！'), RenderableString('\\#ff888888    当然如果已经完全成长就不会受到伤害')]))
		self._player.preTick.append(self.onTick)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffee8844揠苗')
		else:
			return RenderableString('\\10\\#ffee8844揠苗' + toRomanNumeral(self._level))
	
	def upgrade(self) -> bool:
		if super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[1] = RenderableString(f'\\#ffee55dd    每秒获得{self._level / 5:.2f}点成长')
			self.description.d[2] = RenderableString(f'\\#ffee0000    但是每秒受到{self._level * 20 / (200 + self._level << 1):.2f}点伤害！')
			return True
		return False
	
	def onTick(self):
		if self._player.grow(self._level / 100, 'SkillFastGrow') != 0:
			self._player.damage(self._level / (200 + self._level << 1), self._player)


class SkillRevive(Skill):
	def __init__(self):
		super().__init__(4, SkillDescription([RenderableString('\\#ffffff66屹立不倒'), RenderableString('\\#ffee55dd    死亡时可以立刻复活'), RenderableString('\\#ffee5555    体力回复 0.00%'), RenderableString('\\#ffee0000    冷却时间 ∞')]))
		self._player.preTick.append(self.onTick)
		self._player.preDeath.append(self.onDeath)
		self._time = 0
	
	def render(self, delta: float, at: BlockVector) -> int:
		ret = super().render(delta, at)
		if self._time > 0:
			s = Surface(self.texture.getSystemScaledSurface().get_size())
			s.set_alpha(0xaa)
			renderer.getCanvas().blit(s, at.getTuple())
			renderer.renderString(RenderableString(f'\\11{int(self._time / 20)}'), at.x + (s.get_width() >> 1), at.y + (s.get_height() >> 1), 0xffffffff, Location.CENTER)
		return ret
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffffff66屹立不倒')
		else:
			return RenderableString('\\10\\#ffffff66屹立不倒' + (toRomanNumeral(self._level) if self._level < 20 else "(MAX)"))
	
	def upgrade(self) -> bool:
		if self._level < 20:
			self._level += 1
			self.description.d[0] = self.getName()
			self.description.d[2] = RenderableString(f'\\#ffee5555    体力回复 {20 + 3 * self._level:.2f}%')
			self.description.d[3] = RenderableString(f'\\#ffee0000    冷却时间 {int(125 - self._level * 5):.2f}秒')
			return True
		return False
	
	def onDeath(self):
		if self._time <= 0:
			self._player.setHealth((20 + 3 * self._level) / 100 * self._player.getMaxHealth())
			self._time = (2500 - self._level * 100)
			game.hud.sendMessage(RenderableString('\\.ccff0000\\#ffeeeeee                 复生！                '))
			return True
		return False
	
	def onTick(self):
		if self._time > 0:
			self._time -= 1


class SkillSwift(Skill):
	def __init__(self):
		super().__init__(5, SkillDescription([RenderableString('\\#ff96F8F5迅捷'), RenderableString('\\#ffee55dd    快，快，快')]))
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ff96F8F5迅捷')
		else:
			return RenderableString('\\10\\#ff96F8F5迅捷' + (toRomanNumeral(self._level) if self._level < 20 else "(MAX)"))
	
	def upgrade(self) -> bool:
		if self._level < 20:
			self._level += 1
			self._player.basicMaxSpeed += 0.01
			self.description.d[0] = self.getName()
			return True
		return False


skillManager.register(0, Skill)
skillManager.register(1, SkillEasySatisfaction)
skillManager.register(2, SkillResistance)
skillManager.register(3, SkillFastGrow)
skillManager.register(4, SkillRevive)
skillManager.register(5, SkillSwift)
