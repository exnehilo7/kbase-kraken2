#!/bin/bash

set -e;

usage(){
cat << EOF
USAGE: $0 -i <FASTQ> -d <DATABASE> -o <OUTDIR> -p <PREFIX> [OPTIONS]

OPTIONS:
   -i      Input a FASTQ file (singleton or pair-end sequences separated by comma)
   -d      Database
   -n      Additional options for centrifuge
   -o      Output directory
   -p      Output prefix
   -t      Number of threads (default: 24)
   -h      help
EOF
}

FASTQ=
REFDB=
PREFIX=
OUTPATH=
THREADS=
OPTIONS=
rootdir=$( cd $(dirname $0) ; pwd -P )
while getopts "i:d:o:p:t:n:h" OPTION
do
     case $OPTION in
        i) FASTQ=$OPTARG
           ;;
        d) REFDB=$OPTARG
           ;;
        o) OUTPATH=$OPTARG
           ;;
        p) PREFIX=$OPTARG
           ;;
        t) THREADS=$OPTARG
           ;;
        n) OPTIONS=$OPTARG
           ;;
        h) usage
           exit
           ;;
     esac
done
export PATH=$rootdir:$PATH;

mkdir -p $OUTPATH

echo "[BEGIN]"

set -x;

REPORT=$OUTPATH/$PREFIX.report.csv
echo "$DB, $REPORT, $THREADS, $FASTQ"
kraken2 --db $REFDB --report $REPORT --threads $THREADS $FASTQ

#generate out.list
convert_krakenRep2list.pl < $REPORT > $OUTPATH/$PREFIX.out.list
convert_krakenRep2tabTree.pl < $REPORT > $OUTPATH/$PREFIX.out.tab_tree

# Make Krona plot
ktImportText  $OUTPATH/$PREFIX.out.tab_tree -o $OUTPATH/$PREFIX.krona.html

#generate Tree Dendrogram
phylo_dot_plot.pl -i $OUTPATH/$PREFIX.out.tab_tree -p $OUTPATH/$PREFIX.tree -t 'Kraken2'

set +xe;
echo "";
echo "[END] $OUTPATH $PREFIX";