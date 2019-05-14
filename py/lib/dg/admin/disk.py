import dg.conn
import dg.xtable

def xt_disk(conn):
    sql = """
    select t1.tabname, t1.totalsz, t2.skew_coefficient, 
           (t1.totalsz * t2.skew_coefficient / t3.nseg / 100.0)::bigint as skewsz 
    from (select sotdschemaname || '.' || sotdtablename as tabname,
                 sotdsize + sotdtoastsize + sotdadditionalsize as totalsz
          from gp_toolkit.gp_size_of_table_disk) as t1,
         (select skcnamespace || '.' || skcrelname as tabname,
                 skccoeff as skew_coefficient 
          from gp_toolkit.gp_skew_coefficients) as t2,
         (select max(content) + 1 as nseg from gp_segment_configuration) as t3
    where t1.tabname = t2.tabname
    """
    return dg.xtable.fromQuery(conn, sql)
    
if __name__ == '__main__':
    import sys
    c = dg.conn.Conn("ftian", port=5555, database=sys.argv[1]) 
    xt = xt_disk(c) 
    print(xt.show())


