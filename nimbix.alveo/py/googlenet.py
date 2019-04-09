#
# 
# A server running googlenet on FPGA.  See Xilinx ml-suite tutorial notebook
# Right now, it is a multi threaded server, but each thread locks the device
#
import os, sys
import threading

import numpy as np
import xdnn, xdnn_io

import xdrive_pb2, server

fpga_lock = threading.RLock()

g_mlsuite = "/opt/MLsuite"
g_platform = "alveo-u200"
g_datadir = g_mlsuite + "/examples/classification/data"
g_xclbin = g_mlsuite + "/overlaybins/alveo-u200/overlay_2.xclbin"
g_netFile = g_datadir + "/googlenet_v1_56.json" 
g_fpgaCfgFile = g_datadir + "/googlenet_v1_8b.json"
g_doQuant = True
g_xdnnLib = g_mlsuite + "/xfdnn/rt/xdnn_cpp/lib/libxfdnn.so"
g_fpgaOutputSize = 1024
g_firstFpgaLayerName = "conv1/7x7_s2"
g_xdnnTestDataDir = g_datadir + "/googlenet_v1_data"
g_lableFile = g_mlsuite + "/examples/classification/synset_words.txt"
g_raw_scale = 255.0
g_mean = [104.007, 116.669, 122.679]
g_input_scale = 1.0

g_scaleA = 10000
g_scaleB = 30
g_img_shape = [3, 224, 224]
g_outputSize = 1000

g_img_c = 3
g_img_h = 224
g_img_w = 224

g_batchSize = 1
g_numDevices = 1
g_useBlas = False

# Do not mess with this one.  Xilinx notebook set g_PE to 0
# the code runs fine for a few images then crash.  Setting to
# -1 seesm to run fine.
g_PE = -1

g_fcWeight = None
g_fcBias = None
g_weightsBlob = None
g_labelarray = []
g_inputs = None
g_inputbuf = None
g_fpgaOutput = None

def init_fpga():
    global g_inputs
    global g_inputbuf
    global g_fpgaOutput
    global g_weightsBlob
    global g_fcWeight
    global g_fcBias
    print (" --- INIT FPGA --- \n")
    print ("xclbin: {0}.\n".format(g_xclbin))
    print ("xdnnLib: {0}.\n".format(g_xdnnLib))
    ret = xdnn.createManager(g_xdnnLib)
    if ret != True:
        raise SystemExit("Error: xdnn createManager failed.")
    (g_fcWeight, g_fcBias) = xdnn_io.loadFCWeightsBias(g_xdnnTestDataDir)

    ret = xdnn.createHandle(g_xclbin, "kernelSxdnn_0", g_xdnnLib, g_numDevices) 
    if ret:
        raise SystemExit("ERROR: Unable to create handle to FPGA")
    else:
        print("INFO: Sucessfully create handle to FPGA.")

    # magics.   See ml-suite/notebooks tutorial.   Should we overwrite PE?
    args = { 'datadir': g_xdnnTestDataDir,
             'quantizecfg': g_fpgaCfgFile,
             'scaleA': g_scaleA,
             'scaleB': g_scaleB,
             'PE': -1,
             'netcfg': g_netFile }

    print (" --- load weights --- \n")
    g_weightsBlob = xdnn_io.loadWeightsBiasQuant(args)

    print (" --- read lable file --- \n")
    with open(g_lableFile, 'r') as f:
        for line in f:
            g_labelarray.append(line.strip())

    print (" --- prepare inputs --- \n")
    g_inputs = np.zeros((g_batchSize, g_img_c, g_img_h, g_img_w), dtype=np.float32);
    g_inputbuf = np.zeros((g_batchSize, g_img_c, g_img_h, g_img_w), dtype=np.float32);

    print "g_inputs", g_inputs

    print (" --- prepare outputs --- \n")
    g_fpgaOutput, fpgaHandle = xdnn.makeFPGAFloatArray(g_fpgaOutputSize * g_batchSize) 

def get_classification(output, fn): 
    # See xdnn_io.py, but the code there will just print to stdout.
    # We return the values.
    if isinstance (output, np.ndarray):
        output = output.flatten().tolist()

    ret = []
    idxArr = []
    for i in range(g_outputSize): 
        idxArr.append(i)

    l_batchsz = len(output) / g_outputSize 
    for i in range(l_batchsz):
        inputImage = fn 
        startIdx = i * g_outputSize 
        vals = output[startIdx:startIdx + g_outputSize]
        top5 = sorted(zip(vals, idxArr), reverse=True)[:5]
        for j in range(len(top5)):
            ret.append((inputImage, j, top5[j][0], g_labelarray[top5[j][1]]))

    # print("get_classification: {0}.\n".format(ret))
    return ret

def img_classify(msg):
    global g_inputs
    global g_inputbuf
    global g_fpgaOutput
    global g_weightsBlob
    global g_fcWeight
    global g_fcBias

    # message is a rowset, one col, a list of file names.
    rs = msg.rowset
    if len(rs.columns) == 0 or rs.columns[0].nrow == 0:
        print("Img classify request size is 0.\n") 
        return None
    print("Img classify request size is {0}.\n".format(rs.columns[0].nrow))
    # Lock the fpga device.   config is protected by this lock as well.

    fpga_lock.acquire()
    ret = None
    
    for i in range(rs.columns[0].nrow):
        fname = rs.columns[0].sdata[i]
        print("Running classification for images: {0}\n".format(fname))
        print("Prepare inputs ...\n")

        # g_batchSize = 1, for now.
        print "g_inputs", g_inputs
        g_inputs[0] = xdnn_io.loadImageBlobFromFile(str(fname), g_raw_scale, g_mean, g_input_scale, g_img_h, g_img_w)

        print("Quantize inputs ...\n") 
        quantizeInputs = xdnn.quantizeInputs(g_firstFpgaLayerName, g_fpgaCfgFile, g_scaleB, g_inputs)

        print("Prepare inputs for fpga inputs ...\n") 
        fpgaInputs = xdnn.prepareInputsForFpga(quantizeInputs, g_fpgaCfgFile, g_scaleB, -1, g_firstFpgaLayerName) 

        print("Run FPGA commands ...\n") 
        xdnn.execute(g_netFile,
                g_weightsBlob, fpgaInputs, g_fpgaOutput,
                g_batchSize,
                g_fpgaCfgFile, g_scaleB, g_PE)

        print("Compute FC ...\n")
        fcOutput = xdnn.computeFC(g_fcWeight, g_fcBias, g_fpgaOutput,
                g_batchSize, g_outputSize, g_fpgaOutputSize, g_useBlas)

        print("Softmax ...\n")
        softmaxOut = xdnn.computeSoftmax(fcOutput, g_batchSize) 
        ret = get_classification(softmaxOut, fname) 

    fpga_lock.release()

    # Now construct return msg
    if ret == None:
        print("Return None: ???\n")
        return None

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
        (a, b, c, d) = ret[i]
        # print("Return {0}, {1}, {2}, {3}.\n".format(a, b, c, d))
        col1.nullmap.append(False)
        col1.sdata.append(a)
        col2.nullmap.append(False)
        col2.i32data.append(b)
        col3.nullmap.append(False)
        col3.f64data.append(c)
        col4.nullmap.append(False)
        col4.sdata.append(d)

    return retmsg


if __name__=='__main__':
    init_fpga()
    server.server_start("/tmp/ml.sock", img_classify)
