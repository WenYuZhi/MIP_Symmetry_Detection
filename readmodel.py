import gurobipy as gp
import numpy as np
from scipy.sparse import csr_matrix
from matrixgraph import MatrixGraph
import os

class ModelData:
    def __init__(self, benchmark_path) -> None:
        self.path = benchmark_path
        self.file_info = [(f, os.path.getsize(self.path + f)) \
        for f in os.listdir(self.path) if ".mps" in f]
        self.file_info = sorted(self.file_info, key = lambda x: x[1])
        
    def load(self, n, presolve = False):
        self.read_file = self.file_info[n][0]
        assert(n < len(self.file_info))
        assert(".mps" in self.read_file)
        self.model = gp.read(self.path + self.read_file)
        if presolve:
            self.model = self.model.presolve()
            self.model.update()
        return self.read_file

    def get_A(self):
        return self.model.getA()
    
    def get_rhs(self):
        return self.model.RHS
    
    def get_obj(self):
        return self.model.obj
    
    def get_sense(self):
        return self.model.Sense
    
    def get_vtype(self):
        return self.model.VType
    
    def write_model(self, model_path):
        self.model.write(model_path + self.read_file.replace('.mps','') + '.lp')

class Presolve:
    def __init__(self, A, obj, rhs, sense) -> None:
        self.A, self.obj, self.rhs, self.sense = A, obj, rhs, sense
        self.data1 = self.A.data.copy()
        self.indices1, self.indptr1 = self.A.indices.copy(), self.A.indptr.copy()
        
    def to_standard(self):
        n_row = self.A.shape[0]
        for i, s in enumerate(self.sense):
            if s == ">":
                 self.data1[self.A.indptr[i]:self.A.indptr[i+1]] = -1.0 *self.A.data[self.A.indptr[i]:self.A.indptr[i+1]]
                 self.rhs[i] = -1.0*self.rhs[i]
            elif s == "=":
                 self.data1 = np.hstack((self.data1, -1.0*self.A.data[self.A.indptr[i]:self.A.indptr[i+1]]))
                 self.indptr1 = np.hstack((self.indptr1, self.data1.size))
                 self.indices1 = np.hstack((self.indices1, self.A.indices[self.A.indptr[i]:self.A.indptr[i+1]]))
                 self.rhs.append(-1.0*self.rhs[i])
                 n_row += 1
            elif s == "<":
                pass
            else:
                print("sense error")
                 
        self.A1 = csr_matrix((self.data1, self.indices1, self.indptr1), shape=(n_row, self.A.shape[1]))
        assert(self.A.shape[1] == self.A1.shape[1])
        assert(self.A1.shape[0] == len(self.sense) + len([s for s in self.sense if s == "="])) # add constrs assert
        assert(self.A1.shape[0] == len(self.rhs))

        self.sense = ["<" for i in range(self.A1.shape[0])]
        self._print_status()
        return self.A1, np.array(self.rhs), np.array(self.obj), self.sense
    
    def _print_status(self):
        print("standard model: {} rows, {} columns, {} nonzeros".format(self.A1.shape[0], self.A1.shape[1], self.A1.nnz))

LIB_NAME = "MIPLIB2010"
BENCHMARK_PATH = "./" + "benchmark/{}/".format(LIB_NAME)
MODEL_PATH = "./" + "benchmark/model/"

if __name__ == "__main__":
    model_data = ModelData(BENCHMARK_PATH)
    read_file = model_data.load(n = 3, presolve = False)    
    rhs = model_data.get_rhs()
    sense = model_data.get_sense()
    A = model_data.get_A()

    obj = model_data.get_obj()
    vtype = model_data.get_vtype()
    model_data.write_model(MODEL_PATH)

    presolve_model = Presolve(A, obj, rhs, sense)
    A1, rhs, obj, sense = presolve_model.to_standard()

    g = MatrixGraph(A1, rhs, obj, vtype)
    g.bulid_node()
    adjacency_dict = g.connect()
    vertex_coloring = g.color_node()
    #print("vertex coloring: {}".format(vertex_coloring))
    