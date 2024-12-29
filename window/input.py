import pygame.event
from pygame import Surface

from interact import interact
from render.renderer import Location, renderer
from utils import utils
from utils.text import RenderableString, Description
from utils.vector import Vector
from window.widget import Widget
from window.window import Window


class InputWidget(Widget):
	
	def __init__(self, location: Location, x: float, y: float, width: float, height: float, name: RenderableString, description: Description, maxChar: int = 200):
		super().__init__(location, x, y, width, height, name, description, Location.LEFT, None)
		self._maxTextCount: int = 30
		self.textColor.click = self.textColor.hovering = self.textColor.active
		self.caret: int = 0
		self._caretOffset: int = 0  # 用于输入法那头的选中
		self._caret: int = -1  # 用于选中
		self.timeCount: int = 6
		self._realText: str = ''
		self._displayText: str | None = None
		self._dealTimeLimit: int = -1
		self._keyDealing: int = -1
	
	@staticmethod
	def emptyChar(c: chr) -> bool:
		if c == ' ' or c == '\n' or c == '\t' or c == '\r' or c == '\b' or c == '\v' or c == '\f' or c == '\0':
			return True
		return False
	
	def tick(self) -> None:
		if self.timeCount <= -10:
			self.timeCount = 10
		else:
			self.timeCount -= 1
		if self._dealTimeLimit > 0:
			self._dealTimeLimit -= 1
		if interact.keys[pygame.K_BACKSPACE].peek():
			if self._keyDealing == -1:
				interact.keys[pygame.K_BACKSPACE].deal()
				self._keyDealing = pygame.K_BACKSPACE
				self._dealTimeLimit = -1
			elif self._keyDealing != pygame.K_BACKSPACE and interact.keys[pygame.K_BACKSPACE].deal():
				self._keyDealing = pygame.K_BACKSPACE
				self._dealTimeLimit = -1
		else:
			if self._keyDealing == pygame.K_BACKSPACE:
				self._keyDealing = -1
				self._dealTimeLimit = -1
		if interact.keys[pygame.K_DELETE].peek():
			if self._keyDealing == -1:
				interact.keys[pygame.K_DELETE].deal()
				self._keyDealing = pygame.K_DELETE
				self._dealTimeLimit = -1
			elif self._keyDealing != pygame.K_DELETE and interact.keys[pygame.K_DELETE].deal():
				self._keyDealing = pygame.K_DELETE
				self._dealTimeLimit = -1
		else:
			if self._keyDealing == pygame.K_DELETE:
				self._keyDealing = -1
				self._dealTimeLimit = -1
		if interact.specialKeys[pygame.K_UP & interact.KEY_COUNT].peek():
			if self._keyDealing == -1:
				interact.specialKeys[pygame.K_UP & interact.KEY_COUNT].deal()
				self._keyDealing = pygame.K_UP
				self._dealTimeLimit = -1
			elif self._keyDealing != pygame.K_UP and interact.specialKeys[pygame.K_UP & interact.KEY_COUNT].deal():
				self._keyDealing = pygame.K_UP
				self._dealTimeLimit = -1
		else:
			if self._keyDealing == pygame.K_UP:
				self._keyDealing = -1
				self._dealTimeLimit = -1
		if interact.specialKeys[pygame.K_DOWN & interact.KEY_COUNT].peek():
			if self._keyDealing == -1:
				interact.specialKeys[pygame.K_DOWN & interact.KEY_COUNT].deal()
				self._keyDealing = pygame.K_DOWN
				self._dealTimeLimit = -1
			elif self._keyDealing != pygame.K_DOWN and interact.specialKeys[pygame.K_DOWN & interact.KEY_COUNT].deal():
				self._keyDealing = pygame.K_DOWN
				self._dealTimeLimit = -1
		else:
			if self._keyDealing == pygame.K_DOWN:
				self._keyDealing = -1
				self._dealTimeLimit = -1
		if interact.specialKeys[pygame.K_LEFT & interact.KEY_COUNT].peek():
			if self._keyDealing == -1:
				interact.specialKeys[pygame.K_LEFT & interact.KEY_COUNT].deal()
				self._keyDealing = pygame.K_LEFT
				self._dealTimeLimit = -1
			elif self._keyDealing != pygame.K_LEFT and interact.specialKeys[pygame.K_LEFT & interact.KEY_COUNT].deal():
				self._keyDealing = pygame.K_LEFT
				self._dealTimeLimit = -1
		else:
			if self._keyDealing == pygame.K_LEFT:
				self._keyDealing = -1
				self._dealTimeLimit = -1
		if interact.specialKeys[pygame.K_RIGHT & interact.KEY_COUNT].peek():
			if self._keyDealing == -1:
				interact.specialKeys[pygame.K_RIGHT & interact.KEY_COUNT].deal()
				self._keyDealing = pygame.K_RIGHT
				self._dealTimeLimit = -1
			elif self._keyDealing != pygame.K_RIGHT and interact.specialKeys[pygame.K_RIGHT & interact.KEY_COUNT].deal():
				self._keyDealing = pygame.K_RIGHT
				self._dealTimeLimit = -1
		else:
			if self._keyDealing == pygame.K_RIGHT:
				self._keyDealing = -1
				self._dealTimeLimit = -1
		if self._dealTimeLimit > 0:
			self._dealTimeLimit -= 1
		else:
			if self._dealTimeLimit == -1:
				self._dealTimeLimit = 8  # 时间限制 ##########
			match self._keyDealing:
				case pygame.K_BACKSPACE:
					if self._caret != -1:
						self._caret, self.caret = min(self._caret, self.caret), max(self._caret, self.caret)
						self._realText = self._realText[:self._caret] + self._realText[self.caret:]
						self._dealTimeLimit = -1
						self._caret = -1
					else:  # self._caret == -1，需要单个删除
						if self.caret >= len(self._realText):
							self._realText = self._realText[:-1]
							self.caret = len(self._realText)
						else:
							if self.caret == 1:
								self._realText = self._realText[1:]
								self.caret -= 1
							elif self.caret != 0:
								self._realText = self._realText[:self.caret - 1] + self._realText[self.caret:]
								self.caret -= 1
					self._keyDealing = pygame.K_BACKSPACE
					self._displayText = None
				case pygame.K_DELETE:
					if self._caret != -1:
						self._caret, self.caret = min(self._caret, self.caret), max(self._caret, self.caret)
						self._realText = self._realText[:self._caret] + self._realText[self.caret:]
						self._dealTimeLimit = -1
						self._caret = -1
					else:  # self._caret == -1，需要单个删除
						if self._dealTimeLimit > 0:
							self._dealTimeLimit -= 1
						if self.caret < len(self._realText):
							self._realText = self._realText[:self.caret] + self._realText[self.caret + 1:]
				case pygame.K_LEFT:
					if self.caret > 0:
						self.caret -= 1
					self.timeCount = 10
				case pygame.K_RIGHT:
					if self.caret < len(self._realText):
						self.caret += 1
					self.timeCount = 10

	def onInput(self, event) -> None:
		assert isinstance(event, pygame.event.Event)
		assert event.type == pygame.TEXTINPUT
		self.timeCount = 10
		if self._caret != -1:
			self._caret, self.caret = min(self._caret, self.caret), max(self._caret, self.caret)
			self._realText = self._realText[:self._caret] + event.text + self._realText[self.caret:]
			self._caret = -1
		else:
			if self.caret >= len(self._realText):
				self._realText += event.text
				self.caret = len(self._realText)
			else:
				self._realText = self._realText[:self.caret] + event.text + self._realText[self.caret:]
				self.caret += len(event.text)
		self._displayText = None
		self._caretOffset = 0
	
	def onEdit(self, event) -> None:
		assert isinstance(event, pygame.event.Event)
		assert event.type == pygame.TEXTEDITING
		self.timeCount = 10
		if self._caret != -1:
			self._caret, self.caret = min(self._caret, self.caret), max(self._caret, self.caret)
			self._displayText = self._realText[:self._caret] + event.text + self._realText[self.caret:]
		else:
			if self.caret >= len(self._realText):
				self._displayText = self._realText + event.text
			else:
				self._displayText = self._realText[:self.caret] + event.text + self._realText[self.caret:]
		self._caretOffset = event.start
	
	def render(self, delta: float, at: Vector | None = None) -> None:
		colorSelector = self.color.inactive if not self.active else self.color.active
		head = colorSelector & 0xff000000
		colorSelector -= head
		colorSelector = ((colorSelector >> 16) & 0xff, (colorSelector >> 8) & 0xff, colorSelector & 0xff)
		if head == 0xff000000:
			renderer.getCanvas().fill(colorSelector, (self._x, self._y, self._w, self._h))
		elif head != 0:
			s = Surface((self._w, self._h))
			s.fill(colorSelector)
			s.set_alpha(head >> 24)
			renderer.getCanvas().blit(s, (self._x, self._y))
		
		text = self._realText if self._displayText is None else self._displayText
		texts = []
		from utils.text import font as _f
		font = _f.allFonts[10].get(False, False, False, False)
		length = len(text)
		pr = 0
		pe = min(30, length)
		while pr < length:
			while font.size(text[pr:pe])[0] < self._w:
				pe += 1
				if pe >= length:
					break
			while font.size(text[pr:pe])[0] > self._w:
				if pe - pr == 1:
					break
				pe -= 1
			texts.append(text[pr:pe])
			pr = pe
			pe = min(30 + pr, length)
			continue
		if len(texts) == 0:
			offset = renderer.getOffset()
			rect = (self._x + offset.x, offset.y + self._y, 200, 100)
			pygame.key.set_text_input_rect(rect)
			if self.timeCount > 0:
				renderer.getCanvas().blit(font.render('  ', True, ((self.textColor.active >> 16) & 0xff ^ 0xff, (self.textColor.active >> 8) & 0xff ^ 0xff, self.textColor.active & 0xff ^ 0xff), ((self.color.active >> 16) & 0xff ^ 0xff, (self.color.active >> 8) & 0xff ^ 0xff, self.color.active & 0xff ^ 0xff)), (self._x, self._y))
		else:
			y0 = 0
			cc = self.caret + self._caretOffset
			c0 = self.caret
			sfc = Surface((self._w, self._h))
			sfc.fill(((self.color.active >> 16) & 0xff, (self.color.active >> 8) & 0xff, self.color.active & 0xff))
			for i in texts:
				sfc.blit(font.render(i, True, ((self.textColor.active >> 16) & 0xff, (self.textColor.active >> 8) & 0xff, self.textColor.active & 0xff), ((self.color.active >> 16) & 0xff, (self.color.active >> 8) & 0xff, self.color.active & 0xff)), (0, y0))
				if c0 > len(i):
					c0 -= len(i)
				else:
					offset = renderer.getOffset()
					rect = (self._x + font.size(i[:c0])[0] + offset.x, offset.y + y0 + self._y, 200, 100)
					pygame.key.set_text_input_rect(rect)
				if self.timeCount > 0:
					if cc > len(i):
						cc -= len(i)
					else:
						sfc.blit(font.render(i[cc] if cc < len(i) else '  ', True, ((self.textColor.active >> 16) & 0xff ^ 0xff, (self.textColor.active >> 8) & 0xff ^ 0xff, self.textColor.active & 0xff ^ 0xff), ((self.color.active >> 16) & 0xff ^ 0xff, (self.color.active >> 8) & 0xff ^ 0xff, self.color.active & 0xff ^ 0xff)), (font.size(i[:cc])[0], y0))
				y0 += _f.realHalfHeight
			renderer.getCanvas().blit(sfc, (self._x, self._y))


class InputWindow(Window):
	def __init__(self):
		super().__init__('name')
		self._widgets.append(InputWidget(Location.BOTTOM, 0, -0.05, 0.9, 0.2, RenderableString(""), Description()))
		pygame.key.start_text_input()
	
	def onInput(self, event) -> None:
		self._widgets[0].onInput(event)
	
	def onEdit(self, event) -> None:
		self._widgets[0].onEdit(event)
