#
# 
# A server running googlenet on FPGA.  See Xilinx ml-suite example test_classify.py 
# Right now, it is a multi threaded server, but each thread locks the device
#
import os, sys
import threading

import numpy as np
import xdnn, xdnn_io

import xdrive_pb2, server

fpga_lock = threading.RLock()

g_mlsuite = os.getenv("MLSUITE_ROOT", "/opt/MLsuite")
g_mode = os.getenv("MLSUITE_MODE", "example/classification") 
g_platform = "alveo-u200"

g_args = {}
g_ctxt = {}

def is_deploymode():
    return g_mode == "deployment_modes"

def build_xdnn_args():
    if is_deploymode(): 
        exdata = g_mlsuite + "/examples/deployment_modes/data" 
        xclbin = g_mlsuite + "/overlaybins/alveo-u200/overlay_4.xclbin"
        netcfg = exdata + "/googlenet_v1_8b_autoAllOpt.json"
        weights = exdata + "/googlenet_v1_data.h5"
        labels = g_mlsuite + "/examples/deployment_modes/synset_words.txt"
        quantizecfg = exdata + "/googlenet_v1_8b_xdnnv3.json"
        return [
            "--xclbin", xclbin,
            "--netcfg", netcfg, 
            "--weights", weights,
            "--labels", labels, 
            "--quantizecfg", quantizecfg,
            "--img_input_scale", "1.0", 
            "--batch_sz", "1", 
            "--images", "/tmp" 
            ]
    else:
        exdata = g_mlsuite + "/examples/classification/data/"
        xclbin = g_mlsuite + "/overlaybins/alveo-u200/overlay_2.xclbin"
        netcfg = exdata + "/googlenet_v1_56.json" 
        labels = g_mlsuite + "/examples/classification/synset_words.txt"
        datadir = exdata + "/googlenet_v1_data"
        quantizecfg = exdata + "/googlenet_v1_8b.json"
        return [
            "--xclbin", xclbin,
            "--netcfg", netcfg, 
            "--fpgaoutsz", "1024", 
            "--datadir", datadir,
            "--labels", labels, 
            "--quantizecfg", quantizecfg,
            "--img_input_scale", "1.0", 
            "--batch_sz", "1" ,
            "--images", "/tmp" 
            ]

def init_fpga():
    # Instead of using command line, we hard code it here. 
    # Typing correct args is almost impossible so either do it in .sh or .py
    # 
    global g_args
    global g_ctxt
    print(" --- INIT FPGA --- \n")
    xdnnArgs = build_xdnn_args()
    print(xdnnArgs)
    g_args = xdnn_io.processCommandLine(xdnnArgs)
    print(" --- After parsing --- \n")
    print(g_args)

    print(" --- Create handle --- \n")
    ret, handles = xdnn.createHandle(g_args['xclbin'], "kernelSxdnn_0")
    if ret != 0:
        print(" --- !!! FAILED: Cannot create handle. --- \n")
        sys.exit(1)

    print(" --- Create fpgaRT --- \n")
    fpgaRT = xdnn.XDNNFPGAOp(handles, g_args)
    g_ctxt["fpgaRT"] = fpgaRT

    print(" --- Weight and Bias --- \n")
    fcWeight, fcBias = xdnn_io.loadFCWeightsBias(g_args)
    g_ctxt["fcWeight"] = fcWeight
    g_ctxt["fcBias"] = fcBias
    
    print(" --- Init input input/output area --- \n")
    if is_deploymode(): 
        g_ctxt['fpgaOutput'] = fpgaRT.getOutputs()
        g_ctxt['fpgaInput'] = fpgaRT.getInputs()
        g_ctxt['inShape'] = (g_args['batch_sz'],) + tuple(fpgaRT.getInputDescriptors().itervalues().next()[1:])
    else:
        g_ctxt['fpgaOutput'] = np.empty((g_args['batch_sz'], g_args['fpgaoutsz'],), dtype=np.float32, order='C')
        g_ctxt['batch_array'] = np.empty(((g_args['batch_sz'],) + g_args['in_shape']), dtype=np.float32, order='C')

    g_ctxt['fcOutput'] = np.empty((g_args['batch_sz'], g_args['outsz'],), dtype=np.float32, order='C')

    print (" --- Get lables --- \n")
    g_ctxt['labels'] = xdnn_io.get_labels(g_args['labels'])
    # golden?   What is that?
    # Seems we are done.

    print(" --- FPGA INITIALIZED! ---\n")

