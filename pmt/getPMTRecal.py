import uproot
import ROOT as r
import numpy as np
import awkward as ak
import array as arr
import pandas as pd
import os
import sys

#https://docs.google.com/spreadsheets/d/1Kra6eIflTKS_sMghBqgpy1h86Z8WKkibZLrLnDAdWaQ/edit?gid=0#gid=0
bad_runs = [9304, 9305, 9306, 9320, 9321, 9322, 9323, 9324, 9325, 9326, 9348, 9349, 9350, 9351, 9352, 9381, 9382, 9395, 9396, 9397, 9398, 9399, 9400, 9401, 9402, 9403, 9404, 9405, 9406, 9407, 9408, 9410, 9411, 9413, 9414, 9416, 9433, 9434, 9440, 9446, 9447, 9449, 9451, 9452, 9453, 9454, 9455, 9456, 9459, 9461, 9462, 9463, 9465, 9466, 9467, 9468, 9469, 9470, 9471, 9476, 9479, 9480, 9483, 9484, 9485, 9486, 9487, 9488, 9489, 9490, 9491, 9492, 9493, 9494, 9496, 9497, 9498, 9500, 9501, 9502, 9503, 9505, 9506, 9507, 9508, 9509, 9510, 9511, 9512, 9519, 9520, 9521, 9522, 9523, 9524, 9525, 9526, 9527, 9528, 9529, 9530, 9535, 9536, 9537, 9538, 9539, 9540, 9541, 9542, 9543, 9544, 9545, 9546, 9547, 9548, 9549, 9550, 9551, 9552, 9553, 9554, 9555, 9556, 9557, 9561, 9567, 9572, 9573, 9574, 9575, 9576, 9577, 9578, 9579, 9581, 9591, 9592, 9596, 9600, 9601, 9603, 9604, 9605, 9606, 9607, 9608, 9609, 9611, 9612, 9613, 9614, 9615, 9616, 9617, 9618, 9619, 9620, 9621, 9622, 9623, 9628, 9629, 9630, 9632, 9633, 9635, 9636, 9637, 9638, 9639, 9640, 9641, 9643, 9644, 9645, 9650, 9651, 9652, 9653, 9654, 9655, 9656, 9657, 9659, 9660, 9661, 9662, 9663, 9664, 9665, 9666, 9667, 9668, 9669, 9670, 9671, 9676, 9677, 9678, 9679, 9680, 9681, 9682, 9683, 9684, 9685, 9686, 9701, 9702, 9706, 9707, 9708, 9709, 9710, 9711, 9712, 9713, 9718, 9719, 9736, 9737, 9738, 9739, 9740, 9741, 9742, 9759, 9767, 9768, 9769, 9770, 9771, 9772, 9773, 9774, 9775, 9776, 9777, 9778, 9787, 9789, 9790, 9798, 9799, 9800, 9801, 9802, 9803, 9804, 9805, 9806, 9808, 9809, 9810, 9811, 9812, 9813, 9815, 9816, 9817, 9818, 9819, 9820, 9821, 9822, 9823, 9824, 9825, 9826, 9827, 9828, 9829, 9830, 9831, 9832, 9833, 9845, 9846, 9856, 9857, 9864, 9865, 9866, 9872, 9873, 9874, 9875, 9876, 9877, 9878, 9879, 9880, 9881, 9882, 9883, 9884, 9885, 9886, 9887, 9888, 9889, 9890, 9891, 9895, 9898, 9899, 9900, 9901, 9902, 9903, 9904, 9905, 9906, 9907, 9908, 9909, 9910, 9912, 9927, 9928, 9930, 9936, 9937, 9938, 9939, 9952, 9957, 9958, 9963, 9964, 9965, 9966, 9967, 9969, 9976, 9990, 9992, 9993, 9994, 9995, 9996, 9997, 9998, 9999, 10000, 10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10011, 10012, 10013, 10014, 10016, 10017, 10018, 10019, 10020, 10021, 10022, 10023, 10024, 10025, 10026, 10027, 10028, 10029, 10031, 10032, 10033, 10034, 10035, 10036, 10037, 10038, 10039, 10041, 10042, 10043, 10044, 10045, 10046, 10047, 10049, 10050, 10051, 10052, 10053, 10069, 10070, 10071, 10072, 10073, 10074, 10075, 10076, 10077, 10078, 10079, 10080, 10081, 10082, 10083]

