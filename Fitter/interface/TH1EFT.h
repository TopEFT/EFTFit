#ifndef TH1EFT_H_
#define TH1EFT_H_

#include "TH1D.h"
#include <vector>

#include "WCFit.h"
#include "WCPoint.h"

class TH1EFT : public TH1D
{
    public:
    
        // ROOT needs these:
        TH1EFT();
        ~TH1EFT();
        
        // usual constructor:
        TH1EFT(const char *name, const char *title, Int_t nbinsx, Double_t xlow, Double_t xup);
        
        std::vector<WCFit> hist_fits;
        //TODO(maybe?): Add over/underflow bin fit functions and update Fill to use them accordingly
        WCFit overflow_fit;
        WCFit underflow_fit;

        using TH1D::Fill;           // Bring the TH1D Fill fcts into scope
        using TH1D::GetBinContent;  // Bring the TH1D GetBinContent fcts into scope
        using TH1D::Scale;          // Bring the TH1D Scale fcts into scope (likely not needed)

        Int_t Fill(Double_t x, Double_t w, WCFit fit);
        WCFit GetBinFit(Int_t bin);
        WCFit GetSumFit();
        Double_t GetBinContent(Int_t bin, WCPoint wc_pt);
        TH1EFT* Scale(WCPoint wc_pt);
        void ScaleFits(double amt);
        void DumpFits();
        
        ClassDef(TH1EFT,1); // ROOT needs this here
        //TODO(maybe?): Add member function to return specifically fit coeffs (rather then entire WCFit object)
};

// ROOT needs this here:
ClassImp(TH1EFT);
TH1EFT::TH1EFT() {}
TH1EFT::~TH1EFT() {}


TH1EFT::TH1EFT(const char *name, const char *title, Int_t nbinsx, Double_t xlow, Double_t xup)
 : TH1D (name, title, nbinsx, xlow, xup) 
{
    // Create/Initialize a fit function for each bin in the histogram
    WCFit new_fit;
    for (Int_t i = 0; i < nbinsx; i++) {
        this->hist_fits.push_back(new_fit);
    }
}

Int_t TH1EFT::Fill(Double_t x, Double_t w, WCFit fit)
{
    Int_t bin_idx = this->FindFixBin(x) - 1;
    Int_t nhists  = this->hist_fits.size();
    if (bin_idx >= nhists) {
        // For now ignore events which enter overflow bin
        this->overflow_fit.addFit(fit);
        return Fill(x,w);
    } else if (bin_idx < 0) {
        // For now ignore events which enter underflow bin
        this->underflow_fit.addFit(fit);
        return Fill(x,w);
    }
    this->hist_fits.at(bin_idx).addFit(fit);
    return Fill(x,w); // the original TH1D member function
}

// Returns a fit function for a particular bin (no checks are made if the bin is an over/underflow bin)
WCFit TH1EFT::GetBinFit(Int_t bin)
{
    Int_t nhists = this->hist_fits.size();
    if (bin < 0) {
        return this->underflow_fit;
    } else if (bin >= nhists) {
        return this->overflow_fit;
    }
    return this->hist_fits.at(bin - 1);
}

// Returns a WCFit whose structure constants are determined by summing structure constants from all bins
WCFit TH1EFT::GetSumFit()
{
    WCFit summed_fit;
    for (uint i = 0; i < this->hist_fits.size(); i++) {
        summed_fit.addFit(this->hist_fits.at(i));
    }
    return summed_fit;
}

// Returns a bin scaled by the the corresponding fit evaluated at a particular WC point
Double_t TH1EFT::GetBinContent(Int_t bin, WCPoint wc_pt)
{
    double scale_value = this->GetBinFit(bin).evalPoint(&wc_pt);
    Double_t num_events = GetBinContent(bin);
    if (num_events == 0) {
        return 0.0;
    }

    //return num_events*scale_value;
    //return scale_value/num_events;  // Counter-intuitive, but the scale value is a sum of normalized wgts so needs to be adjusted for number of events in the bin
    return scale_value;
}

// Return a copy of the histogram which has bins scaled using the internal WCFits
TH1EFT* TH1EFT::Scale(WCPoint wc_pt)
{
    TH1EFT* new_hist = (TH1EFT*)this->Clone("clone");
    for (Int_t i = 1; i <= this->GetNbinsX(); i++) {
        Double_t new_content = this->GetBinContent(i,wc_pt);
        new_hist->SetBinContent(i,new_content);
    }

    return new_hist;
}

// Uniformly scale all fits by amt
void TH1EFT::ScaleFits(double amt)
{
    for (uint i = 0; i < this->hist_fits.size(); i++) {
        this->hist_fits.at(i).scale(amt);
    }
}

// Display the fit parameters for all bins
void TH1EFT::DumpFits()
{
    for (uint i = 0; i < this->hist_fits.size(); i++) {
        this->hist_fits.at(i).dump();
    }
}
#endif