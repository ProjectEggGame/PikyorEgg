from typing import overload

import pygame.image
from pygame import Surface

from interact.interact import Vector
from render.renderer import renderer


# 锁定窗口比例，要么4:3，要么16:9。主要按高度分配

class Resource:
	"""
	注意，资源渲染的计算方式不同。如果是基于地图渲染，请使用renderAtMap，会根据game.camera等自动计算相对位置。Point给出相对于地图的位置。如果是基于屏幕渲染，例如额外窗口、UI部分，请使用renderAtInterface，会自动适应margin等，Point给出浮点数的屏幕相对
	"""
	def __init__(self, file: str):
		try:
			self._file = open(f'assets/texture/{file}.bmp', 'rb')
		except FileNotFoundError:
			try:
				self._file = open('assets/texture/no_texture.bmp', 'rb')
			except FileNotFoundError:
				raise FileNotFoundError("没有找到默认纹理")
		self._surface: Surface = pygame.image.load_basic(self._file)
		self._mapScaled: Surface = renderer.mapScaleSurface(self._surface)
	
	def renderAtInterface(self, screen: Surface, at: Vector) -> None:
		renderer.render(self._surface, screen, 0, 0, self._surface.get_width(), self._surface.get_height(), at.x, at.y)
	
	def renderAtMap(self, screen: Surface, at: Vector | None = None) -> None:
		"""
		相对于地图渲染
		:param screen: 渲染目标屏幕
		:param at: 地图位置
		"""
		renderer.renderAtMap(self._mapScaled, screen, at)
	
	def changeMapScale(self, scale: float) -> None:
		self._mapScaled = renderer.mapScaleSurface(self._surface)
	
	
class ResourceManager:
	def __init__(self):
		self._textures: dict[str, Resource] = {}
	
	def getOrNew(self, key: str):
		if key in self._textures:
			return self._textures[key]
		resource: Resource = Resource(key)
		self._textures[key] = resource
		return resource
	
	def changeMapScale(self, scale: float) -> None:
		for texture in self._textures.values():
			texture.changeMapScale(scale)


resourceManager: ResourceManager = ResourceManager()
