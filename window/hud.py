from pygame import Surface

from render import font
from render.renderable import Renderable
from render.renderer import renderer
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
		self.displayHunger = player.hunger / 100
		
		w, h = renderer.getSize().getTuple()
		margin = h >> 4
		renderer.fill(0x88222222, margin >> 1, margin >> 1, int(w * self.defaultLength) << 1, font.fontHeight + margin)
		
		barWidth = int(w * self.defaultLength * self.displayHealth)
		renderer.getCanvas().fill((0x68, 0xa0, 0x10), (margin, margin, barWidth, font.fontHeight >> 1))
		d = self.lastDisplayHealth - self.displayHealth
		if d < 0:  # 有回血
			d = -d
			renderer.getCanvas().fill((0x33, 0x88, 0xff), (barWidth + margin - (w2 := int(w * self.defaultLength * d)), margin, w2, font.fontHeight >> 1))
			if d <= 0.01:
				self.lastDisplayHealth = self.displayHealth
			else:
				self.lastDisplayHealth += 0.001 + d * 0.01
		elif d > 0:  # 有扣血
			renderer.getCanvas().fill((0xff, 0x33, 0x33), (barWidth + margin, margin, int(d * w * self.defaultLength), font.fontHeight >> 1))
			if d <= 0.01:
				self.lastDisplayHealth = self.displayHealth
			else:
				self.lastDisplayHealth -= 0.001 + d * 0.01
		font.allFonts.get(12).draw(renderer.getCanvas(), f'{player.getHealth():.2f}/{player.getMaxHealth():.2f}',  int(self.defaultLength * w + margin), margin, 0xffeeeeee, False, False, False, False, 0)
		
		barWidth = int(w * self.defaultLength * self.displayHunger)
		posY = margin + (font.fontHeight >> 1) + 1
		renderer.getCanvas().fill((0xbb, 0x99, 0x44), (margin, posY, barWidth, font.fontHeight >> 1))
		d = self.lastDisplayHunger - self.displayHunger
		if d < 0:  # 有回血
			d = -d
			renderer.getCanvas().fill((0xff, 0xff, 0x88), (barWidth + margin - (w2 := int(w * self.defaultLength * d)), posY, w2, font.fontHeight >> 1))
			if d <= 0.01:
				self.lastDisplayHunger = self.displayHunger
			else:
				self.lastDisplayHunger += 0.001 + d * 0.01
		elif d > 0:  # 有扣血
			renderer.getCanvas().fill((0xaa, 0x33, 0), (barWidth + margin, posY, int(d * w * self.defaultLength), font.fontHeight >> 1))
			if d <= 0.01:
				self.lastDisplayHunger = self.displayHunger
			else:
				self.lastDisplayHunger -= 0.001 + d * 0.01
		font.allFonts.get(12).draw(renderer.getCanvas(), f'{player.hunger:.2f}/100.00',  int(self.defaultLength * w + margin), posY, 0xffeeeeee, False, False, False, False, 0)
