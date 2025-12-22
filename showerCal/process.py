import os
import glob

def getProcessedFiles(outputDir, caf=False):
    """Get all files from all subdirectories in outputDir"""
    processed_files = []
    for root, dirs, files in os.walk(outputDir):
        if 'log' in os.path.basename(root):
            continue
        for file in files:
            if caf:
                processed_files.append(int(file.split('/')[-1].replace('.root', '').replace('output_', '').split('.')[0]))        
            else:
                processed_files.append(int(file.split('/')[-1].replace('.root', '').replace('output_', '')))
    return processed_files

def getSourceFiles(sourceFileList):
    """Read source file list and return a list of file paths"""
    sourceFiles = {}
    with open(sourceFileList, 'r') as f:
        for i, line in enumerate(f):
            sourceFiles[i] = line.strip()
    return sourceFiles


def getUnprocessedFiles(sourceFiles, pFiles):
    unProcessedFiles = {}
    for i in sourceFiles.keys():
        if i not in pFiles:
            if list(sourceFiles.keys())[i] != i: print("Mismatch in file indexing!")
            unProcessedFiles[i] = sourceFiles[i]
    return unProcessedFiles

if __name__ == "__main__":

    outputDir = "/pnfs/icarus/scratch/users/micarrig/showerEnergyCalCafV2/outputs/"

    sourceFileList = "/pnfs/icarus/scratch/users/micarrig/showerEnergyCalCafV2/stage1_numiRun2.list"

    caf = True # alters the string search pattern 

    sourceFiles = getSourceFiles(sourceFileList)
    pFiles = sorted(getProcessedFiles(outputDir, caf=caf))

    unProcessedFiles = getUnprocessedFiles(sourceFiles, pFiles)


    print(f"There are {len(unProcessedFiles)} unprocessed files out of {len(sourceFiles)}.")

    # for i, (key, value) in enumerate(unProcessedFiles.items()):
    #     if i > 10: break
    #     print(f"{key}: {value}")

    with open('reprocessCaf.list', 'w') as f:
        for key, value in unProcessedFiles.items():
            f.write(f"{key} {value}\n")