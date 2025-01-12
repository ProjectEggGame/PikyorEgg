import json
import os


class Archive:
	def __init__(self, name: str):
		"""
		:param name: 存档名称
		"""
		self.dic = {}
		self._name = name
		if not os.path.exists("user/archive"):
			os.makedirs("user/archive")
		try:
			self._file = open(f"user/archive/{name}.json", "r+")
		except FileNotFoundError:
			self._file = open(f"user/archive/{name}.json", "x")
	
	def read(self) -> None:
		self.dic.clear()
		self.dic = json.loads(self._file.read())
		self.dic['world']
	
	def write(self) -> None:
		self.dic = {
			"123": 123,
			"flag": True,
		}
		s = json.dumps(self.dic)
		self._file.close()
		self._file = open(f"user/archive/{self._name}.json", "w")
		self._file.write(s)
	
	def close(self) -> None:
		self._file.close()
	
	def __del__(self):
		if not self._file.closed:
			self.close()
