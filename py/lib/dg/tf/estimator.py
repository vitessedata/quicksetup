import dg.xtable
import dg.tf.input_fn

class Estimator:
    def __init__(self, batch_sz=100):
        self.batch_sz = batch_sz
        self.tfinput = dg.tf.input_fn.InputFn()
        self.out_cols = []

    def add_out_col(self, name, typ):
        self.out_cols.append(dg.xtable.XCol(name, typ))

    def add_tf_code(self, tfcode): 
        self.tfcode = tfcode

    def build_xt(self, conn):
        sql = self.__build_xtsql()
        xt = dg.xtable.fromSQL(conn, sql)
        return xt.select(select=','.join([col.name for col in self.out_cols]))

    def build_sql(self):
        sql = self.__build_xtsql()
        return sql

    def __build_tr_out_cols(self):
        s = ""
        for idx, col in enumerate(self.out_cols):
            pgt, trt = col.pg_tr_type()
            s += "dg_utils.transducer_column_{0}({1}) as {2},\n".format(pgt, idx+1, col.name)
        return s

    def __build_tr_in_types(self):
        tft = self.tfinput.build_xt()
        return "\n".join(["// {0} {1}".format(col.name, col.tr_type()) for col in tft.schema])

    def __build_tr_out_types(self):
        return "\n".join(["// {0} {1}".format(col.name, col.tr_type()) for col in self.out_cols]) 

    def __build_input_fn_types(self):
        tft = self.tfinput.build_xt()
        return ",".join(["tf.{0}".format(col.tr_type()) for col in tft.schema[2:]])

    def __build_input_fn_shapes(self):
        tft = self.tfinput.build_xt()
        return ",".join(["[]" for col in tft.schema[2:]])

    def __build_input_fn_colnames(self):
        tft = self.tfinput.build_xt()
        return ",".join(['"{0}"'.format(col.name) for col in tft.schema[2:]])

    def __build_tr_sql(self):
        tft = self.tfinput.build_xt()
        return tft.sql

    def __build_xtsql(self):
        sql = """ select {0} 
dg_utils.transducer($PHI$PhiExec python2
import vitessedata.phi
vitessedata.phi.DeclareTypes('''
//
// BEGIN INPUT TYPES
{1}
// END INPUT TYPES
//
// BEGIN OUTPUT TYPES
{2}
// END OUTPUT TYPES
//
''')
import sys, os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

class TfPhiReader:
    def __init__(self):
        self.tf_aux_ii = 0
        self.nextrow = None
        self.rowset = [] 

    def clear_rs(self):
        self.rowset = []

    def next(self, ii, cache_rs): 
        if self.tf_aux_ii == ii:
            if self.nextrow != None:
                sys.stderr.write("result set " + str(ii) + " read cached first row.\\n") 
                sys.stderr.flush() 
                rec = self.nextrow
                self.nextrow = None
                if cache_rs:
                    self.rowset.append(rec[2:])
                return rec[2:]
            else:
                rec = vitessedata.phi.NextInput()
                if rec == None:
                    sys.stderr.write("result set " + str(ii) + " read EOS\\n") 
                    sys.stderr.flush() 
                    return None
                if rec[0] != ii:
                    sys.stderr.write("resultset switch from " + str(ii) + " to " + str(rec[0]) + "\\n") 
                    sys.stderr.flush() 
                    self.tf_aux_ii = rec[0]
                    self.nextrow = rec
                    return None
                else:
                    if cache_rs:
                        self.rowset.append(rec[2:])
                    return rec[2:]
        else:
            sys.stderr.write("result set, try to read " + str(ii) + " tf_aux_ii is " + str(self.tf_aux_ii) + "\\n") 
            sys.stderr.flush() 
            if self.nextrow != None:
                sys.stderr.write("result set, try to read " + str(ii) + " tf_aux_ii is " + str(self.tf_aux_ii) + " cached mismatch\\n") 
                sys.stderr.flush() 
                return None
            else:
                rec = vitessedata.phi.NextInput()
                if rec == None:
                    sys.stderr.write("result set " + str(ii) + " tf_aux_ii " + str(self.tf_aux_ii) + " read EOS\\n")
                    sys.stderr.flush() 
                    return None
                if rec[0] == ii:
                    self.tf_aux_ii = rec[0]
                    if rec[0] == ii:
                        if cache_rs:
                            self.rowset.append(rec[2:])
                        return rec[2:]
                    else:
                        self.nextrow = rec
                        return None
            
tf_phi_reader = TfPhiReader()

def sql_clear_cached_rs():
    tf_phi_reader.clear_rs()

def sql_cached_rs():
    return tf_phi_reader.rowset

def phi_generator(ii, cache_rs):
    cnt = 0
    rec = tf_phi_reader.next(ii, cache_rs)
    while rec != None:
        cnt += 1
        yield tuple(rec)
        rec = tf_phi_reader.next(ii, cache_rs)
    sys.stderr.write("Done reading resultset " + str(ii) + " total " + str(cnt) + " records\\n")

def sql_input_fn(ii, cache_rs=False): 
    ds = tf.data.Dataset.from_generator(lambda: phi_generator(ii, cache_rs), 
            ({3}),
            ({4}))
    ds = ds.batch({5}) 
    cols = ds.make_one_shot_iterator().get_next()
    features = dict(zip([{6}], cols)) 
    return features

{7}

if __name__ == '__main__':
    sys.stderr = open("/tmp/phi_py2_tf.log", "w")
    tf.logging.set_verbosity(tf.logging.ERROR)
    tf.app.run(main=main) 

$PHI$), phitft.* from (
{8}
) phitft
""".format(self.__build_tr_out_cols(),
           self.__build_tr_in_types(), 
           self.__build_tr_out_types(),
           self.__build_input_fn_types(),
           self.__build_input_fn_shapes(),
           self.batch_sz,
           self.__build_input_fn_colnames(),
           self.tfcode,
           self.__build_tr_sql())
        return sql




