# Examples Directory

This directory contains example scripts demonstrating how to use the gallery framework to read and analyze ICARUS art/ROOT files.

## Overview

Gallery is a lightweight framework for reading art/ROOT files without the full art framework overhead. It's ideal for:
- Quick analysis scripts
- Prototyping new analyses
- Reading specific data products without running full reconstruction

## Files

### galleryEx.py

Basic example demonstrating how to read ICARUS reconstruction files using gallery with PyROOT.

**Purpose**: 
- Demonstrate gallery framework basics
- Show how to access data products (Hits, Wires)
- Create simple histograms
- Provide a template for new analyses

### Usage

```bash
python galleryEx.py input_file.root
```

**Arguments**:
- `input_file.root`: Path to an art/ROOT file (stage0, stage1, or reco file)

### What It Does

1. **Setup**: Loads necessary headers and libraries
2. **Configuration**: Sets up InputTags for data products
3. **Event Loop**: Iterates through events in the file
4. **Data Access**: Retrieves Hit objects from each event
5. **Analysis**: Prints hit information and fills histograms
6. **Output**: Saves histograms to `hist.root`

### Output

**ROOT File** (`hist.root`):
- `npart`: Histogram of number of hits per event
