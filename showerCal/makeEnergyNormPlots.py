import ROOT as r
import uproot
import matplotlib.pyplot as plt
import awkward as ak
import numpy as np
from scipy import stats
import pandas as pd
import matplotlib.colors as colors
import array as arr
import os
import fnmatch
import argparse
import sys

class Variable:
    def __init__(self, name, bins, range, var=None):
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
        if var is None:
            self.var = name
        else:
            self.var = var

    def __repr__(self):
        """
        Return a string representation of the Variable object.
        """
        return f"Variable(name='{self.name}', bins={self.bins}, range={self.range}, var='{self.var}')"

def getFilesFromList(list):
    files = []
    with open(list, 'r') as f:
        lines = f.readlines()
        files = [f'{line.strip()}:recTree' for i, line in enumerate(lines)]
    return files


def savePlots(fout, hists):
    for key in hists.keys():
        fout.mkdir(key)

    for k, v in hists.items():
        fout.cd(k)
        for hist in v:
            hist.Write()

def getFilesFromDir(directory, pattern="*.root", debug=False):

    matched_files = []
    for root, dirs, files in os.walk(directory):
        for filename in fnmatch.filter(files, pattern):
            #if debug and len(matched_files) >= 10:
            #    break
            matched_files.append(os.path.join(root, filename) + ':recTree')
    return matched_files

# function to return only the files that succeeded processing in both norm and raw files
def matchFiles(normFiles, rawFiles, inputList, normIndex=True, rawIndex=True, normPattern="*.flat.caf.root", rawPattern="*.flat.caf.root"):
    # Assuming both lists are sorted and have a one-to-one correspondence
    matchedNormFiles = []
    matchedRawFiles = []

    if '*' in normPattern:
        normPattern = normPattern.replace('*', '')
    if '*' in rawPattern:
        rawPattern = rawPattern.replace('*', '')
    if ':' in normFiles[0]:
        normPattern = f'{normPattern}:{normFiles[0].split(":")[-1]}'
    if ':' in rawFiles[0]:
        rawPattern = f'{rawPattern}:{rawFiles[0].split(":")[-1]}'

    normJobs = [f.split('_')[-1].replace(normPattern, '') for f in normFiles]
    rawJobs = [f.split('_')[-1].replace(rawPattern, '') for f in rawFiles]

    with open(inputList, 'r') as f:
        valid_files = [line.strip().split('/')[-1] for line in f.readlines()]
        for ifile, file_ in enumerate(valid_files):
            norm_match = False
            raw_match = False
            raw_idx, norm_idx = -1, -1

            file_str = file_.split('.root')[0]

            # use job number to match files
            if rawIndex:
                if str(ifile) in rawJobs:
                    raw_idx = rawJobs.index(str(ifile))
                    raw_match = True

            # Use output file string to match files
            else:
                raw_basename_to_index = {os.path.basename(f.split('.flat.caf.root')[0]): i for i, f in enumerate(rawFiles)}
                if file_str in raw_basename_to_index:
                    raw_idx = raw_basename_to_index[file_str]
                    raw_match = True
            
            # Use job number to match files
            if normIndex:
                if str(ifile) in normJobs:
                    norm_idx = normJobs.index(str(ifile))
                    norm_match = True
            if norm_match and raw_match:
                matchedNormFiles.append(normFiles[norm_idx])
                matchedRawFiles.append(rawFiles[raw_idx])
            
            # if norm_idx >= 0 and raw_idx >= 0:
            #print("Raw match:", raw_match, "Norm match:", norm_match)
            #print(f"File: {file_}, ifile: {ifile}, Norm match: {normFiles[norm_idx]}, Raw match: {rawFiles[raw_idx]}")


    return matchedNormFiles, matchedRawFiles


