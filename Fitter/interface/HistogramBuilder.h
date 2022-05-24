#ifndef HISTOGRAMBUILDER_H_
#define HISTOGRAMBUILDER_H_

#include <string>
#include <vector>
#include <unordered_map>

#include "TString.h"
#include "TColor.h"
#include "TH1D.h"
#include "RooFitResult.h"

#include "AnalysisCategory.h"

int bin_size = 4; // Number of bins for the differnetial distributions

// Container for info found by the 'get_extremum_fitresult' function from a particular AnalysisCategory
// TODO: I don't know if this struct def should go here or somewhere else
struct ExtremumPoint {
    // Note: Each element in every vector corresponds to a process and the ordering for every vector
    //       should be identical (at least for a given ExtremumPoint)
    TString cat_name;
    TString wc_name;
    std::vector<TString> procs;
    std::vector<TString> lo_fnames;
    std::vector<TString> hi_fnames;
    std::vector<TString> lo_snps;   // The RooWorkspace snapshot names
    std::vector<TString> hi_snps;   // The RooWorkspace snapshot names
    std::vector<double> lo_ylds;    // The actual bin yields
    std::vector<double> hi_ylds;    // The actual bin yields
    std::vector<double> lo_vals;    // The WC values
    std::vector<double> hi_vals;    // The WC values

    // Special data members for holding information related to the sum of processes
    TString sum_lo_fname;
    TString sum_hi_fname;
    TString sum_lo_snp;
    TString sum_hi_snp;
    double sum_lo_yld;
    double sum_hi_yld;
    double sum_lo_val;
    double sum_hi_val;

    // This is bonus stuff to aid the making of the ratio fluct plots
    TString nom_snp;    // The snapshot name for the nominal point
    TString base_snp;   // The snapshot name for the base point
    std::vector<double> nom_ylds;   // The nominal bin yields
    std::vector<double> base_ylds;  // The base bin yields, i.e. the divisor for the ratio calculation
};

// (Static?) class for building histograms from AnalysisCategory objects
class HistogramBuilder {
    public:
        HistogramBuilder();
        ~HistogramBuilder();

        TH1D* buildDataHistogram(TString title,std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels);
        TH1D* buildDataDifferentialHistogram(TString title,std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels);
        TH1D* buildProcessHistogram(TString title, TString proc, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, std::unordered_map<std::string,Color_t> color_map);
        TH1D* buildProcessDifferentialHistogram(TString title, TString proc, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, std::unordered_map<std::string,Color_t> color_map);
        // TH1D* buildSummedHistogram(TString name, TString title, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels);
        TH1D* buildSummedHistogram(TString name, TString title, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, RooFitResult* fr=0);
        TH1D* buildSummedDifferentialHistogram(TString name, TString title, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, RooFitResult* fr=0);
        TH1D* buildExtremumHistogram(TString title, TString proc, std::vector<ExtremumPoint> pts, TString pt_type, std::unordered_map<std::string,std::string> bin_labels, std::unordered_map<std::string,Color_t> color_map);
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

TH1D* HistogramBuilder::buildDataDifferentialHistogram(TString title,std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels) {
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
        TString bin_label = cat->getName();
        if (bin_labels.count(bin_label.Data())) {
            bin_label = bin_labels[bin_label.Data()];
        }
        int cat_idx = bin_size * i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        h_data->GetXaxis()->SetBinLabel(cat_idx, bin_label);
        for (uint bin_idx = 0; bin_idx < bin_size; bin_idx++) {
            double bin_val = cat->getDataBin(bin_idx);
            h_data->SetBinContent( cat_idx + bin_idx, bin_val);
        }
        h_data->SetBinErrorOption(TH1::kPoisson);
    }
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

// Turns a vector of AnalysisCategory objects into a histogram for a particular process with four bins per category
TH1D* HistogramBuilder::buildProcessDifferentialHistogram(TString title, TString proc, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, std::unordered_map<std::string,Color_t> color_map) {
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
        int cat_idx = bin_size * i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        TString bin_label = cat->getName();
        if (bin_labels.count(bin_label.Data())) {
            bin_label = bin_labels[bin_label.Data()];
        }
        h->GetXaxis()->SetBinLabel(cat_idx, bin_label);
        for (uint bin_idx = 0; bin_idx < bin_size; bin_idx++) {
            if (cat->hasProc(proc)) {
                h->SetBinContent( cat_idx + bin_idx, cat->getExpProcBin(proc, bin_idx));
            } else {
                h->SetBinContent( cat_idx + bin_idx, 0.0);
            }
        }
    }
    return h;
}

