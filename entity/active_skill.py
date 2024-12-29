from entity.skill import Skill
from utils.text import SkillDescription
from utils.vector import Vector


class Active(Skill):
	def __init__(self, skillID: int, description: SkillDescription):
		super().__init__(skillID, description)
	
	def onUse(self, mouseAtMap: Vector) -> None:
		pass
	
	def render(self, delta: float, mouseAtMap: Vector) -> None:
		"""
		渲染效果。不管是技能释放预览，还是技能最终释放，都执行这个函数
		:param delta: tick偏移
		:param mouseAtMap: 鼠标在地图上的地图坐标，一般用于确定技能释放位置或方向
		"""
		pass
