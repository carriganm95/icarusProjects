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

    #crete new log file names incase job numbers are not sequential
    errFileName="job_${jobNum}.err"
    outFileName="job_${jobNum}.out"
    
    # Attempt to copy logs, but don't fail if it doesn't work
    if [[ -f "$errFile" ]]; then
        echo "Transferring err file to $log_dir/$errFileName"
        ifdh cp "$errFile" "$log_dir/$errFileName" 2>/dev/null || echo "Warning: Failed to transfer $errFile"
    fi

    echo "Transferring out file to $log_dir"
    
    if [[ -f "$outFile" ]]; then
        echo "Transferring out file to $log_dir/$outFileName"
        ifdh cp "$outFile" "$log_dir/$outFileName" 2>/dev/null || echo "Warning: Failed to transfer $outFile"
    fi
    
    exit $exit_code
}

required_vars=(fclFile fileList outputDir JOBSUBJOBSECTION CONDOR_DIR_INPUT)
for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "ERROR: environment variable $var is unset or empty" >&2
        cleanup_and_exit 10
    fi
done

echo "Starting run.sh script on grid worker node $HOSTNAME"

echo "doing general  software setup"
source /cvmfs/icarus.opensciencegrid.org/products/icarus/setup_icarus.sh

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

# Read the specific line from inputFile.list
line=$(sed -n "$((JOBSUBJOBSECTION + 1))p" "${CONDOR_DIR_INPUT}/${fileList}")
echo "Read line: $line"

# Check if line contains both a number and filename (space-separated)
if [[ $line =~ ^[0-9]+[[:space:]]+(.+)$ ]]; then
    # Extract number and filename
    jobNum=$(echo "$line" | awk '{print $1}')
    runFile=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ *//')
    echo "Found number and file: jobNum=$jobNum, runFile=$runFile"
else
    # Treat entire line as filename
    runFile="$line"
    echo "Selected file: $runFile"
    
    # If caf is true, extract job number from filename
    if [[ "$caf" == "true" ]]; then
        # Extract number after last underscore and before .root
        if [[ "$runFile" =~ _([0-9]+)\.root$ ]]; then
            jobNum="${BASH_REMATCH[1]}"
            echo "Extracted jobNum from filename: $jobNum"
        else
            echo "WARNING: Could not extract job number from filename $runFile"
        fi
    fi
fi

# Check if file was found
if [ -z "$runFile" ]; then
    echo "ERROR: No file found at line $jobid in $fileList"
    cleanup_and_exit 21
fi

echo "the job number is: $jobNum" 

#Make sure we know where we are working and where to look for certain files
echo "printing working directory of grid node" 
pwd
local_dir=`pwd`
#see whats there
echo "the local repo has the following folders and files:"  
ls -ltrha 
echo "the script that we are trying to run looks like this:" 
cat run.sh 
echo "now cd-ing to CONDOR_DIR_INPUT AT $CONDOR_DIR_INPUT" 
cd $CONDOR_DIR_INPUT
echo "now printing the CONDOR_DIR_INPUT path:" 
pwd 
echo "now ls-ing within CONDOR_DIR_INPUT at $CONDOR_DIR_INPUT" 
ls -ltrha 
echo "now trying to untar the data files and the job input files" 
mkdir run
cd run

echo "checking contents of input tar file if it exists at ${INPUT_TAR_DIR_LOCAL} with products ${PRODUCTS}"
ls -alh ${INPUT_TAR_DIR_LOCAL}

echo $PWD
if ! setup icaruscode v10_06_00_04p02 -q e26:prof -z ${INPUT_TAR_DIR_LOCAL}:${PRODUCTS}; then
    echo "ERROR: setup icaruscode failed" >&2
    cleanup_and_exit 30
fi

if ! ups active; then
    echo "ERROR: ups active failed" >&2
    cleanup_and_exit 31
fi

cd ..

echo "Running on file ${runFile}"
if [ "$caf" == "false" ]; then
    larCmd="lar -c ${fclFile} -n ${nEvents} -s ${runFile} -o output_${jobNum}.root"
else
    larCmd="lar -c ${fclFile} -n ${nEvents} -s ${runFile}"
fi
echo "Executing: $larCmd"
if ! eval $larCmd; then
    echo "ERROR: lar command failed for file $runFile" >&2
    cleanup_and_exit 40
fi

echo "now trying to ifdf cp all output files over to scratch area"
ls -alh 
# Calculate subdirectory based on jobNum (groups of 100)
subdir=$(printf "%02d" $((jobNum / 100)))
target_dir="${outputDir}/outputs/${subdir}"

# Check if target directory exists, create if it doesn't
if ! ifdh ls "$target_dir" >/dev/null 2>&1; then
    echo "Target directory: $target_dir does not exist"
    cleanup_and_exit 50
fi

if [ $caf == true ]; then
    base="${runFile##*/}"
    base="${base%.root}"

    for f in ${base}*.caf.root; do
        if [[ -e "$f" ]]; then
            ifdh cp "$f" "$target_dir/" || cleanup_and_exit 61
        fi
    done
else
    if ! ifdh cp "output_${jobNum}.root" "$target_dir/"; then
        echo "ERROR: ifdh cp failed for output_${jobNum}.root -> $target_dir/" >&2
        cleanup_and_exit 60
    fi
fi

ls -alh

echo "Job completed successfully"
cleanup_and_exit 0

exit 0
#End of script