def iterateTrees(list1, list2, branches, hists, outputFile, MC=False):

    fout = r.TFile.Open(outputFile, "RECREATE")

    totalEvents = 0
    if MC:
        allBranches = branches + ['rec.slc.reco.pfp.trk.truth.p.pdg', 'rec.slc.reco.pfp.shw.truth.bestmatch.energy']
    for bunch1, bunch2 in zip(uproot.iterate(list1,filter_name=allBranches, allow_missing=True), uproot.iterate(list2,filter_name=allBranches, allow_missing=True)):
        
        if args.debug and totalEvents > 100: break
        totalEvents += len(bunch1[branches[0]])

        if MC:
            sel1 = (np.abs(bunch1['rec.slc.reco.pfp.trk.truth.p.pdg']) == 11)  # select electrons and positrons
            sel2 = (np.abs(bunch2['rec.slc.reco.pfp.trk.truth.p.pdg']) == 11)  # select electrons and positrons

            t_energy = ak.flatten(bunch1['rec.slc.reco.pfp.shw.truth.bestmatch.energy'][sel1]) #truth energy
            hists['Truth'][0].FillN(len(t_energy), arr.array('d', t_energy), np.ones(len(t_energy)))
        else:
            sel1 = np.ones(len(bunch1[branches[0]]), dtype=bool)
            sel2 = np.ones(len(bunch2[branches[0]]), dtype=bool)    

        if ak.any(sel1 != sel2):
            print("Selection mismatch between norm and raw files!")
            continue

        if totalEvents % 1000 == 0 or args.debug:
            print(f"Processing event number: {totalEvents}")

        for ivar, var_ in enumerate(branches):
            br1 = bunch1[var_]
            br2 = bunch2[var_]

            br1 = br1[sel1]
            br2 = br2[sel2] 

            br1 = ak.to_numpy(ak.flatten(br1))
            br2 = ak.to_numpy(ak.flatten(br2))
            
            br1[br1 < 0] = -1 
            br2[br2 < 0] = -1 
            br1[br1 > 10] = 10
            br2[br2 > 10] = 10

            diff = arr.array('d', br1 - br2)

            br1 = arr.array('d', br1)
            br2 = arr.array('d', br2)

            if MC and var_.endswith('energy'):
                # also fill truth - reco difference histograms
                hists['Raw'][ivar + len(branches) - 4].FillN(len(t_energy), arr.array('d', t_energy - br2), np.ones(len(t_energy)))
                hists['Norm'][ivar + len(branches) - 4].FillN(len(t_energy), arr.array('d', t_energy - br1), np.ones(len(t_energy)))
                hists['Comparison'][ivar + len(branches) - 4].FillN(len(t_energy), br1, arr.array('d', t_energy), np.ones(len(t_energy)))
                hists['Comparison'][ivar + len(branches)].FillN(len(t_energy), br2, arr.array('d', t_energy), np.ones(len(t_energy)))


            hists['Raw'][ivar].FillN(len(br2), br2, np.ones(len(br2)))
            hists['Norm'][ivar].FillN(len(br1), br1, np.ones(len(br1)))
            hists['Comparison'][ivar].FillN(len(br1), br1, br2, np.ones(len(br1)))
            hists['Difference'][ivar].FillN(len(br1), diff, np.ones(len(br1)))

    savePlots(fout, hists)
    fout.Close()

def parse_args():
    parser = argparse.ArgumentParser(description="Make energy norm plots")
    parser.add_argument('--normDir', type=str, help='Path to the list of normalized files', required=False, default=None)
    parser.add_argument('--rawDir', type=str, help='Path to the list of raw files', required=False, default=None)  
    parser.add_argument('-o', '--output', type=str, help='Output ROOT file name', default=None)
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--mc', action='store_true', help='Indicate if the files are from MC')
    return parser.parse_args()

