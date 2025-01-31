#ifndef PLOTTER1D_H
#define PLOTTER1D_H

#include <ChargedAnalysis/Analysis/include/plotter.h>

#include "TFile.h"
#include "TH1F.h"
#include "TGraph.h"
#include "THStack.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "TPad.h"
#include "Rtypes.h"
#include "TMath.h"

#include <sstream>
#include <iostream>
#include <functional>

class Plotter1D : public Plotter{
    
    private:
        std::vector<std::vector<TH1F*>> background;
        std::vector<std::vector<TH1F*>> signal;
        std::vector<TH1F*> data;

        std::string channel;
        std::vector<std::string> xParameters;
        std::vector<std::string> processes;

    public:
        Plotter1D();
        Plotter1D(std::string &histdir, std::vector<std::string> &xParameters, std::string &channel,std::vector<std::string> &processes);
        void ConfigureHists();
        void Draw(std::vector<std::string> &outdirs);
        
};

#endif
