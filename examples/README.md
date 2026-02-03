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

### Code Structure

#### Header Loading
```python
def read_header(h):
    ROOT.gROOT.ProcessLine(f'#include "{h}"')

read_header("gallery/Event.h")
read_header("gallery/ValidHandle.h")
read_header("nusimdata/SimulationBase/MCTruth.h")
read_header("canvas/Utilities/InputTag.h")
read_header("lardataobj/RecoBase/Hit.h")
read_header("lardataobj/RecoBase/Wire.h")
```

**Purpose**: Load C++ header files so PyROOT can understand LArSoft data structures

#### Library Loading
```python
ROOT.gSystem.Load("libgallery")
ROOT.gSystem.Load("libnusimdata_SimulationBase")
ROOT.gSystem.Load("libart_Framework_Principal")
```

**Purpose**: Load shared libraries containing the compiled code

#### InputTag Configuration
```python
hits_tag = ROOT.art.InputTag("gaushit2dTPCWW", "")
```

**InputTag Components**:
- **Module Label**: "gaushit2dTPCWW" - The producer module name
- **Instance Name**: "" - Empty for default instance
- **Process Name**: "" - Empty for any process

**Common ICARUS InputTags**:
- Hits: `gaushit2dTPCEE`, `gaushit2dTPCEW`, `gaushit2dTPCWE`, `gaushit2dTPCWW`
- Wires: `channel2wire` with instances like `PHYSCRATEDATATPCEE`
- Tracks: `pandoraTrackGausCryoE`, `pandoraTrackGausCryoW`
- Showers: `pandoraShowerGausCryoE`, `pandoraShowerGausCryoW`

#### Event Loop
```python
ev = ROOT.gallery.Event(filenames)
GetVH_Hits = ROOT.gallery.Event.getValidHandle['std::vector<recob::Hit>']

while not ev.atEnd():
    hits_handle = GetVH_Hits(ev, hits_tag)
    if hits_handle:
        hits = hits_handle.product()
        print("Number of hits", hits.size())
        
        for ih, h in enumerate(hits):
            if ih > 10: break
            print("peak amplitude", h.PeakAmplitude())
        
        npart_hist.Fill(hits.size())
    
    ev.next()
```

**Key Methods**:
- `Event(filenames)`: Create event object
- `getValidHandle[TYPE]`: Template to get typed handles
- `hits_handle.product()`: Get the actual data object
- `ev.next()`: Move to next event
- `ev.atEnd()`: Check if reached end of file

### Output

**Console Output**:
```
Starting demo...
Reading headers...
Loading libraries...
Preparing before event loop...
Creating event object ...
Entering event loop...
Number of hits 1234
peak amplitude 15.2
peak amplitude 23.7
...
Writing histograms...
```

**ROOT File** (`hist.root`):
- `npart`: Histogram of number of hits per event (51 bins, 0-50)

### Extending the Example

#### Reading Multiple Data Products

```python
# Configure InputTags
hits_tag = ROOT.art.InputTag("gaushit2dTPCWW", "")
wire_tag = ROOT.art.InputTag("channel2wire", "PHYSCRATEDATATPCWW")
track_tag = ROOT.art.InputTag("pandoraTrackGausCryoW", "")

# Get handles
GetVH_Hits = ROOT.gallery.Event.getValidHandle['std::vector<recob::Hit>']
GetVH_Wire = ROOT.gallery.Event.getValidHandle['std::vector<recob::Wire>']
GetVH_Track = ROOT.gallery.Event.getValidHandle['std::vector<recob::Track>']

# In event loop
hits_handle = GetVH_Hits(ev, hits_tag)
wire_handle = GetVH_Wire(ev, wire_tag)
track_handle = GetVH_Track(ev, track_tag)
```

#### Accessing Hit Properties

```python
for h in hits:
    channel = h.Channel()           # Wire channel
    peak_time = h.PeakTime()        # Time of peak (ticks)
    peak_amp = h.PeakAmplitude()    # Peak amplitude (ADC)
    charge = h.Integral()           # Integrated charge
    rms = h.RMS()                   # Width (sigma)
    multiplicity = h.Multiplicity() # Number of hits in ROI
```

