import dg.conn
import dg.xtable

def xt_activity(conn):
    return dg.xtable.fromQuery(conn, "select * from pg_stat_activity") 

def xt_longrunning_query(conn, nsec=60):
    sql = """select * from pg_stat_activity where current_query <> '<IDLE>'
             and current_timestamp - query_start > interval '{0} second'
            """.format(nsec)
    return dg.xtable.fromQuery(conn, sql) 

def xt_waiting(conn):
    return dg.xtable.fromQuery(conn, "select * from pg_stat_activity where waiting") 

    
if __name__ == '__main__':
    import sys
    c = dg.conn.Conn("ftian", port=5555, database=sys.argv[1]) 
    xt = xt_activity(c) 
    print(xt.show())

    xt = xt_longrunning_query(c, nsec=10) 
    print(xt.show())

    xt = xt_waiting(c) 
    print(xt.show())

