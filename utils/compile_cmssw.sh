### Setup of CMSSW release
export SCRAM_ARCH=el9_amd64_gcc12
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

CMSSW=CMSSW_14_1_0_pre4
cmsrel $CMSSW
cd $CMSSW/src/
cmsenv

scram b -j 8
cd ../../