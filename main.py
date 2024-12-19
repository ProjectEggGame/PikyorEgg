import time

import pygame
from threading import Thread

from entity.entity import Player
from interact import interact
from interact.key_process import processKeys
from render import font

from render.renderer import renderer
from render.resource import resourceManager
from save import configs
from utils import utils
from utils.game import game
from window.window import FloatWindow, StartWindow
from world.world import World

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
				if renderer.dealMapScaleChange():
					resourceManager.changeMapScale()
					font.setScale(renderer.getSystemScale() * 0.5)
				game.render((nowRender - lastTick) / 60_000_000)
				lastRender = nowRender
				count += 1
			else:
				time.sleep(0.0001)
			if nowRender - lastCount >= 1_000_000_000:
				utils.trace(f"{count}帧/秒")
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
				processKeys()
				lastTick = nowTick
				count += 1
			if nowRender - lastCount >= 1_000_000_000:
				utils.trace(f"{count}tick/秒")
				count = 0
				lastCount = nowRender
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
	renderer.setScreen(screen)
	del info
	# begin 读取设置
	try:
		config: dict[str, any] = configs.readConfig()
		game.readConfig(config)
		renderer.readConfig(config)
		utils.readConfig(config)
	except Exception as e:
		utils.printException(e)
		game.running = False
	# end 读取设置
	# 游戏初始化
	font.initializeFont()
	player: Player = Player('Anonymous')
	renderer.cameraAt(player)
	game.setWindow(StartWindow())
	game.mainWorld = World.generateDefaultWorld()
	game.mainWorld.addPlayer(player)
	game.floatWindow = FloatWindow()
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
						game.floatWindow.submit(None)  # 移动更新floatWindow
						interact.onMouse(event)
						interact.mouse.subtract(renderer.getOffset())  # interact不能导入renderer，委托此处修正鼠标位置
						if game.getWindow() is not None:
							game.getWindow().passMouseMove(event)
					case pygame.MOUSEBUTTONDOWN:
						interact.onMouse(event)
						if game.getWindow() is not None:
							game.getWindow().passMouseDown(event)
					case pygame.MOUSEBUTTONUP:
						interact.onMouse(event)
						if game.getWindow() is not None:
							game.getWindow().passMouseUp(event)
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
		config: dict[str, any] = game.writeConfig()
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
