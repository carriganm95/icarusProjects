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

**Output**:
- ROOT file: `comparison_plots.root`
- PNG plots: Overlaid distributions with legend
- Normalized histograms for fair comparison
## References

- Gain Values: [PMT Calibration Spreadsheet](https://docs.google.com/spreadsheets/d/1Kra6eIflTKS_sMghBqgpy1h86Z8WKkibZLrLnDAdWaQ/)
- Standard Gain (fcl): `icaruscode/PMT/OpReco/fcl/icarus_spe.fcl`
