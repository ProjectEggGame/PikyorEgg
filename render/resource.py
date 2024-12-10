from typing import overload

import pygame.image
from pygame import Surface

from interact.interact import Point
from render.renderer import renderer
from utils import utils


# 锁定窗口比例，要么4:3，要么16:9。主要按高度分配

class Resource:
	def __init__(self, file: str):
		try:
			self._file = open(f'assets/texture/{file}.bmp', 'rb')
		except FileNotFoundError:
			try:
				self._file = open('assets/texture/no_texture.bmp', 'rb')
			except FileNotFoundError:
				raise FileNotFoundError("没有找到默认纹理")
		self._surface = pygame.image.load_basic(self._file)
	
	def renderCenter(self, screen: Surface, at: Point | None = None) -> None:
		if at is None:
			screen.blit(self._surface, (0, 0))
		else:
			screen.blit(self._surface, (at.x, at.y))
	
	
class ResourceManager:
	def __init__(self):
		self._textures: dict[str, Resource] = {}
	
	def getOrNew(self, key: str):
		if key in self._textures:
			return self._textures[key]
		resource: Resource = Resource(key)
		self._textures[key] = resource
		return resource


resourceManager: ResourceManager = ResourceManager()
