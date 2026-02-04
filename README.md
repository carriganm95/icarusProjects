# ICARUS Projects

This repository contains a collection of analysis tools and scripts for the ICARUS (Imaging Cosmic And Rare Underground Signals) neutrino detector experiment. The tools are organized into several directories, each focused on specific aspects of detector calibration, hit finding, and reconstruction.

## Repository Structure

```
icarusProjects/
├── hitTuning/     # Hit finding parameter optimization tools
├── pmt/           # PMT (Photomultiplier Tube) calibration and analysis
├── showerCal/     # Shower energy calibration and normalization
└── examples/      # Example scripts for using gallery framework
```

## Directories

### hitTuning/
Tools for determining optimal parameters for hit finding in ICARUS. Includes grid search capabilities and event display tools.

**Key Files:**
- `hitTuning.py` - Main script for hit tuning parameter optimization
- `mergeDBFiles.py` - Merge database files from grid searches
- `eventDisplay.py` - Create event displays from reconstructed data
- `galleryMC.cpp` & `galleryMacro.cpp` - Gallery macros for hit analysis
- `submitJobs.sh` & `runJob.sh` - Grid job submission scripts

See [hitTuning/README.md](hitTuning/README.md) for detailed documentation.

### pmt/
Scripts for PMT calibration, recalibration, and waveform analysis.

**Key Files:**
- `getPMTRecal.py` - PMT recalibration using SPE (Single Photo-Electron) measurements
- `analyzePMTs.py` - PMT waveform analysis and comparison
- `*.fcl` - FHiCL configuration files for PMT processing
- `submitJobs.sh` & `runJob.sh` - Grid job submission scripts

### showerCal/
Tools for shower energy calibration and dE/dx normalization analysis.

**Key Files:**
- `process.py` - Track processed/unprocessed files
- `makeEnergyNormPlots.py` - Compare normalized vs raw shower energies
- `*.sh` - Shell scripts for file processing and job submission

See [showerCal/README.md](showerCal/README.md) for more information.

### examples/
Example scripts demonstrating the use of the gallery framework for analyzing ICARUS data files.

**Key Files:**
- `galleryEx.py` - Basic example of reading art/ROOT files with gallery

## Requirements

### Python Dependencies
- ROOT (PyROOT)
- uproot
- awkward
- numpy
- pandas
- matplotlib
- scipy

### C++ Dependencies
- gallery
- art/ROOT framework
- LArSoft data products

## Getting Started

1. **Set up your environment** with the necessary LArSoft and ICARUS software
2. **Navigate to the relevant directory** for your analysis task
3. **Review the README** in that directory for specific instructions
4. **Run the example scripts** in `examples/` to familiarize yourself with the framework

## General Workflow

### For Hit Tuning:
1. Create FCL files with different parameter sets using `hitTuning.py -c`
2. Submit grid jobs with `submitJobs.sh`
3. Merge results with `mergeDBFiles.py`
4. Analyze and visualize with notebooks

### For PMT Calibration:
1. Prepare lists of calibration and SPE files
2. Run `getPMTRecal.py` with appropriate run ranges
3. Analyze output histograms and compare recalibrations

### For Shower Calibration:
1. Process files with shower energy normalization tools
2. Use `process.py` to track processing status
3. Generate comparison plots with `makeEnergyNormPlots.py`

## Contributing

When adding new scripts or tools:
- Follow the existing directory structure
- Update the relevant README files
- Include command-line argument parsing with helpful descriptions
- Add docstrings to functions and classes

## Contact

For questions about specific tools, refer to the individual README files in each directory or contact the repository maintainer.
