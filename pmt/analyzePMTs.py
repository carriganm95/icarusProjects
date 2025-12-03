import uproot
import ROOT as r
import matplotlib.pyplot as plt
import numpy as np
import awkward as ak
import array as arr

class Variable:
    def __init__(self, name, bins, range):
        """
        Initialize a Variable object.

        Parameters:
        - name (str): Name of the variable.
        - bins (int): Number of bins for the histogram.
        - range (tuple): Range of the histogram as (min, max).
        """
        self.name = name
        self.bins = bins
        self.range = range

    def __repr__(self):
        """
        Return a string representation of the Variable object.
        """
        return f"Variable(name='{self.name}', bins={self.bins}, range={self.range})"


if __name__ == "__main__":

    r.gROOT.SetBatch(True)

    f_overlay = uproot.open("stage0_overlay_tree.root")
    t_overlay = f_overlay["mcana/mcwfs"]

    f_mcv4 = uproot.open("stage0_mcv4_tree.root")
    t_mcv4 = f_mcv4["mcana/mcwfs"]

    f_mc = uproot.open("stage0_mc_tree.root")
    t_mc = f_mc["mcana/mcwfs"]

    f_data = uproot.open("stage0_data_tree.root")
    t_data = f_data["mcana/mcwfs"]


    variables_to_plot = [
        Variable(name='rise_time', bins=100, range=(0, 50)),
        Variable(name='integral', bins=50, range=(0, 1000)),
        Variable(name='amplitude', bins=75, range=(0, 500)),
    ]

    step_size = '100 MB'

    all_vars = [var.name for var in variables_to_plot]

    datasets = {
        'Overlay': uproot.iterate("stage0_overlay_tree.root:mcana/mcwfs", all_vars, step_size=step_size),
        'MC v4': uproot.iterate("stage0_mcv4_tree.root:mcana/mcwfs", all_vars, step_size=step_size),
        'MC Standard': uproot.iterate("stage0_mc_tree.root:mcana/mcwfs", all_vars, step_size=step_size),
        'Data': uproot.iterate("stage0_data_tree.root:mcana/mcwfs", all_vars, step_size=step_size)
    }

    hists = {}

    for label, data in datasets.items():
        
        hists[label] = []

        for batch in data:

            for var in variables_to_plot:

                # Flatten and convert to NumPy
                data_array = ak.flatten(batch[var.name])
                data_array = ak.to_numpy(data_array)
                
                # Count underflow and overflow
                underflow = np.sum(data_array < var.range[0])
                overflow = np.sum(data_array > var.range[1])

                h = r.TH1F(f"h_{label}_{var.name}", f"{label} {var.name} distribution", var.bins, var.range[0], var.range[1])
                h.FillN(len(data_array), arr.array('d', data_array), np.ones(len(data_array)))
                h.Scale(1/h.Integral())
                hists[label].append(h)

    c1 = r.TCanvas("c1", "c1", 800, 600)

    r.gStyle.SetCanvasPreferGL(r.kTRUE)

    colors = [r.kBlue+2, r.kAzure+7, r.kGreen-2, r.kYellow-4]
    colors = [r.kRed, r.kBlue, r.kGreen, r.kYellow]

    fout = r.TFile("comparison_plots.root", "RECREATE")

    for i in range(len(hists['Data'])):
        #if i > 0: break
        c1.Clear()

        maxY = 0
        l = r.TLegend(0.7, 0.7, 0.9, 0.9)
        for j, (label, hist_list) in enumerate(hists.items()):
            hist_list[i].SetFillColorAlpha(colors[j], 0.2)
            if hist_list[i].GetMaximum() > maxY:
                maxY = hist_list[i].GetMaximum()
        for j, (label, hist_list) in enumerate(hists.items()):
            if j == 0:
                hist_list[i].SetMaximum(maxY * 1.2)
                hist_list[i].SetTitle(f"Comparison of {variables_to_plot[i].name} Distributions")
                hist_list[i].GetXaxis().SetTitle(variables_to_plot[i].name)
                hist_list[i].GetYaxis().SetTitle("Normalized Counts")
                r.gStyle.SetOptStat(0)
                hist_list[i].Draw("hist")
            if label == 'Data':
                hist_list[i].SetMarkerStyle(20)
                hist_list[i].Draw("same pe")
                l.AddEntry(hist_list[i], label, "p")
            else:
                hist_list[i].Draw("hist same f")
                l.AddEntry(hist_list[i], label, "f")

        c1.Update()
        l.Draw()

        fout.cd()
        c1.Write(f'c_{variables_to_plot[i].name}')
        c1.SaveAs(f'outputPlots/c_{variables_to_plot[i].name}.png')

    fout.Close()


