#!/bin/bash

jobNum=$JOBSUBJOBSECTION
# Calculate subdirectory based on job section (groups of 100)
subdir=$(printf "%02d" $(($jobNum / 100)))
log_dir="${outputDir}/logs/${subdir}"

errFile="${CONDOR_DIR_INPUT}/job_${jobNum}.err"
outFile="${CONDOR_DIR_INPUT}/job_${jobNum}.out"

# Redirect stdout and stderr to log files in subdirectories
exec > >(tee -a "$outFile") 2> >(tee -a "$errFile" >&2)

# Cleanup function to transfer logs before exit
cleanup_and_exit() {
    local exit_code=$1
    echo "Cleanup: transferring log files before exit with code $exit_code"
    
    # Check if log directory exists, create if it doesn't
    if ! ifdh ls "$log_dir" >/dev/null 2>&1; then
        echo "Creating log directory: $log_dir"
        ifdh mkdir "$log_dir" 2>/dev/null || true
    fi

    echo "Transferring log files to $log_dir"
    
    # Attempt to copy logs, but don't fail if it doesn't work
    if [[ -f "$errFile" ]]; then
        echo "Transferring err file to $log_dir"
        ifdh cp "$errFile" "$log_dir/" 2>/dev/null || echo "Warning: Failed to transfer $errFile"
    fi

    echo "Transferring out file to $log_dir"
    
    if [[ -f "$outFile" ]]; then
        echo "Transferring out file to $log_dir"
        ifdh cp "$outFile" "$log_dir/" 2>/dev/null || echo "Warning: Failed to transfer $outFile"
    fi
    
    exit $exit_code
}


required_vars=(outputDir JOBSUBJOBSECTION CONDOR_DIR_INPUT anaFile)
for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "ERROR: environment variable $var is unset or empty" >&2
        cleanup_and_exit 10
    fi
done

echo "Starting run.sh script on grid worker node $HOSTNAME"

echo "doing general software setup"

# Run setup commands in the current shell using curly braces
if ! {

    # Experiment and common product setups
    source /cvmfs/icarus.opensciencegrid.org/products/icarus/setup_icarus.sh || { echo "Failed to setup ICARUS environment"; exit 15; }
    source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh || { echo "Failed to setup Fermilab common products"; exit 15; }

    # SAM client setup
    setup sam_web_client || { echo "Failed to setup SAM client"; exit 15; }

}; then
    echo "Issue setting up packages"
    cleanup_and_exit 15
fi

echo "Running on python version $(which python3)"

export SAM_EXPERIMENT=sbn
export SAM_GROUP=sbn
export SAM_STATION=sbn
export SAM_WEB_HOST=samsbn.fnal.gov
export IFDH_BASE_URI=http://samsbn.fnal.gov:8480/sam/sbn/api/

echo "software setup complete"
echo "Running on fclFile: $fclFile and fileList: $fileList"
echo "outputDir is set to: $outputDir"
echo "logDir is set to: $log_dir"
echo "echo-ing JOBSUBID: $JOBSUBJOBID" 

ls -ltrha
echo $PWD
ls -ltrha $CONDOR_DIR_INPUT

# Add this after the jobid extraction
echo "Reading file from $fileList at line $JOBSUBJOBSECTION"
if [[ ! -s ${CONDOR_DIR_INPUT}/${fileList} ]]; then
    echo "ERROR: File list ${CONDOR_DIR_INPUT}/${fileList} is missing or empty" >&2
    cleanup_and_exit 20
fi

echo "the job number is: $jobNum" 
outputFile="output_${jobNum}.root"

#Make sure we know where we are working and where to look for certain files
echo "printing working directory of grid node" 
pwd
local_dir=`pwd`
#see whats there
echo "the local repo has the following folders and files:"  
ls -ltrha 
echo "now cd-ing to CONDOR_DIR_INPUT AT $CONDOR_DIR_INPUT" 
cd $CONDOR_DIR_INPUT
work_dir="${PWD}"
echo "now printing the CONDOR_DIR_INPUT path:" 
pwd 
echo "now ls-ing within CONDOR_DIR_INPUT at $CONDOR_DIR_INPUT" 
ls -ltrha 

# echo $PWD
# if ! setup sbnana v10_01_02 -q e26:prof; then
#     echo "ERROR: setup sbnana failed with exit code $?" >&2
#     cleanup_and_exit 30
# fi

export CAFANA_DISABLE_SNAPSHOTS=1

# if ! ups active; then
#     echo "ERROR: ups active failed" >&2
#     cleanup_and_exit 31
# fi

if [ -f ${CONDOR_DIR_INPUT}/${anaFile} ]; then
    echo "Found analysis file: ${anaFile}"
    #cp "${CONDOR_DIR_INPUT}/${anaFile}" "${work_dir}/"
else
    echo "ERROR: Analysis file ${anaFile} not found in ${CONDOR_DIR_INPUT}" >&2
    cleanup_and_exit 25
fi

macro_file=$(basename "${anaFile}")
macro_path="${work_dir}/${macro_file}"

if [[ ! -f "${macro_path}" ]]; then
    echo "ERROR: Expected macro ${macro_path} not present after copy" >&2
    cleanup_and_exit 26
