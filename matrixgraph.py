import numpy as np
from scipy.sparse import csr_matrix
import pynauty as na
import pysaucy2 as sa
from collections import defaultdict
from postsolve import Postsolve
import time
import timeout_decorator

VTYPE = ['C', 'B', 'I', 'S', 'N']
TIMELIM = 60

class GraphFactory():
    def __init__(self, A:csr_matrix, b:np.array, c:np.array, vtype:list) -> None:
        self.A, self.b, self.c, self.vtype = A, b, c, vtype
    
    def set_solver(self, SOLVER):
        self.SOLVER = SOLVER
    
    def bulid_graph(self):
        if self.SOLVER == 'Nauty':
            return DictGraph(self.A, self.b, self.c, self.vtype)
        elif self.SOLVER == 'Saucy':
            return MatrixGraph(self.A, self.b, self.c, self.vtype)
        else:
            return None

class DictGraph:
    def __init__(self, A:csr_matrix, b:np.array, c:np.array, vtype:list) -> None:
        self.A, self.b, self.c, self.vtype = A, b, c, vtype
        self.m, self.n = self.A.shape[0], self.A.shape[1] # m: number of constraints, n: number of vars
        self._eliminate_explict_zeros(self.A) # in place operation

    def bulid_node(self):
        self.constrs_node = [i for i in range(self.m)]
        self.vars_node = [i + self.m for i in range(self.n)]
        self.rows, self.cols = np.nonzero(self.A)
        self.nonzero_num = self.rows.size 
        self.intermediate_node = [i + self.m + self.n for i in range(self.nonzero_num)]
    
    def connect(self):
        self.adj = dict([(i, []) for i in range(self.m + self.n + self.nonzero_num)])
        for i in range(self.nonzero_num):
            self.adj[i + self.m + self.n].append(self.rows[i]) # connect constrs with coeff
            self.adj[i + self.m + self.n].append(self.cols[i] + self.m) # connect vars with coeff
            #self.adj[self.rows[i]].append(i + self.m + self.n) # connect constrs with coeff
            #self.adj[self.cols[i] + self.m].append(i + self.m + self.n) # connect vars with coeff
        return self.adj
    
    def color_node(self):
        s1 = self._color_node(self.intermediate_node, self.A.data)
        s2 = self._color_node(self.vars_node, list(zip(self.c, self.vtype)))
        s3 = self._color_node(self.constrs_node, self.b)
        self.vertex_coloring = s1 + s2 + s3
        return self.vertex_coloring

    def _color_node(self, uncolor_node:list, coeff:np.array):
        vertex_coloring = defaultdict(set)
        for i in range(len(uncolor_node)):
            vertex_coloring[coeff[i]] = vertex_coloring[coeff[i]] | set([uncolor_node[i]])
        vertex_coloring = list(vertex_coloring.values())
        return vertex_coloring

    @timeout_decorator.timeout(TIMELIM)
    def run(self, adjacency, vertex_coloring):
        group = na.Graph(number_of_vertices=len(adjacency), directed=False, 
        adjacency_dict = adjacency, vertex_coloring = vertex_coloring)
        self.autgrp_output = na.autgrp(group)
        self.orbits = self.autgrp_output[3]
        return self.autgrp_output[1], self.autgrp_output[2]
    
    def get_orbits(self):
        return self.orbits

    def _eliminate_explict_zeros(self, A:np.array):
        csr_matrix.eliminate_zeros(A)

    def get_number_of_node(self):
        return self.m + self.n + self.nonzero_coeff

