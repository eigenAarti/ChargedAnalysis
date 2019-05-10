#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import os
import yaml
import argparse
import copy
import pandas as pd
from random import randint, uniform

def parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--background", nargs="+", default = ["TT+X"], help = "Name of background processes")
    parser.add_argument("--signal", nargs = "+", default = [], help = "Name of data process")   

    parser.add_argument("--skim-dir", type = str, help = "Directory with skimmed files")
    parser.add_argument("--process-yaml", type = str, default = "{}/src/ChargedHiggs/analysis/data/process.yaml".format(os.environ["CMSSW_BASE"]), help = "Yaml configuration which maps process name and skimmed files names")
    parser.add_argument("--tree-dir", type = str, default = "{}/src/Trees".format(os.environ["CMSSW_BASE"]), help = "Output directory of root file")
    parser.add_argument("--result-dir", type = str, default = "{}/src/BDT".format(os.environ["CMSSW_BASE"]), help = "Output directory of BDT results")

    parser.add_argument("--show-result", type = str, help = "Name of root file of BDT training")
    parser.add_argument("--create-trees", action = "store_true", default = False, help = "State if input trees for BDT should be created")

    parser.add_argument("--channel", type = str, help = "Final state which is of interest")
    parser.add_argument("--x-parameters", nargs="+", default = [], help = "Name of parameters to be plotted")
    parser.add_argument("--cuts", nargs="+", default=[], help = "Name of cut implemented in TreeReader class")
    parser.add_argument("--optimize", action = "store_true", default = False, help = "Optimize hyperparameter space")

    return parser.parse_args()

def createTrees(treedir, process, xParameters, cuts, filenames, channel):
    outname = ROOT.std.string("{}/{}.root".format(treedir, process))

    reader = ROOT.TreeReader(ROOT.std.string(process), xParameters, ROOT.std.vector("string")(), cuts, outname, ROOT.kTRUE)
    reader.SetHistograms();
    reader.EventLoop(filenames, ROOT.std.string(channel))
    reader.Write()

def optimize(xParameters, background, signal, treeDir, resultDir, evType):
    paramSet = {}

    for i in xrange(300):
        params = [
                    ("NTrees", randint(100, 1400)), 
                    ("MindNodeSize", uniform(0.5, 10.)), 
                    ("AdaBoostBeta", uniform(0.1, 1.)),
                    ("nCuts", randint(5, 40)), 
                    ("MaxDepth", randint(2, 3)), 
                    ("Dropout", randint(2, len(xParameters) -1)),
                    ("SeparationType", ["GiniIndex", "CrossEntropy", "SDivSqrtSPlusB", "MisClassificationError"][randint(0, 3)]),
        ]

        for key, value in params:
            paramSet.setdefault(key, []).append(value)

        trainer = ROOT.BDT(params[0][1], params[1][1], params[2][1], params[3][1], params[4][1], params[5][1], params[6][1])
        ROC = trainer.Train(xParameters, ROOT.std.string(treeDir), ROOT.std.string(resultDir), signal, background, ROOT.std.string(evType)) 
    
        paramSet.setdefault("ROC", []).append(ROC)


        if(i%5==0):
            df = pd.DataFrame(paramSet)
            df = df.sort_values(by="ROC", ascending=False)
            df.to_csv("{}/hyperparameter_200_2.csv".format(resultDir), sep='\t', index=False)

def trainBDT(xParameters, background, signal, treeDir, resultDir, evType):
    trainer = ROOT.BDT(1271, 1.1504595857486688, 0.26042540109105, 35, 3, 14, "MisClassificationError")
    trainer.Train(xParameters, ROOT.std.string(treeDir), ROOT.std.string(resultDir), signal, background, ROOT.std.string(evType)) 

def main():
    ##Parser
    args = parser()

    ##Show results of BDT training
    if args.show_result:
        ROOT.TMVA.TMVAGui(args.show_result)
        raw_input("Press Enter to exit")
        return 0
    
    ##Load filenmes of processes
    process_dic = yaml.load(file(args.process_yaml, "r"))

    for dirext in ["Even", "Odd"]:
        if not os.path.exists("{}/{}".format(args.tree_dir, dirext)):
            print "Created output path: {}/{}".format(args.tree_dir, dirext)
            os.system("mkdir -p {}/{}".format(args.tree_dir, dirext))

        if not os.path.exists("{}/{}".format(args.result_dir, dirext)):
            print "Created output path: {}/{}".format(args.result_dir, dirext)
            os.system("mkdir -p {}/{}".format(args.result_dir, dirext))

    ##Create std::vector for parameters
    xParameters = ROOT.std.vector("string")()
    [xParameters.push_back(param) for param in args.x_parameters]

    signal = ROOT.std.vector("string")()
    [signal.push_back(proc) for proc in args.signal]

    background = ROOT.std.vector("string")()
    [background.push_back(proc) for proc in args.background]

    cuts = ROOT.std.vector("string")()
    [cuts.push_back(cut) for cut in args.cuts]

    ##Create Trees for training
    for processes in [background, signal]:
        for process in processes:
            filenames = ROOT.std.vector("string")()
            
            [filenames.push_back(fname) for fname in ["{skim}{file}/{file}.root".format(skim = args.skim_dir, file = process_file) for process_file in process_dic[process]["filenames"]]]       

            if args.create_trees:
                for (dirext, cut) in [("Even", "evNr_%_2"), ("Odd", "evNr_%!_2")]:
                    extCuts = copy.deepcopy(cuts)
                    extCuts.push_back(cut)
                    createTrees("{}/{}".format(args.tree_dir, dirext), process, xParameters, extCuts, filenames, args.channel)

    if args.optimize:
        optimize(xParameters, background, signal, args.tree_dir, args.result_dir, "Even")

    else:
        #Train the BDT
        for dirext in ["Even", "Odd"]:
            trainBDT(xParameters, background, signal, args.tree_dir, args.result_dir, dirext)

if __name__ == "__main__":
    main()
