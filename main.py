from readmodel import ModelData
from readmodel import Presolve
from matrixgraph import GraphFactory
from postsolve import Postsolve
from moniter import Moniter
from tqdm import tqdm
import datetime
import time

LIB_NAME = "MIPLIB2017"
BENCHMARK_PATH = "./" + "benchmark/{}/".format(LIB_NAME)
MODEL_PATH = "./" + "benchmark/model/"
SOLVER = "Saucy" # Nauty, Saucy

n_start, n_end = 0, 50
symmetry_moniter = Moniter()
symmetry_moniter.read_prob_stat(LIB_NAME)

for n in tqdm(range(n_start, n_end)):
    model_data = ModelData(BENCHMARK_PATH)
    read_file = model_data.load(n, presolve = True)    
    A, rhs, obj, sense = model_data.get_coeff()
    vtype = model_data.get_vtype()
    # model_data.write_model(MODEL_PATH)

    presolve_model = Presolve(A, obj, rhs, sense)
    A1, rhs, obj, sense = presolve_model.to_standard()
    graph_factory = GraphFactory(A1, rhs, obj, vtype)
    graph_factory.set_solver(SOLVER)
    g = graph_factory.bulid_graph()

    g.bulid_node()
    adj = g.connect()
    vertex_coloring = g.color_node()

    try:
        ts = datetime.datetime.now()
        grpsize1, grpsize2 = g.run(adj, vertex_coloring)
    except Exception as e:
        print("Timeout Error Catched!")
        symmetry_moniter.set_log(read_file, '--', '--', g, '--', '--', '--')
        continue

    te = datetime.datetime.now()
    orbits = g.get_orbits()

    postsolve = Postsolve(g=g, orbits=orbits)
    n_orbits, per_orbits_node, orbits_group = postsolve.stat()
    
    cpu_time = (te - ts).seconds
    symmetry_moniter.set_log(read_file, grpsize1, grpsize2, g, n_orbits, per_orbits_node, cpu_time)
    symmetry_moniter.save_equal_orbits(LIB_NAME, read_file, orbits_group)

symmetry_moniter.save(LIB_NAME, SOLVER, n_start, n_end)
print(symmetry_moniter.benchmark_stat)
