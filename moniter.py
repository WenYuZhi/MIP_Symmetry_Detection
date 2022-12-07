import pandas as pd
import datetime

class Moniter:
    def __init__(self) -> None:
        self.log_file = []
    
    def read_prob_stat(self, LIB_NAME):
        self.benchmark_stat = pd.read_csv("./" + "benchmark/{}/The Benchmark Set.csv"
        .format(LIB_NAME), index_col = False)
        self.benchmark_stat = self.benchmark_stat[["Instance  Ins.", "Status  Sta.", "Objective  Obj.", "Tags  Tag.",
        'Submitter  Sub.', 'Group  Gro.']]
        self.benchmark_stat.columns = ['instance', 'status', 'objectve','tags', 'submitter', 'group']
    
    def save_equal_orbits(self, LIB_NAME, read_file, equal_orbits):
        self.equal_orbits = pd.DataFrame([equal_orbits]).T
        self.equal_orbits.columns = ["equivalent variables"]
        self.equal_orbits.to_csv("./" + "orbits/{}/{}.csv".format(LIB_NAME, read_file), index=0)
    
    def set_log(self, read_file, grpsize1, grpsize2, g, n_orbits, per_orbits_node, cpu_time):
        read_file = read_file.replace(".mps", "")
        self.log_file.append([read_file, grpsize1, grpsize2, g.m, g.n, n_orbits, per_orbits_node, cpu_time])

    def save(self, LIB_NAME, SOLVER, n_start, n_end):
        ts = datetime.datetime.now()
        ts = ts.strftime('%Y%m%d%H%M%S')
        self.log_file = pd.DataFrame(self.log_file, columns = ["instance","grpsize1","grpsize2", 
        "constraints","variables","equivalent vars","#oribits(%)", "CPU time(s)"])
        self.log_file = self._merge_data(self.log_file, self.benchmark_stat)
        self.log_file.to_csv("./" + "log/{}_{}_{}_{}_{}.csv".format(LIB_NAME, SOLVER, str(n_start), 
        str(n_end), ts))
    
    def _merge_data(self, df1, df2):
        df3 = pd.merge(df1, df2, on = "instance")
        return df3

        