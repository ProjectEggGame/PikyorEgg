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
		utils.info(interact.mouse)
	if interact.keys[pygame.K_SPACE].deal():
		if renderer.getCameraAt() is None:
			renderer.cameraAt(game.mainWorld.getPlayer())
		else:
			renderer.cameraAt(None)
