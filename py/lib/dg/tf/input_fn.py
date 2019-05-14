import dg.xtable

class Xt: 
    def __init__(self, xt, repeat, shuffle, gather): 
        self.xt = xt
        self.shuffle = shuffle
        self.gather = gather
        self.repeat = repeat

    def build_xt(self, itn):
        if not self.gather:
            raise ValueError("Notebook tensorflow must gather.  For a distributed version, contact vitessedata.")

        # use limit to gather.
        lg = " limit 1000000000000000 "

        if self.shuffle:
            return dg.xtable.fromQuery(self.xt.conn, 
                    "select {0}::int as __tf_aux_iter, random()::float4 as __tf_aux_rr, #0#.* from #0# order by __tf_aux_rr {1}".format(itn, lg), 
                    inputs = [self.xt])
        else:
            return dg.xtable.fromQuery(self.xt.conn, 
                    "select {0}::int as __tf_aux_iter, 0.0::float4 as __tf_aux_rr, #0#.* from #0# {1}".format(itn, lg),
                    inputs = [self.xt])

class InputFn:
    def __init__(self):
        self.phitft = None
        self.xts = []

    def add_xt(self, xt, repeat=1, shuffle=False, gather=True):
        tfxt = Xt(xt, repeat=repeat, shuffle=shuffle, gather=gather)
        self.xts.append(tfxt)

    def build_xt(self):
        if len(self.xts) == 0:
            raise ValueError("Deepgreen TF Input need input xts.")
        if self.phitft != None:
            return self.phitft

        sql = ""
        sep = ""
        inputs = []
        for idx, xt in enumerate(self.xts):
            withxt = xt.build_xt(idx)
            inputs.append(withxt)
            for rn in range(xt.repeat):
                sql += "{0} select * from #{1}# \n".format(sep, idx)
                sep = " union all "
        sql += " limit 1000000000000000 "

        self.phitft = dg.xtable.fromQuery(self.xts[0].xt.conn, sql, inputs=inputs)
        return self.phitft