def getToken():
    os.system('~/root/bin/htgettoken -a htvaultprod.fnal.gov -i icarus')

def getSPECalInfo(sPEList='/nashome/m/micarrig/icarus/pmt/v10_06_00_01p04/speFiles.txt'):
    speFiles = {}
    with open(sPEList, 'r') as f:
        for line in f:
            filename = line.strip()
            run_num = int(filename.split('_')[1].replace('run', ''))  # Extract run number
            if run_num in bad_runs: continue
            if run_num in speFiles:
                print("Duplicate SPE run found:", run_num)
            else:
                speFiles[run_num] = filename
    return speFiles

def getSPECalInfoDir(dir=None):
    speFiles = {}
    for filename in os.listdir(dir):
        if not filename.endswith('.csv'):
            continue
        run_num = int(filename.split('_')[1].replace('run', ''))  # Extract run number
        if run_num in bad_runs: continue
        if run_num in speFiles:
            print("Duplicate SPE run found:", run_num)
        else:
            speFiles[run_num] = os.path.join(dir, filename)
    return speFiles

def getCalFiles(start=None, stop=None, cList='/nashome/m/micarrig/icarus/pmt/v10_06_00_01p04/calFiles.list'):
    calRuns = []
    calFiles = []
    with open(cList, 'r') as cal_files:
        for line in cal_files:
            this_run = int(line.strip().split('/')[-1].split('_')[5].replace('run', ''))
            if this_run in bad_runs: continue
            if start is not None and this_run < start:
                continue
            if stop is not None and this_run > stop:
                continue
            calRuns.append(this_run)
            calFiles.append(f'{line.strip()}:simpleLightAna/ophit_ttree')
            #calFiles.append(f'{line.strip()}:simpleLightAna/ophit_ttree')          
            #calFiles.append(f'{line.strip()}:simpleLightAna/opflashCryoE_flashtree')
            #calRuns.append(this_run)
            #calFiles.append(f'{line.strip()}:simpleLightAna/opflashCryoW_flashtree')
    if len(calRuns) > 0:
        calRuns, calFiles = zip(*sorted(zip(calRuns, calFiles)))
    print("Number of cal files found:", len(calFiles))
    return calRuns, calFiles

def getSPECalibrationRun(calRuns, speFiles):
    # For each calRun, find the most recent speRun
    recent_spe_for_cal = {}
    for cal_run in calRuns:
        # Find all speRuns that are <= cal_run
        valid_spe_runs = [spe_run for spe_run in list(speFiles.keys()) if spe_run <= cal_run]
        if valid_spe_runs:
            # Get the most recent (maximum) speRun
            recent_spe_for_cal[cal_run] = [max(valid_spe_runs), speFiles[max(valid_spe_runs)]]
        else:
            print("No valid SPE run found for cal run:", cal_run)
            recent_spe_for_cal[cal_run] = [None, None]
    return recent_spe_for_cal

# https://github.com/SBNSoftware/icaruscode/blob/develop/icaruscode/PMT/OpReco/fcl/icarus_spe.fcl#L20C9-L20C16
def recalibratePE(pe, newGain, oldGain=256.658):
    recalPE = pe * (oldGain / newGain)
    return recalPE

def recalibratePEFit(pe, run, y=261.71273, m=-0.01136, oldGain=256.658):
    f1 = r.TF1("f1", f"{y} + x*{m}")
    newGain = f1.Eval(run)
    recalPE = pe * (oldGain / newGain)
    return recalPE

#convert q from electrons to adc * tick
# clock tick = 2ns
# resistance = 50 ohm
# 1 ADC * tick = 0.00488 pC
# electron charge = 1.602e-19 C
def calculate_qADC(cal):
    cal['qADC'] = cal['q'] * 1e7 * 1.602e-19 / (0.00488e-12)
    cal['qADCErr'] = cal['eq'] * 1e7 * 1.602e-19 / (0.00488e-12)
    cal.loc[cal['fitstatus'] != 0, 'qADC'] = -1
    cal.loc[cal['fitstatus'] != 0, 'qADCErr'] = -1

