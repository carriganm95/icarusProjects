# PMT Calibration Directory

This directory contains scripts for PMT (Photomultiplier Tube) calibration, recalibration, and waveform analysis for the ICARUS detector.

## Overview

ICARUS uses 360 PMTs for light detection. Accurate calibration of PMT gain is essential for:
- Photo-electron (PE) counting
- Light yield measurements
- Energy scale calibration
- Trigger studies

The tools in this directory implement SPE (Single Photo-Electron) calibration methods and apply time-dependent gain corrections.

## Files

### getPMTRecal.py

Main script for PMT recalibration using Single Photo-Electron (SPE) measurements.

**Purpose**:
- Apply gain corrections to PMT measurements based on SPE calibrations
- Compare standard (nominal) vs recalibrated PE values
- Track gain evolution over time
- Generate histograms for validation

**Key Functions**:

#### `getPMTRecal(start, stop, output_dir, grid=False, calFiles)`
Recalibrate PMT PE values for flash-based data.

**Parameters**:
- `start`: Starting run number
- `stop`: Ending run number  
- `output_dir`: Directory for output ROOT file
- `grid`: Boolean, whether running on grid (affects authentication)
- `calFiles`: Path to list of calibration files

**Outputs**:
- ROOT file: `pmtPEHistograms_{start}_{stop}.root`
- Histograms organized by run and channel

#### `getPMTRecalNoFlash(start, stop, output_dir, grid=False, calFiles)`
Recalibrate PMT PE values for individual hit-level data (no flash grouping).

**Additional Features**:
- Applies isolation cuts to remove overlapping hits
- Time-based vetoes for hit selection
- Width-based quality cuts

**Isolation Cuts**:
- `timeCut = 0.2 μs`: Time window to check for adjacent hits
- Rejects hits in same channel within time window
- Rejects hits if previous hit width > timeCut
- Rejects hits with width > timeCut

#### Helper Functions:

**`getSPECalInfo(sPEList)` / `getSPECalInfoDir(dir)`**
Load SPE calibration files from list or directory.

**Returns**: Dictionary mapping run numbers to SPE file paths

**`getCalFiles(start, stop, cList)`**
Get calibration files for specified run range.

**Returns**: 
- `calRuns`: List of run numbers
- `calFiles`: List of file paths with tree names

**`getSPECalibrationRun(calRuns, speFiles)`**
Match each calibration run to most recent SPE calibration.

**Logic**: For each cal run, find the highest SPE run number ≤ cal run

**`calculateNewGains(speRuns)`**
Extract gain values from SPE CSV files.

**Returns**:
- `newGains`: Dictionary of gain values per PMT per run
- `newGainsErr`: Uncertainties
- `fit`: Fit quality (chi2/ndf)

**`recalibratePE(pe, newGain, oldGain=256.658)`**
Apply gain correction to PE values.

**Formula**: `recalPE = pe * (oldGain / newGain)`

**`recalibratePEFit(pe, run, y=261.71273, m=-0.01136, oldGain=256.658)`**
Apply linear time-dependent gain correction.

**Formula**: `newGain = y + run * m`

**`calculate_qADC(cal)`**
Convert charge from electrons to ADC×tick units.

**Constants**:
- Clock tick = 2 ns
- Resistance = 50 Ω
- 1 ADC×tick = 0.00488 pC
- Electron charge = 1.602×10⁻¹⁹ C

### Command Line Usage

**Standard usage** (edit script parameters):
```python
# In getPMTRecal.py main section:
speFiles = getSPECalInfo()
newGains, newGainsErr, fits = calculateNewGains(speFiles)

# Process runs 9400-9419
getPMTRecalNoFlash(9400, 9419, 
                   output_dir="/path/to/output/")
```

**Grid usage** (command line arguments):
```bash
python getPMTRecal.py JOB_INDEX OUTPUT_FILE SPE_DIR
```

**Arguments**:
- `JOB_INDEX`: Integer index for job array
- `OUTPUT_FILE`: Output ROOT file path
- `SPE_DIR`: Directory containing SPE CSV files

### analyzePMTs.py

Compare PMT waveform properties across different samples (overlay, MC, data).

**Purpose**:
- Validate PMT simulation
- Compare waveform characteristics
- Identify detector effects

**Input Files** (hardcoded in script):
- `stage0_overlay_tree.root`: MC with detector overlay
- `stage0_mcv4_tree.root`: MC version 4
- `stage0_mc_tree.root`: Standard MC
- `stage0_data_tree.root`: Real data

**Variables Analyzed**:
- `rise_time`: Waveform rise time (0-50 ns)
- `integral`: Pulse integral (0-1000)
- `amplitude`: Peak amplitude (0-500)

**Output**:
- ROOT file: `comparison_plots.root`
- PNG plots: Overlaid distributions with legend
- Normalized histograms for fair comparison

**Datasets Compared**:
1. Overlay (MC + detector effects)
2. MC v4 (newer MC version)
3. MC Standard (baseline MC)
4. Data (detector data)

**Usage**:
```python
python analyzePMTs.py
```

**Note**: Edit file paths in script before running

### FHiCL Configuration Files

#### data-wf-analyze.fcl
Configuration for analyzing data PMT waveforms.

**Purpose**: Process raw PMT data to extract waveform properties

#### spr-calibration-local.fcl
Configuration for SPR (Single Photo-electron Response) calibration.

**Purpose**: Generate SPE calibration parameters from calibration runs

### Shell Scripts

#### makeFileList.sh
Generate file lists for processing.

