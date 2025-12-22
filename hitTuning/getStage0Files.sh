#!/bin/bash

# This script retrieves Stage 0 files for hit tuning analysis

dataset="production_mc_2025A_ICARUS_Overlays_BNB_MC_RUN2_September_v10_06_00_04p04_stage0"

files=$(samweb -e icarus list-files "defname: $dataset")

combineFiles=()
counter=0
for file in $files; do
    if [ $counter -le 30 ]; then
        ((counter++))
        continue
    fi
    if [ $counter -ge 60 ]; then
        break
    fi
    loc=$(samweb -e icarus locate-file $file)
    loc=${loc#dcache:/pnfs/}
    path="root://fndcadoor.fnal.gov:/$loc/$file"
    #echo "File $counter: $path"
    combineFiles+=("$path")
    ((counter++))
done

# Write combineFiles to a txt file, one entry per line
output_file="stage0_files2.txt"
printf '%s\n' "${combineFiles[@]}" > "$output_file"
echo "Wrote ${#combineFiles[@]} entries to $output_file"
