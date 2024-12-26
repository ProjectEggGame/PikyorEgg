from typing import TYPE_CHECKING

from pygame import Surface

from render import font
from utils import utils

if TYPE_CHECKING:
	from block.block import Block


class Description:
	"""
	元素描述。如果重写，可以实现按时间不同变化的
	"""
	
	def __init__(self, d: list['RenderableString'] | None = None):
		self._d = [] if d is None else d
	
	def generate(self) -> list['RenderableString']:
		return self._d
	
	
class BlockDescription(Description):
	"""
	元素描述。如果重写，可以实现按时间不同变化的
	"""
	def __init__(self, block: 'Block', d: list['RenderableString'] | None = None):
		super().__init__(d)
		self._block = block
	
	def generate(self) -> list['RenderableString']:
		return [RenderableString('\\#ffaa4499' + self._block.getBlockPosition().getTuple().__str__())] + self._d


class InnerStringConfig:
	"""
	这是内部类，外部不应直接使用
	"""
	
	def __init__(self):
		self.string: str | None = None
		self.color: int = 0x1_ffff_ffff  # 多打一个一是为了后面的“默认颜色”用的
		self.background: int = 0x1_ffff_ffff  # 同上
		self.font: int = 0
		self.italic: bool = False
		self.bold: bool = False
		self.delete: bool = False
		self.underline: bool = False
		
	def renderAt(self, screen: Surface, x: int, y: int, defaultColor: int, defaultBackground: int = 0) -> int:
		dx = font.allFonts[self.font].draw(screen, self.string, x, y, defaultColor if self.color == 0x1_ffff_ffff else self.color, self.bold, self.italic, self.underline, self.delete, defaultBackground if self.background == 0x1_ffff_ffff else self.background)
		return x + dx
	
	def renderSmall(self, screen: Surface, x: int, y: int, defaultColor: int, defaultBackground: int = 0) -> int:
		smallFont = self.font if self.font >= 10 else self.font + 10
		dx = font.allFonts[smallFont].draw(screen, self.string, x, y, defaultColor if self.color == 0x1_ffff_ffff else self.color, self.bold, self.italic, self.underline, self.delete, defaultBackground if self.background == 0x1_ffff_ffff else self.background)
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
		if self.string is None:
			return 0
		return font.allFonts[self.font].get(self.bold, self.italic, self.underline, self.delete).size(self.string)[0]
	
	def lengthSmall(self) -> int:
		if self.string is None:
			return 0
		smallFont = self.font if self.font >= 10 else self.font + 10
		return font.allFonts[smallFont].get(self.bold, self.italic, self.underline, self.delete).size(self.string)[0]
	
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
	\\xx
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
				config.appendString('\\')
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
				case 'r':
					config = InnerStringConfig()
					if len(i) >= 1:
						config.appendString(i[1:])
				case '0':
					config.font = 0
					if len(i) >= 1:
						if ord('0') <= ord(i[1]) <= ord('2'):
							config.font = int(i[1])
					if len(i) >= 2:
						config.appendString(i[2:])
				case '1':
					config.font = 1
					if len(i) >= 1:
						if ord('0') <= ord(i[1]) <= ord('2'):
							config.font = int(i[1]) + 10
					if len(i) >= 2:
						config.appendString(i[2:])
				case _:
					utils.warn(f'无法识别的字符序列：{i}，来自\n{string}')
		if config.string is not None:
			self.set.append(config)
		
	def length(self) -> int:
		s = 0
		for i in self.set:
			s += i.length()
		return s
	
	def lengthSmall(self) -> int:
		s = 0
		for i in self.set:
			s += i.lengthSmall()
		return s
	
	def renderAt(self, screen: Surface, x: int, y: int, defaultColor: int, defaultBackground: int = 0) -> int:
		for i in self.set:
			x = i.renderAt(screen, x, y, defaultColor, defaultBackground)
		return x
	
	def renderSmall(self, screen: Surface, x: int, y: int, defaultColor: int, defaultBackground: int = 0) -> int:
		for i in self.set:
			x = i.renderSmall(screen, x, y, defaultColor, defaultBackground)
		return x
	
	def __str__(self):
		return '\n'.join([str(i) for i in self.set])