def calculateNewGains(speRuns):
    newGains = {}
    newGainsErr = {}
    fit = {}
    for ifile, (run, file) in enumerate(speRuns.items()):
        if not file.endswith('.csv'): continue
        cal = pd.read_csv(file).sort_values('pmt').reset_index(drop=True)
        calculate_qADC(cal)
        newGains[run] = cal['qADC'].tolist()
        newGainsErr[run] = cal['qADCErr'].tolist()
        fit[run] = [(x / y) if y > 0 else -1 for x, y in zip(cal['chi2'].tolist(), cal['ndf'].tolist())]

    return newGains, newGainsErr, fit

def initializeHistograms(calRuns, name, nbins, xmin, xmax, chans=360):
    h_normPE = {}
    for run in np.unique(calRuns):
        h_normPE[run] = []
        if chans == 1:
            h_normPE[run].append(r.TH1F(f"h_{name}_run{run}", f"Run {run} {name}", nbins, xmin, xmax))
        else:
            for ichan in range(chans):
                h_normPE[run].append(r.TH1F(f"h_{name}_run{run}_chan{ichan}", f"Run {run} Channel {ichan} {name}", nbins, xmin, xmax))

    return h_normPE

def writeHists(fout, hists, dir_name):
    for key, val in hists.items():
        if not fout.GetDirectory(f"run{key}"):
            fout.mkdir(f"run{key}")
        fout.mkdir(f"run{key}/{dir_name}")
        fout.cd(f"run{key}/{dir_name}")
        for hist in val:
            hist.Write()

