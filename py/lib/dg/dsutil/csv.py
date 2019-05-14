import urllib
import dg.xtable
from dg.xtable import XCol

class CsvXt: 
    def __init__(self, url, delim=',', strip=True):
        self.url = url
        self.schema = []
        self.delim = delim
        self.strip = strip

    def add_col(self, name, typ):
        self.schema.append(XCol(name, typ)) 
        return self

    def xtable_sql(self):
        sql = "select " + ",".join([col.name for col in self.schema]) + " from ( select "
        for idx, col in enumerate(self.schema):
            pgt = col.pg_tr_type()[0]
            sql += "dg_utils.transducer_column_{0}({1})::{2} as {3},\n".format(pgt, idx+1, pgt, col.name)
        sql += """dg_utils.transducer($PHI$PhiExec python2
## Python reader.
import vitessedata.phi
import urllib
import csv

vitessedata.phi.DeclareTypes('''
//
// BEGIN INPUT TYPES
// dummy int32
// END INPUT TYPES
//
// BEGIN OUTPUT TYPES
"""
        for idx, col in enumerate(self.schema):
            trt = col.pg_tr_type()[1]
            sql += "// {0} {1}\n".format(col.name, trt)

        sql += """// END OUTPUT TYPES
// 
''')

if __name__ == '__main__':
    while True:
        rec = vitessedata.phi.NextInput()
        if not rec:
            break
    f = urllib.urlopen('{0}')
    r = csv.reader(f, delimiter='{1}')
    for row in r:
        outrec = []
        if len(row) != {2}:
            continue
""".format(self.url, self.delim, len(self.schema))

        for idx, col in enumerate(self.schema):
            pgt = col.pg_tr_type()[0]
            if pgt in ['int4', 'int8']:
                sql += """
        fff = row[{0}]
        if fff.strip() == '':
            outrec.append(None)
        else:
            outrec.append(int(fff)) 

""".format(idx)
            elif pgt in ['float4', 'float8']:
                sql += """
        fff = row[{0}]
        if fff.strip() == '':
            outrec.append(None)
        else:
            outrec.append(float(fff)) 
""".format(idx)
            else:
                if self.strip:
                    sql += """
        outrec.append(row[{0}].strip())
""".format(idx)
                else:
                    sql += """
        outrec.append(row[{0}])
""".format(idx)

        
        sql += """
        vitessedata.phi.WriteOutput(outrec)

    vitessedata.phi.WriteOutput(None)
$PHI$), t.* from (select 1::int4) t) tmpcsvt
"""
        return sql

    def xtable(self, conn):
        sql = self.xtable_sql()
        return dg.xtable.fromQuery(conn, sql)

if __name__ == '__main__':
    import dg.conn
    c = dg.conn.Conn("ftian", port=5555) 
 
    csv = CsvXt('http://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data') 
    csv.add_col('sepal_length', 'float')
    csv.add_col('sepal_width', 'float') 
    csv.add_col('petal_length', 'float') 
    csv.add_col('petal_width', 'float') 
    csv.add_col('iris_class', 'text')

    xt = csv.xtable(c)
    print(xt.show())
