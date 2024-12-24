import pygame

from interact import interact
from render.renderer import renderer
from utils import utils
from utils.game import game
from window.window import PauseWindow


def processKeys():
	if interact.keys[pygame.K_ESCAPE].deal():
		game.setWindow(PauseWindow())
	if interact.keys[pygame.K_q].deal():
		if game.getWorld() is not None and (p := game.getWorld().getPlayer()) is not None:
			p.heal(10)
			if p.hunger > 100:
				p.hunger = 0
			else:
				p.hunger += 40
	if interact.keys[pygame.K_SPACE].deal():
		if renderer.getCameraAt() is None:
			renderer.cameraAt(game.getWorld().getPlayer())
		else:
			renderer.cameraAt(None)
