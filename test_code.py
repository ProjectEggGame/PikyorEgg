from utils.util import times


@times
def func(*args, **kwagrs):
	print(args[0])


func(123, 234, 'hello', kw=('EmsiaetKadosh', 213))
