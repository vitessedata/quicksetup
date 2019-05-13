import os 
import socket, struct, sys
import thread
import traceback
import xdrive_pb2

def readXMsg(sock):
    s = sock.recv(4)
    if s is None or s == '':
        return None
    sz = struct.unpack('<i', s)[0] 
    if sz != 0x20aa30bb:
        raise Exception('Bad magic')

    s = sock.recv(4) 
    if s is None or s == '':
        raise Exception('Cannot read message sz') 
    sz = struct.unpack('<i', s)[0] 

    recvsz = 0
    msgstr = ""
    while recvsz < sz:
        r = sock.recv(sz-recvsz)
        msgstr = msgstr + r
        recvsz = recvsz + len(r)

    xmsg = xdrive_pb2.XMsg()
    xmsg.ParseFromString(msgstr) 
    return xmsg

def writeXMsg(sock, xmsg):
    xs = xmsg.SerializeToString()
    sz = len(xs) 

    magic = struct.pack('<i', 0x20aa30bb)
    sock.sendall(magic)

    szstr = struct.pack('<i', sz) 
    sock.sendall(szstr)

    sock.sendall(xs)


def handler_wrapper(hndl, conn): 
    while True:
        try:
            msg = readXMsg(conn)
            if msg == None:
                break

            ret = hndl(msg)
            if ret == None:
                break
            writeXMsg(conn, ret)

        except:
            traceback.print_exc()
            break
    conn.close()

def server_start(addr, hndl):
    # Unix domain socket, already exists.
    if os.path.exists(addr):
        raise SystemExit("Socket path exists.")

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(addr)
    sock.listen(2)

    while True:
        conn, cliaddr = sock.accept()
        thread.start_new_thread(handler_wrapper, (hndl, conn)) 

def cli_connect(addr):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(addr)
    except socket.error, msg:
        raise SystemExit("Socket client connect failed.", msg)
    return sock


def echo(msg):
    msg.info = "Echo " + msg.name
    return msg

if __name__=='__main__':
    # Test: an echo server.
    if len(sys.argv) != 3:
        raise SystemExit("Usage: server.py [server|client] addr")

    if sys.argv[1] == "server":
        server_start(sys.argv[2], echo)
    elif sys.argv[1] == "client":
        xmsg = xdrive_pb2.XMsg()
        xmsg.name = "client"
        sock = cli_connect(sys.argv[2])
        writeXMsg(sock, xmsg)
        ret = readXMsg(sock)
        print("Echo: {0}, {1}.\n".format(ret.name, ret.info))
    else:
        raise SystemExit("Usage: server.py [server|client] addr")

    print("Done!")