fi

echo "Macro directory contents:"
ls -alh "${work_dir}"


if ! setup icaruscode v10_06_00_07 -q e26:prof; then
    echo "ERROR: setup icaruscode failed" >&2
    cleanup_and_exit 30
else
    ups active
    echo "Python version after sbnana setup: $(python3 --version)"
fi

echo "Checking local tar directory ${INPUT_TAR_DIR_LOCAL} contents:"
ls -alh "${INPUT_TAR_DIR_LOCAL}"

#update python patch to include the python packages tarball
if [ -f "${CONDOR_DIR_INPUT}/python.tar.gz" ]; then
    echo "Found python packages tarball: python.tar.gz, extracting..."
    tar -xzf "${CONDOR_DIR_INPUT}/python.tar.gz" -C "${work_dir}/" || { echo "ERROR: Failed to extract python packages from python.tar.gz" >&2; cleanup_and_exit 27; }
    export PYTHONPATH="${work_dir}/nashome/m/micarrig/.local/lib/python3.9/site-packages:${PYTHONPATH}"
    echo PYTHONPATH is now $PYTHONPATH
else
    echo "ERROR: Python packages tarball python.tar.gz not found in ${CONDOR_DIR_INPUT}" >&2
    cleanup_and_exit 28
fi

#check that input file is valid and has events if a tree name is provided
if [ -n "$treeName" ]; then
    if ! root -l -n -b -q -e \
        "TFile* f = TFile::Open(\"${runFile}\"); \
        if (!f || f->IsZombie()) { \
            std::cout << \"ERROR: Cannot open file ${runFile}\" << std::endl; \
            gSystem->Exit(1); \
        } \
        TTree* tree = (TTree*)f->Get(\"${treeName}\"); \
        if (!tree) { \
            std::cout << \"ERROR: Tree ${treeName} not found in ${runFile}\" << std::endl; \
            f->Close(); \
            gSystem->Exit(1); \
        } \
        Long64_t entries = tree->GetEntries(); \
        std::cout << \"File ${runFile} has \" << entries << \" entries\" << std::endl; \
        if (entries == 0) { \
            std::cout << \"ERROR: File ${runFile} has no events\" << std::endl; \
            f->Close(); \
            gSystem->Exit(1); \
        } \
        f->Close(); \
        gSystem->Exit(0);"; then
        echo "ERROR: File $runFile is empty or invalid" >&2
        cleanup_and_exit 35
    fi
fi

inputFile="${INPUT_TAR_DIR_LOCAL}/gridSkimFiles.list"
fclFile="${INPUT_TAR_DIR_LOCAL}/gridFcl/hitTuning_test_${jobNum}.fcl"
echo "Running job ${jobNum} with script ${macro_file} on input file ${inputFile} with output ${outputFile}"

pushd "${work_dir}" >/dev/null
echo "Executing: python3 ${macro_file} ${inputFile} ${work_dir}/${outputFile} ${fclFile} ${jobNum} ${INPUT_TAR_DIR_LOCAL}"
if ! python3 ${macro_file} ${inputFile} ${work_dir}/${outputFile} ${fclFile} ${jobNum} ${INPUT_TAR_DIR_LOCAL}; then
    popd >/dev/null
    echo "ERROR:  Command failed for file $runFile with exit code $?" >&2
    cleanup_and_exit 40
fi
popd >/dev/null

echo "JOb completed checking contents of working directory"
ls -ltrha "${work_dir}"

if [[ ! -f "${work_dir}/${outputFile}" ]]; then
    echo "ERROR: Expected output ${work_dir}/${outputFile} not produced" >&2
    cleanup_and_exit 45
else
    mv -f "${work_dir}/${outputFile}" "${CONDOR_DIR_INPUT}/"
fi

echo "now trying to ifdf cp all output files over to scratch area"

# Calculate subdirectory based on jobNum (groups of 100)
subdir=$(printf "%02d" $((jobNum / 100)))
target_dir="${outputDir}/outputs/${subdir}"

# Check if target directory exists, create if it doesn't
if ! ifdh ls "$target_dir" >/dev/null 2>&1; then
    echo "Target directory: $target_dir does not exist"
    cleanup_and_exit 50

fi

if ! ifdh cp "${CONDOR_DIR_INPUT}/output_${jobNum}.root" "$target_dir/"; then
    echo "ERROR: ifdh cp failed for output_${jobNum}.root -> $target_dir/" >&2
    cleanup_and_exit 60
fi
if ! ifdh cp "${work_dir}/hist_output_${jobNum}.root" "$target_dir/"; then
    echo "ERROR: ifdh cp failed for hist_output_${jobNum}.root -> $target_dir/" >&2
    cleanup_and_exit 61
fi
if ! ifdh cp "${work_dir}/hitTuning_${jobNum}.db" "$target_dir/"; then
    echo "ERROR: ifdh cp failed for hitTuning_${jobNum}.db -> $target_dir/" >&2
    cleanup_and_exit 62
fi


echo "Job completed successfully"
cleanup_and_exit 0

exit 0
#End of script
