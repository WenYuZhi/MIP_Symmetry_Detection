from pynauty import *
g = Graph(number_of_vertices=9, directed=False,
 adjacency_dict = {
  0: [5],
  1: [6],
  2: [7, 8],
  3: [6, 7],
  4: [5, 8],
  5: [0, 4],
  6: [1, 3],
  7: [2, 3],
  8: [2, 4],
 },

 vertex_coloring = [
  set([0, 1]),
  set([2]),
  set([3, 4]), 
  set([5, 6]), 
  set([7, 8])
 ],
)

print(g)
print(autgrp(g))

g = Graph(number_of_vertices=4, directed=False,
 adjacency_dict = {
  0: [1, 3],
  1: [0, 2],
  2: [1, 3],
  3: [0, 2],
 },

 vertex_coloring = [
  set([1, 3]),
  set([0, 2]),
 ],
)

print(g)
print(autgrp(g))


g = Graph(number_of_vertices=4, directed=False,
 adjacency_dict = {
  0: [1, 3],
  1: [0, 2],
  2: [1, 3],
  3: [0, 2],
 },

 vertex_coloring = [
  set([0, 1, 2, 3]),
 ],
)

print(g)
print(autgrp(g))