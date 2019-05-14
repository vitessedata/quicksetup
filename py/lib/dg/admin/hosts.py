import dg.conn
import dg.xtable

def xt_vmstat(conn, nsec=5):
    if nsec < 2 or nsec > 60:
        raise ValueError("A reasonable nsec values should be in [2, 60]")
    
    sql = """
select 
--
-- vmstat output columns, whatever does that mean
-- r b swpd free buff cache si so bi bo in cs us sy id wa st
-- 
dg_utils.transducer_column_int4(1) as vmstat_segid,
dg_utils.transducer_column_int4(2) as vmstat_sec, 
dg_utils.transducer_column_int8(3) as vmstat_r, 
dg_utils.transducer_column_int8(4) as vmstat_b, 
dg_utils.transducer_column_int8(5) as vmstat_swpd, 
dg_utils.transducer_column_int8(6) as vmstat_free, 
dg_utils.transducer_column_int8(7) as vmstat_buff, 
dg_utils.transducer_column_int8(8) as vmstat_cache, 
dg_utils.transducer_column_int8(9) as vmstat_si, 
dg_utils.transducer_column_int8(10) as vmstat_so, 
dg_utils.transducer_column_int8(11) as vmstat_bi, 
dg_utils.transducer_column_int8(12) as vmstat_bo, 
dg_utils.transducer_column_int8(13) as vmstat_in, 
dg_utils.transducer_column_int8(14) as vmstat_cs, 
dg_utils.transducer_column_int8(15) as vmstat_us, 
dg_utils.transducer_column_int8(16) as vmstat_sy, 
dg_utils.transducer_column_int8(17) as vmstat_id, 
dg_utils.transducer_column_int8(18) as vmstat_wa, 
dg_utils.transducer_column_int8(19) as vmstat_st, 
--
-- transducer function call, as UDF.
--
dg_utils.transducer($PHI$PhiExec python2
## A valid python program below
import vitessedata.phi
import subprocess
## Python declare input/output types.
vitessedata.phi.DeclareTypes('''
//
// BEGIN INPUT TYPES
// segid int32
// nsec int32
// END INPUT TYPES
//
// BEGIN OUTPUT TYPES
// vmstat_segid int32
// vmstat_sec int32
// vmstat_r int64
// vmstat_b int64
// vmstat_swpd int64
// vmstat_free int64
// vmstat_buff int64
// vmstat_cache int64
// vmstat_si int64
// vmstat_so int64
// vmstat_bi int64
// vmstat_bo int64
// vmstat_in int64
// vmstat_cs int64
// vmstat_us int64
// vmstat_sy int64
// vmstat_id int64
// vmstat_wa int64
// vmstat_st int64
// END OUTPUT TYPES
//
''')

def do_x():
    segid = 0
    nsec = 0
    cnt = 0
    while True: 
        rec = vitessedata.phi.NextInput()
        if not rec:
            break
        segid = rec[0]
        nsec = rec[1]

    if nsec <= 0:
        raise ValueError("Must supply a good nsec value")

    output = subprocess.Popen(["/usr/bin/vmstat", "1", str(nsec)], 
        stdout=subprocess.PIPE).communicate()[0]
    lines = output.split("\\n")
    for line in lines[2:]:
        if line.strip() == '':
            continue
        fields = line.split()
        outrec = [segid, cnt]
        cnt += 1
        for field in fields:
            outrec.append(int(field))
        ## Output
        vitessedata.phi.WriteOutput(outrec)

    ## Write None to signal end of output
    vitessedata.phi.WriteOutput(None)

if __name__ == '__main__':
    do_x()
$PHI$), 
-- 
-- Input to Transducer
-- 
t.*
--
-- From, any SQL table/view subquery
-- 
from (
    select gp_segment_id::int4, {0}::int4 from dg_utils.eachseg
) t 
""".format(nsec)
    return dg.xtable.fromQuery(conn, sql)

def xt_segs(conn):
    return dg.xtable.fromQuery(conn, "select * from gp_segment_configuration")
    
def xt_vmstat_hosts(conn, nsec=5):
    vt = xt_vmstat(conn, nsec)
    segs = xt_segs(conn)
    vh = dg.xtable.fromQuery(conn, """select #1.address# as addr, #0.vmstat_sec# as n, 
        avg(#0.vmstat_r#) as vmstat_r,
        avg(#0.vmstat_b#) as vmstat_b,
        avg(#0.vmstat_swpd#) as vmstat_swpd,
        avg(#0.vmstat_free#) as vmstat_free,
        avg(#0.vmstat_buff#) as vmstat_buff,
        avg(#0.vmstat_cache#) as vmstat_cache,
        avg(#0.vmstat_si#) as vmstat_si,
        avg(#0.vmstat_so#) as vmstat_so,
        avg(#0.vmstat_bi#) as vmstat_bi,
        avg(#0.vmstat_bo#) as vmstat_bo,
        avg(#0.vmstat_in#) as vmstat_in,
        avg(#0.vmstat_cs#) as vmstat_cs,
        avg(#0.vmstat_us#) as vmstat_us,
        avg(#0.vmstat_sy#) as vmstat_sy,
        avg(#0.vmstat_id#) as vmstat_id,
        avg(#0.vmstat_wa#) as vmstat_wa,
        avg(#0.vmstat_st#) as vmstat_st
        from #0#, #1#
        where #0.vmstat_segid# = #1.content#
        group by #1.address#, #0.vmstat_sec#
        order by #1.address#, #0.vmstat_sec# """, inputs = [vt, segs])
    return vh

if __name__ == '__main__':
    import sys
    c = dg.conn.Conn(user="ftian", database=sys.argv[1], port=5555) 
    vh = xt_vmstat_hosts(c)
    print(vh.sql)
    print(vh.show())
