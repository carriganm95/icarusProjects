#! /bin/bash

sourceDir="/pnfs/icarus/scratch/users/micarrig/showerEnergyCalCafMCV2/"
exe="run.sh"
#export fclFile="stage1_run2_shwcal_mc_icarus.fcl"
export fclFile="cafmakerjob_icarus_detsim2d.fcl" #for MC caf making
#export fclFile="cafmakerjob_icarus_data.fcl" #for data caf making
#export fclFile="stage1_run2_shwcal_icarus.fcl"
#export tarFile="showerCal.tar.gz"
tarFile=""
#export fileList="mcFilesReco.list"
#export fileList="numiMC_run2_stage1Norm.list"
export fileList="mcFiles.list"
export outputDir=$sourceDir
export nEvents=-1
export caf=true
nJobs=$(wc -l < ${sourceDir}/${fileList})
recopy=true

if [ ! -f $outputDir/outputs ]; then
    mkdir -p $outputDir
fi
if [ ! -f $outputDir/logs ]; then
    mkdir -p $outputDir/logs
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
if [ ! -f ${sourceDir}/${fileList} ] || [ "$recopy" = true ]; then
    echo "Copying file list to scratch area"
    cp $PWD/${fileList} ${sourceDir}/.
fi  
if [ ! -f ${sourceDir}/${fclFile} ] || [ "$recopy" = true ]; then
    echo "Copying fcl file to scratch area"
    cp $PWD/${fclFile} ${sourceDir}/.
fi
if [ -n "$tarFile" ] && { [ ! -f "${sourceDir}/${tarFile}" ] || [ "$recopy" = true ]; }; then
    echo "Copying tar file to scratch area"
    cp $PWD/${tarFile} ${sourceDir}/.
fi

#not clear to me whether the following two lines are needed
export BEARER_TOKEN_FILE=/tmp/bt_u$(id -u) && htgettoken -a htvaultprod.fnal.gov -i icarus

echo "Submitting $nJobs jobs to process file list $fileList with fcl file $fclFile"
echo "Will process $nEvents events per job"
echo "Using executable $exe and tar file $tarFile"
echo "Output will be stored in $outputDir"


if [ -n "$tarFile" ]; then
    jobsub_submit -G icarus -N ${nJobs} --expected-lifetime=18h --disk=25GB --memory=12000MB -e IFDH_CP_MAXRETRIES=4 -e IFDH_CP_UNLINK_ON_ERROR=2 --site=FermiGrid --lines '+FERMIHTC_AutoRelease=True' --lines '+FERMIHTC_GraceMemory=4096' --lines '+FERMIHTC_GraceLifetime=3600'  -l '+SingularityImage=\"/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7:latest\"' --append_condor_requirements='(TARGET.HAS_Singularity==true)' --tar_file_name dropbox://${sourceDir}/${tarFile} --use-cvmfs-dropbox -e fileList -e tarFile -e fclFile -e outputDir -e nEvents -e caf -f ${sourceDir}/${fileList} -f ${sourceDir}/${fclFile} file://${exe} 
else
    jobsub_submit -G icarus -N ${nJobs} --expected-lifetime=24h --disk=30GB --memory=15000MB -e IFDH_CP_MAXRETRIES=4 -e IFDH_CP_UNLINK_ON_ERROR=2 --site=FermiGrid --lines '+FERMIHTC_AutoRelease=True' --lines '+FERMIHTC_GraceMemory=4096' --lines '+FERMIHTC_GraceLifetime=3600'  -l '+SingularityImage=\"/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7:latest\"' --append_condor_requirements='(TARGET.HAS_Singularity==true)' --use-cvmfs-dropbox -e fileList -e fclFile -e outputDir -e nEvents -e caf -f ${sourceDir}/${fileList} -f ${sourceDir}/${fclFile} file://${exe} 
fi

