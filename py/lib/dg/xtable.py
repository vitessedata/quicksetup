import tabulate

class XCol:
    def __init__(self, n, t):
        self.name = n
        self.type = t
    def pg_tr_type(self):
        if self.type in ["int", "int4", "integer"]:
            return ("int4", "int32")
        elif self.type in ["int8", "bigint"]:
            return ("int8", "int64")
        elif self.type in ["real", "float4"]:
            return ("float4", "float32")
        elif self.type in ["float", "double precision", "float8"]:
            return ("float8", "float64")
        else:
            return ("text", "string")
    def pg_type(self):
        return self.pg_tr_type()[0]
    def tr_type(self):
        return self.pg_tr_type()[1]

class XTable:
    def __init__(self, c, origsql="", alias="", inputs=None):
        self.conn = c
        self.origsql = origsql
        self.sql = None 
        if alias == "":
            self.alias = c.next_tmpname()
        else:
            self.alias = alias 
        self.inputs = inputs
        self.rows = 0.0
        self.cost = 0.0
        self.row_width = 0.0
        self.schema = None
        self.cur = None

    def coldef(self, idx):
        return self.schema[idx]

    # resolve a column.  
    # #x# where x is a number -> tablealias
    # #x.y# where x is a number, y is either a number or colname -> tablealias.colname
    # ## espcases #
    def resolve_col(self, s):
        strs = s.split('#')
        rs = []
        i = 0

        while i < len(strs):
            rs.append(strs[i])
            i += 1 

            if i == len(strs):
                break

            if strs[i] == '':
                rs.append('#')
            else:
                xy = strs[i].split('.')
                if len(xy) == 1:
                    idx = int(xy[0])
                    rs.append(self.inputs[idx].alias)
                elif len(xy) == 2:
                    idx = int(xy[0])
                    tab = self.inputs[idx].alias
                    colidx = -1
                    col = ''
                    try:
                        colidx = int(xy[1])
                    except ValueError:
                        pass
                    if colidx == -1:
                        col = xy[1]
                    else:
                        col = self.inputs[idx].coldef(colidx).name
                    rs.append(tab + "." + col)
                else:
                    raise ValueError("sql place holder must be #x# or #x.y#")
            i += 1 

        return "".join(rs)

    def build_sql(self): 
        if self.sql != None:
            return

        rsql = self.resolve_col(self.origsql)
        if self.inputs == None or len(self.inputs) == 0:
            self.sql = rsql
        else:
            self.sql = "WITH "
            self.sql += ",\n".join([t.alias + " as (" + t.sql + ")" for t in self.inputs])
            self.sql += "\n"
            self.sql += rsql

    def explain(self):
        self.build_sql()
        self.schema = [XCol("", "")]
        rows = self.conn.execute("explain verbose " + self.sql)
        state = 'beforeCol'
        for row in rows:
            line = row[0].strip()
            if state == 'beforeCol':
                if line.startswith("ERROR:"):
                    raise ValueError(line)
                elif line.startswith(":total_cost"):
                    self.cost = float(line[len(":total_cost") + 1:])
                elif line.startswith(":plan_rows"):
                    self.rows = float(line[len(":plan_rows") + 1:])
                elif line.startswith(":plan_width"):
                    self.row_width = float(line[len(":plan_width") + 1:])
                elif line.startswith(":targetlist"):
                    state = 'readingCol'
            elif state == 'readingCol':
                if line.startswith(":vartype"):
                    vt = int(line[len(":vartype") + 1:])
                    self.schema[-1].type = self.conn.typemap[vt]
                elif line.startswith(":resname"):
                    self.schema[-1].name = line[len(":resname") + 1:]
                elif line.startswith(":resjunk"):
                    if line[len(":resjunk") + 1:] == "false":
                        self.schema.append(XCol("", ""))
                elif line.startswith(":flow"):
                    state = "doneCol"
        self.schema.pop()

    def select(self, alias='', select=None, where=None, limit=None, samplerows=None, samplepercent=None): 
        sql = '' 
        if select == None:
            sql = 'select * from #0#'
        else:
            sql = 'select {0} from #0#'.format(select)

        if where != None:
            sql = sql + " where " + where

        nlimit = 0
        if limit != None:
            nlimit += 1
            sql = sql + " limit {0}".format(limit)

        if samplerows != None:
            nlimit += 1
            sql = sql + " limit sample {0} rows".format(samplerows)

        if samplepercent != None:
            nlimit += 1
            sql = sql + " limit sample {0} percent".format(samplepercent)

        if nlimit > 1:
            raise ValueError("SQL Select can have at most one limit/sample clause")

        ret = XTable(self.conn, sql, alias, inputs=[self])
        ret.explain()
        return ret

    def cursor(self):
        self.build_sql()
        return self.conn.cursor(self.sql)

    def execute(self):
        self.build_sql()
        return self.conn.execute(self.sql) 

    def ctas(self, tablename, distributed_by=None):
        sql = "create table {0} as {1}".format(tablename, self.sql) 
        if distributed_by != None:
            sql += " distributed by ({0})".format(distributed_by)
        self.conn.execute_only(sql)

    def insert_into(self, tablename, cols=None):
        sql = "insert into {0} ".format(tablename)
        if cols != None:
            sep = '('
            for col in cols:
                sql += sep + col
            sql += ')'
        sql += self.sql
        self.conn.execute_only(sql)

    def coldata(self, colname, rows):
        for idx, col in enumerate(self.schema):
            if col.name == colname:
                return [r[idx] for r in rows]
        raise ValueError("{0} is not a valid column name.".format(colname))

    def show(self, tablefmt='psql'):
        res = self.execute()
        return tabulate.tabulate(res, [col.name for col in self.schema], tablefmt)


def fromQuery(conn, qry, alias="", inputs=None):
    xt = XTable(conn, qry, alias, inputs)
    xt.explain()
    return xt

def fromSQL(conn, sql, alias=""):
    xt = XTable(conn, sql, alias, None) 
    xt.sql = xt.origsql
    xt.explain()
    return xt

def fromTable(conn, tn, alias=""):
    return fromSQL(conn, "select * from " + tn, alias)

def sameData(xt1, xt2):
    st1 = fromQuery(xt1.conn, "select dg_utils.sha1_checksum(byteain(record_out(#0#.*))) from #0#", inputs = [xt1])
    st2 = fromQuery(xt2.conn, "select dg_utils.sha1_checksum(byteain(record_out(#0#.*))) from #0#", inputs = [xt2])
    res1 = st1.execute()
    res2 = st2.execute()
    return res1 == res2

if __name__ == '__main__':
    import dg.conn
    c1 = dg.conn.Conn("ftian", database="ftian") 
    c2 = dg.conn.Conn("ftian", database="tpch1f") 
    t1 = fromTable(c1, "dg_utils.eachseg")
    t2 = fromTable(c2, "dg_utils.eachseg")
    t3 = fromTable(c1, "t")
    t4 = fromTable(c2, "nation")

    print("Same: {0}\n".format( sameData(t1, t2)))
    print("Same: {0}\n".format( sameData(t4, t4)))
    print("Not Same: {0}\n".format( sameData(t1, t3)))
    print("Not Same: {0}\n".format( sameData(t1, t4)))

    t5 = t4.select(select = 'n_comment', samplerows='3')
    print(t5.show())

    rows = t4.execute()
    print(t4.coldata('n_comment', rows))

    tu = fromQuery(c1, """select 'num_train', count(*) from widedeep_train 
                          union all
                          select 'num_test', count(*) from widedeep_test
                          """)
    print(tu.show())
