import time

import pygame
from threading import Thread, Lock

from entity.entity import Player
from interact import interact
from render import font

from render.renderer import renderer
from render.resource import resourceManager
from save import configs
from utils import utils
from utils.game import game
from window.hud import Hud
from window.window import FloatWindow, StartWindow

# 这句是必要的，会注册到entityManager上
from entity import enemy

nowRender = time.perf_counter_ns()
lastRender = nowRender
nowTick = nowRender
lastTick = nowRender


def renderThread():
	utils.info("渲染线程启动")
	global lastRender
	global nowRender
	count = 0
	lastCount = time.perf_counter_ns()
	while game.running:
		try:
			nowRender = time.perf_counter_ns()
			if nowRender - lastRender >= 5_000_000:
				if renderer.dealScreen4to3Change():
					game.getWindow().onResize()
				if renderer.peekScaleChange():
					resourceManager.changeScale()
					if renderer.systemScaleChanged():
						font.setScale(renderer.getSystemScale() * 0.6)
					renderer.dealScaleChange()
				game.render((nowRender - lastTick) / 60_000_000)
				lastRender = nowRender
				count += 1
			else:
				time.sleep(0.0001)
			if nowRender - lastCount >= 1_000_000_000:
				renderer.fps = count * 1_000_000_000 / (nowRender - lastCount)
				count = 0
				lastCount = nowRender
		except Exception as e:
			utils.printException(e)
			game.running = False
			break
	utils.info("渲染线程退出")


def gameThread():
	utils.info("游戏线程启动")
	count = 0
	lastCount = time.perf_counter_ns()
	global lastTick
	global nowTick
	while game.running:
		try:
			nowTick = time.perf_counter_ns()
			if nowTick - lastTick >= 45_000_000:
				game.tick()
				lastTick = nowTick
				count += 1
			if nowTick - lastCount >= 1_000_000_000:
				renderer.tps = count * 1_000_000_000 / (nowTick - lastCount)
				count = 0
				lastCount = nowTick
			else:
				time.sleep(0.0001)
		except Exception as e:
			utils.printException(e)
			game.running = False
			break
	utils.info("游戏线程退出")


#########################
#         主线程         #
#########################
def mainThread():
	SCREEN_FLAGS = pygame.RESIZABLE
	info = pygame.display.Info()
	pygame.display.set_caption("捡蛋")
	screen = pygame.display.set_mode((info.current_w / 2, info.current_h / 2), SCREEN_FLAGS)
	del info
	# begin 读取设置
	try:
		config: dict[str, any] = configs.readConfig()
		renderer.readConfig(config)
		utils.readConfig(config)
	except Exception as e:
		utils.printException(e)
		game.running = False
	# end 读取设置
	# 游戏初始化
	renderer.setScreen(screen)
	font.initializeFont()
	game.setWindow(StartWindow())
	game.floatWindow = FloatWindow()
	game.hud = Hud()
	# 游戏初始化
	# 启动线程
	gt: Thread = Thread(name="GameThread", target=gameThread)
	rt: Thread = Thread(name="RenderThread", target=renderThread)
	gt.start()
	rt.start()
	utils.info("主线程启动")
	while game.running:
		try:
			for event in pygame.event.get():
				match event.type:
					case pygame.QUIT:
						game.running = False
						utils.info("退出游戏")
					case pygame.KEYDOWN:
						interact.onKey(event)
					case pygame.KEYUP:
						interact.onKey(event)
					case pygame.MOUSEMOTION:
						game.floatWindow.clear()  # 移动更新floatWindow
						interact.onMouse(event)
						interact.mouse.subtract(renderer.getOffset())  # interact不能导入renderer，委托此处修正鼠标位置
						if game.getWindow() is not None:
							game.getWindow().passMouseMove(interact.mouse.x, interact.mouse.y, event.buttons)
						game.processMouse(event)
					case pygame.MOUSEBUTTONDOWN:
						game.floatWindow.clear()
						interact.onMouse(event)
						if game.getWindow() is not None:
							match event.button:
								case 1:
									buttons = (1, 0, 0)
								case 2:
									buttons = (0, 1, 0)
								case 3:
									buttons = (0, 0, 1)
								case _:
									buttons = (0, 0, 0)
							game.getWindow().passMouseDown(interact.mouse.x, interact.mouse.y, buttons)
					case pygame.MOUSEBUTTONUP:
						game.floatWindow.clear()
						interact.onMouse(event)
						if game.getWindow() is not None:
							match event.button:
								case 1:
									buttons = (1, 0, 0)
								case 2:
									buttons = (0, 1, 0)
								case 3:
									buttons = (0, 0, 1)
								case _:
									buttons = (0, 0, 0)
							game.getWindow().passMouseUp(interact.mouse.x, interact.mouse.y, buttons)
					case pygame.VIDEORESIZE:
						renderer.setScreen(pygame.display.set_mode(event.size, SCREEN_FLAGS))
						pygame.display.update()
						if game.getWindow() is not None:
							game.getWindow().onResize()
					case pygame.TEXTINPUT:
						pass
					case pygame.TEXTEDITING:
						pass
					case pygame.ACTIVEEVENT:
						pass
					case pygame.WINDOWENTER:
						pass
					case pygame.WINDOWLEAVE:
						pass
					case pygame.MOUSEWHEEL:
						pass
					case _:
						utils.trace(event)
		except Exception as e:
			utils.printException(e)
			game.running = False
			break
	utils.info("主线程退出")
	if gt.is_alive():
		gt.join()
	if rt.is_alive():
		rt.join()
	# begin 写入设置
	try:
		config: dict[str, any] = {}
		config.update(renderer.writeConfig())
		config.update(utils.writeConfig())
		configs.writeConfig(config)
	except Exception as e:
		utils.printException(e)
		game.running = False
	# end 写入设置
	pygame.display.quit()


#########################
#                       #
#      Pickyor Egg      #
#      Entry Point      #
#                       #
#########################
if __name__ == '__main__':
	ret = pygame.init()
	utils.info(f"pygame初始化成功{ret[0]}模块，失败{ret[1]}模块")
	mainThread()
	pygame.quit()
