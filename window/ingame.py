import pygame

from entity.skill import SkillEasySatisfaction
from interact import interact
from render.renderer import Location
from render.resource import resourceManager
from utils.game import game
from utils.text import RenderableString, toRomanNumeral
from utils.vector import Vector
from window.widget import Button
from window.window import Window


class StatusWindow(Window):
	def __init__(self):
		super().__init__("Status", None)
		self.backgroundColor = 0x88000000
		y: float = -0.4
		
		def _1(s, bt):
			def wrapper(x, y_, b_):
				if b_[0] == 1:
					s.upgrade()
					bt.description = s.description
					bt.name = s.getName()
				return True
			return wrapper
		
		for sk in game.getWorld().getPlayer().skills.values():
			b = Button(Location.CENTER, -0.1, y, 0.2, 0.05, sk.getName(), sk.description, Location.CENTER)
			b.onMouseDown = _1(sk, b)
			self._widgets.append(b)
			y += 0.05
	
	def render(self, delta: float, at=None) -> None:
		if game.getWorld().getPlayer() is not None:
			game.getWorld().getPlayer().getTexture().renderAtInterface()
	
	def tick(self) -> None:
		if interact.keys[pygame.K_ESCAPE].deal() or interact.keys[pygame.K_e].deal():
			game.setWindow(self.lastOpen)