**Usage**:
```bash
./makeFileList.sh /path/to/pmt/files/ pmt_files.list
```

#### processFiles.sh
Process PMT files locally (for testing).

**Purpose**: Run PMT analysis on small file sets before grid submission

#### submitJobs.sh
Submit PMT processing jobs to grid.

**Configuration**:
- Input file lists
- Output directories  
- FCL configurations
- Resource requirements

#### runJob.sh
Grid job execution script.

**Purpose**: Called by grid system to run individual jobs

### Jupyter Notebooks

#### analyzePMTs.ipynb
Interactive analysis of PMT calibration results.

**Contents**:
- Load and plot histograms
- Compare gains across runs
- Fit distributions
- Quality assessment

#### pmtSPEFit.ipynb
Single Photo-Electron fitting and calibration.

**Contents**:
- Fit SPE charge distributions
- Extract gain values
- Generate calibration CSV files
- Diagnostic plots

## Typical Workflow

### 1. Generate SPE Calibrations

```bash
# Process SPE calibration runs
./submitJobs.sh spe_runs.list spr-calibration-local.fcl

# Analyze results in notebook
jupyter notebook pmtSPEFit.ipynb

# Generates CSV files with gains per PMT per run
```

### 2. Apply Recalibrations

**Interactive** (for testing):
```python
# Edit getPMTRecal.py to set paths and run range
speFiles = getSPECalInfo(sPEList='/path/to/speFiles.txt')
newGains, newGainsErr, fits = calculateNewGains(speFiles)

getPMTRecalNoFlash(9400, 9419, 
                   output_dir="/path/to/output/")
```

**Grid** (for production):
```bash
# Submit array jobs
for i in {0..50}; do
  python getPMTRecal.py $i output_$i.root /path/to/spe/dir/
done
```

### 3. Validation

```bash
# Compare waveform properties
python analyzePMTs.py

# Analyze in notebook
jupyter notebook analyzePMTs.ipynb
```

## Output Structure

### ROOT Files from getPMTRecal

**Directory Structure**:
```
output.root
├── run9400/
│   ├── NormalizedPE/
│   │   ├── h_normPE_run9400_chan0
│   │   ├── h_normPE_run9400_chan1
│   │   └── ...
│   ├── RecalibratedPE/
│   │   ├── h_recalPE_run9400_chan0
│   │   └── ...
│   ├── RecalibratedFitPE/
│   ├── SumPE/
│   ├── SumPERecal/
│   └── SumPEFitRecal/
├── run9401/
│   └── ...
```

**Histogram Types**:
- **NormalizedPE**: PE values with nominal gain (256.658 ADC×tick)
- **RecalibratedPE**: PE values with run-specific SPE gain
- **RecalibratedFitPE**: PE values with time-dependent gain fit
- **SumPE**: Total PE per event (various versions)

### CSV Format for SPE Files

```csv
pmt,q,eq,chi2,ndf,fitstatus
0,245.3,2.1,45.2,38,0
1,251.7,2.3,52.1,38,0
...
```

**Columns**:
- `pmt`: PMT channel number (0-359)
- `q`: Fitted SPE charge (electrons ×10⁷)
- `eq`: Uncertainty on q
- `chi2`: Fit chi-squared
- `ndf`: Number of degrees of freedom
- `fitstatus`: 0=good, non-zero=bad

## Bad Run List

The script maintains a list of runs with known issues (line 11 in getPMTRecal.py). These runs are excluded from processing.

**Source**: [PMT Calibration Spreadsheet](https://docs.google.com/spreadsheets/d/1Kra6eIflTKS_sMghBqgpy1h86Z8WKkibZLrLnDAdWaQ/edit?gid=0#gid=0)

## Requirements

### Python Dependencies
- ROOT (PyROOT) >= 6.22
- uproot >= 4.0
- awkward >= 1.0
- numpy
- pandas

### Constants Used

**ICARUS PMT System**:
- Total PMTs: 360
- Nominal gain: 256.658 ADC×tick per PE
- Clock period: 2 ns

**ADC Conversion**:
- 1 ADC×tick = 0.00488 pC
- Impedance = 50 Ω

## Common Issues and Solutions

### Authentication for Grid Files
If accessing files on `/pnfs/`:
```python
getToken()  # Call before accessing grid files
# Runs: htgettoken -a htvaultprod.fnal.gov -i icarus
```

### Duplicate SPE Runs
The code checks for duplicate runs. If found:
```
Duplicate SPE run found: XXXX
```
This indicates multiple SPE calibrations for the same run. The script uses the first one found.

### No Valid SPE Run
```
No valid SPE run found for cal run: XXXX
```
Means no SPE calibration exists before this run. The run will be skipped.

### Mismatch in Run Numbers
```
Mismatch in run numbers: XXXX YYYY skipping run/file...
```
File contains different run number than expected. Likely a file list ordering issue.

## Performance Notes

### Memory Usage
- Each run processes ~50-200 MB chunks
- Memory scales with number of PMTs and events
- Peak memory ~2-4 GB per run for standard processing

### Processing Time
- ~5-10 minutes per run (depending on event count)
- Uproot iteration allows processing larger-than-memory datasets
- Grid jobs typically request 2-4 hours

## References

- SPE Calibration Method: [ICARUS PMT Calibration Documentation]
- Gain Values: [PMT Calibration Spreadsheet](https://docs.google.com/spreadsheets/d/1Kra6eIflTKS_sMghBqgpy1h86Z8WKkibZLrLnDAdWaQ/)
- Standard Gain (fcl): `icaruscode/PMT/OpReco/fcl/icarus_spe.fcl`
