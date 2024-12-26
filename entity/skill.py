from typing import TYPE_CHECKING, Union

from entity.manager import skillManager
from render.renderable import Renderable
from utils.game import game
from utils.text import Description, RenderableString, toRomanNumeral

if TYPE_CHECKING:
	from entity.entity import Entity


class Skill:
	def __init__(self, skillID: int, description: Description):
		self._level: int = 0
		self._id: int = skillID
		from entity.entity import Player
		self._player: Player = game.getWorld().getPlayer()
		self.description: Description = description
		self.description.d.append(RenderableString('\\#ffee0000  尚未学习此技能'))
	
	def getLevel(self) -> int:
		return self._level
	
	def upgradeCost(self) -> int:
		return self._level + 1
	
	def getName(self=None) -> RenderableString:
		return RenderableString('\\00空白技能')
	
	def upgrade(self) -> bool:
		"""
		升级这个技能
		:return: True - 成功，False - 失败
		"""
		self._level += 1
		return True


class SkillEasySatisfaction(Skill):
	def __init__(self):
		super().__init__(1, Description([RenderableString('\\#ffeeee00爱米'), RenderableString('\\#ffee55dd  可以从米粒中获得额外成长')]))
		self._player.preGrow.append(self.onGrow)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffeeee00爱米')
		else:
			return RenderableString('\\10\\#ffeeee00爱米' + toRomanNumeral(self._level))
	
	def upgrade(self) -> bool:
		if super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[1] = RenderableString(f'\\#ffee55dd  从米粒中获得额外{self._level}点成长')
			return True
		return False
	
	def onGrow(self, amount: int, src: Union['Entity', str]) -> int:
		from entity.entity import Rice
		if isinstance(src, Rice):
			amount += self._level
		return amount
	

class SkillResistance(Skill):
	def __init__(self):
		super().__init__(2, Description([RenderableString('\\#ffeeee00坚毅'), RenderableString(f'\\#ffee55dd  减少受到的0.00%伤害')]))
		self._player.preDamage.append(self.onDamage)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffeeeedd坚毅')
		else:
			return RenderableString('\\10\\#ffeeeedd坚毅' + toRomanNumeral(self._level))
	
	def upgrade(self) -> bool:
		if super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[1] = RenderableString(f'\\#ffee55dd  减少受到的{float(self._level * 100 / (10 + self._level)):.2f}%伤害')
			return True
		return False
	
	def upgradeCost(self) -> int:
		return 1
	
	def onDamage(self, amount: float, src: 'Entity') -> float:
		return amount * 10 / (10 + self._level)


class SkillFastGrow(Skill):
	def __init__(self):
		super().__init__(3, Description([RenderableString('\\#ffee8844揠苗'), RenderableString('\\#ffee55dd  每秒获得0.00点成长'), RenderableString('\\#ffee0000  但是每秒受到0.00点伤害！'), RenderableString('\\#ff888888  当然如果已经完全成长就不会受到伤害')]))
		self._player.preTick.append(self.onTick)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffee8844揠苗')
		else:
			return RenderableString('\\10\\#ffee8844揠苗' + toRomanNumeral(self._level))
	
	def upgrade(self) -> bool:
		if super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[2] = RenderableString(f'\\#ffee0000  但是每秒受到{self._level / 200:.2f}点伤害！')
			return True
		return False
	
	def onTick(self):
		if self._player.grow(self._level / 100, 'SkillFastGrow') != 0:
			self._player.damage(self._level / 200, self._player)


class SkillRevive(Skill):
	def __init__(self):
		super().__init__(4, Description([RenderableString('\\#ffffff66屹立不倒'), RenderableString('\\#ffee55dd  死亡时可以立刻复活'), RenderableString('\\#ffee5555  体力回复 0.00%'), RenderableString('\\#ffee0000  冷却时间 ∞')]))
		self._player.preTick.append(self.onTick)
		self._player.preDeath.append(self.onDeath)
		self._time = 0
		
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffffff66屹立不倒')
		else:
			return RenderableString('\\10\\#ffffff66屹立不倒' + toRomanNumeral(self._level))
	
	def upgrade(self) -> bool:
		if super().upgrade():
			self.description.d[0] = self.getName()
			self.description.d[2] = RenderableString(f'\\#ffee5555  体力回复 {self._level * 100 / (20 + self._level):.2f}%')
			self.description.d[3] = RenderableString(f'\\#ffee0000  冷却时间 {int(120 * 20 / (20 + self._level)):.2f}秒')
			return True
		return False
	
	def onDeath(self):
		if self._time <= 0:
			self._player.setHealth((5 + self._level) / (20 + self._level) * self._player.getMaxHealth())
			self._time = int(2400 * 20 / (20 + self._level))
			return True
		return False
	
	def onTick(self):
		if self._time > 0:
			self._time -= 1


class SkillSwift(Skill):
	def __init__(self):
		super().__init__(5, Description([RenderableString('\\#ffeeee00迅捷'), RenderableString('\\#ffee55dd  快，快，快')]))
		self._player.preTick.append(self.onTick)
	
	def getName(self=None) -> RenderableString:
		if self is None or self._level == 0:
			return RenderableString('\\10\\#ffeeee00迅捷')
		else:
			return RenderableString('\\10\\#ffeeee00迅捷' + toRomanNumeral(self._level))
	
	def upgrade(self) -> bool:
		if super().upgrade():
			self.description.d[0] = self.getName()
			return True
		return False
	
	def onTick(self):
		pass


skillManager.register(0, Skill)
skillManager.register(1, SkillEasySatisfaction)
skillManager.register(2, SkillResistance)
skillManager.register(3, SkillFastGrow)
skillManager.register(4, SkillRevive)
