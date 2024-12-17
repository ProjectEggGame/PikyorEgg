from block.block import Block
from utils.vector import *

b = BlockVector(0, 0)
s = Vector(1.754345, 0)
d = Vector(-1.1204, 0.1904)


print(b.getHitPoint(s, d))
print(b.getHitPoint(s, d) + s)