def get_classification(output, pl, labels, topK=5): 
    # See xdnn_io.py, but the code there will just print to stdout.
    # We return the values.
    ret = []
    for i, p in enumerate(pl):
        topXs = xdnn_io.getTopK(output[i,...], labels, topK)
        for prob, lbl in topXs:
            ret.append([p, i, prob, lbl])
    return ret


def img_classify(msg):
    global g_args
    global g_ctxt

    # message is a rowset, one col, a list of file names.
    rs = msg.rowset
    if len(rs.columns) == 0 or rs.columns[0].nrow == 0:
        print("Img classify request size is 0.\n") 
        return None
    print("Img classify request size is {0}.\n".format(rs.columns[0].nrow))
    # Lock the fpga device.   config is protected by this lock as well.

    fpga_lock.acquire()
    ret = []
    
    if is_deploymode():
        firstInput = g_ctxt['fpgaInput'].itervalues().next()
        firstOutput = g_ctxt['fpgaOutput'].itervalues().next()

    for i in xrange(0, rs.columns[0].nrow, g_args['batch_sz']):
        pl = []
        for j in range(g_args['batch_sz']):
            fname = str(rs.columns[0].sdata[i + j])
            print("Running classification for {0}-th images: {1}\n".format(i+j, fname))
            if is_deploymode():
                firstInput[j, ...], _ = xdnn_io.loadImageBlobFromFile(fname,
                    g_args['img_raw_scale'], g_args['img_mean'], g_args['img_input_scale'],
                    g_ctxt['inShape'][2], g_ctxt['inShape'][3])
            else:
                g_ctxt['batch_array'][j, ...], _ = xdnn_io.loadImageBlobFromFile(fname,
                    g_args['img_raw_scale'], g_args['img_mean'], g_args['img_input_scale'],
                    g_args['in_shape'][2], g_args['in_shape'][1])
            pl.append(fname)
        
        if is_deploymode():
            g_ctxt['fpgaRT'].execute(g_ctxt['fpgaInput'], g_ctxt['fpgaOutput'])
            xdnn.computeFC(g_ctxt['fcWeight'], g_ctxt['fcBias'], firstOutput, g_ctxt['fcOutput'])
        else:
            g_ctxt['fpgaRT'].execute(g_ctxt['batch_array'], g_ctxt['fpgaOutput'])
            xdnn.computeFC(g_ctxt['fcWeight'], g_ctxt['fcBias'], g_ctxt['fpgaOutput'], 
                g_args['batch_sz'], g_args['outsz'], g_args['fpgaoutsz'],
                g_ctxt['fcOutput'])

        softmaxOut = xdnn.computeSoftmax(g_ctxt['fcOutput'])
        ret = ret + get_classification(softmaxOut, pl, g_ctxt['labels'])

    fpga_lock.release()

    retmsg = xdrive_pb2.XMsg()
    rs = retmsg.rowset
    # return 4 columns, (filename, ordinal, score, class)
    col1 = rs.columns.add()
    col2 = rs.columns.add()
    col3 = rs.columns.add()
    col4 = rs.columns.add()
    col1.nrow = len(ret)
    col2.nrow = len(ret)
    col3.nrow = len(ret)
    col4.nrow = len(ret)

    for i in range(len(ret)):
        # print("Return {0}, {1}, {2}, {3}.\n".format(a, b, c, d))
        col1.nullmap.append(False)
        col1.sdata.append(ret[i][0])
        col2.nullmap.append(False)
        col2.i32data.append(ret[i][1])
        col3.nullmap.append(False)
        col3.f64data.append(ret[i][2])
        col4.nullmap.append(False)
        col4.sdata.append(ret[i][3])

    return retmsg


if __name__=='__main__':
    init_fpga()
    server.server_start("/tmp/ml.sock", img_classify)
