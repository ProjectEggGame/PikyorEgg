from pygame import Surface

from interact.interact import Vector
from render.resource import Resource


class Renderable:
	"""
	所有能渲染的东西都继承这个类，game.py:class Game除外
	"""
	def __init__(self, texture: Resource | None):
		self._texture = texture
	
	def render(self, screen: Surface, delta: float, at: Vector | None) -> None:
		"""
		渲染时调用
		:param screen: pygame提供的屏幕
		:param delta: tick偏移。由于20tick/s但是渲染至少60f/s，每tick至少渲染3次。为了保证一些移动的流畅性，delta用于辅助计算移动部件的位置。delta的值为(timePresent - timeLastTick) / timeEveryTick
		:param at: 确定在屏幕上渲染的位置。一般来说，实体位置可以在函数内直接计算，可以忽略这个参数；物品位置需要上级传递。
		"""
		pass
	
	def passRender(self, screen: Surface, delta: float, at: Vector | None = None) -> None:
		"""
		用于内部调用，尽可能地避免重写。重写时必须调用父类方法
		"""
		self.render(screen, delta, at)
		
	def getTexture(self) -> Resource:
		return self._texture
