"""
这个文件主要用于导出和导入设置。
"""
import json

from utils import utils


def readConfig() -> dict[str, any]:
	"""
	读取配置文件。！！！由于文件位置问题，只能在main.py中调用！！！
	"""
	try:
		f = open("user/config.json", "r")
	except FileNotFoundError:
		f2 = open("user/config.json", "x")
		f2.write("{}")
		f2.close()
		return {}
	file: str = f.read()
	f.close()
	try:
		return json.loads(file)
	except Exception as e:
		utils.printException(e)
		return {}


def writeConfig(d: dict[str, any]) -> None:
	"""
	写入配置文件。！！！由于文件位置问题，只能在main.py中调用！！！
	"""
	with open("user/config.json", "w") as f:
		f.write(json.dumps(d))
		f.close()
