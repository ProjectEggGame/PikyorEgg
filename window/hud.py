import pygame.draw
from pygame import Surface

from render import font
from render.renderable import Renderable
from render.renderer import renderer
from utils import utils
from utils.game import game
from utils.vector import Vector


class Hud(Renderable):
	def __init__(self):
		super().__init__(None)
		self.displayHealth: float = 1.0
		self.lastDisplayHealth: float = 0.0
		self.displayHunger: float = 1.0
		self.lastDisplayHunger: float = 0.0
		self.defaultLength: float = 0.2
	
	def render(self, delta: float, at: Vector | None = None) -> None:
		if game.getWorld() is None:
			return
		player = game.getWorld().getPlayer()
		if player is None:
			return
		self.displayHealth = player.getHealth() / player.getMaxHealth()
		self.displayHunger = player.growth_value / 100
		
		w, h = renderer.getSize().getTuple()
		margin = h >> 6
		barLength = int(w * self.defaultLength)
		sw, sh = (barLength + (margin >> 1), margin << 1)
		barHeight = sh // 3
		surface: Surface = Surface((sw, sh))
		surface.set_colorkey((0, 0, 0))
		surface.set_alpha(0xcc)
		pygame.draw.polygon(surface, (0xff, 0xff, 0xff), [(0, 0), (sw, 0), (sw - (sh >> 1), sh), (0, sh)])
		x0 = (barHeight - 1)
		up = sw - x0 - (barHeight >> 1)
		down = sw - x0 - barHeight
		pygame.draw.polygon(surface, (1, 1, 1), [(x0, x0), (up, x0), (down, h2 := (sh - x0)), (x0, h2)])
		renderer.getCanvas().blit(surface, (margin, margin))
		surface.fill((0, 0, 0))
		surface.set_alpha(0xff)
		up -= barHeight + 1
		down -= barHeight + 1
		
		upNow = barHeight + up * self.displayHealth
		downNow = barHeight + down * self.displayHealth
		pygame.draw.polygon(surface, (0x70, 0xb0, 0x10), [
			(barHeight, barHeight),
			(upNow, barHeight),
			(downNow, barHeight << 1),
			(barHeight, barHeight << 1)
		])
		d = self.lastDisplayHealth - self.displayHealth
		if d < 0:  # 有回血
			d = -d
			pygame.draw.polygon(surface, (0x33, 0x88, 0xff), [
				(upNow, barHeight),
				(barHeight + up * self.lastDisplayHealth, barHeight),
				(barHeight + down * self.lastDisplayHealth, barHeight << 1),
				(downNow, barHeight << 1)
			])
			if d <= 0.002:
				self.lastDisplayHealth = self.displayHealth
			else:
				self.lastDisplayHealth += 0.002 + d * 0.01
		elif d > 0:  # 有扣血
			pygame.draw.polygon(surface, (0xff, 0x33, 0x33), [
				(upNow, barHeight),
				(barHeight + up * self.lastDisplayHealth, barHeight),
				(barHeight + down * self.lastDisplayHealth, barHeight << 1),
				(downNow, barHeight << 1)
			])
			if d <= 0.002:
				self.lastDisplayHealth = self.displayHealth
			else:
				self.lastDisplayHealth -= 0.002 + d * 0.01
		
		upStart = barHeight + (up >> 1) - (barHeight >> 2)
		upEnd = barHeight + up - (barHeight >> 2)
		downStart = barHeight + (down >> 1)
		upNow = upStart + (up - (barHeight >> 2) + 1 >> 1) * self.displayHunger
		downNow = downStart + (down + 1 >> 1) * self.displayHunger
		h = margin
		pygame.draw.polygon(surface, (0xc0, 0xb0, 0x10), [
			(upNow, h),
			(upStart, h),
			(downStart, barHeight << 1),
			(downNow, barHeight << 1)
		])
		d = self.lastDisplayHunger - self.displayHunger
		if d < 0:  # 有回血
			d = -d
			pygame.draw.polygon(surface, (0xf0, 0xf0, 0x60), [
				(upNow, h),
				(upStart + (up - (barHeight >> 2) + 1 >> 1) * self.lastDisplayHunger, h),
				(downStart + (down + 1 >> 1) * self.lastDisplayHunger, barHeight << 1),
				(downNow, barHeight << 1)
			])
			if d <= 0.002:
				self.lastDisplayHunger = self.displayHunger
			else:
				self.lastDisplayHunger += 0.002 + d * 0.01
		elif d > 0:  # 有扣血
			ur = upStart + (up - (barHeight >> 2) + 1 >> 1) * self.lastDisplayHunger
			dr = downStart + (down + 1 >> 1) * self.lastDisplayHunger
			pygame.draw.polygon(surface, (0xee, 0, 0), [
				(upNow, h),
				(ur, h),
				(dr, barHeight << 1),
				(downNow, barHeight << 1)
			])
			if d <= 0.002:
				self.lastDisplayHunger = self.displayHunger
			else:
				self.lastDisplayHunger -= 0.002 + d * 0.01
			upNow = ur
			downNow = dr
		pygame.draw.polygon(surface, (1, 1, 1), [
			(upEnd, h),
			(upNow, h),
			(downNow, barHeight << 1),
			(barHeight + down, barHeight << 1)
		])
		renderer.getCanvas().blit(surface, (margin, margin))
