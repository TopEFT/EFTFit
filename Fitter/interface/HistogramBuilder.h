#ifndef HISTOGRAMBUILDER_H_
#define HISTOGRAMBUILDER_H_

#include <string>
#include <vector>
#include <unordered_map>

#include "TString.h"
#include "TColor.h"
#include "TH1D.h"

#include "AnalysisCategory.h"

// Static class for building histograms from AnalysisCategory objects

class HistogramBuilder {
    public:
        HistogramBuilder();
        ~HistogramBuilder();

        TH1D* buildDataHistogram(TString title,std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels);
        TH1D* buildProcessHistogram(TString title, TString proc, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, std::unordered_map<std::string,Color_t> color_map);
        TH1D* buildSummedHistogram(TString name, TString title, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels);
};

HistogramBuilder::HistogramBuilder() {}
HistogramBuilder::~HistogramBuilder() {}

// For error bars see: https://twiki.cern.ch/twiki/bin/view/CMS/PoissonErrorBars
TH1D* HistogramBuilder::buildDataHistogram(TString title,std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels) {
    TString plot_title = TString::Format("%s;category;Events",title.Data());
    TH1D* h_data = new TH1D("data_yield",plot_title,cats.size(),0.0,cats.size());
    h_data->SetLineColor(1);
    h_data->SetLineWidth(2);
    h_data->SetMarkerStyle(20);
    h_data->SetMarkerSize(1.00);
    h_data->GetYaxis()->SetTitleSize(0.05);
    h_data->GetYaxis()->SetTitleOffset(1.1);
    h_data->GetYaxis()->SetLabelSize(0.05);
    h_data->Sumw2(kFALSE);
    // Fill and label the data histogram
    for (uint i = 0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        int bin_idx = i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        double bin_val = cat->getData();
        h_data->SetBinContent(bin_idx,bin_val);
        TString bin_label = cat->getName();
        if (bin_labels.count(bin_label.Data())) {
            bin_label = bin_labels[bin_label.Data()];
        }
        h_data->GetXaxis()->SetBinLabel(bin_idx,bin_label);
    }
    h_data->SetBinErrorOption(TH1::kPoisson);

    return h_data;
}

// Turns a vector of AnalysisCategory objects into a histogram for a particular process with one bin per category
TH1D* HistogramBuilder::buildProcessHistogram(TString title, TString proc, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, std::unordered_map<std::string,Color_t> color_map) {
    TString plot_title = TString::Format("%s;category;Events",proc.Data());
    // TH1D* h = new TH1D(proc+"_yield",plot_title,cats.size(),0.0,1.0);
    TString hname = TString::Format("%s_%s_yield",title.Data(),proc.Data());
    TH1D* h = new TH1D(hname,plot_title,cats.size(),0.0,cats.size());
    h->GetYaxis()->SetTitleSize(0.05);
    h->GetYaxis()->SetTitleOffset(1.1);
    h->GetYaxis()->SetLabelSize(0.05);

    Color_t h_clr = kBlack;
    if (color_map.count(proc.Data())) {
        h_clr = color_map[proc.Data()];
    }

    h->SetFillColor(h_clr);
    h->SetLineColor(kBlack);
    h->SetLineWidth(1);

    // Fill and label the histogram
    for (uint i = 0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        int bin_idx = i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        TString bin_label = cat->getName();
        if (bin_labels.count(bin_label.Data())) {
            bin_label = bin_labels[bin_label.Data()];
        }
        h->GetXaxis()->SetBinLabel(bin_idx,bin_label);
        if (cat->hasProc(proc)) {
            h->SetBinContent(bin_idx,cat->getExpProc(proc));
        } else {
            h->SetBinContent(bin_idx,0.0);
        }
    }
    return h;
}

// Returns a histogram built from the vector of categories, summed over all processes
TH1D* HistogramBuilder::buildSummedHistogram(TString name, TString title, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels) {
    TH1D* h = new TH1D(name,title,cats.size(),0.0,cats.size());
    h->SetFillColor(0);
    h->SetLineWidth(1);
    // Fill and label the histogram
    for (uint i = 0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        int bin_idx = i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        TString bin_label = cat->getName();
        if (bin_labels.count(bin_label.Data())) {
            bin_label = bin_labels[bin_label.Data()];
        }
        h->GetXaxis()->SetBinLabel(bin_idx,bin_label);
        h->SetBinContent(bin_idx,cat->getExpSum());
    }
    return h;
}

#endif
/* HISTOGRAMBUILDER_H_ */