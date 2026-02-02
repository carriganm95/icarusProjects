#! /bin/bash

sourceDir="/pnfs/icarus/scratch/users/micarrig/hitTuning/mc/gridTest/"
exe="runJob.sh"
export fclFile=""
export tarFile="hitTuning.tar.gz"
export fileList=""
export outputDir=$sourceDir
export nEvents=-1
export anaFile="hitTuning.py"
nJobs=$(ls -l ${sourceDir}/gridFcl/*.fcl | wc -l)
recopy=false
export treeName="" #if a tree name is passed the input file will be checked to see if the tree has entries
pythonPackages="python.tar.gz"

if [ ! -f $outputDir ]; then
    mkdir -p $outputDir
fi
if [ ! -f $outputDir/logs ]; then
    mkdir -p $outputDir/logs
fi
if [ ! -f "$outputDir/outputs" ]; then
    mkdir -p "$outputDir/outputs"
fi

# Create subdirectories for outputs and logs based on number of jobs
for ((i=0; i<$((($nJobs + 99) / 100)); i++)); do
    subdir=$(printf "%02d" $i)
    if [ ! -d $outputDir/outputs/$subdir ]; then
        mkdir -p $outputDir/outputs/$subdir
    fi
    if [ ! -d $outputDir/logs/$subdir ]; then
        mkdir -p $outputDir/logs/$subdir
    fi
done

#check if files exist in scratch and if not copy them over
# if [ ! -f ${sourceDir}/${fileList} ] || [ "$recopy" = true ]; then
#     echo "Copying file list to scratch area"
#     cp $PWD/${fileList} ${sourceDir}/.
# fi
if [ -n "$fclFile" ] && ( [ ! -f ${sourceDir}/${fclFile} ] || [ "$recopy" = true ] ); then
    echo "Copying fcl file to scratch area"
    cp $PWD/${fclFile} ${sourceDir}/.
fi
if [ -n "$tarFile" ] && ( [ ! -f ${sourceDir}/${tarFile} ] || [ "$recopy" = true ] ); then
    echo "Copying tar file to scratch area"
    cp /pnfs/icarus/scratch/users/micarrig/${tarFile} ${sourceDir}/.
fi
if [ -n "$anaFile" ] && ( [ ! -f ${sourceDir}/${anaFile} ] || [ "$recopy" = true ] ); then
    echo "Copying analysis file to scratch area"
    cp $PWD/${anaFile} ${sourceDir}/.
fi
if [ -n "$pythonPackages" ] && ( [ ! -f ${sourceDir}/${pythonPackages} ] || [ "$recopy" = true ] ); then
    echo "Copying python packages file to scratch area"
    cp /pnfs/icarus/scratch/users/micarrig/${pythonPackages} ${sourceDir}/.
fi
if [ -n "$fileList" ] && ( [ ! -f ${sourceDir}/${fileList} ] || [ "$recopy" = true ] ); then
    echo "Copying python packages file to scratch area"
    cp ${fileList} ${sourceDir}/.
fi

#not clear to me whether the following two lines are needed
export BEARER_TOKEN_FILE=/tmp/bt_u$(id -u) && htgettoken -a htvaultprod.fnal.gov -i icarus

echo "Submitting $nJobs jobs to process"
echo "Will process $nEvents events per job"
echo "Using executable $exe and tar file $tarFile"
echo "Output will be stored in $outputDir"

#
#jobsub_cmd="jobsub_submit -G icarus -N ${nJobs} --expected-lifetime=18h --disk=25GB --memory=8000MB -e IFDH_CP_MAXRETRIES=4 -e IFDH_CP_UNLINK_ON_ERROR=2 --lines '+FERMIHTC_AutoRelease=True' --lines '+FERMIHTC_GraceMemory=4096' --lines '+FERMIHTC_GraceLifetime=3600' -l '+SingularityImage=\"/cvmfs/singularity.opensciencegrid.org/carriganm95/uproot\:latest\"' --append_condor_requirements='(TARGET.HAS_Singularity==true)'"
jobsub_cmd="jobsub_submit -G icarus -N ${nJobs} --maxConcurrent 50 --expected-lifetime=18h --disk=25GB --memory=8000MB -e IFDH_CP_MAXRETRIES=4 -e IFDH_CP_UNLINK_ON_ERROR=2 --lines '+FERMIHTC_AutoRelease=True' --lines '+FERMIHTC_GraceMemory=4096' --lines '+FERMIHTC_GraceLifetime=3600' -l '+SingularityImage=\"/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7\:latest\"' --append_condor_requirements='(TARGET.HAS_Singularity==true)'"

if [ -n "$tarFile" ] && [ -f "${sourceDir}/${tarFile}" ]; then
    jobsub_cmd="${jobsub_cmd} --tar_file_name dropbox://${sourceDir}/${tarFile} --use-cvmfs-dropbox -e tarFile"
fi

if [ -n "$fclFile" ] && [ -f "${sourceDir}/${fclFile}" ]; then
    jobsub_cmd="${jobsub_cmd} -e fclFile -f ${sourceDir}/${fclFile}"
fi

if [ -n "$anaFile" ] && [ -f "${sourceDir}/${anaFile}" ]; then
    jobsub_cmd="${jobsub_cmd} -e anaFile -f ${sourceDir}/${anaFile}"
fi

if [ -n "$treeName" ]; then
    jobsub_cmd="${jobsub_cmd} -e treeName"
fi

if [ -n "$pythonPackages" ]; then
    jobsub_cmd="${jobsub_cmd} -f ${sourceDir}/${pythonPackages}"
fi

if [ -n "$fileList" ]; then
    jobsub_cmd="${jobsub_cmd} -e fileList -f ${sourceDir}/${fileList}"
fi

jobsub_cmd="${jobsub_cmd} -e outputDir -e nEvents file://${exe}"

echo "Executing jobsub command:"
echo "$jobsub_cmd"
eval $jobsub_cmd
