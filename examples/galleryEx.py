import os, sys
import ROOT

print("Starting demo...")

if len(sys.argv) < 2:
    print("Please specify an art/ROOT file to read")
    sys.exit(1)

def read_header(h):
    ROOT.gROOT.ProcessLine(f'#include "{h}"')

print("Reading headers...")
read_header("gallery/Event.h")
read_header("gallery/ValidHandle.h")
read_header("nusimdata/SimulationBase/MCTruth.h")
read_header("canvas/Utilities/InputTag.h")
read_header("lardataobj/RecoBase/Hit.h")
read_header("lardataobj/RecoBase/Wire.h")
read_header("gallery/Handle.h")

print("Loading libraries...")
ROOT.gSystem.Load("libgallery")
ROOT.gSystem.Load("libnusimdata_SimulationBase")
ROOT.gSystem.Load("libart_Framework_Principal")


print("Preparing before event loop...")
hits_tag = ROOT.art.InputTag("gaushit2dTPCWW", "")

filenames = ROOT.vector(ROOT.string)(1, sys.argv[1])

histfile = ROOT.TFile("hist.root", "RECREATE")
npart_hist = ROOT.TH1F("npart", "Number of Hits", 51, -0.5, 50.5)

print("Creating event object ...")
ev = ROOT.gallery.Event(filenames)

GetVH_Hits = ROOT.gallery.Event.getValidHandle['std::vector<recob::Hit>']

print("Entering event loop...")
while not ev.atEnd():
        
    # Call the specialized member; handle missing product gracefully
    try:
        hits_handle = GetVH_Hits(ev, hits_tag)
    except Exception:
        hits_handle = None
    if hits_handle:
        hits = hits_handle.product()  # std::vector<recob::Hit>*
        # Count hits per event (or iterate to fill a hit attribute)
        print("Number of hits", hits.size())

        for ih, h in enumerate(hits):
                if ih > 10: break
                print("peak amplitude", h.PeakAmplitude())

        npart_hist.Fill(hits.size())

    ev.next()

print("Writing histograms...")
histfile.Write()
histfile.Close()
