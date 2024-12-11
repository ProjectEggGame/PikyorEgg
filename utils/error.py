class InvalidOperationException(Exception):
	"""
	当操作无效时抛出
	"""
	
	def __init__(self, message: str) -> None:
		super().__init__(message)


class NullPointerException(Exception):
	"""
	当指针为空时抛出
	"""
	
	def __init__(self, message: str) -> None:
		super().__init__(message)


class IllegalStatusException(Exception):
	"""
	某个状态错误的时候
	"""
	def __init__(self, message: str) -> None:
		super().__init__(message)


class CodeBasedException(Exception):
	"""
	代码逻辑的异常
	"""
	def __init__(self, message: str, code: int) -> None:
		super().__init__(message)
		self.code: int = code
