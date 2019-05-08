drop external table if exists imagefiles;
create external table imagefiles
(
    dir text,
    basename text,
    size text,
    mode text,
    modtime text,
    isdir text,
    content_base64 text
) location ('xdrive://127.0.0.1:31416/images/**') 
format 'csv';

drop function if exists textcol(i int);
create function textcol(i int) returns text as 
$$ select dg_utils.transducer_column_text($1); $$ 
language sql;

drop function if exists i4col(i int);
create function i4col(i int) returns int as 
$$ select dg_utils.transducer_column_int4($1); $$ 
language sql;

drop function if exists f4col(i int);
create function f4col(i int) returns float4 as 
$$ select dg_utils.transducer_column_float4($1); $$ 
language sql;

drop function if exists gnet();
create function gnet () returns bigint 
as $BODY$ 
select dg_utils.transducer($PHI$PhiExec python2
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
$PHI$)
$BODY$
language sql;

