import pygame.font
from pygame import Surface

from utils import utils

fontHeight: int = 30


class Font:
	def __init__(self, file: str, yOffset: int = 0):
		self._addr: str = file
		self._yOffset: float = yOffset
		self._scaledOffset: int = int(yOffset * fontHeight * 0.01)
		try:
			self._file = open(file, 'rb')
			self._font = pygame.font.Font(self._file, fontHeight)
		except Exception as e:
			utils.printException(e)
	
	def close(self) -> None:
		self._file.close()
	
	def get(self, bold: bool, italic: bool, underline: bool, strikeThrough: bool) -> pygame.font.Font:
		self._font.set_bold(bold)
		self._font.set_italic(italic)
		self._font.set_underline(underline)
		self._font.set_strikethrough(strikeThrough)
		return self._font
	
	def draw(self, screen: Surface, string: str, x: int, y: int, color: int, bold: bool, italic: bool, underline: bool, strikeThrough: bool) -> int:
		if color & 0xffffff != 0:
			surface: Surface = self.get(bold, italic, underline, strikeThrough).render(string, True, ((color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff))
			surface.set_colorkey((0, 0, 0))
			surface.set_alpha(color >> 24)
		else:
			surface: Surface = self.get(bold, italic, underline, strikeThrough).render(string, True, ((color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff), (0xff, 0xff, 0xff))
			surface.set_colorkey((0, 0, 0))
			surface.set_alpha(color >> 24)
		screen.blit(surface, (x, y - self._scaledOffset))
		return surface.get_size()[0]
	
	def setHeight(self, h: int) -> None:
		self._file.close()
		self._file = open(self._addr, 'rb')
		self._font = pygame.font.Font(self._file, h)
		self._scaledOffset = int(self._yOffset * h * 0.01)


allFonts: dict[int, Font] = {}


def setScale(scale: float) -> None:
	global fontHeight
	fontHeight = int(scale)
	for i, f in allFonts.items():
		f.setHeight(fontHeight)


def initializeFont() -> None:
	allFonts[0] = Font('./assets/font/stsong.ttf', 19)
	allFonts[1] = Font('./assets/font/stz.ttf', 20)
	allFonts[2] = Font('./assets/font/sword_art_online.ttf')
	allFonts[3] = Font('./assets/font/yumindb.ttf', 2)
	allFonts[4] = Font('./assets/font/jetbrains.ttf', 18)


def finalize() -> None:
	for f in allFonts.values():
		f.close()
