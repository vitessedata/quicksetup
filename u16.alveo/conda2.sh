export MLSUITE_ROOT=/home/ftian/data/xilinx/ml-suite
export CONDA2=/opt/anaconda2
export PATH=$CONDA2/bin:$PATH
source $CONDA2/etc/profile.d/conda.sh 

conda activate ml-suite
source $MLSUITE_ROOT/overlaybins/setup.sh alveo-u200
