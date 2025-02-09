#!/bin/bash

### Setup of CMSSW release
CMSSW=CMSSW_14_1_0_pre4

export SCRAM_ARCH=el9_amd64_gcc12
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project $CMSSW
pushd $CMSSW/src
eval `scramv1 runtime -sh`

# combine on 102X slc7
git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
# cd HiggsAnalysis/CombinedLimit
# git fetch origin
# git checkout v8.0.1
# cd -

# CombineHarvester (current master for 102X)
git clone git@github.com:cms-analysis/CombineHarvester.git CombineHarvester

# SM analysis specific code
git clone git@github.com:KIT-CMS/SMRun2Legacy.git CombineHarvester/SMRun2Legacy -b ul

# TauID analysis specific code
git clone git@github.com:conformist89/TauIDSFMeasurement.git CombineHarvester/TauIDSFMeasurement -b combined-fit

# compile everything
# Build
scram b clean
scram b -j 10