class Postsolve():
    def __init__(self, g, orbits) -> None:
        self.g, self.orbits = g, orbits.copy()
    
    def _remove_non_vars(self):
        self.orbits_var = [self.orbits[i] for i in range(len(self.orbits)) if i in self.g.vars_node]
        return self.orbits_var
    
    def _get_n_orbits(self):
        symmetry_var_count = 0
        for n in range(self.g.n):
            if self.orbits_var.count(self.orbits_var[n]) > 1:
                symmetry_var_count += 1
        return symmetry_var_count
    
    def _get_orbits_group(self):
        self.orbits_group = []
        for o in list(set(self.orbits_var)):
            self.orbits_group.append([int(i) for i, b in enumerate(self.orbits_var) if b == o])
        return self.orbits_group

    def stat(self):
        self.orbits_var = self._remove_non_vars()
        self.symmetry_var_count = self._get_n_orbits()
        self.orbits_group = self._get_orbits_group()
        self.per_orbits_node = (100 * self.symmetry_var_count / self.g.n)
        return self.symmetry_var_count, self.per_orbits_node, self.orbits_group

        

            
                