def getPMTRecal(start, stop, output_dir=None, grid=False, calFiles='/nashome/m/micarrig/icarus/pmt/v10_06_00_01p04/calFiles.list'):

    if not grid:
        getToken()

    fout = r.TFile.Open(f"{output_dir}/pmtPEHistograms_{start}_{stop}.root", "RECREATE")


    calRuns, calFiles = getCalFiles(start, stop, calFiles)

    if len(calFiles) == 0:
        print("No calibration files found for the specified run range.")
        fout.Close()
        return

    speRuns = getSPECalibrationRun(calRuns, speFiles)

    print(f"There are {len(calFiles)}, calibration files to process over {len(np.unique(calRuns))} runs.")

    h_normPE = initializeHistograms(np.unique(calRuns), "normPE", 200, 0, 20)
    h_recalPE = initializeHistograms(np.unique(calRuns), "recalPE", 200, 0, 20)
    h_recalFitPE = initializeHistograms(np.unique(calRuns), "recalFitPE", 200, 0, 20)
    h_sumPE = initializeHistograms(np.unique(calRuns), "sumPE", 5000, 0, 100000, chans=1)
    h_sumPE2 = initializeHistograms(np.unique(calRuns), "sumPE", 5000, 0, 100000, chans=1)
    h_sumPERecal = initializeHistograms(np.unique(calRuns), "sumPERecal", 5000, 0, 100000, chans=1)
    h_sumPEFitRecal = initializeHistograms(np.unique(calRuns), "sumPEFitRecal", 5000, 0, 100000, chans=1)

    branches = ['run', 'pe_pmt', 'sum_pe']
    for ifile, batch in enumerate(uproot.iterate(calFiles, branches, step_size='50 MB')):
        if ifile %10 == 0:
            print(f"Processing calibration file {ifile+1} / {len(calFiles)}")
        
        thisRun = batch['run'].to_numpy()[0]

        if ak.any(batch['run'].to_numpy() != calRuns[ifile]):
            print("Mismatch in run numbers:", batch['run'].to_numpy()[0], calRuns[ifile], "skipping run/file...", calRuns[ifile], calFiles[ifile])
            continue

        calRun = speRuns[thisRun][0]

        sumPE2 = batch['sum_pe'].to_numpy()

        sumPERecal = np.zeros_like(sumPE2)
        sumPE = np.zeros_like(sumPE2)
        sumPEFit = np.zeros_like(sumPE2)

        sumPE2 = sumPE2[sumPE2 >= 1e-9]

        #cut tail for sumPE2
        sumPE2 = sumPE2[sumPE2 <= 50000]
        h_sumPE2[thisRun][0].FillN(len(sumPE2), arr.array('d', sumPE2), np.ones(len(sumPE2)))
        
        for i in range(0, nPMTs):

            nPE = batch['pe_pmt'][:, i].to_numpy()
            
            nPERecal = recalibratePE(nPE, newGain=newGains[calRun][i])
            nPEFitRecal = recalibratePEFit(nPE, run=thisRun)
            sumPERecal += nPERecal
            sumPE += nPE
            sumPEFit += nPEFitRecal

            #define single PMT nPE cut
            nPECut = nPE <= 10

            nPE = nPE[nPECut]
            nPE = nPE[nPE >= 1e-9]
            if len(nPE) > 0:
                h_normPE[thisRun][i].FillN(len(nPE), arr.array('d', nPE), np.ones(len(nPE)))
            
            nPERecal = nPERecal[nPECut]
            nPERecal = nPERecal[nPERecal >= 1e-9]
            if len(nPERecal) > 0:
                h_recalPE[thisRun][i].FillN(len(nPERecal), arr.array('d', nPERecal), np.ones(len(nPERecal)))

            nPEFitRecal = nPEFitRecal[nPECut]
            nPEFitRecal = nPEFitRecal[nPEFitRecal >= 1e-9]
            if len(nPEFitRecal) > 0:
                h_recalFitPE[thisRun][i].FillN(len(nPEFitRecal), arr.array('d', nPEFitRecal), np.ones(len(nPEFitRecal)))
        
        sumPERecal = sumPERecal[sumPERecal >= 1e-9]
        if len(sumPERecal) > 0:
            h_sumPERecal[thisRun][0].FillN(len(sumPERecal), arr.array('d', sumPERecal), np.ones(len(sumPERecal)))

        sumPE2 = sumPE2[sumPE2 >= 1e-9]
        if len(sumPE2) > 0:
            h_sumPE[thisRun][0].FillN(len(sumPE), arr.array('d', sumPE), np.ones(len(sumPE)))

        sumPEFit = sumPEFit[sumPEFit >= 1e-9]
        if len(sumPEFit) > 0:
            h_sumPEFitRecal[thisRun][0].FillN(len(sumPEFit), arr.array('d', sumPEFit), np.ones(len(sumPEFit)))

    writeHists(fout, h_normPE, "NormalizedPE")
    writeHists(fout, h_recalPE, "RecalibratedPE")
    writeHists(fout, h_sumPE, "SumPE")
    writeHists(fout, h_sumPE2, "SumPE2")
    writeHists(fout, h_sumPERecal, "SumPERecal")
    writeHists(fout, h_recalFitPE, "RecalibratedFitPE")
    writeHists(fout, h_sumPEFitRecal, "SumPEFitRecal")

    del h_normPE
    del h_recalPE
    del h_sumPE
    del h_sumPE2
    del h_sumPERecal
    del h_recalFitPE
    del h_sumPEFitRecal

    fout.Close()

