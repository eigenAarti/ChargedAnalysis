#ifndef JETANALYZER_H
#define JETANALYZER_H

#include <ChargedHiggs/Skimming/interface/baseanalyzer.h>

#include <random>

#include <CondFormats/BTauObjects/interface/BTagCalibration.h>
#include <CondTools/BTau/interface/BTagCalibrationReader.h>
#include <JetMETCorrections/Modules/interface/JetResolution.h>
#include <JetMETCorrections/Modules/interface/JetCorrectionProducer.h>
#include <CondFormats/JetMETObjects/interface/JetCorrectorParameters.h>
#include <CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h>


#include <DataFormats/PatCandidates/interface/Jet.h>
#include <DataFormats/PatCandidates/interface/MET.h>

//Jet class to be safed in tree
struct Jet {
    TLorentzVector fourVec;
    Bool_t isLooseB = false;
    Bool_t isMediumB = false;
    Bool_t isTightB = false;

    Float_t loosebTagSF = 1.;
    Float_t mediumbTagSF = 1.;
    Float_t tightbTagSF = 1.;

    Int_t fatJetIdx = -1.;

    TLorentzVector genVec;
    Bool_t isFromh1 = false;
    Bool_t isFromh2 = false;
};

struct FatJet : public Jet {
    Float_t oneSubJettiness = 1.;
    Float_t twoSubJettiness = 1.;
    Float_t threeSubJettiness = 1.;
};

class JetAnalyzer: public BaseAnalyzer{
    enum JetType {AK4, AK8};

    private:
        //Bool for checking if data file
        bool isData;

        //Map for SF files
        std::map<JetType, std::map<int, std::vector<std::string>>> JEC;
        std::map<JetType, std::map<int, std::string>> bTagSF;
        std::map<JetType, std::map<int, std::string>> JMESF;
        std::map<JetType, std::map<int, std::string>> JMEPtReso;

        //Values for bTag cuts
        std::map<JetType, std::map<int, std::vector<float>>> bTagCuts; 

        //Classes for reading btag SF
        std::map<JetType, BTagCalibration> calib;
        std::map<JetType, BTagCalibrationReader> looseReader;
        std::map<JetType, BTagCalibrationReader> mediumReader;
        std::map<JetType, BTagCalibrationReader> tightReader;

        //Classes for reading jet energy SF 
        JME::JetParameters jetParameter;
        std::map<JetType, JME::JetResolution> resolution;
        std::map<JetType, JME::JetResolutionScaleFactor> resolution_sf;

        //Input for selecting jets
        int era;
        float ptCut;
        float etaCut;
        std::vector<std::pair<unsigned int, unsigned int>> minNJet;

        //EDM Token for MINIAOD analysis
        std::vector<jToken> jetTokens;
        std::vector<genjToken> genjetTokens;
        mToken metToken;
        edm::EDGetTokenT<double> rhoToken;

        //TTreeReader Values for NANO AOD analysis
        std::unique_ptr<TTreeReaderArray<float>> fatJetPt;
        std::unique_ptr<TTreeReaderArray<float>> fatJetEta;
        std::unique_ptr<TTreeReaderArray<float>> fatJetPhi;
        std::unique_ptr<TTreeReaderArray<float>> fatJetMass;
        std::unique_ptr<TTreeReaderArray<float>> fatJetCSV;
        std::unique_ptr<TTreeReaderArray<float>> fatJetTau1;
        std::unique_ptr<TTreeReaderArray<float>> fatJetTau2;
        std::unique_ptr<TTreeReaderArray<float>> fatJetTau3;

        std::unique_ptr<TTreeReaderArray<float>> jetPt;
        std::unique_ptr<TTreeReaderArray<float>> jetEta;
        std::unique_ptr<TTreeReaderArray<float>> jetPhi;
        std::unique_ptr<TTreeReaderArray<float>> jetMass;
        std::unique_ptr<TTreeReaderArray<int>> jetGenIdx;
        std::unique_ptr<TTreeReaderValue<float>> jetRho;
        std::unique_ptr<TTreeReaderArray<float>> jetDeepBValue;
        std::unique_ptr<TTreeReaderValue<float>> valueHT;

        std::unique_ptr<TTreeReaderArray<float>> genJetPt;
        std::unique_ptr<TTreeReaderArray<float>> genJetEta;
        std::unique_ptr<TTreeReaderArray<float>> genJetPhi;
        std::unique_ptr<TTreeReaderArray<float>> genJetMass;

        std::unique_ptr<TTreeReaderArray<float>> genFatJetPt;
        std::unique_ptr<TTreeReaderArray<float>> genFatJetEta;
        std::unique_ptr<TTreeReaderArray<float>> genFatJetPhi;
        std::unique_ptr<TTreeReaderArray<float>> genFatJetMass;

        std::unique_ptr<TTreeReaderValue<float>> metPhi;
        std::unique_ptr<TTreeReaderValue<float>> metPt;

        //Parameter for HT
        float HT;

        //Valid jet collection
        std::vector<Jet> validJets;
        std::vector<Jet> subJets;
        std::vector<FatJet> validFatJets;

        //met Lorentzvector
        TLorentzVector met;

        //Get jet energy correction
        float CorrectEnergy(TLorentzVector &jet, const float &rho, float &area, const JetType &type);

        //Get JER smear factor
        float SmearEnergy(TLorentzVector &jet, const float &rho, const float &coneSize, const JetType &type, const std::vector<reco::GenJet> &genJet = {});

        //Set Gen particle information
        std::vector<int> alreadyMatchedJet; 
        void SetGenParticles(Jet &validJet, const int &i);

    public:
        JetAnalyzer(const int &era, const float &ptCut, const float &etaCut, const std::vector<std::pair<unsigned int, unsigned int>> minNJet, TTreeReader& reader);
        JetAnalyzer(const int &era, const float &ptCut, const float &etaCut, const std::vector<std::pair<unsigned int, unsigned int>> minNJet, std::vector<jToken>& jetTokens, std::vector<genjToken>& genjetTokens, mToken &metToken, edm::EDGetTokenT<double> &rhoToken);

        void BeginJob(TTree* tree, bool &isData);
        bool Analyze(std::pair<TH1F*, float> &cutflow, const edm::Event* event);
        void EndJob(TFile* file);
};

#endif