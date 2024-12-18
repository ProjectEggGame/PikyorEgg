import pygame.transform
from pygame import Surface

from render import font
from render.font import Font
from utils import utils


class Description:
	"""
	元素描述。这个可以实现按时间不同变化的
	"""
	
	def __init__(self, d: list['RenderableString'] | None = None):
		self._d = [] if d is None else d
	
	def generate(self) -> list['RenderableString']:
		return self._d


class InnerStringConfig:
	"""
	这是内部类，外部不应直接使用
	"""
	
	def __init__(self):
		self.string: str | None = None
		self.color: int = 0x1_ffff_ffff  # 多打一个一是为了后面的“默认颜色”用的
		self.background: int = 0xffffffff
		self.font: int = 0
		self.italic: bool = False
		self.bold: bool = False
		self.delete: bool = False
		self.underline: bool = False
		
	def renderAt(self, screen: Surface, x: int, y: int, defaultColor: int) -> int:
		dx = font.allFonts[self.font].draw(screen, self.string, x, y, defaultColor if self.color == 0x1_ffff_ffff else self.color, self.bold, self.italic, self.underline, self.delete)
		return x + dx
	
	def clone(self) -> 'InnerStringConfig':
		ret: 'InnerStringConfig' = InnerStringConfig()
		ret.color = self.color
		ret.background = self.background
		ret.font = self.font
		ret.italic = self.italic
		ret.bold = self.bold
		ret.delete = self.delete
		ret.underline = self.underline
		return ret
	
	def appendString(self, string: str) -> None:
		if self.string is None:
			self.string = string
		else:
			self.string += string
	
	def length(self) -> int:
		return font.allFonts[self.font].get(self.bold, self.italic, self.underline, self.delete).size(self.string)[0] if self.string is not None else 0
	
	def __str__(self) -> str:
		return \
			f'#{hex(self.color)[2:]}.{hex(self.background)[2:]}"' \
			f'"F?{"/" if self.italic else " "}' \
			f'{"=" if self.bold else " "}' \
			f'{"-" if self.delete else " "}' \
			f'{"_" if self.underline else " "}\n  ' \
			f'{self.string}'


class RenderableString:
	"""
	用于风格化字符串输出。以反斜线开头
	\\#AARRGGBB
	\\.AARRGGBB背景色
	\\f<fontName>
	\\-删除线
	\\_下划线
	\\/斜体
	\\=粗体
	\\r重置
	"""
	
	def __init__(self, string: str):
		self.set: list[InnerStringConfig] = []
		self._parseAppend(string)
	
	def _parseAppend(self, string: str) -> None:
		config = InnerStringConfig()
		subs = string.split('\\')
		if len(subs) == 0:
			return
		if subs[0] != '':
			config.appendString(subs[0])
		self.set.append(config)
		config = config.clone()
		for index in range(1, len(subs)):
			i = subs[index]
			if config.string is not None:
				self.set.append(config)
				config = config.clone()
			if len(i) == 0:
				continue
			match i[0]:
				case '#':
					if len(i) < 9:
						continue
					if len(i) > 9:
						config.appendString(i[9:])
					config.color = int(i[1:9], 16)
				case '.':
					if len(i) < 9:
						continue
					if len(i) > 9:
						config.appendString(i[9:])
					config.background = int(i[1:9], 16)
				case 'f':
					if len(i) < 2:
						continue
					if len(i) > 2:
						config.appendString(i[2:])
					config.font = int(i[1])
				case '-' | 's' | 'S':
					config.delete = True
					if len(i) >= 1:
						config.appendString(i[1:])
				case '_' | 'u' | 'U':
					config.underline = True
					if len(i) >= 1:
						config.appendString(i[1:])
				case '/' | 'i' | 'I':
					config.italic = True
					if len(i) >= 1:
						config.appendString(i[1:])
				case '=' | 'b' | 'B':
					config.bold = True
					if len(i) >= 1:
						config.appendString(i[1:])
				case '\\':
					config.appendString('\\')
				case 'r':
					config = InnerStringConfig()
					if len(i) >= 1:
						config.appendString(i[1:])
				case '0':
					config.font = 0
					if len(i) >= 1:
						config.appendString(i[1:])
				case '1':
					config.font = 1
					if len(i) >= 1:
						config.appendString(i[1:])
				case '2':
					config.font = 2
					if len(i) >= 1:
						config.appendString(i[1:])
				case '3':
					config.font = 3
					if len(i) >= 1:
						config.appendString(i[1:])
				case '4':
					config.font = 4
					if len(i) >= 1:
						config.appendString(i[1:])
				case _:
					utils.warn(f'无法识别的字符序列：{i}，来自\n{string}')
		if config.string is not None:
			self.set.append(config)
		
	def length(self) -> int:
		s = 0
		for i in self.set:
			s += i.length()
		return s
	
	def renderAt(self, screen: Surface, x: int, y: int, defaultColor: int) -> int:
		for i in self.set:
			x = i.renderAt(screen, x, y, defaultColor)
		return x
	
	def __str__(self):
		return '\n'.join([str(i) for i in self.set])
