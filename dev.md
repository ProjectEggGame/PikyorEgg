# 写在前面

这是使用说明。
这是EmsiaetKadosh自己写的用于《简简单单捡蛋煎蛋》的游戏基底。

# 运行

核心文件为main.py。只需要运行main.py就可以了。

# 库说明

### 一些术语

- tick 游戏刻，刻。游戏最小时间单位
- entity 实体。游戏中所有的鸡/蛋/人物，几乎所有“不长在地上的东西”都叫实体。
- world 场景，世界，其实叫scene也行。相当于地图。但是地图上的环境等等不算实体。
- thread 线程，计算机原本同时只能链式执行一个任务（单线程）。但是“多线程”可以让计算机人格分裂，同时执行多个任务。

### 总体运行逻辑

- 由main.py开始，启动两个主要线程：
	- 主线程，用于响应各个输入操作事件；
	- 游戏线程，用于每秒20次执行游戏循环和渲染。
- 主线程 mainThread()
	- 主线程的工作是接受操作输入，然后把操作状态填充到interact/interact.py中；
	- 主线程负责最终捕获错误。也就是说，游戏中没有被捕获的raise最终会被主线程捕获，输出对应的错误信息，然后退出游戏（游戏崩溃）。
- 游戏线程 gameThread()
	- 令世界执行tick()
		- 会执行一些场景上的每tick判定，比如植物生长、天气更新等。
	- 令所有实体执行tick()
		- 实际上在游戏线程中调用的是每个实体的passTick()，然后在passTick()内再调用tick()。这么做是为了防止passTick()里的一些必要重要逻辑被随意重写覆盖。如果一定要重写passTick()，那么一定要原封不动地照抄父类的passTick，或者最好调用super().passTick()。代码中所有pass前缀的函数都要这样对待。
		- 进行实体移动。
		- 进行蛋/鸡成长/交配判定。
		- 一些其他逻辑。
	- 令player执行tick
- 渲染线程 renderThread()
	- 执行渲染。
		- 世界渲染
		- 实体渲染
		- UI渲染
# 总体结构
- 所有游戏内的元素全部继承Element类
  - 所有实体继承Entity类
    - 后续会有class Egg、class Chicken之类的，现在暂时没有
  - 所有物品继承Item类，有必要可以改为继承Weapon类等
    - 子类有Weapon
    - 为了管理多个物品堆叠，添加ItemStack类。Item类类似于一个抽象描述，描述一个ItemStack装载了什么物品。交互上以ItemStack为主
    - 为了管理一坨物品，添加Inventory类，也就是物品栏。很多东西都可以有独特的物品栏，比如鸡可以有饰品栏，也可以有装备栏，它们都属于物品栏的一种
  - 所有地图继承Block类
    - 子类有Ground地面，默认可以踩上去；有Wall墙，默认不能通过
  - <font color = 'red'>所有Element类的继承者应当重写save()函数，并包含一个@classmethod load()函数，用于存档和读档。</font>
- 交互UI方面
  - 类Window窗口。
    - 游戏会显示game.window指示的窗口，同时只能显示一个窗口。
    - 有时需要实现鼠标移过时在鼠标下方显示一些内容，这一功能另写，不在Window中直接实现。
    - Window的大小一定是整个程序窗口的大小。你可以自行缩小显示范围。在此基础上如果你希望打开窗口时还可以同时与地图交互，找找注释，可以实现。
  - 类Widget控件。所有UI组件都继承Widget，但Window除外。你可以自己在代码中找你想要的组件。没有的话，可以自己写，也可以找EmsiaetKadosh催他搞一个出来。
# 字符串
  - 所有能够被渲染出来的字符串，都转化为RenderableString类。
  - 简而言之：以反斜杠开头
    - ```\\#```后续8位16进制，表示颜色。
    - ```\\.```后续8位16进制，表示背景颜色。
    - ```\\xx```标记字体。
    - ```\\/``` ```\\i``` ```\\I```标记斜体。
    - ```\\=``` ```\\b``` ```\\B```标记粗体。
    - ```\\_``` ```\\u``` ```\\U```标记下划线。
    - ```\\-``` ```\\s``` ```\\S```标记删除线。
    - 否则，原样输出。
  - 具体说说，RenderableString的格式化字符序列全部以反斜杠\开头，在python中往往需要两个反斜杠表示一个反斜杠
    - 标记字符颜色：```RenderableString('\\#AARRGGBBtext_to_display')```，其中AA表示透明度，RGB分别为红绿蓝。均为16进制表示。如果不足8位，或格式不符，\\#后的8个字符会被一并全部舍弃不显示
    - 标记字符背景色：```RenderableString('\\.AARRGGBBtext_to_display')```，同上。
    - 标记字符字体：```RenderableString('\\xx')```，其中xx为字体编号，参考render/font.py中的```allFonts```字典，0号字体标记为```'\\00'```。
    - 标记斜体：```RenderableString('\\/')```或者```RenderableString('\\i')```或者```RenderableString('\\I')```，斜体英文为italic。
    - 标记粗体：```RenderableString('\\=')```或者```RenderableString('\\b')```或者```RenderableString('\\B')```，粗体为bold。
    - 标记下划线：```RenderableString('\\_')```或者```RenderableString('\\u')```或者```RenderableString('\\U')```，下划线为underline。
    - 标记删除线：```RenderableString('\\-')```或者```RenderableString('\\s')```或者```RenderableString('\\S')```，删除线为strikethrough。
