#!/bin/bash

DB=/data/gottcah2/RefSeq90/RefSeq-r90.cg.BacteriaArchaeaViruses.species.fna

while getopts "input:report:db:threads:h" OPTION
do
     case $OPTION in
        input) FASTA=$OPTARG
           ;;
        report) REPORT=$OPTARG
           ;;
        db) DB=$OPTARG
           ;;
        threads) THREADS=$OPTARG
           ;;
        h) usage
           exit
           ;;
     esac

done

kraken2 -db $DATABASE --report $REPORT --threads $THREADS $FASTA