def getPMTRecalNoFlash(start, stop, output_dir=None, grid=False, calFiles='/nashome/m/micarrig/icarus/pmt/v10_06_00_01p04/calFiles.list'):

    #if not grid:
    #    getToken()

    if output_dir.endswith('.root'):
        fout = r.TFile.Open(output_dir, "RECREATE")
    else:
        fout = r.TFile.Open(f"{output_dir}/pmtPEHistograms_{start}_{stop}.root", "RECREATE")

    calRuns, calFiles = getCalFiles(start, stop, calFiles)

    if len(calFiles) == 0:
        print("No calibration files found for the specified run range.")
        fout.Close()
        return

    speRuns = getSPECalibrationRun(calRuns, speFiles)

    print(f"There are {len(calFiles)}, calibration files to process over {len(np.unique(calRuns))} runs.")

    h_normPE = initializeHistograms(np.unique(calRuns), "normPE", 200, 0, 20)
    h_recalPE = initializeHistograms(np.unique(calRuns), "recalPE", 200, 0, 20)
    h_recalFitPE = initializeHistograms(np.unique(calRuns), "recalFitPE", 200, 0, 20)
    h_sumPE = initializeHistograms(np.unique(calRuns), "sumPE", 5000, 0, 2000000, chans=1)
    h_sumPERecal = initializeHistograms(np.unique(calRuns), "sumPERecal", 5000, 0, 2000000, chans=1)
    h_sumPEFitRecal = initializeHistograms(np.unique(calRuns), "sumPEFitRecal", 5000, 0, 2000000, chans=1)

    branches = ['run', 'pe', 'channel_id', 'event', 'start_time', 'width']
    for ifile, batch in enumerate(uproot.iterate(calFiles, branches, step_size='200 MB')):
        if ifile %10 == 0:
            print(f"Processing calibration file {ifile+1} / {len(calFiles)}")

        thisRun = batch['run'].to_numpy()[0]

        if ak.any(batch['run'].to_numpy() != calRuns[ifile]):
            print("Mismatch in run numbers:", batch['run'].to_numpy()[0], calRuns[ifile], "skipping run/file...", calRuns[ifile], calFiles[ifile])
            continue

        #get first run, require all runs are equal to this
        calRun = speRuns[thisRun][0]

        #define arrays from branches
        event = batch['event']
        nPE = batch['pe']
        startTime = batch['start_time']
        width = batch['width']
        channels = batch['channel_id']

        #apply nPE cut
        nPECut = (nPE <= 10) & (nPE >= 0)

        channel_ids = channels[nPECut]
        nPE = nPE[nPECut]
        startTime = startTime[nPECut]
        width = width[nPECut]
        event = event[nPECut]

        #need to manually group by event
        sort_idx = ak.argsort(event)
        sorted_event = event[sort_idx]
        nPE = nPE[sort_idx]
        start_time = startTime[sort_idx]
        width = width[sort_idx]
        channel_ids = channel_ids[sort_idx]

        # Find where event numbers change
        run_lengths = ak.run_lengths(sorted_event)

        # Use these to split the pe array
        g_nPE = ak.unflatten(nPE, run_lengths)
        g_start_time = ak.unflatten(start_time, run_lengths)
        g_width = ak.unflatten(width, run_lengths)
        g_channel_ids = ak.unflatten(channel_ids, run_lengths)

        #apply isolation selections

        #sort by start time
        args = ak.argsort(g_start_time, axis=1)
        g_nPE = g_nPE[args]
        g_start_time = g_start_time[args]
        g_width = g_width[args]
        g_channel_ids = g_channel_ids[args]

        #check if sequential hits are in the same channel
        ch_prev = ak.concatenate([ak.Array([[-999]] * len(g_channel_ids)), g_channel_ids[:, :-1]], axis=1)
        ch_next = ak.concatenate([g_channel_ids[:, 1:], ak.Array([[-999]] * len(g_channel_ids))], axis=1)
        adjacent_mask = ((abs(g_channel_ids - ch_prev) == 0) | (abs(g_channel_ids - ch_next) == 0))

        # If adjacent hits are within timeCut and in same channel veto
        timeCut = 0.2
        time_prev = ak.concatenate([ak.Array([[1e9]] * len(g_start_time)), g_start_time[:, :-1]], axis=1)
        time_next = ak.concatenate([g_start_time[:, 1:], ak.Array([[1e9]] * len(g_start_time))], axis=1)
        dt_prev = abs(g_start_time - time_prev)
        dt_next = abs(time_next - g_start_time)
        time_mask = (dt_prev < timeCut) | (dt_next < timeCut)
        time_mask = adjacent_mask & time_mask

        # If adjacent hits are in the same channel and previous hit width > timeCut veto
        width_prev = ak.concatenate([ak.Array([[0.0]] * len(g_width)), g_width[:, :-1]], axis=1)
        width_next = ak.concatenate([g_width[:, 1:], ak.Array([[0.0]] * len(g_width))], axis=1)
        prev_width_mask = (width_prev > timeCut) & adjacent_mask

        #if this hit has width > timeCut veto
        width_mask = g_width > timeCut

        #final mask and cut on g_nPE
        mask = ~(time_mask | prev_width_mask | width_mask)
        g_nPE = g_nPE[mask]
        g_channel_ids = g_channel_ids[mask]
    
        #get the gains and recalibrate nPE
        runGains = ak.Array([newGains[calRun] for _ in range(len(g_channel_ids))])
        gains = runGains[g_channel_ids]
        g_nPERecal = recalibratePE(g_nPE, newGain=gains)
        g_nPEFitRecal = recalibratePEFit(g_nPE, run=thisRun)

        nPE_sum = ak.sum(g_nPE, axis=1).to_numpy()
        nPERecal_sum = ak.sum(g_nPERecal, axis=1).to_numpy()
        nPEFitRecal_sum = ak.sum(g_nPEFitRecal, axis=1).to_numpy()
        h_sumPE[thisRun][0].FillN(len(nPE_sum), arr.array('d', nPE_sum), np.ones(len(nPE_sum)))
        h_sumPERecal[thisRun][0].FillN(len(nPERecal_sum), arr.array('d', nPERecal_sum), np.ones(len(nPERecal_sum)))
        h_sumPEFitRecal[thisRun][0].FillN(len(nPEFitRecal_sum), arr.array('d', nPEFitRecal_sum), np.ones(len(nPEFitRecal_sum)))

        for i in range(0, nPMTs):

            chanCut = g_channel_ids == i #cut on channel id

            nPE_chan = ak.flatten(g_nPE[chanCut])
            nPERecal_chan = ak.flatten(g_nPERecal[chanCut])
            nPEFitRecal_chan = ak.flatten(g_nPEFitRecal[chanCut])

            nPE_chan = nPE_chan[nPE_chan >= 1e-9].to_numpy()
            if len(nPE_chan) > 0:
                h_normPE[thisRun][i].FillN(len(nPE_chan), arr.array('d', nPE_chan), np.ones(len(nPE_chan)))

            nPERecal_chan = nPERecal_chan[nPERecal_chan >= 1e-9].to_numpy()
            if len(nPERecal_chan) > 0:
                h_recalPE[thisRun][i].FillN(len(nPERecal_chan), arr.array('d', nPERecal_chan), np.ones(len(nPERecal_chan)))

            nPEFitRecal_chan = nPEFitRecal_chan[nPEFitRecal_chan >= 1e-9].to_numpy()
            if len(nPEFitRecal_chan) > 0:
                h_recalFitPE[thisRun][i].FillN(len(nPEFitRecal_chan), arr.array('d', nPEFitRecal_chan), np.ones(len(nPEFitRecal_chan)))


    writeHists(fout, h_normPE, "NormalizedPE")
    writeHists(fout, h_recalPE, "RecalibratedPE")
    writeHists(fout, h_sumPE, "SumPE")
    writeHists(fout, h_sumPERecal, "SumPERecal")
    writeHists(fout, h_recalFitPE, "RecalibratedFitPE")
    writeHists(fout, h_sumPEFitRecal, "SumPEFitRecal")

    del h_normPE
    del h_recalPE
    del h_sumPE
    del h_sumPERecal
    del h_recalFitPE
    del h_sumPEFitRecal

    fout.Close()

