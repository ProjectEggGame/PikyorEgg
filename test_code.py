from block.block import Block
from utils.vector import *

b = BlockVector(4, -3)
s = Vector(2.911, -1.471)
d = Vector(0.113, -0.113)

b = BlockVector(3, -2)
s = Vector(2.9301933598375625, -1.8101933598375621)
d = Vector(0.11313708498984759, -0.11313708498984759)


print(b.getHitPoint(s, d))
print(b.getHitPoint(s, d) + s)
