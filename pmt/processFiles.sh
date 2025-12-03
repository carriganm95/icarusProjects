#!/usr/bin/bash

# Debug mode settings
debug=false
max_files=10
file_count=0

fcl="overlays-wf-analyze.fcl" #mc
#fcl="data-wf-analyze.fcl" #data   

#list="/exp/icarus/data/users/mvicenzi/pmt-calibration/input/files-run9271.list" #data
list="/nashome/m/micarrig/icarus/pmt/v10_06_00_01p04/overlay-files.list" #overlay

outDir="/pnfs/icarus/scratch/users/micarrig/pmt-calibration/overlay/"

for file in $(cat $list); do

    #echo $file
    # Skip if no files match the pattern
    #[[ ! -e "$file" ]] && continue
    
    echo "Processing file: $file"
    htgettoken -v -a htvaultprod.fnal.gov -i icarus
    ((file_count++))
    
    if [[ "$debug" == true ]]; then
        if [[ $file_count -gt $max_files ]]; then
            echo "Debug mode: stopping after $max_files files"
            break
        fi
    fi

    cmd="lar -c $fcl -n -1 -s $file"
    echo "Running command: $cmd"
    eval $cmd
    mkdir -p $outDir/
    mv *mcana*.root $outDir/
done
