-- explain analyze 
select 
dg_utils.transducer_column_text(1) as filename,
dg_utils.transducer_column_int4(2) as nth, 
dg_utils.transducer_column_float4(3) as score,
dg_utils.transducer_column_text(4) as tag,
dg_utils.transducer($PHI$PhiExec python2
import vitessedata.phi as phi
import vitessedata.phi.xdrive_pb2 as xdrive_pb2
import vitessedata.phi.server as server

phi.DeclareTypes('''
//
// BEGIN INPUT TYPES
// fn string 
// END INPUT TYPES
//
// BEGIN OUTPUT TYPES
// filename string
// nth int32 
// score float32
// tag string
// END OUTPUT TYPES
//
''')

def gnet(sock, fn):
    xmsg = xdrive_pb2.XMsg()
    col = xmsg.rowset.columns.add()
    col.nrow = 1
    col.nullmap.append(False)
    col.sdata.append(fn)

    server.writeXMsg(sock, xmsg)
    ret = server.readXMsg(sock)
    nrow = ret.rowset.columns[0].nrow

    result = []
    for i in range(nrow):
        result.append([fn, i, ret.rowset.columns[2].f64data[i], ret.rowset.columns[3].sdata[i]])
    return result
     
if __name__ == '__main__':
    sock = server.cli_connect('/tmp/ml.sock')
    while True:
        rec = phi.NextInput()
        if not rec:
            break

        res = gnet(sock, rec[0])
        for r in res:
            phi.WriteOutput(r)
    phi.WriteOutput(None)
$PHI$), t.*
from (
    select dir || '/' || basename from imagefiles where 
    dir like '%panda%' and (basename like '%jpeg' or basename like '%jpg')
) t
;

