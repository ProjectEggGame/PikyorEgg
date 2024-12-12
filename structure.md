# 类工具包，可以任意导入
	import utils
	import sync
	import error
	from utils.game import game
	from interact import interact
	from render.renderer import renderer
	from window.window import Window
	from window.widget import *
	# 以下不常用
	from render.resource import Resource
	from render.renderable import Renderable
	# 以下当前没用
	from render.texture import Texture, Font
# 基类包
	from item.itme import Item
	from entity.entity import Entity
	from block.block import Block
- 基类包基本没有依赖，可以视情况任意导入。
# 统治性包
	world/world.py 依赖于 block, entity
- 请注意，扩展被依赖的包时，不可以导入依赖包。
- 例如，扩展block时，不可以导入world/world.py
# 类型检查导入
	# e.g. 导入World仅用于类型检查
	from typing import TYPE_CHECKING
	if TYPE_CHECKING:
		from world.world import World
	
	def func(world: World):
		pass
- 如果导入类仅用于类型检查，请用如上代码。
