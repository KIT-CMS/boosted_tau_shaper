#!/bin/bash

if [[ $(hostname) =~ portal1 || $(hostname) =~ centos7 ]]; then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh
elif [[ $(hostname) =~ bms ]]; then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-dbg/setup.sh
fi

export PYTHONPATH=$PWD:$PYTHONPATH