if __name__ == "__main__":

    args = parse_args()

    outputFile = 'energyNormalizationPlots_data.root'
    normDir = '/pnfs/icarus/scratch/users/micarrig/showerEnergyCalCafNorm/outputs/'
    rawDir = '/pnfs/icarus/scratch/users/micarrig/showerEnergyCalCafV2/outputs/'

    if args.normDir is not None:
        normDir = args.normDir
    if args.rawDir is not None:
        rawDir = args.rawDir
    if args.output is not None:
        outputFile = args.output

    if args.debug:
        print("Running in debug mode")   

    # normFileList = '/exp/icarus/app/users/micarrig/showerCal/v10_06_00_04p02/mcFilesCAFNorm.list'
    # rawFileList = '/exp/icarus/app/users/micarrig/showerCal/v10_06_00_04p02/mcFilesCAF.list'
    # print("Getting normalized files...")
    # normFiles = getFilesFromList(normFileList)
    # print("Getting standard files...")   
    # rawFiles = getFilesFromList(rawFileList)

    if args.mc:
        normPattern = "*.flat.caf.root"
        rawPattern = "*.flat.caf.root"
        fileList = '/exp/icarus/app/users/micarrig/showerCal/v10_06_00_04p02/mcFiles.list'        
    else:
        normPattern = "*.Unblind.DONOTLOOK.flat.caf.root"
        rawPattern = "*.Unblind.DONOTLOOK.flat.caf.root"
        fileList = '/exp/icarus/app/users/micarrig/showerCal/v10_06_00_04p02/stage0_numiRun2.list'

    normFiles = getFilesFromDir(normDir, pattern=normPattern, debug=args.debug)
    rawFiles = getFilesFromDir(rawDir, pattern=rawPattern, debug=args.debug)

    print(f"Found {len(normFiles)} normalized files and {len(rawFiles)} raw files")

    if args.mc:
        normFiles, rawFiles = matchFiles(normFiles, rawFiles, fileList, normIndex=True, rawIndex=False, normPattern=normPattern, rawPattern=rawPattern)
    else:
        normFiles, rawFiles = matchFiles(normFiles, rawFiles, fileList, normIndex=True, rawIndex=True, normPattern=normPattern, rawPattern=rawPattern)


    print(f"Norm files: {len(normFiles)}, Raw files: {len(rawFiles)}")

    print(normFiles[:5], rawFiles[:5])

    fout = r.TFile.Open(outputFile, "RECREATE")

    dirs = {"Norm": normFiles, "Raw": rawFiles}

    hists = {}
    saveVars = {}

    h_dedx_plane0 = r.TH1F("h_dedx_plane0", "dEdx Induction 1;dEdx [MeV/cm]", 65, -2, 11)
    h_dedx_plane1 = r.TH1F("h_dedx_plane1", "dEdx Induction 2;dEdx [MeV/cm]", 65, -2, 11)
    h_dedx_plane2 = r.TH1F("h_dedx_plane2", "dEdx Collection;dEdx [MeV/cm]", 65, -2, 11)
    h_dedx_bestplane = r.TH1F("h_dedx_bestplane", "dEdx Best Plane;dEdx [MeV/cm]", 65, -2, 11)

    h_dedx_plane0_norm = r.TH1F("h_dedx_plane0_norm", "dEdx Induction 1 Norm;dEdx [MeV/cm]", 65, -2, 11)
    h_dedx_plane1_norm = r.TH1F("h_dedx_plane1_norm", "dEdx Induction 2 Norm;dEdx [MeV/cm]", 65, -2, 11)
    h_dedx_plane2_norm = r.TH1F("h_dedx_plane2_norm", "dEdx Collection Norm;dEdx [MeV/cm]", 65, -2, 11) 
    h_dedx_bestplane_norm = r.TH1F("h_dedx_bestplane_norm", "dEdx Best Plane Norm;dEdx [MeV/cm]", 65, -2, 11)

    h_energy_plane0 = r.TH1F("h_energy_plane0", "Shower Energy Induction 1;Energy [GeV]", 150, -1, 2)
    h_energy_plane1 = r.TH1F("h_energy_plane1", "Shower Energy Induction 2;Energy [GeV]", 150, -1, 2)
    h_energy_plane2 = r.TH1F("h_energy_plane2", "Shower Energy Collection;Energy [GeV]", 150, -1, 2)
    h_energy_bestplane = r.TH1F("h_energy_bestplane", "Shower Energy Best Plane;Energy [GeV]", 150, -1, 2)

    h_truthEnergy_bestMatch = r.TH1F("h_truthEnergy_bestMatch", "Truth Shower Energy;Energy [GeV]", 150, -1, 2)

    h_tEnergyDiff_plane0 = r.TH1F("h_tEnergyDiff_plane0", "Truth - Reco Shower Energy Induction 1;#Delta Energy [GeV]", 200, -1, 1)
    h_tEnergyDiff_plane1 = r.TH1F("h_tEnergyDiff_plane1", "Truth - Reco Shower Energy Induction 2;#Delta Energy [GeV]", 200, -1, 1)
    h_tEnergyDiff_plane2 = r.TH1F("h_tEnergyDiff_plane2", "Truth - Reco Shower Energy Collection;#Delta Energy [GeV]", 200, -1, 1)
    h_tEnergyDiff_bestplane = r.TH1F("h_tEnergyDiff_bestplane", "Truth - Reco Shower Energy Best Plane;#Delta Energy [GeV]", 200, -1, 1)

    h_energy_plane0_norm = r.TH1F("h_energy_plane0_norm", "Shower Energy Induction 1 Norm;Energy [GeV]", 150, -1, 2)
    h_energy_plane1_norm = r.TH1F("h_energy_plane1_norm", "Shower Energy Induction 2 Norm;Energy [GeV]", 150, -1, 2)
    h_energy_plane2_norm = r.TH1F("h_energy_plane2_norm", "Shower Energy Collection Norm;Energy [GeV]", 150, -1, 2)
    h_energy_bestplane_norm = r.TH1F("h_energy_bestplane_norm", "Shower Energy Best Plane Norm;Energy [GeV]", 150, -1, 2)

    h_tEnergyDiff_plane0_norm = r.TH1F("h_tEnergyDiff_plane0_norm", "Truth - Reco Shower Energy Induction 1 Norm;#Delta Energy [GeV]", 200, -1, 1)
    h_tEnergyDiff_plane1_norm = r.TH1F("h_tEnergyDiff_plane1_norm", "Truth - Reco Shower Energy Induction 2 Norm;#Delta Energy [GeV]", 200, -1, 1)
    h_tEnergyDiff_plane2_norm = r.TH1F("h_tEnergyDiff_plane2_norm", "Truth - Reco Shower Energy Collection Norm;#Delta Energy [GeV]", 200, -1, 1)
    h_tEnergyDiff_bestplane_norm = r.TH1F("h_tEnergyDiff_bestplane_norm", "Truth - Reco Shower Energy Best Plane Norm;#Delta Energy [GeV]", 200, -1, 1)

    h_dedx2d_plane0 = r.TH2F("h_dedx2d_plane0", "dEdx Induction 1 Norm vs Nominal;dEdx Norm [MeV/cm];dEdx Nominal [MeV/cm]", 65, -2, 11, 65, -2, 11)
    h_dedx2d_plane1 = r.TH2F("h_dedx2d_plane1", "dEdx Induction 2 Norm vs Nominal;dEdx Norm [MeV/cm];dEdx Nominal [MeV/cm]", 65, -2, 11, 65, -2, 11)
    h_dedx2d_plane2 = r.TH2F("h_dedx2d_plane2", "dEdx Collection Norm vs Nominal;dEdx Norm [MeV/cm];dEdx Nominal [MeV/cm]", 65, -2, 11, 65, -2, 11)
    h_dedx2d_bestplane = r.TH2F("h_dedx2d_bestplane", "dEdx Best Plane Norm vs Nominal;dEdx Norm [MeV/cm];dEdx Nominal [MeV/cm]", 65, -2, 11, 65, -2, 11)

    h_energy2d_plane0 = r.TH2F("h_energy2d_plane0", "Shower Energy Induction 1 Norm vs Nominal;Energy Norm [GeV];Energy Nominal [GeV]", 150, -1, 2, 150, -1, 2)
    h_energy2d_plane1 = r.TH2F("h_energy2d_plane1", "Shower Energy Induction 2 Norm vs Nominal;Energy Norm [GeV];Energy Nominal [GeV]", 150, -1, 2, 150, -1, 2)
    h_energy2d_plane2 = r.TH2F("h_energy2d_plane2", "Shower Energy Collection Norm vs Nominal;Energy Norm [GeV];Energy Nominal [GeV]", 150, -1, 2, 150, -1, 2)
    h_energy2d_bestplane = r.TH2F("h_energy2d_bestplane", "Shower Energy Best Plane Norm vs Nominal;Energy Norm [GeV];Energy Nominal [GeV]", 150, -1, 2, 150, -1, 2)

    h_tEnergy2d_plane0 = r.TH2F("h_tEnergy2d_plane0", "Truth vs Reco Shower Energy Induction 1;Energy Reco [GeV];Energy Truth [GeV]", 150, -1, 2, 150, -1, 2)
    h_tEnergy2d_plane1 = r.TH2F("h_tEnergy2d_plane1", "Truth vs Reco Shower Energy Induction 2;Energy Reco [GeV];Energy Truth [GeV]", 150, -1, 2, 150, -1, 2)
    h_tEnergy2d_plane2 = r.TH2F("h_tEnergy2d_plane2", "Truth vs Reco Shower Energy Collection;Energy Reco [GeV];Energy Truth [GeV]", 150, -1, 2, 150, -1, 2)
    h_tEnergy2d_bestplane = r.TH2F("h_tEnergy2d_bestplane", "Truth vs Reco Shower Energy Best Plane;Energy Reco [GeV];Energy Truth [GeV]", 150, -1, 2, 150, -1, 2)

    h_tEnergy2d_plane0_norm = r.TH2F("h_tEnergy2d_plane0_norm", "Truth vs Reco Shower Energy Induction 1 Norm;Energy Reco [GeV];Energy Truth [GeV]", 150, -1, 2, 150, -1, 2)
    h_tEnergy2d_plane1_norm = r.TH2F("h_tEnergy2d_plane1_norm", "Truth vs Reco Shower Energy Induction 2 Norm;Energy Reco [GeV];Energy Truth [GeV]", 150, -1, 2, 150, -1, 2)
    h_tEnergy2d_plane2_norm = r.TH2F("h_tEnergy2d_plane2_norm", "Truth vs Reco Shower Energy Collection Norm;Energy Reco [GeV];Energy Truth [GeV]", 150, -1, 2, 150, -1, 2)
    h_tEnergy2d_bestplane_norm = r.TH2F("h_tEnergy2d_bestplane_norm", "Truth vs Reco Shower Energy Best Plane Norm;Energy Reco [GeV];Energy Truth [GeV]", 150, -1, 2, 150, -1, 2)

    h_dedxDiff_plane0 = r.TH1F("h_dedxDiff_plane0", "dEdx Induction 1 Norm - Nominal;#Delta dEdx [MeV/cm]", 200, -1, 1)
    h_dedxDiff_plane1 = r.TH1F("h_dedxDiff_plane1", "dEdx Induction 2 Norm - Nominal;#Delta dEdx [MeV/cm]", 200, -1, 1)
    h_dedxDiff_plane2 = r.TH1F("h_dedxDiff_plane2", "dEdx Collection Norm - Nominal;#Delta dEdx [MeV/cm]", 200, -1, 1)
    h_dedxDiff_bestplane = r.TH1F("h_dedxDiff_bestplane", "dEdx Best Plane Norm - Nominal;#Delta dEdx [MeV/cm]", 200, -1, 1)

    h_energyDiff_plane0 = r.TH1F("h_energyDiff_plane0", "Shower Energy Induction 1 Norm - Nominal;#Delta Energy [GeV]", 200, -1, 1)
    h_energyDiff_plane1 = r.TH1F("h_energyDiff_plane1", "Shower Energy Induction 2 Norm - Nominal;#Delta Energy [GeV]", 200, -1, 1)
    h_energyDiff_plane2 = r.TH1F("h_energyDiff_plane2", "Shower Energy Collection Norm - Nominal;#Delta Energy [GeV]", 200, -1, 1)
    h_energyDiff_bestplane = r.TH1F("h_energyDiff_bestplane", "Shower Energy Best Plane Norm - Nominal;#Delta Energy [GeV]", 200, -1, 1)

    hists['Raw'] = [h_dedx_plane0,  h_dedx_plane1, h_dedx_plane2, h_dedx_bestplane, h_energy_plane0, h_energy_plane1, h_energy_plane2, 
                    h_energy_bestplane, h_tEnergyDiff_plane0, h_tEnergyDiff_plane1, h_tEnergyDiff_plane2, h_tEnergyDiff_bestplane]
    hists['Norm'] = [h_dedx_plane0_norm,  h_dedx_plane1_norm, h_dedx_plane2_norm, h_dedx_bestplane_norm, h_energy_plane0_norm, h_energy_plane1_norm, 
                    h_energy_plane2_norm, h_energy_bestplane_norm, h_tEnergyDiff_plane0_norm, h_tEnergyDiff_plane1_norm, h_tEnergyDiff_plane2_norm, h_tEnergyDiff_bestplane_norm]
    hists['Comparison'] = [h_dedx2d_plane0, h_dedx2d_plane1, h_dedx2d_plane2, h_dedx2d_bestplane, h_energy2d_plane0, h_energy2d_plane1, h_energy2d_plane2, h_energy2d_bestplane,
                          h_tEnergy2d_plane0, h_tEnergy2d_plane1, h_tEnergy2d_plane2, h_tEnergy2d_bestplane,
                          h_tEnergy2d_plane0_norm, h_tEnergy2d_plane1_norm, h_tEnergy2d_plane2_norm, h_tEnergy2d_bestplane_norm]
    hists['Difference'] = [h_dedxDiff_plane0, h_dedxDiff_plane1, h_dedxDiff_plane2, h_dedxDiff_bestplane, h_energyDiff_plane0, h_energyDiff_plane1, h_energyDiff_plane2, h_energyDiff_bestplane]
    hists['Truth'] = [h_truthEnergy_bestMatch]

    branches = [
        "rec.slc.reco.pfp.shw.plane.0.dEdx",
        "rec.slc.reco.pfp.shw.plane.1.dEdx",
        "rec.slc.reco.pfp.shw.plane.2.dEdx",
        "rec.slc.reco.pfp.shw.bestplane_dEdx",
        "rec.slc.reco.pfp.shw.plane.0.energy",
        "rec.slc.reco.pfp.shw.plane.1.energy",
        "rec.slc.reco.pfp.shw.plane.2.energy",
        "rec.slc.reco.pfp.shw.bestplane_energy"
    ]

    iterateTrees(normFiles, rawFiles, branches, hists, outputFile, args.mc)

    