#!/bin/bash

. /kb/deployment/user-env.sh

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  mkdir -p /data/kraken2
  cd /data/kraken2

  mkdir -p /data/kraken2/kraken2-microbial
  echo "downloading https://refdb.s3.climb.ac.uk/kraken2-microbial"
  if [ -s "/data/kraken2/kraken2-microbial/hash.k2d" ];
  then
    echo "kraken2-microbial exists"
  else
    cd kraken2-microbial
    wget -c https://refdb.s3.climb.ac.uk/kraken2-microbial/hash.k2d
    wget https://refdb.s3.climb.ac.uk/kraken2-microbial/opts.k2d
    wget https://refdb.s3.climb.ac.uk/kraken2-microbial/taxo.k2d
  fi

  cd /data/kraken2
  echo "downloading ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/minikraken2_v1_8GB_201904_UPDATE.tgz"
  if [ -s "/data/kraken2/minikraken2_v1_8GB/database100mers.kmer_distrib" ];
  then
    echo "minikraken2_v1_8GB exists"
  else
    wget -q ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/minikraken2_v1_8GB_201904_UPDATE.tgz
    tar -xzvf minikraken2_v1_8GB_201904_UPDATE.tgz
    rm minikraken2_v1_8GB_201904_UPDATE.tgz
  fi

  echo "downloading ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_Greengenes_20190418.tgz"

  if [ -s "/data/kraken2/16S_Greengenes_20190418/database100mers.kmer_distrib" ];
  then
    echo "16S_Greengenes_20190418 exists"
  else
    wget -q ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_Greengenes_20190418.tgz
    tar -xzvf 16S_Greengenes_20190418.tgz
    rm 16S_Greengenes_20190418.tgz
  fi

  echo "downloading ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_RDP_20190418.tgz"
  if [ -s "/data/kraken2/16S_RDP_20190418/database100mers.kmer_distrib" ];
  then
    echo "16S_RDP_20190418.tgz exists"
  else
    wget -q ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_RDP_20190418.tgz
    tar -xzvf 16S_RDP_20190418.tgz
    rm 16S_RDP_20190418.tgz
  fi

  echo "downloading ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_Silva_20190418.tgz"
  if [ -s "/data/kraken2/16S_Silva_20190418/database200mers.kmer_distrib" ];
  then
    echo "16S_Silva_20190418 exists"
  else
    wget -q ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_Silva_20190418.tgz
    tar -xzvf 16S_Silva_20190418.tgz
    rm 16S_Silva_20190418.tgz
  fi

  if [ -s "/data/kraken2/minikraken2_v1_8GB/database100mers.kmer_distrib" -a -s "/data/kraken2/16S_Greengenes_20190418/database100mers.kmer_distrib" -a -s "/data/kraken2/16S_RDP_20190418/database100mers.kmer_distrib" -a -s "/data/kraken2/16S_Silva_20190418/database200mers.kmer_distrib" ] ; then
    echo "DATA DOWNLOADED SUCCESSFULLY"
    touch /data/__READY__
  else
    echo "Init failed"
  fi


elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
