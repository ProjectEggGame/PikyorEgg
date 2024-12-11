import time
import pygame
from threading import Thread
from interact import interact
from render.renderer import renderer
from render.resource import resourceManager
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
	count = 0
	lastCount = time.perf_counter_ns()
	while game.running:
		nowRender = time.perf_counter_ns()
		if renderer.dealMapScaleChange():
			resourceManager.changeMapScale(renderer.getMapScale())
		game.render((nowRender - lastTick) / 50_000)
		lastRender = nowRender
		count += 1
		if nowRender - lastCount >= 1_000_000_000:
			utils.info(f"{count}帧/秒")
			count = 0
			lastCount = nowRender
	utils.info("渲染线程退出")


def gameThread():
	utils.info("游戏线程启动")
	global lastTick
	global nowTick
	while game.running:
		nowTick = time.perf_counter_ns()
		if nowTick - lastTick >= 50_000:
			game.tick()
			# test
			if interact.keys[pygame.K_w].peek():
				renderer.getCamera().add(0, -0.04)
			if interact.keys[pygame.K_a].peek():
				renderer.getCamera().add(-0.04, 0)
			if interact.keys[pygame.K_s].peek():
				renderer.getCamera().add(0, 0.04)
			if interact.keys[pygame.K_d].peek():
				renderer.getCamera().add(0.04, 0)
			# test
			lastTick = nowTick
		else:
			time.sleep(0.001)
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
	renderer.setMapScale(min(info.current_w / 20, info.current_h / 15))
	gt: Thread = Thread(name="GameThread", target=gameThread)
	rt: Thread = Thread(name="RenderThread", target=renderThread)
	gt.start()
	rt.start()
	utils.info("主线程启动")
	del info
	while game.running:
		try:
			for event in pygame.event.get():
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
						renderer.setMapScale(min(event.size[0] / 20, event.size[1] / 15))
						renderer.setScreen(pygame.display.set_mode(event.size, SCREEN_FLAGS))
						pygame.display.update()
						break
		except Exception as e:
			utils.printException(e)
			game.running = False
			break
	utils.info("主线程退出")
	if gt.is_alive():
		gt.join()
	if rt.is_alive():
		rt.join()
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
