import pygame

from interact import interact
from utils import utils
from utils.game import game
from window.window import PauseWindow


def processKeys():
	if interact.keys[pygame.K_ESCAPE].deal():
		game.setWindow(PauseWindow())
	if interact.keys[pygame.K_q].deal():
		utils.info(interact.mouse)
