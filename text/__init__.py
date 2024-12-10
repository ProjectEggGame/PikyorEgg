
class Description:
	"""
	元素描述。这个可以实现按时间不同变化的
	"""
	def __init__(self, d: list[str] | None = None):
		self._d = [] if d is None else d
	
	def generate(self) -> list[str]:
		return self._d
