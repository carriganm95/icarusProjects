#!/bin/bash


definition="Icaruspro_2025_wcdnn_production_Reproc_Run2_SBN_v10_06_00_01p05_bnbmajority_calibtuples"

files=$(samweb list-definition-files "$definition")

counter=0
> calFiles.list

for f in $files; do
    #if [ $counter -ge 10 ]; then
    #    break
    #fi

    loc=$(samweb locate-file "$f" | awk '{print $1; exit}')
    if [[ -z "$loc" ]]; then
        echo "Warning: no location found for $f" >&2
        continue
    fi

    root_uri=${loc#dcache:/pnfs}
    root_uri="root://fndcadoor.fnal.gov:${root_uri}"

    #if ! root -l -b -q -e "TFile* tf = TFile::Open(\"${root_uri}/${f}\"); if (!tf || tf->IsZombie()) gSystem->Exit(1);" &>/dev/null; then
    #    echo "Warning: failed to open ${root_uri}/${f} with ROOT" >&2
    #    continue
    #fi

    echo "${root_uri}/${f}" >> calFiles.list
    counter=$((counter + 1))

done

echo "Total files processed: $counter"