#### Accessing Wire Signals

```python
for w in wires:
    channel = w.Channel()
    n_ticks = w.NSignal()
    signal = w.Signal()  # std::vector<float>
    
    for tick, adc in enumerate(signal):
        # Process signal
        pass
```

#### Accessing Track Properties

```python
for t in tracks:
    length = t.Length()
    n_points = t.NumberTrajectoryPoints()
    start = t.Vertex()      # TVector3
    end = t.End()           # TVector3
    start_dir = t.VertexDirection()  # TVector3
```

### ICARUS TPC Structure

ICARUS has four TPC volumes (East/West × East/West):
- **EE**: East-East
- **EW**: East-West
- **WE**: West-East
- **WW**: West-West

Many data products are split by TPC volume, hence InputTags like:
- `gaushit2dTPCEE`
- `gaushit2dTPCEW`
- `gaushit2dTPCWE`
- `gaushit2dTPCWW`

To process all volumes, loop over all four InputTags.

## Requirements

### Software Setup

**LArSoft Environment**:
```bash
source /cvmfs/icarus.opensciencegrid.org/products/icarus/setup_icarus.sh
setup icaruscode v09_XX_XX -q eXX:prof
```

Replace `v09_XX_XX` with appropriate version and `eXX` with compiler version.

### Python Dependencies
- ROOT with PyROOT (from LArSoft setup)
- gallery (from LArSoft setup)

### C++ Dependencies
- art framework
- LArSoft data products:
  - `lardataobj` (Hit, Wire, Track, Shower)
  - `nusimdata` (MCTruth, MCParticle)

## Common Issues and Solutions

### Missing Headers
```
Error: cannot open file "gallery/Event.h"
```
**Solution**: Source LArSoft environment first

### Library Not Found
```
Error: libgallery.so: cannot open shared object file
```
**Solution**: Run `setup icaruscode` before running script

### InputTag Not Found
```
Event: no data products of any type with input tag ...
```
**Solution**: 
1. Check the InputTag module label matches producer in file
2. Verify the file contains that data product
3. For multiple TPC volumes, ensure you're using correct TPC suffix

### Type Mismatch
```
TypeError: getValidHandle<...>
```
**Solution**: Ensure template argument matches actual data product type

## Tips and Best Practices

1. **Batch Mode**: For non-interactive plots:
   ```python
   ROOT.gROOT.SetBatch(1)
   ```

2. **Error Handling**: Wrap data access in try-except:
   ```python
   try:
       hits_handle = GetVH_Hits(ev, hits_tag)
   except Exception:
       hits_handle = None
   ```

3. **Memory**: Close files and delete large objects when done:
   ```python
   histfile.Close()
   del ev
   ```

4. **Multiple Files**: Pass multiple files as vector:
   ```python
   filenames = ROOT.vector(ROOT.string)()
   filenames.push_back("file1.root")
   filenames.push_back("file2.root")
   ev = ROOT.gallery.Event(filenames)
   ```

5. **Run/Event Information**:
   ```python
   run = ev.eventAuxiliary().run()
   event = ev.eventAuxiliary().event()
   subrun = ev.eventAuxiliary().subRun()
   ```

## Further Reading

- **Gallery Documentation**: [LArSoft Gallery Wiki](https://cdcvs.fnal.gov/redmine/projects/gallery/wiki)
- **LArSoft Data Products**: [LArSoft Doxygen](https://code-doc.fnal.gov/docs/larsoft/) (Replace version in URL with your installed version)
- **ICARUS Software**: [ICARUS Code Documentation](https://github.com/SBNSoftware/icaruscode)

## Building Your Own Analysis

To create a new gallery-based analysis:

1. **Copy the example**:
   ```bash
   cp galleryEx.py my_analysis.py
   ```

2. **Modify InputTags** for your data products

3. **Add your analysis logic** in the event loop

4. **Add histograms or output** as needed

5. **Test on a small file** first:
   ```bash
   python my_analysis.py small_test_file.root
   ```

6. **Scale up** to full file lists once working
