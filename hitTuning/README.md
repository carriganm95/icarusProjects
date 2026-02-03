This directory contains scripts used in determining the parameters to be used for hit finding in Icarus. There are tools for creating and running a grid search over parameters on the grid.

## hitTuning.py
This script can be run interactively or over the grid to implement specific hit tuning parameters with a minimal stage0 data or MC fcl file. There is also an option (-c) to create the fcl files for a grid search.

## galleryMC.cpp and galleryMacro.cpp
These are gallery macros that run on the Wire, ChannelROI, and Hits. The MC version computes the hit vs truth IDE energy per event for all particles and different types of particles to be used as a metric for determining the best set of parameters. Both scripts also make a set of basic hit histograms as well as a ROI vs hit plot for a specific channel.

## runJob.sh
Executable for grid jobs

## submitJobs.sh
Executable to run the grid search. 

## mergeDBFiles.py
Script to merge all of the .db files created in a grid search

## eventDisplay.py
Gallery script to create event displays from stage1 reco files with both wires/ROIs and hits.
