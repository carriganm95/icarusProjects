# Shower Calibration Directory

This directory contains scripts used in analyzing the addition of energy and dE/dx normalization tools for electromagnetic showers in ICARUS.

## Overview

The shower calibration tools implement and validate energy normalization corrections for shower reconstruction. These corrections account for detector effects and improve the energy resolution for electromagnetic showers.

## Related Branches

Development branches for this work:
- **icaruscode**: https://github.com/carriganm95/icaruscode/tree/showerNormTools
- **larpandora**: https://github.com/carriganm95/larpandora/tree/showerCal

## Files

### process.py

Track the status of file processing in large-scale batch jobs.

**Purpose**: 
- Identify which files have been successfully processed
- Generate lists of unprocessed files for resubmission
- Useful for recovering from failed grid jobs

**Key Functions**:
- `getProcessedFiles(outputDir, caf=False)`: Scan output directory for processed files
- `getSourceFiles(sourceFileList)`: Read list of source files to process
- `getUnprocessedFiles(sourceFiles, pFiles)`: Find which files remain unprocessed

**Usage**:
```python
# Edit the script to set:
outputDir = "/path/to/output/directory/"
sourceFileList = "/path/to/source/file.list"
caf = True  # If using CAF (Common Analysis Format) files

# Run to generate reprocess list
python process.py
# Creates: reprocessCaf.list with unprocessed file indices
```

**Output**:
- Console: Number of unprocessed files
- File: `reprocessCaf.list` - List of indices and paths for unprocessed files

### makeEnergyNormPlots.py

Compare normalized vs raw (standard) shower energy and dE/dx measurements.

**Purpose**:
- Generate comparison histograms between normalized and standard reconstruction
- Validate energy normalization corrections
- Analyze truth vs reco energy for MC
- Identify systematic effects of normalization

**Command Line Options**:
- `--normDir`: Path to directory with normalized output files
- `--rawDir`: Path to directory with standard/raw output files  
- `-o, --output`: Output ROOT file name [default: energyNormalizationPlots_data.root]
- `-d, --debug`: Enable debug mode (process fewer events)
- `--mc`: Indicate files are from MC (enables truth comparisons)

**Usage Examples**:
```bash
# Data comparison
python makeEnergyNormPlots.py --normDir /path/to/norm/ --rawDir /path/to/raw/ -o plots_data.root

# MC comparison with truth
python makeEnergyNormPlots.py --normDir /path/to/norm/ --rawDir /path/to/raw/ -o plots_mc.root --mc

# Debug mode (fewer events)
python makeEnergyNormPlots.py --normDir /path/to/norm/ --rawDir /path/to/raw/ -d
```

**Branches Analyzed**:
The script analyzes shower properties from CAF files:
- `rec.slc.reco.pfp.shw.plane.{0,1,2}.dEdx`: dE/dx for each plane
- `rec.slc.reco.pfp.shw.bestplane_dEdx`: dE/dx from best plane
- `rec.slc.reco.pfp.shw.plane.{0,1,2}.energy`: Shower energy for each plane
- `rec.slc.reco.pfp.shw.bestplane_energy`: Shower energy from best plane

**MC-Only Branches** (when `--mc` flag is used):
- `rec.slc.reco.pfp.trk.truth.p.pdg`: PDG code for particle ID
- `rec.slc.reco.pfp.shw.truth.bestmatch.energy`: True shower energy

**Output Histograms**:

*1D Histograms (per plane and best plane):*
- **Raw**: Standard reconstruction values
  - dE/dx distributions
  - Energy distributions
  - (MC only) Truth - Reco energy difference
- **Norm**: Normalized reconstruction values
  - dE/dx distributions
  - Energy distributions
  - (MC only) Truth - Reco energy difference
- **Difference**: Normalized - Raw
  - dE/dx differences
  - Energy differences

*2D Histograms:*
- **Comparison**: Normalized vs Raw (x vs y)
  - dE/dx comparison
  - Energy comparison
- **MC Truth Comparisons**:
  - Truth vs Reco energy (raw)
  - Truth vs Reco energy (normalized)

