import math

import pygame
from pygame import Surface, Color

from entity.skill import Skill
from render.renderer import renderer, Location
from render.resource import resourceManager
from utils import utils
from utils.game import game
from utils.text import SkillDescription, RenderableString
from utils.vector import Vector, BlockVector


def renderSkill(distance: float, halfWidth: float, direction: Vector, color: int) -> None:
	pos: Vector = game.getWorld().getPlayer().updatePosition()
	basis = renderer.getMapBasis()
	canvas: Surface = renderer.getCanvas()
	scale = renderer.getMapScale()
	ver = Vector(direction.y, -direction.x)
	ver.normalize().multiply(halfWidth)
	d = direction.clone().normalize().multiply(scale)
	r = pos + ver
	r.multiply(scale)
	l = pos - ver
	l.multiply(scale)
	pts = [
		r.getBlockVector(),
		(r + (dh := d * (distance - halfWidth))).getBlockVector(),
		(pos * scale + d * distance).getBlockVector(),
		(l + dh).getBlockVector(),
		l.getBlockVector(),
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


class Active(Skill):
	def __init__(self, skillID: int, description: SkillDescription):
		super().__init__(skillID, description)
	
	def onUse(self, mouseAtMap: Vector) -> None:
		pass
	
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
		self.name = RenderableString('\\#ff44aaee闪现')
		super().__init__(101, SkillDescription(self, [self.name, RenderableString('    \\#ffaa4499向前方闪现一段距离')]))
		self.coolDown = 0
		self.maxCoolDown = 1200
	
	def init(self, player) -> None:
		super().init(player)
		self.player.preTick.append(self.onTick)
	
	def onTick(self) -> None:
		self.coolDown -= 1
	
	def render(self, delta: float, at: Vector | BlockVector, chosen: bool = False, isRenderIcon: bool = False) -> None:
		if isRenderIcon:
			ret = super().render(delta, at)
			if self.coolDown > 0:
				s = Surface(self.texture.getSystemScaledSurface().get_size())
				s.set_alpha(0xaa)
				renderer.getCanvas().blit(s, at.getTuple())
				renderer.renderString(RenderableString(f'\\11{int(self.coolDown / 20)}'), at.x + (s.get_width() >> 1), at.y + (s.get_height() >> 1), 0xffffffff, Location.CENTER)
			return ret
		elif chosen:
			renderSkill(3, 0.2, at - game.getWorld().getPlayer().getPosition(), 0x554499ee if self.coolDown <= 0 else 0x55ee4444)
	
	def onUse(self, mouseAtMap: Vector) -> None:
		if self.coolDown > 0:
			return
		direction = (mouseAtMap - game.getWorld().getPlayer().getPosition()).normalize().multiply(3)
		game.getWorld().getPlayer().setVelocity(direction)
		game.getWorld().getPlayer().processMove()
		self.coolDown = self.maxCoolDown
