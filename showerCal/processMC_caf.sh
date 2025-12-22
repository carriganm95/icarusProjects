#!/usr/bin/bash

# Debug mode settings
debug=false
max_files=40
file_count=0

directory="/pnfs/icarus/scratch/users/micarrig/showerDeDx_MC/norm3/" 

for file in "$directory"/stage1_*.root; do
    # Skip if no files match the pattern
    [[ ! -e "$file" ]] && continue
    
    echo "Processing file: $file"
    htgettoken -v -a htvaultprod.fnal.gov -i icarus
    ((file_count++))
    
    if [[ "$debug" == true ]]; then
        if [[ $file_count -gt $max_files ]]; then
            echo "Debug mode: stopping after $max_files files"
            break
        fi
    fi

    cmd="lar -c srcs/icaruscode/fcl/caf/cafmakerjob_icarus_detsim2d.fcl -n -1 -s $file"
    echo "Running command: $cmd"
    eval $cmd
    mkdir -p $directory/caf/
    mv *.flat.caf*.root $directory/caf/
done