import os, sys
import ROOT as r

tag = 'Ind1Tune'
plane = 0

print("Starting demo...")

if len(sys.argv) < 2:
	print("Please specify an art/ROOT file to read")
	sys.exit(1)

def read_header(h):
	r.gROOT.ProcessLine(f'#include "{h}"')

print("Reading headers...")
read_header("gallery/Event.h")
read_header("gallery/ValidHandle.h")
read_header("nusimdata/SimulationBase/MCTruth.h")
read_header("canvas/Utilities/InputTag.h")
read_header("lardataobj/RecoBase/Hit.h")
read_header("lardataobj/RecoBase/Wire.h")
read_header("gallery/Handle.h")

print("Loading libraries...")
r.gSystem.Load("libgallery")
r.gSystem.Load("libnusimdata_SimulationBase")
r.gSystem.Load("libart_Framework_Principal")


print("Preparing before event loop...")
hitsEE_tag = r.art.InputTag("gaushit2dTPCEW", "")
wireEE_tag = r.art.InputTag("channel2wire", "PHYSCRATEDATATPCEW") #*ev.getValidHandle<std::vector<recob::Wire>>({"channel2wire", "PHYSCRATEDATATPCEE"});

filenames = r.vector(r.string)(1, sys.argv[1])

histfile = r.TFile(f"eventDisplays/display_{tag}.root", "RECREATE")
npart_hist = r.TH1F("npart", "Number of Hits", 51, -0.5, 50.5)


print("Creating event object ...")
ev = r.gallery.Event(filenames)

GetVH_HitsEE = r.gallery.Event.getValidHandle['std::vector<recob::Hit>']
GetVH_WireEE = r.gallery.Event.getValidHandle['std::vector<recob::Wire>']

if plane == 0:
	r_wires = [15600, 15800]
	r_time = [1000, 2500]
elif plane == 1:
	r_wires = [20800, 21300]
	r_time = [900, 2500]
elif plane == 2:
	r_wires = [26800, 27417]
	r_time = [1000, 2500]
else:
	print("need to ask for valid plane 0, 1, 2")
	sys.exit(1)

r.gROOT.SetBatch(1)
r.gStyle.SetOptStat(0)

c1 = r.TCanvas("c1", "c1", 1200, 800)

print("Entering event loop...")
event = 0
while not ev.atEnd():

	event = ev.eventAuxiliary().event()
	run = ev.eventAuxiliary().run()
	print(f"Run {run}, event {event}")
	
	# Call the specialized member; handle missing product gracefully
	hitsEE_handle = GetVH_HitsEE(ev, hitsEE_tag)
	wireEE_handle = GetVH_WireEE(ev, wireEE_tag)

	h_wire2d = r.TH2F(f"h_wire2d{event}", f"Display: Run {run} Event {event};Channel;Time Ticks", r_wires[1]-r_wires[0], r_wires[0], r_wires[1], r_time[1]-r_time[0], r_time[0], r_time[1])

	if wireEE_handle:
		wireEE = wireEE_handle.product()
		nWires = wireEE.size()
		nTicks = wireEE[1].NSignal()
		print(f"There are {nWires} wires with {nTicks} clock ticks")
		

		for iw, w in enumerate(wireEE):
			if w.Channel() < r_wires[0]: continue
			if w.Channel() > r_wires[1]: continue

			totalTicks = w.NSignal()
			for it, t in enumerate(w.Signal()):
				if it < r_time[0] or it > r_time[1]: continue
				#bin_ = h_wire2d.FindFixBin(w.Channel(), it)
				binX_ = h_wire2d.GetXaxis().FindBin(w.Channel())
				binY_ = h_wire2d.GetYaxis().FindBin(it)
				binY_ = h_wire2d.GetNbinsY() - binY_

				#print(f"Wire: {w.Channel()}, time: {it}, bin {bin_} value {w.Signal()[it]}")
				#h_wire2d.SetBinContent(bin_, w.Signal()[it])
				h_wire2d.SetBinContent(binX_, binY_, w.Signal()[it])

		
		c1.cd()
		if h_wire2d.GetMinimum() >= 0: h_wire2d.GetZaxis().SetRangeUser(-1, h_wire2d.GetMaximum()*1.2)
		#c1.SetLogz()
		h_wire2d.Draw("colz")
		c1.SaveAs(f"eventDisplays/event_{tag}_run{run}_evt{event}.png")
		histfile.cd()
		h_wire2d.Write(f"wire_{event}")

	if hitsEE_handle:
		hitsEE = hitsEE_handle.product()  # std::vector<recob::Hit>*
		# Count hits per event (or iterate to fill a hit attribute)
		print("Number of hits", hitsEE.size())

		#h_hits2d = r.TH2F(f"h_hits2d{event}", "Hits Event", r_wires[1]-r_wires[0], r_wires[0], r_wires[1], r_time[1]-r_time[0], r_time[0], r_time[1])
		c_hits2d = r.TCanvas("c_hits2d", "Hits", 800, 800)

		c1.cd()
		for ih, h in enumerate(hitsEE):
			#print(h.Channel(), h.WireID().Plane)
			chan = h.Channel()
			if chan < r_wires[0] or chan > r_wires[1]: continue

			mean = h.PeakTime()
			if mean < r_time[0] or mean > r_time[1]: continue

			rad = float(h.RMS())
			# if rad <= 0:
			# 	rad = 0.5  # ensure visible radius

			#convert mean time to flip y axis
			mean = r_time[1] - mean + r_time[0]

			ellipse = r.TEllipse(chan, mean, 1, rad)
			ellipse.SetFillStyle(1001)
			ellipse.SetFillColorAlpha(r.kRed, 0.2)
			ellipse.SetLineColor(r.kRed)
			ellipse.SetLineWidth(0)

			ellipse.Draw("f same")
			h_wire2d.GetListOfFunctions().Add(ellipse)

		histfile.cd()
		h_wire2d.Write("c_hits2d")


		npart_hist.Fill(hitsEE.size())

	event += 1
	ev.next()

print("Writing histograms...")
histfile.cd()
c1.Write("c1")
c1.SaveAs(f"eventDisplays/eventHits_{tag}_run{run}_evt{event}.png")
histfile.Write()
histfile.Close()
