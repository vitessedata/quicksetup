#
# googlenet test
#

import xdrive_pb2, server

if __name__=='__main__':
    # Test: an echo server.
    sock = server.cli_connect("/tmp/ml.sock")
    imgs = ["apple.jpeg", "banana.jpeg", "beer.jpeg", "coffee.jpeg", "egg.jpeg", "salad.jpeg"]
    for ii in range(6):
        xmsg = xdrive_pb2.XMsg()
        col = xmsg.rowset.columns.add()
        col.nrow = 1
        col.nullmap.append(False)
        col.sdata.append("./test/" + imgs[ii]) 

        server.writeXMsg(sock, xmsg)
        ret = server.readXMsg(sock)
        col1 = ret.rowset.columns[0]
        col2 = ret.rowset.columns[1]
        col3 = ret.rowset.columns[2]
        col4 = ret.rowset.columns[3]

        nrow = ret.rowset.columns[0].nrow
        for i in range(nrow):
            print("Ret {0}: ({1}, {2}, {3}, {4}).\n".format(
                i, 
                col1.sdata[i], 
                col2.i32data[i], 
                col3.f64data[i], 
                col4.sdata[i]))

    print("Done!")

