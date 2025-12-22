#!/usr/bin/bash

# Debug mode settings
debug=true
max_files=40
file_count=0

outputDir="/pnfs/icarus/scratch/users/micarrig/showerDeDx_MC/norm3/"

while read -r file; do
    echo "Processing file: $file"
    htgettoken -v -a htvaultprod.fnal.gov -i icarus

    ((file_count++))

    output_file="/pnfs/icarus/scratch/users/micarrig/showerDeDx_MC/stage1_mc_${file_count}.root"
    if [[ -f "$output_file" ]]; then
        echo "Output file $output_file already exists, skipping..."
        continue
    fi

    if [[ "$debug" == true ]]; then
        if [[ $file_count -gt $max_files ]]; then
            echo "Debug mode: stopping after $max_files files"
            break
        fi
    fi

    outputFile="${outputDir}/stage1_mc_${file_count}.root"
    # Check if output file already exists
    if [[ -f "$outputFile" ]]; then
        echo "Output file already exists, skipping..."
        continue
    fi
    cmd="lar -c srcs/icaruscode/fcl/standard/mc/stage1_run2_shwcal_mc_icarus.fcl -n -1 -s $file -o $outputFile"
    echo "Running command: $cmd"
    eval $cmd
done < testFiles.txt