**File Matching**:
The script automatically matches normalized and raw files from the same input using job indices. This ensures like-to-like comparisons.

**Planes**:
- Plane 0: Induction 1
- Plane 1: Induction 2  
- Plane 2: Collection

### Shell Scripts

#### makeFileList.sh
Create lists of input files for processing.

**Purpose**: Generate `.list` files containing paths to input files

**Usage**:
```bash
./makeFileList.sh /path/to/files/ output.list
```

#### run.sh
Local execution script for testing.

**Purpose**: Run processing locally before submitting to grid

#### processMC.sh
Process Monte Carlo simulation files.

**Purpose**: Submit MC files for shower calibration processing

**Workflow**:
1. Reads MC file list
2. Submits grid jobs with appropriate configurations
3. Outputs processed files to specified directory

#### processMC_caf.sh
Process Monte Carlo CAF (Common Analysis Format) files.

**Purpose**: Submit MC CAF files for analysis

**CAF Files**: Simplified analysis format with selected branches

#### submitJobs.sh
Submit processing jobs to the grid.

**Purpose**: Batch submission of shower calibration jobs

**Typical Configuration**:
- Input file list
- Output directory
- Number of jobs/files per job
- Memory requirements
- Expected runtime

## Jupyter Notebooks

### checkCalibrations.ipynb
Interactive analysis of calibration results.

**Contents**:
- Load and visualize calibration histograms
- Compare distributions across runs/periods
- Calculate normalization factors
- Quality checks

### getRawFiles.ipynb  
Helper notebook for file management.

**Contents**:
- Query file locations
- Generate file lists
- Check file availability

## Typical Workflow

### 1. File Processing
```bash
# Create file list
./makeFileList.sh /pnfs/icarus/data/ input_files.list

# Submit grid jobs
./submitJobs.sh input_files.list

# Monitor job progress
jobsub_q --user $USER

# Check processing status
python process.py
# Creates reprocessCaf.list if needed

# Resubmit failed jobs if necessary
./submitJobs.sh reprocessCaf.list
```

### 2. Generate Comparison Plots

**For Data**:
```bash
python makeEnergyNormPlots.py \
    --normDir /pnfs/icarus/scratch/users/user/normalized/ \
    --rawDir /pnfs/icarus/scratch/users/user/standard/ \
    -o energy_comparison_data.root
```

**For MC**:
```bash
python makeEnergyNormPlots.py \
    --normDir /pnfs/icarus/scratch/users/user/normalized_mc/ \
    --rawDir /pnfs/icarus/scratch/users/user/standard_mc/ \
    -o energy_comparison_mc.root \
    --mc
```

### 3. Analysis
Open the output ROOT files or use Jupyter notebooks:
```bash
jupyter notebook checkCalibrations.ipynb
```

## Requirements

### Python Dependencies
- ROOT (PyROOT) >= 6.22
- uproot >= 4.0
- awkward >= 1.0
- numpy
- pandas
- matplotlib
- scipy

### Input File Formats
- **Stage 1 Files**: ICARUS reconstruction output (art/ROOT format)
- **CAF Files**: Common Analysis Format (flattened ROOT trees)

### Expected Directory Structure
```
scratch_area/
├── normalized_output/
│   ├── output_0.flat.caf.root
│   ├── output_1.flat.caf.root
│   └── ...
└── standard_output/
    ├── output_0.flat.caf.root
    ├── output_1.flat.caf.root
    └── ...
```

## Analysis Notes

### Energy Normalization
The normalization corrects for:
- Detector response variations
- Wire plane differences  
- Recombination effects
- Electronics gain variations

### Expected Improvements
- Better energy resolution
- Reduced systematic uncertainties
- Improved plane-to-plane agreement
- Better agreement with MC truth (for MC samples)

### Quality Checks
When reviewing outputs, check for:
1. **Mean shifts**: Energy/dE/dx distributions should shift appropriately
2. **Resolution**: Width of truth-reco difference should improve for MC
3. **Consistency**: All three planes should show consistent corrections
4. **Outliers**: Check for any unexpected large corrections
