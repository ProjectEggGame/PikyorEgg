from sys import stdout, stderr
import traceback
from threading import Lock


class Utils:
	def __init__(self):
		self._lock = Lock()
		if self._lock.locked():
			self._lock.release()
	
	def _output(self, head: str, *args, sep=' ', end='\n', file=stdout):
		self._lock.acquire()
		print(head, sep='', end='', file=file)
		print(*args, sep=sep, end=end, file=file)
		self._lock.release()
	
	def debug(self, *args, sep=' ', end='\n') -> None:
		self._output('[IKUN] [DEBUG] ', *args, sep=sep, end=end)
	
	def info(self, *args, sep=' ', end='\n') -> None:
		self._output('[IKUN] [INFO]  ', *args, sep=sep, end=end)
	
	def warn(self, *args, sep=' ', end='\n') -> None:
		self._output('[IKUN] [WARN]  ', *args, sep=sep, end=end, file=stderr)
	
	def error(self, *args, sep=' ', end='\n') -> None:
		self._output('[IKUN] [ERROR] ', *args, sep=sep, end=end, file=stderr)
	
	def traceStack(self, e: Exception, msg: str | None = None) -> None:
		"""
		建议改为调用printException()
		:param e: 被抛出的错误
		"""
		result = []
		last_file = None
		last_line = None
		last_name = None
		count = 0
		traces = traceback.extract_tb(e.__traceback__)
		result.append(f'  {traces[-1].line}\n')
		for frame in traces:
			if last_file is None or last_file != frame.filename or last_line is None or last_line != frame.lineno or last_name is None or last_name != frame.name:
				if count > 3:
					count -= 3
					result.append(f'  [Previous line repeated {count} more time{"s" if count > 1 else ""}]\n')
				last_file = frame.filename
				last_line = frame.lineno
				last_name = frame.name
				count = 0
			count += 1
			if count > 3:
				continue
			row = [f'  @ {frame.name} @ File "{frame.filename}", line {frame.lineno}']
			if frame.locals:
				for name, value in sorted(frame.locals.items()):
					row.append(f'    {name} = {value}')
			row.append('\n')
			result.append(''.join(row))
		if count > 3:
			count -= 3
			result.append(f'  [Previous line repeated {count} more time{"s" if count > 1 else ""}]\n')
		self._lock.acquire()
		if msg is not None:
			print(f'[IKUN] [ERROR] {msg}', file=stderr)
		else:
			print('[IKUN] [WARN]  Stack trace:', file=stderr)
		for line in result:
			print(line, file=stderr, end='')
		self._lock.release()
	
	def printException(self, e: Exception) -> None:
		"""
		抛出错误时调用
		:param e: 被抛出的错误
		"""
		self.traceStack(e, f'[{type(e).__name__}] {str(e)}!! when running code:')


utils: Utils = Utils()
