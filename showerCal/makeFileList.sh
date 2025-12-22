#!/bin/bash


#definition="micarrig_shower_dEdx_cal_reco1_to_caf_shower_dEdx_cal"
definition="micarrig_NUMIRun2_10pct_reco1_to_caf_shower_dEdx_cal" #stage 0 10% numi run2
#localPath="/pnfs/sbn/data/sbn_fd/poms_production/mc/2025A_ICARUS_NuGraph2/NuMI_MC_FullTrainingSample/v10_06_00_04p02/stage1/*/*/*/*.root"
#localPath="/pnfs/icarus/scratch/users/micarrig/showerEnergyCal/*/*.root"
#localPath="/pnfs/icarus/scratch/users/micarrig/showerEnergyCalCaf/outputs/*/output*.flat.caf.root"
#localPath="/pnfs/icarus/scratch/users/micarrig/showerEnergyCalV2/outputs/*/*.root" #stage 1 numi data run2 (10%)
#localPath="/pnfs/icarus/scratch/users/micarrig/showerEnergyCalNormMC/outputs/*/*.root" #stage 1 numi MC run2
localPath="/pnfs/icarus/scratch/users/micarrig/showerEnergyCalNorm/outputs/*/*.root" #stage 1 numi MC run2 normalized
outputList="numiMC_run2_stage1Norm.list"
treeName="Events"

checkFile=false
debug=false

declare -A existing_files=()

# check for existing files in output list
load_existing_files() {
    if [[ -f "$outputList" ]]; then
        while IFS= read -r line; do
            [[ -n "$line" ]] && existing_files["$line"]=1
        done < "$outputList"
    else
        touch "$outputList"
    fi
}

# function to check if a ROOT file can be opened and contains a non-empty tree
checkRootFile() {
    local filePath="$1"
    local treeName="$2"
    
    if ! root -l -b -q -e "TFile* tf = TFile::Open(\"$filePath\"); if (!tf || tf->IsZombie()) gSystem->Exit(1); TTree* tree = nullptr; tf->GetObject(\"$treeName\", tree); if (!tree) gSystem->Exit(2); if (tree->GetEntries() == 0) gSystem->Exit(3);" &>/dev/null; then
        status=$?
        case $status in
            1) echo "Warning: failed to open $filePath with ROOT" >&2 ;;
            2) echo "Warning: tree '$treeName' not found in $filePath" >&2 ;;
            3) echo "Warning: tree '$treeName' empty in $filePath" >&2 ;;
            *) echo "Warning: ROOT check failed for $filePath (code $status)" >&2 ;;
        esac
        return 1
    fi
    return 0
}

# function to process local files
process_files_local() {

    echo "Processing local files from $localPath"

    local counter=0
    files=($localPath)
    total_files=${#files[@]}
    echo "Found $total_files files to process"
    
    for f in "${files[@]}"; do
        if [ $counter -ge 100 ] && $debug; then
            break
        fi

        if [ $counter -gt 0 ] && [ $((counter % 10)) -eq 0 ]; then
            echo "Added $counter / $total_files files so far..."
        fi

        if [[ ! -f "$f" ]]; then
            echo "Warning: $f not found" >&2
            continue
        fi

        remote_path="root://fndcadoor.fnal.gov://${f#/pnfs/}"

        if [[ -n "${existing_files["$remote_path"]}" ]]; then
            if $debug; then
                echo "Skipping existing file: $remote_path"
            fi
            continue
        fi

        if [ $checkFile = true ]; then
            if ! checkRootFile "$remote_path" "$treeName"; then
                continue
            fi
        fi

        if $debug; then
            echo "Adding new file: $remote_path"
        fi

        echo "$remote_path" >> "$outputList"
        existing_files["$remote_path"]=1
        counter=$((counter + 1))

    done

    echo "Total new files added: $counter"
}

# function to process SAM files
process_files_sam() {

    files=$(samweb -e icarus list-files "defname: $definition")

    local counter=0

    for f in $files; do
        # if [ $counter -ge 10 ]; then
        #     break
        # fi

        loc=$(samweb locate-file "$f" | awk '{print $1; exit}')
        if [[ -z "$loc" ]]; then
            echo "Warning: no location found for $f" >&2
            continue
        fi

        root_uri=${loc#dcache:/pnfs}
        root_uri="root://fndcadoor.fnal.gov:${root_uri}"
        full_uri="${root_uri}/${f}"

        if [[ -n "${existing_files["$full_uri"]}" ]]; then
            if $debug; then
                echo "Skipping existing file: $full_uri"
            fi
            continue
        fi

        # if ! checkRootFile "$full_uri" "$treeName"; then
        #     continue
        # fi

        if $debug; then
            echo "Adding new file: $full_uri"
        fi

        echo "$full_uri" >> "$outputList"
        existing_files["$full_uri"]=1
        counter=$((counter + 1))
    done

    echo "Total new files added: $counter"
}

htgettoken -a htvaultprod.fnal.gov -i icarus

load_existing_files
process_files_local
#process_files_sam