// Returns a histogram built from the vector of categories, summed over all processes
// TH1D* HistogramBuilder::buildSummedHistogram(TString name, TString title, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels) {
TH1D* HistogramBuilder::buildSummedHistogram(TString name, TString title, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, RooFitResult* fr=0) {
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

        if (fr) {
            h->SetBinError(bin_idx,cat->getExpSumError(fr));
        }
    }
    return h;
}

// Returns a differential histogram built from the vector of categories, summed over all processes
TH1D* HistogramBuilder::buildSummedDifferentialHistogram(TString name, TString title, std::vector<AnalysisCategory*> cats, std::unordered_map<std::string,std::string> bin_labels, RooFitResult* fr=0) {
    TH1D* h = new TH1D(name,title,cats.size(),0.0,cats.size());
    h->SetFillColor(0);
    h->SetLineWidth(1);
    // Fill and label the histogram
    for (uint i = 0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        int cat_idx = bin_size * i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        TString bin_label = cat->getName();
        if (bin_labels.count(bin_label.Data())) {
            bin_label = bin_labels[bin_label.Data()];
        }
        h->GetXaxis()->SetBinLabel(cat_idx, bin_label);
        for (uint bin_idx = 0; bin_idx < bin_size; bin_idx++) {
            h->SetBinContent( cat_idx + bin_idx, cat->getExpSumBin(bin_idx));
            if (fr) {
                h->SetBinError( cat_idx + bin_idx, cat->getExpSumErrorBin(bin_idx, fr));
            }
        }
    }
    return h;
}

// Turns a vector of ExtremumPoint structs into a histogram for a particular process
// Note: The histogram style here should attempt to be kept in sync with 'buildProcessHistogram'
TH1D* HistogramBuilder::buildExtremumHistogram(TString title, TString proc, std::vector<ExtremumPoint> pts, TString pt_type, std::unordered_map<std::string,std::string> bin_labels, std::unordered_map<std::string,Color_t> color_map) {
    bool valid_type = false;
    if (pt_type == "lo") {
        valid_type = true;
    } else if (pt_type == "hi") {
        valid_type = true;
    } else if (pt_type == "base") {
        valid_type = true;
    } else if (pt_type == "nom") {
        valid_type = true;
    }

    if (!valid_type) {
        std::cout << TString::Format("ERROR: Invalid point type passed to 'buildExtremumHistogram': %s",pt_type.Data()) << std::endl;
        return nullptr;
    }

    TString plot_title = TString::Format("%s;category;Events",proc.Data());
    TString hname = TString::Format("%s_%s_yield",title.Data(),proc.Data());
    TH1D* h = new TH1D(hname,plot_title,pts.size(),0.0,pts.size());
    h->GetYaxis()->SetTitleSize(0.05);
    h->GetYaxis()->SetTitleOffset(1.1);
    h->GetYaxis()->SetLabelSize(0.05);

    Color_t h_clr = kBlack;
    if (color_map.count(proc.Data())) {
        h_clr = color_map[proc.Data()];
    }
    // h->SetFillColor(h_clr);
    // h->SetLineColor(h_clr);
    // h->SetLineWidth(0);

    h->SetFillColor(h_clr);
    h->SetLineColor(kBlack);
    h->SetLineWidth(1);

    // Fill and label the histogram
    for (uint i = 0; i < pts.size(); i++) {
        ExtremumPoint pt = pts.at(i);
        int proc_idx = -1;
        for (uint j = 0; j < pt.procs.size(); j++) {
            if (proc == pt.procs.at(j)) {
                proc_idx = j;
                break;
            }
        }
        if (proc_idx == -1) {
            std::cout << TString::Format("ERROR: Unable to find process index of the ExtremumPoint") << std::endl;
            delete h;
            return nullptr;
        }
        int bin_idx = i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        TString bin_label = pt.cat_name;
        if (bin_labels.count(bin_label.Data())) {
            bin_label = bin_labels[bin_label.Data()];
        }
        h->GetXaxis()->SetBinLabel(bin_idx,bin_label);

        if (proc_idx != -1) {
            double bin_yld;
            if (pt_type == "lo") {
                bin_yld = pt.lo_ylds.at(proc_idx);
            } else if (pt_type == "hi") {
                bin_yld = pt.hi_ylds.at(proc_idx);
            } else if (pt_type == "base") {
                bin_yld = pt.base_ylds.at(proc_idx);
            } else if (pt_type == "nom") {
                bin_yld = pt.nom_ylds.at(proc_idx);
            }

            h->SetBinContent(bin_idx,bin_yld);
        } else {
            h->SetBinContent(bin_idx,0.0);
        }
    }
    return h;
}

#endif
/* HISTOGRAMBUILDER_H_ */