if __name__ == "__main__":

    nPMTs = 360

    if len(sys.argv) > 3:
        fileDir = sys.argv[3]
        speFiles = getSPECalInfoDir(dir=fileDir)
        newGains, newGainsErr, fits = calculateNewGains(speFiles)
        allRuns = sorted(list(speFiles.keys()))
        print("All runs:", allRuns)
        index = int(sys.argv[1])
        start_run = allRuns[0] + index * 20
        print("Running for runs:", start_run, "to", start_run + 19)
        getPMTRecalNoFlash(start_run, start_run+19, output_dir=sys.argv[2], grid=True, calFiles=fileDir+'/calFiles.list')

    else:
        speFiles = getSPECalInfo()
        newGains, newGainsErr, fits = calculateNewGains(speFiles)
        for start_run in range(9400, 9420, 20):
            #getPMTRecal(start_run, start_run + 19, output_dir="/nashome/m/micarrig/icarus/pmt/v10_06_00_01p04/pmtRecalNoFlash")
            try:
                getPMTRecalNoFlash(start_run, start_run + 19, output_dir="/nashome/m/micarrig/icarus/pmt/v10_06_00_01p04/pmtRecalNoFlash")
            except Exception as e:
                print(f"Error processing runs {start_run} to {start_run + 19}: {e}")