class MatrixGraph:
    def __init__(self, A:csr_matrix, b:np.array, c:np.array, vtype:list) -> None:
        self.A, self.b, self.c, self.vtype = A, b, c, vtype
        self.m, self.n = self.A.shape[0], self.A.shape[1] # m: number of constraints, n: number of vars
        self._eliminate_explict_zeros(self.A) # in place operation

    def bulid_node(self):
        self.constrs_node = [i for i in range(self.m)]
        self.vars_node = [i + self.m for i in range(self.n)]
        self.rows, self.cols = np.nonzero(self.A)
        self.nonzero_num = self.rows.size 
        self.intermediate_node = [i + self.m + self.n for i in range(self.nonzero_num)]
    
    def connect(self):
        self.adj = [[] for i in range(self.m + self.n + self.nonzero_num)]
        for i in range(self.nonzero_num):
            self.adj[self.rows[i]].append(i + self.m + self.n) # connect constrs with coeff
            self.adj[self.cols[i] + self.m].append(i + self.m + self.n) # connect vars with coeff
        return self.adj
    
    def color_node(self):
        self._vertex_coloring = self._color_node_vertex()
        self._vertex_coloring = sorted(self._vertex_coloring, key = lambda x: min(x))
        self.vertex_coloring = [None]*(self.n + self.m + self.nonzero_num)
        for i in range(len(self._vertex_coloring)):
            for j in list(self._vertex_coloring[i]):
                self.vertex_coloring[j] = i
        return self.vertex_coloring

    def _color_node_vertex(self):
        s1 = self._color_node(self.intermediate_node, self.A.data)
        s2 = self._color_node(self.vars_node, list(zip(self.c, self.vtype)))
        s3 = self._color_node(self.constrs_node, self.b)
        self._vertex_coloring = s1 + s2 + s3
        return self._vertex_coloring

    def _color_node(self, uncolor_node:list, coeff:np.array):
        vertex_coloring = defaultdict(set)
        for i in range(len(uncolor_node)):
            vertex_coloring[coeff[i]] = vertex_coloring[coeff[i]] | set([uncolor_node[i]])
        vertex_coloring = list(vertex_coloring.values())
        return vertex_coloring

    def _eliminate_explict_zeros(self, A:np.array):
        csr_matrix.eliminate_zeros(A)

    def get_number_of_node(self):
        return self.m + self.n + self.nonzero_coeff
    
    @timeout_decorator.timeout(TIMELIM)
    def run(self, adjacency, vertex_coloring):
        self.group = sa.graph.Graph(adjacency, vertex_coloring)
        self.autgrp = sa.run_saucy(self.group)
        return self.autgrp[1], self.autgrp[2]

    def get_orbits(self):
        return self.group.orbits

if __name__ == "__main__":
    A = np.array(([[0,1], [1,0], [2,2]]))
    A = csr_matrix(A)
    b, c = np.array([1,1,2]), np.array([1,1])
    vtype = ['I', 'I']

    grp_factory = GraphFactory(A, b, c, vtype)
    grp_factory.set_solver("Nauty")
    g = grp_factory.bulid_graph()

    g.bulid_node()
    adj = g.connect()
    vertex_coloring = g.color_node()
    autgrp_output = g.run(adj, vertex_coloring)
    orbits = g.get_orbits()

    postsolve = Postsolve(g=g, orbits=orbits)
    n_orbits, per_orbits_node, orbits_group = postsolve.stat()
    print("num of orbits: {}".format(n_orbits))
    print("percetage orbits node: {}".format(per_orbits_node))
    print("orbits group: {}".format(orbits_group))


    A = np.array(([[1,2,3,4], [2,3,4,1], [3,4,1,2], [4,1,2,3]]))
    A = csr_matrix(A)
    b, c = np.array([5,5,5,5]), np.array([1,1,1,1])
    vtype = ['I', 'I', 'I', 'I']

    grp_factory = GraphFactory(A, b, c, vtype)
    grp_factory.set_solver("Nauty")
    g = grp_factory.bulid_graph()

    g.bulid_node()
    adj = g.connect()
    vertex_coloring = g.color_node()
    autgrp_output = g.run(adj, vertex_coloring)
    orbits = g.get_orbits()
    
    postsolve = Postsolve(g=g, orbits=orbits)
    n_orbits, per_orbits_node, orbits_group = postsolve.stat()
    print("num of orbits: {}".format(n_orbits))
    print("percetage orbits node: {}".format(per_orbits_node))
    print("orbits group: {}".format(orbits_group))
    print(autgrp_output)


