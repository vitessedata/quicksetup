# import psycopg2
import pg8000

class Conn:
    def __init__(self, user=None, host='localhost', port=5432, database=None, password=None):
        self.conn = pg8000.connect(user, host=host, port=port, database=database, password=password) 
        self.setversion()
        self.nexttmp = 0
        # autocommit set to true by default.
        self.conn.autocommit = True
    
    def setversion(self):
        cur = self.conn.cursor()
        cur.execute("select version()")
        verstr = cur.fetchone()
        if "Greenplum Database 4" in verstr[0]:
            self.ver = 4
        elif "Greenplum Database 5" in verstr[0]:
            self.ver = 5
        else:
            raise RuntimeError('Unknown Deepgreen Version')
       
        self.typemap = {}
        cur.execute("select oid, typname from pg_type")
        rows = cur.fetchall()
        for row in rows:
            self.typemap[row[0]] = row[1]

        cur.close()
        self.conn.commit()

    def close(self):
        self.conn.close()

    def next_tmpname(self):
        self.nexttmp += 1
        return "tmp_{0}".format(self.nexttmp)

    def execute(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql) 
        rows = cur.fetchall()
        cur.close()
        self.conn.commit()
        return rows

    def execute_only(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql) 
        cur.close()
        self.conn.commit()

    def cursor(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql) 
        return cur


if __name__ == '__main__':
    conn = Conn("ftian") 
    print("Connected to deepgreen database, version is ", conn.ver)

