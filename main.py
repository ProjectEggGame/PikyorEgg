import time
import pygame
from threading import Thread
from interact import interact
from render.renderer import renderer
from utils import utils
from utils.game import game

nowRender = time.perf_counter_ns()
lastRender = nowRender
nowTick = nowRender
lastTick = nowRender


def renderThread():
	utils.info("渲染线程启动")
	global lastRender
	global nowRender
	while game.running:
		nowRender = time.perf_counter_ns()
		if nowRender - lastRender >= 1000:
			game.render((nowRender - lastTick) / 50_000)
			lastRender = nowRender
		else:
			time.sleep(0.001)
	utils.info("渲染线程退出")


def gameThread():
	utils.info("游戏线程启动")
	global lastTick
	global nowTick
	while game.running:
		nowTick = time.perf_counter_ns()
		if nowTick - lastTick >= 50_000:
			game.tick()
			lastTick = nowTick
		else:
			time.sleep(0.001)
	utils.info("游戏线程退出")


def mainThread():
	SCREEN_FLAGS = pygame.RESIZABLE
	info = pygame.display.Info()
	pygame.display.set_caption("捡蛋")
	screen = pygame.display.set_mode((info.current_w / 2, info.current_h / 2), SCREEN_FLAGS)
	renderer.setScreen(screen)
	gt: Thread = Thread(name="GameThread", target=gameThread)
	rt: Thread = Thread(name="RenderThread", target=renderThread)
	gt.start()
	rt.start()
	utils.info("主线程启动")
	while game.running:
		try:
			for event in pygame.event.get():
				utils.info(event)
				match event.type:
					case pygame.QUIT:
						game.running = False
						utils.info("退出游戏")
						break
					case pygame.KEYDOWN:
						interact.onKey(event)
						break
					case pygame.KEYUP:
						interact.onKey(event)
						break
					case pygame.MOUSEMOTION:
						interact.onMouse(event)
						break
					case pygame.MOUSEBUTTONDOWN:
						interact.onMouse(event)
						break
					case pygame.MOUSEBUTTONUP:
						interact.onMouse(event)
						break
					case pygame.VIDEORESIZE:
						renderer.setSize(event.size)
						renderer.setScreen(pygame.display.set_mode(event.size, SCREEN_FLAGS))
						pygame.display.update()
						break
			pygame.event.clear()
		except Exception as e:
			utils.printException(e)
			game.running = False
			break
	pygame.display.quit()
	utils.info("主线程退出")
	if gt.is_alive():
		gt.join()
	if rt.is_alive():
		rt.join()

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
