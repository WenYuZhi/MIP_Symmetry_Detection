import pysaucy2 

edge_list = [[5], [6], [7,8], [6,7], [5,8], [], [], [], []]
colors = [0,0,0,1,2,2,3,0,3]
g = pysaucy2.graph.Graph(edge_list, colors)
autgrp = pysaucy2.run_saucy(g)
print(g.orbits)

# (group size base, group size exponent, levels, nodes, bads, number of generators, support)