#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <unordered_map>
#include <utility>
#include <stdio.h>

#include "TString.h"
#include "TLatex.h"
#include "TLine.h"
#include "TArrow.h"
#include "TColor.h"
#include "TH1D.h"
#include "TPad.h"
#include "TAxis.h"
#include "TGraphErrors.h"
#include "TGraphAsymmErrors.h"
#include "TSystemDirectory.h"
#include "TList.h"
#include "TFile.h"
#include "TSystemFile.h"
#include "TCollection.h"
#include "TIterator.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "THStack.h"
#include "TMath.h"
#include "TStyle.h"

#include "RooFitResult.h"
#include "RooWorkspace.h"
#include "RooArgSet.h"
#include "RooAddition.h"
#include "RooCatType.h"
#include "RooRealVar.h"

#include "EFTFit/Fitter/interface/WSHelper.h"
#include "EFTFit/Fitter/interface/AnalysisCategory.h"
#include "EFTFit/Fitter/interface/CategoryManager.h"
#include "EFTFit/Fitter/interface/HistogramBuilder.h"
#include "EFTFit/Fitter/interface/utils.h"
#include "EFTFit/Fitter/interface/PlotData.h"
#include "EFTFit/Fitter/interface/PlotGroup.h"

typedef std::vector<TString> vTStr;
typedef std::vector<RooAddition*> vRooAdd;
typedef std::vector<RooCatType*> vRooCat;
typedef std::pair<TString,double> pTStrDbl;
typedef std::pair<TString,TString> pTStrTStr;
typedef std::unordered_map<std::string,double> umapStrDbl;

TString save_type1 = "png";
TString save_type2 = "eps";
TString save_type3 = "root";
TString save_type4 = "pdf";

// Change to include the processes that you want to plot
vTStr PLOT_PROCS {
    "charge_flips","fakes",
    "Diboson","Triboson",
    "convs","tWZ",
    "ttH","ttll","ttlnu","tllq","tHq","tttt"
};

// How to color code the processes
std::unordered_map<std::string,Color_t> PROCESS_COLOR_MAP {
    {"ttlnu",kBlue},
    {"ttll",kGreen+2},
    {"ttH",kRed+1},
    {"tllq",kPink+1},
    {"tHq",kCyan+1},
    {"tttt",kViolet-6},
    {"tWZ",kYellow+2},
    {"charge_flips",kAzure-9},
    {"fakes",kYellow-7},
    {"Diboson",kMagenta},
    {"Triboson",kSpring+1},
    {"convs",kOrange+1}
};

// What marker to use for each process
std::unordered_map<std::string,int> PROCESS_MARKER_MAP {
    {"ttlnu",kFullCircle},      // kFullCircle
    {"ttll",kFullSquare},       // kFullSquare
    {"ttH",kFullTriangleUp},  // kFullTriangleUp
    {"tllq",kFullTriangleDown}, // kFullTriangleDown
    {"tHq",kFullDiamond},   // kFullDiamond
    {"tttt",kFullStar},
    {"tWZ",kFullCross}
};

// What marker to use for each process
std::unordered_map<std::string,int> PROCESS_MARKER_SIZE_MAP {
    {"ttlnu",1},
    {"ttll" ,1},
    {"ttH"  ,2},
    {"tllq" ,2},
    {"tHq"  ,2},
    {"tttt" ,2},
    {"tWZ"  ,2},

    {"charge_flips",1},
    {"fakes",1},
    {"Diboson",1},
    {"Triboson",1},
    {"convs",1}
};

// How the processes should be labeled in the legend
std::unordered_map<std::string,std::string> PROCESS_LABEL_MAP {
    {"ttlnu","t#bar{t}l#nu"},
    {"ttll","t#bar{t}l#bar{l}"},
    {"tllq","tl#bar{l}q"},
    {"ttH","t#bar{t}H"},
    {"tHq","tHq"},
    {"tttt","t#bar{t}t#bar{t}"},
    {"tWZ","tWZ"},

    {"charge_flips","Charge misid."},
    {"fakes","Misid. leptons"},
    {"convs","Conv."}
};

// How the processes should be named in the latex yield table
std::unordered_map<std::string,std::string> YIELD_LABEL_MAP {
    {"ttH","\\ttH"},
    {"tHq","\\tHq"},
    {"ttll","\\ttll"},
    {"tllq","\\tllq"},
    {"ttlnu","\\ttlnu"},
    {"tttt","\\tttt"},
    {"tWZ","\\tWZ"},
    {"charge_flips","Charge Flips"},
    {"fakes","Fakes"},
    {"convs","Conversions"}
};

std::unordered_map<std::string,std::string> KIN_LABEL_MAP {
    {"lj0pt", "p_{\\text{T}}(\\ell\\text{j0}) \\: \\text{[100 GeV]}"},
    {"ptz",   "p_{\\text{T}}(\\text{Z}) \\: \\text{[100 GeV]}"},
    {"ptbl",  "p_{\\text{T}}(\\text{b}\\ell) \\: \\text{[GeV]}"},
    {"ht",    "H_{\\text{T}} \\: \\text{[100 GeV]}"},
    {"l0eta", "\\eta(\\ell\\text{0})"},
};

struct CMSTextStyle {
    TString cms_text;
    int cms_frame_loc;      // 0 - Out of frame top-left, 1 - In frame top-left
    int cms_align;
    float cms_size;
    float cms_font;
    float cms_offset;       // offset to position the extra text (e.g. "Supplementary")
    float cms_rel_posX;
    float cms_rel_posY;

    TString lumi_text_all;
    TString lumi_text_2017;
    int lumi_align;
    float lumi_size;
    float lumi_font;
    float lumi_offset; // Percentage of some margin (currently just top margin) to shift text

    TString extra_text;
    int extra_align;
    float extra_text_font;
    float extra_over_cms_text_size; // Ratio of "CMS" and extra text size

    TString arxiv_text;
    float arxiv_font;
    float arxiv_offset;

    CMSTextStyle() {
        cms_text = "CMS";
        cms_frame_loc = 0;
        cms_align = 11;
        cms_size = 0.75;
        cms_font = 61;
        cms_offset = 0.07;
        cms_rel_posX = 0.045;
        cms_rel_posY = 0.100;

        lumi_text_2017 = "41.5 fb^{-1} (13 TeV)";
        lumi_text_all = "138 fb^{-1} (13 TeV)";
        lumi_align = 31;
        lumi_size = 0.60;
        lumi_font = 42;
        lumi_offset = 0.20;

        extra_text = "";
        // extra_text = "Preliminary";
        extra_align = 11;
        extra_text_font = 52; // default is helvetica-italics
        extra_over_cms_text_size = 0.76;    // ratio of "CMS" and extra text size

        // arxiv_text = "arXiv:2012.04120";
        arxiv_text = "";
        arxiv_font = 42;
        arxiv_offset = 0.28;
    }
};

TGraphErrors* get_error_differential_graph(TH1D* base_hist, PlotData pData) {
    int pSize = pData.SR_name.size();
    TGraphErrors* gr_err = new TGraphErrors(base_hist);
    
    int bin_idx = 0;
    // Fill and label the data histogram
    for (TString SR: SR_list) {
        for (uint i = 0; i < pSize; i++) {
            if (SR.Data() != pData.SR_name[i]) continue;
            double x_val,y_val;
            double x_err,y_err;
            gr_err->GetPoint(bin_idx, x_val, y_val);
            y_val = pData.sum[i];
            x_err = gr_err->GetErrorX(bin_idx);
            y_err = pData.err[i];
            gr_err->SetPoint(bin_idx,x_val,y_val);
            gr_err->SetPointError(bin_idx,x_err,y_err);
            bin_idx++;
        }
    }

    gr_err->SetLineColor(kWhite);
    gr_err->SetFillStyle(3154);
    gr_err->SetFillColor(kBlack);
    return gr_err;
}

TH1D* make_ratio_histogram(TString name, TH1D* h1, TH1D* h2) {
    cout << "Making ratio plot for " << name.Data() << endl;
    if (h1->GetXaxis()->GetNbins() != h2->GetXaxis()->GetNbins()) {
        std::cout << "hist1 number of bins: " << h1->GetXaxis()->GetNbins() << std::endl;
        std::cout << "hist2 number of bins: " << h2->GetXaxis()->GetNbins() << std::endl;
        std::cout << "[Error] makeRatioHistogram() - bin mismatch between ratio of hists" << std::endl;
        throw;
    }
    TAxis* xaxis = h1->GetXaxis();
    int bins = xaxis->GetNbins();
    Double_t low = xaxis->GetXmin();
    Double_t high = xaxis->GetXmax();

    TAxis* yaxis = h1->GetYaxis();
    Double_t yaxis_sz = yaxis->GetLabelSize();
    TH1D* h_ratio = new TH1D(name,"",bins,low,high);
    h_ratio->GetYaxis()->SetLabelSize(yaxis_sz*1.5);
    h_ratio->GetXaxis()->SetLabelSize(yaxis_sz*2.5);
    
    for (int i = 1; i <= bins; i++) {
        TString bin_label = xaxis->GetBinLabel(i);
        if (bin_label.Length()) {
            h_ratio->GetXaxis()->SetBinLabel(i,bin_label);
        }
        double val1 = h1->GetBinContent(i);
        double err1 = h1->GetBinError(i);
        double val2 = h2->GetBinContent(i);
        double err2 = h2->GetBinError(i);

        double ratio;
        double ratio_err;
        if (val2 != 0) {
            ratio = abs(val1 / val2);
        } else if (val1 == 0 && val2 == 0) {
            ratio = 1.0;
        } else {
            ratio = -1;
        }
        if (h1->GetName() == h2->GetName()) {
            ratio_err = 0.001;    // Ignore the error for now (makes the y-axis errors tiny)
        } else {
            if (val1) ratio_err = err1 / val1;
            else ratio_err = 0;
        }
        h_ratio->SetBinContent(i,ratio);
        h_ratio->SetBinError(i,ratio_err);
    }
    h_ratio->GetYaxis()->SetRangeUser(0.0,2.0);// was 1.8
    h_ratio->GetYaxis()->SetNdivisions(205,kFALSE); // The kFALSE is important as otherwise it willn'optimize' the tick marks and likely just ignore w/e option you choose
    return h_ratio;
}

TGraphAsymmErrors* make_ratio_error_band(TH1D* h_data, TH1D* h_mc, TGraphErrors* err_mc) {
    TGraphAsymmErrors* gr_err = new TGraphAsymmErrors(h_mc);
    for (uint i = 0; i < gr_err->GetN(); i++) {
        int bin_idx = i + 1;
        double x_val, y_val;
        double err_up,err_lo;
        gr_err->GetPoint(i,x_val,y_val);    // GetPointX doesn't exist in ROOT 6.06
        double data_up = h_data->GetBinErrorUp(i);
        double data_down = h_data->GetBinErrorLow(i);
        double diff_up = err_mc->GetErrorY(i);
        double diff_down = err_mc->GetErrorY(i);
        
        err_up = diff_up;
        err_lo = diff_down;
        err_up = err_up / h_mc->GetBinContent(bin_idx);
        err_lo = err_lo / h_mc->GetBinContent(bin_idx);

        gr_err->SetPoint(i,x_val,1.0);
        gr_err->SetPointEYlow(i,err_lo);
        gr_err->SetPointEYhigh(i,err_up);
    }
    gr_err->SetLineColor(kWhite);
    gr_err->SetFillStyle(3154);
    gr_err->SetFillColor(kBlack);

    return gr_err;
}

void add_cms_text(TPad* pad, CMSTextStyle style, std::string year="all") {
    //////////////////////
    // Extract the style options
    //////////////////////
    TString cmsText     = style.cms_text;
    float cmsTextFont   = style.cms_font;  // default is helvetic-bold
    float cmsTextSize   = style.cms_size;
    int cmsAlign        = style.cms_align;
    int cms_frame_loc   = style.cms_frame_loc;

    TString extraText   = style.extra_text;
    float extraTextFont = style.extra_text_font;  // default is helvetica-italics
    int extraAlign      = style.extra_align;

    TString lumiText;
    if (year == "all")  lumiText = style.lumi_text_all;
    if (year == "2017") lumiText = style.lumi_text_2017;
    
    float lumiTextFont = style.lumi_font;
    float lumiTextSize = style.lumi_size;
    int lumiAlign = style.lumi_align;

    TString arxivText = style.arxiv_text;
    float arxivTextFont = style.arxiv_font;

    //////////////////////
    // text sizes and text offsets with respect to the top frame
    // in unit of the top margin size
    //////////////////////
    float lumiTextOffset = style.lumi_offset;   // Percentage of some margin (currently just top margin) to shift text

    //////////////////////
    // controls where the 'extraText' gets placed relative to 'cmsText'
    // also text sizes and text offsets with respect to frame margins
    // in unit of the margin size
    //////////////////////
    float relPosX = style.cms_rel_posX;
    float relPosY = style.cms_rel_posY;

    //////////////////////
    // ratio of "CMS" and extra text size
    //////////////////////
    float extraOverCmsTextSize = style.extra_over_cms_text_size;
    float extraTextSize = extraOverCmsTextSize*cmsTextSize;
    float arxivTextSize = extraTextSize*0.95;

    //////////////////////
    // Add the text
    //////////////////////

    UInt_t txt_ww = 0;
    UInt_t txt_hh = 0;

    float posX = 0.0;
    float posY = 0.0;

    double cms_ww = 0.0;
    double cms_hh = 0.0;

    double lumi_ww = 0.0;
    double lumi_hh = 0.0;

    float H = pad->GetWh(); // In pixels
    float W = pad->GetWw(); // In pixels
    float l = pad->GetLeftMargin();
    float t = pad->GetTopMargin();
    float r = pad->GetRightMargin();
    float b = pad->GetBottomMargin();

    float fr_w = 1-l-r; // frame width
    float fr_h = 1-t-b; // frame height

    pad->cd();

    TLatex latex;
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(kBlack);

    //////////////////////
    // Draw the lumi text
    //////////////////////
    posX = 1-r;
    posY = 1-t+lumiTextOffset*t;
    latex.SetTextFont(lumiTextFont);
    latex.SetTextAlign(lumiAlign);
    latex.SetTextSize(lumiTextSize*t);
    // std::cout << TString::Format("lumiText:  (%.2f,%.2f), Size: %.2f",posX,posY,lumiTextSize*t) << std::endl;
    TLatex* lumi_latex = latex.DrawLatex(posX,posY,lumiText);
    lumi_latex->GetBoundingBox(txt_ww,txt_hh);
    lumi_ww = txt_ww / W;
    lumi_hh = txt_hh / H;

    //////////////////////
    // Draw the CMS text
    //////////////////////

    //////////////////////
    // Out of frame top-left
    //////////////////////
    if (cms_frame_loc == 0) {    
        posX  = l + 0.01*fr_w;
        posY  = 1 - t + lumiTextOffset*t;
        cmsAlign = 11;
    }

    //////////////////////
    // In frame top-left
    //////////////////////
    if (cms_frame_loc == 1) {
        posX = l + relPosX*fr_w;
        posY = 1 - t - relPosY*fr_h;
        cmsAlign = 11;
    }
    latex.SetTextFont(cmsTextFont);
    latex.SetTextAlign(cmsAlign); 
    latex.SetTextSize(cmsTextSize*t);

    // std::cout << TString::Format("cmsText: %s",cmsText.Data()) << std::endl;
    // std::cout << TString::Format("cmsText:   (%.2f,%.2f), Size: %.2f",posX,posY,cmsTextSize*t) << std::endl;
    TLatex* cms_latex = latex.DrawLatex(posX,posY,cmsText);
    cms_latex->GetBoundingBox(txt_ww,txt_hh);
    cms_ww = txt_ww / W;
    cms_hh = txt_hh / H;


    //////////////////////
    // Draw the extra text (i.e. 'Preliminary')
    //////////////////////

    //////////////////////
    // Out of frame
    //////////////////////
    if (cms_frame_loc == 0) {    
        posX = l + 0.01*fr_w + cms_ww + (25.0 / W);
        posY = 1 - t + lumiTextOffset*t;
    }

    //////////////////////
    // In frame and inline with "CMS" text
    //////////////////////
    if (cms_frame_loc == 1) {
        posX = l + relPosX*fr_w + cms_ww + (25.0 / W);
        posY = 1 - t - relPosY*fr_h;
    }


    latex.SetTextFont(extraTextFont);
    latex.SetTextSize(extraTextSize*t);
    latex.SetTextAlign(extraAlign);
    // std::cout << TString::Format("extraText: (%.2f,%.2f)",posX,posY) << std::endl;
    latex.DrawLatex(posX,posY,extraText);

    //////////////////////
    // Add in the arXiv number text
    //////////////////////
    // if (strncmp(extraText.Data(),"Supplementary",extraText.Length()) == 0) {
    if (extraText.EqualTo("Supplementary")) {
        posX = 1 - r - lumi_ww - (25.0 / W);
        posY = 1 - t + lumiTextOffset*t;
        latex.SetTextFont(arxivTextFont);
        latex.SetTextSize(arxivTextSize*t);
        latex.SetTextAlign(lumiAlign);
        latex.DrawLatex(posX,posY,arxivText);
    }

    return;
}

// This might end up being a bad idea, if we can't make a 'one size fits all' external legend for some reason
void make_external_legend(TLegend* leg, TString title) {
    int n_entries = leg->GetListOfPrimitives()->GetEntries();

    TCanvas* ext_canv;
    int ww; // the canvas size in pixels along X
    int wh; // the canvas size in pixels along Y

    double txt_sz;

    int max_cols = 7;
    int cols = std::min(n_entries,max_cols);

    // This monstrosity calculates the number of rows in the legend
    int n_rows = (n_entries / max_cols) + int(n_entries % max_cols != 0);
    n_rows = std::max(1,n_rows);

    // std::cout << "n_rows: " << n_rows << std::endl;

    // ww = std::min(max_cols,n_entries)*125;  // At 6 cols should be 750
    // wh = n_rows*50;                         // At 2 rows should be 100
    // txt_sz = 0.500 / n_rows;                // At 2 rows should be 0.250

    ww = 750;                                   // At 6 cols should be 750
    // ww = 400;                              // Width for the signal fluctuation plots
    wh = 30 + n_rows*35;                        // At 2 rows should be 0.250
    txt_sz = 0.666 / std::pow(n_rows,1.414);    // At 2 rows should be 0.250

    // TCanvas* ext_canv = new TCanvas("ext_canv","ext_canv",150,10,960,320);
    // TCanvas* ext_canv = new TCanvas("ext_canv","ext_canv",150,10,960,150);
    // TCanvas* ext_canv = new TCanvas("ext_canv","ext_canv",150,10,600,150);
    // TCanvas* ext_canv = new TCanvas("ext_canv","ext_canv",150,10,750,100);
    ext_canv = new TCanvas("ext_canv","ext_canv",150,10,ww,wh);
    ext_canv->cd();


    // Default (x1,y1,x2,y2): (0.14,0.75,0.94,0.89)
    leg->SetX1(0.05); leg->SetY1(0.05);
    leg->SetX2(0.95); leg->SetY2(0.95);

    // leg->SetX1(0.15); leg->SetY1(0.05);
    // leg->SetX2(0.85); leg->SetY2(0.95);

    leg->SetFillColor(kWhite);
    leg->SetLineColor(kWhite);
    leg->SetShadowColor(kWhite);
    leg->SetTextFont(42);   // The 'ones' digit determines Text size precison
    // leg->SetTextFont(43);   // The 'ones' digit determines Text size precison

    // leg->SetTextSize(0.250);
    leg->SetTextSize(txt_sz); // Size for prec. = 2 font
    // leg->SetTextSize(25);   // Size for prec. = 3 font

    // std::cout << "n_entries: " << n_entries << std::endl;


    if (n_entries < max_cols) {
        leg->SetNColumns(n_entries);
        leg->SetColumnSeparation(0.45);  // looks pretty decent with 750 canvas width 5 cols and 1 row
    } else {
        leg->SetNColumns(max_cols);
    }

    leg->Draw();

    
    TString save_format;
    TString save_name;

    // save_format = "png";
    // save_name = TString::Format("%s.%s",title.Data(),save_format.Data());
    // ext_canv->Print(save_name,save_format);

    // save_format = "eps";
    // save_name = TString::Format("%s.%s",title.Data(),save_format.Data());
    // ext_canv->Print(save_name,save_format);

    save_name = TString::Format("%s%s.%s","plots/",title.Data(),save_type1.Data());
    ext_canv->Print(save_name,save_type1);

    save_name = TString::Format("%s%s.%s","plots/",title.Data(),save_type2.Data());
    ext_canv->Print(save_name,save_type2);

    // save_name = TString::Format("%s%s.%s","plots/",title.Data(),save_type4.Data());
    // ext_canv->Print(save_name,save_type4);

    delete ext_canv;
}

void draw_lines(
    PlotData pData,
    PlotGroup pGroup,
    double L_margin,
    double R_margin,
    bool draw_line = true,
    double text_size = 0.04
) {
    for (uint idx=0; idx < pGroup.gname.size(); idx++) {
        double x1,x2,y1,y2;
        Int_t bin_idx = 0;
        for (uint i=0; i < idx+1; i++) {
            if (i == pGroup.gname.size()-1) {
                draw_line = false;
            }
            bin_idx += pGroup.gbins[i];
        }
        double bin_width = (1.0 - L_margin - R_margin) / pData.SR_name.size();

        x1 = L_margin + bin_width*bin_idx;
        x2 = L_margin + bin_width*bin_idx;

        if (draw_line) {
            y1 = 0.03;
            y2 = 0.85;
            TLine* line1 = new TLine(x1,y1,x2,y2);
            line1->SetLineStyle(9);
            line1->Draw();
        }

        x1 = (L_margin + bin_width*bin_idx) - bin_width*pGroup.gbins[idx]/2.0;
        y1 = 0.050;
        TLatex* axis_latex;
                
        UInt_t w,h;

        if(pGroup.gtxt1.size()) {
            TLatex *TL1 = new TLatex(0,0,pGroup.gtxt1[idx].c_str());
            TL1->GetTextExtent(w,h,pGroup.gtxt1[idx].c_str());
            axis_latex = new TLatex(x1, y1, pGroup.gtxt1[idx].c_str());
        }
        if(pGroup.gtxt2.size()) {
            TLatex *TL2 = new TLatex(0,0,pGroup.gtxt2[idx].c_str());
            TL2->GetTextExtent(w,h,pGroup.gtxt2[idx].c_str());
            axis_latex = new TLatex(x1, y1, pGroup.gtxt2[idx].c_str());
        }
        axis_latex->SetTextSize(text_size);
        if(pGroup.gtxt1.size()) {
            if(pGroup.gtxt1[idx].find("2j3j")!=-1 | pGroup.gtxt1[idx].find("4j5j")!=-1) {
                axis_latex->SetTextSize(text_size*1.35); // Apply a 1.35 multiplier on the size for two-line categories 3l onZ 1b 2j3j and 4j5j
            }
        }
        axis_latex->SetTextAlign(22); // center+center aligned
        axis_latex->SetTextFont(62);
        axis_latex->Draw();
    }
}

void draw_labels (
    std::vector<TString> labels,
    PlotData pData,
    double L_margin,
    double R_margin,
    double text_size = 0.05
) {

    if ((pData.SR_name.size()%labels.size()) != 0) {
        std::cout << "[WARNING]Unmatching bin size for channel " << pData.SR_name.at(0) << ". Ignoring labels." << std::endl;
        return;
    }

    double bin_width = (1.0 - L_margin - R_margin) / pData.SR_name.size();
    for (uint idx=0; idx < pData.SR_name.size(); idx++) {

        double x = L_margin + bin_width*idx;
        double y = 0.09;
        TString label = labels[idx%(labels.size())];

        if (label.Index("-1") == TString::kNPOS) {
            TLatex *label_latex = new TLatex(x, y, label);
            label_latex->SetTextAlign(23); // middle+top adjusted
            label_latex->SetTextSize(text_size);
            label_latex->SetTextFont(42);
            label_latex->Draw();
        }

        if (idx && (idx%(labels.size()) == 0) ) {
            double y1 = 0.35;
            double y2 = 0.93;
            TLine* line1 = new TLine(x,y1,x,y2);
            line1->SetLineStyle(9);
            line1->Draw();

            double y3 = 0.10;
            double y4 = 0.28;
            TLine* line2 = new TLine(x,y3,x,y4);
            line2->SetLineStyle(9);
            line2->Draw();
        }
    }
}

void make_overlay_njet_plot(
    TString title,
    std::vector<TLatex*> extra_text,
    PlotData pData,
    PlotGroup pGroup,
    bool incl_ratio,
    bool incl_leg,
    bool ext_leg,
    CMSTextStyle cms_style,
    TString xtitle=""
) {
    bool debug = false;
    int pSize = pData.SR_name.size();

    // Some configuration settings
    Float_t small = 1.e-5;
    const float padding = 1e-5;
    const float xpad = small;   // Pad spacing left to right
    const float ypad = small;   // Pad spacing top to bottom
    const float ygap = 0.11;    // Gap between the main plot and ratio plot
    const float ydiv = 0.3;     // Height of the second pad when making plots with ratios

    HistogramBuilder builder = HistogramBuilder();

    int c_hh = 640;
    int c_ww = 1920;

    TCanvas* c = new TCanvas("canv","canv",150,10,c_ww,c_hh);
    // TCanvas* c = new TCanvas("canv","canv",150,10,960*4,640);
    TLegend *leg = new TLegend(0.14,0.75,0.94,0.89);
    THStack *hs = new THStack("hs_category_yield","");

    std::vector<TH1D*> proc_hists;
    TH1D* h_data = builder.buildDataDifferentialHistogram(title,pData,BIN_LABEL_MAP);
    h_data->SetLineWidth(1); // Try a thiner line for the full njet histogram PDFs

    for (TString proc_name: PLOT_PROCS) {
        if (debug) std::cout << "DEBUG: Getting process histogram for " << proc_name << std::endl;
        TH1D* h_proc = builder.buildProcessDifferentialHistogram(title,proc_name,pData,BIN_LABEL_MAP,PROCESS_COLOR_MAP);
        if (debug) std::cout << "DEBUG: Adding process histogram to legend: " << proc_name << std::endl;
        TString legend_name = proc_name;
        if (PROCESS_LABEL_MAP.count(proc_name.Data())) {
            legend_name = PROCESS_LABEL_MAP[proc_name.Data()];
        }
        if (incl_ratio) {
            // Hide the x-axis labels for the stack plot
            // Note: For some reason this can't be done using the THStack histogram
            for (int i=1; i <= h_proc->GetXaxis()->GetNbins(); i++) {
                h_proc->GetXaxis()->SetBinLabel(i,"");
            }
        }
        leg->AddEntry(h_proc,legend_name,"f");
        proc_hists.push_back(h_proc);
    }

    // for (TH1D* h: overlay_hists) {
    //     leg->AddEntry(h,h->GetTitle(),"f");
    // }

    for (TH1D* h: proc_hists) {
        if (debug) std::cout << "DEBUG: Adding histogram to stack: " << h->GetName() << std::endl;
        hs->Add(h);
    }

    // hs->SetTitle(";Category;Events");
    if (incl_ratio) {
        hs->SetTitle(";;Events");
    } else {
        hs->SetTitle(TString::Format(";%s;Events",xtitle.Data()));
    }

    TH1D* h_exp_sum = builder.buildSummedDifferentialHistogram("expected_sum","",pData,BIN_LABEL_MAP);
    TGraphErrors* gr_err = get_error_differential_graph(h_exp_sum,pData);

    leg->AddEntry(gr_err,"Total unc.","f");
    leg->AddEntry(h_data,"Obs.","lp");

    TH1D* h_ratio;
    TH1D* h_ratio_base;
    TGraphAsymmErrors* h_ratio_band;
    if (incl_ratio) {
        TString ratio_name = "r_" + title;
        h_ratio = make_ratio_histogram(ratio_name,h_data,h_exp_sum);
        h_ratio_base = make_ratio_histogram("r_base",h_data,h_data);
        h_ratio_band = make_ratio_error_band(h_data,h_exp_sum,gr_err);

        h_ratio->SetLineColor(kBlack);
        h_ratio->SetMarkerStyle(20);
        h_ratio->SetMarkerSize(0.75);
        h_ratio->GetYaxis()->SetTitleSize(0.1);
        h_ratio->GetYaxis()->SetTitleOffset(0.25);

        h_ratio_base->SetLineColor(kBlack);
        h_ratio_base->SetLineWidth(1);
        h_ratio_base->SetLineStyle(3);
        // h_ratio_base->GetYaxis()->SetRangeUser(0.2,1.8);
        // h_ratio_base->GetYaxis()->SetRangeUser(0.4,1.6);    // Range for nuisfit ratio as per ARC request
        h_ratio_base->GetYaxis()->SetRangeUser(0.0,2.0);    // Range for 35 bin njets histogram as per ARC request
        h_ratio_base->GetYaxis()->SetNdivisions(204,kFALSE);

        // h_ratio_base->GetXaxis()->SetLabelSize(0.230);//0.230
        // h_ratio_base->GetXaxis()->SetLabelOffset(0.020);  // Default is 0.005
        h_ratio_base->GetXaxis()->SetLabelSize(0.270);//0.230
        h_ratio_base->GetXaxis()->SetLabelOffset(0.040);  // Default is 0.005
        if (pSize > 36) {
            h_ratio_base->GetXaxis()->SetLabelSize(0.200);
            h_ratio_base->GetXaxis()->SetLabelOffset(0.015);
        }

        // h_ratio_base->SetTitle(TString::Format(";%s;#frac{Data}{Pred}",xtitle.Data()));
        // h_ratio_base->GetYaxis()->SetTitleSize(0.150);
        // h_ratio_base->GetYaxis()->SetTitleOffset(0.300);  // Default is 1.0
        h_ratio_base->SetTitle(TString::Format(";%s;Obs. / pred.",xtitle.Data()));
        h_ratio_base->GetYaxis()->SetTitleSize(0.180);
        h_ratio_base->GetYaxis()->SetTitleOffset(0.220);  // Default is 1.0
        h_ratio_base->GetYaxis()->SetLabelSize(0.163);// 0.140
        if (pSize > 36) {
            h_ratio_base->GetYaxis()->SetTitleSize(0.180);
            h_ratio_base->GetYaxis()->SetTitleOffset(0.130);
            h_ratio_base->GetYaxis()->SetLabelSize(0.163);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Actual plotting and Drawing section
    ////////////////////////////////////////////////////////////////////////////////////////////////

    if (debug) std::cout << "DEBUG: Edit canvas object" << std::endl;
    gStyle->SetPadBorderMode(0);
    gStyle->SetFrameBorderMode(0);
    gStyle->SetOptStat(0); // don't display entries, mean or RMS.

    float L = xpad;
    float B = ypad;
    float R = 1-xpad;
    float T = 1-ypad;
    double L_margin = 105.6 / c->GetWw();   // Targets 0.11 at 960 width
    double R_margin =  24.0 / c->GetWw();   // Targets 0.025 at 960 width
    if (incl_ratio) {
        c->Divide(1,2,small,small);
        c->GetPad(1)->SetPad(L,B+ydiv,R,T); // Order: (L B R T)
        c->GetPad(1)->SetLeftMargin(L_margin);
        c->GetPad(1)->SetRightMargin(R_margin);//0.05
        c->GetPad(1)->SetBottomMargin(ygap / 2);
        c->GetPad(1)->Modified();

        c->GetPad(2)->SetPad(L,B,R,ydiv);   // Order: (L B R T)
        c->GetPad(2)->SetTopMargin(ygap / 2);
        c->GetPad(2)->SetLeftMargin(L_margin);
        c->GetPad(2)->SetRightMargin(R_margin);//0.05
        c->GetPad(2)->SetBottomMargin(0.333);//0.3
        c->GetPad(2)->SetGrid(0,1);
        c->GetPad(2)->SetTickx();
        c->GetPad(2)->Modified();
    } else {
        c->Divide(1,1,small,small);
        c->GetPad(1)->SetGrid(0,0);
        c->GetPad(1)->SetLeftMargin(.11);
        c->GetPad(1)->SetRightMargin(.05);
        c->GetPad(1)->SetBottomMargin(.1);

        c->GetPad(1)->SetBottomMargin(.1);
        c->GetPad(1)->Modified();
        c->cd(1);
        gPad->Modified();
    }

    if (debug) std::cout << "DEBUG: Edit legend object" << std::endl;
    leg->SetFillColor(kWhite);
    leg->SetLineColor(kWhite);
    leg->SetShadowColor(kWhite);
    leg->SetTextFont(42);
    leg->SetTextSize(0.035);
    leg->SetNColumns(5);

    if (debug) std::cout << "DEBUG: Making the Latex object" << std::endl;

    // c->cd();
    c->cd(1);

    int max_bin;
    double hmax,max_val,bin_err;

    hmax = 0.0;
    max_bin = h_data->GetMaximumBin();
    max_val = h_data->GetBinContent(max_bin);
    bin_err = h_data->GetBinErrorUp(max_bin);
    hmax = TMath::Max(max_val+bin_err,hmax);

    max_val = hs->GetMaximum();
    hmax = TMath::Max(max_val,hmax);

    // for (TH1D* h: overlay_hists) {
    //     max_bin = h->GetMaximumBin();
    //     max_val = h->GetBinContent(max_bin);
    //     hmax = TMath::Max(max_val,hmax);
    // }

    if (incl_leg) {
        h_data->SetMaximum(hmax*1.5);
        hs->SetMaximum(hmax*1.5);

    } else {
        h_data->SetMaximum(hmax*1.01);
        hs->SetMaximum(hmax*1.01);
        // Uncomment below to fix y-axis scale
        // h_data->SetMaximum(600);
        // hs->SetMaximum(600);
    }

    if (incl_ratio) {
        // hs->SetMinimum(0.01);   // This will avoid drawing the 0 on the y-axis
        hs->SetMinimum(0.0);
    } else {
        hs->SetMinimum(0.0);
        h_data->SetMinimum(0.0);
    }

    if (debug) std::cout << "DEBUG: Drawing stuff" << std::endl;

    hs->Draw("hist");   // draws the stacked histogram
    // h_exp_sum->Draw("hist"); // draws the summed histogram (no process samples shown)

    // h_exp_sum->Draw("same,e");
    if (incl_leg) leg->Draw();
    extra_text.at(0)->Draw();

    h_data->Draw("same,e,p");
    gr_err->Draw("same,2");
    // for (TH1D* h: overlay_hists) h->Draw("same,hist");
    
    add_cms_text((TPad*)c->GetPad(1),cms_style);
    if (incl_ratio) {
        c->cd(1);

        hs->GetYaxis()->SetTitleSize(0.08);
        hs->GetYaxis()->SetTitleOffset(0.63);
        hs->GetYaxis()->SetLabelSize(0.070);
        if (pSize > 36) {
            hs->GetYaxis()->SetTitleSize(0.08);
            hs->GetYaxis()->SetTitleOffset(0.30);
            hs->GetYaxis()->SetLabelSize(0.070);
        }

        c->cd(2);

        h_ratio_base->Draw();
        h_ratio_band->Draw("same,2");
        h_ratio->Draw("same,e,p");

        // The x-axis labeling is determined by the ratio plot
        // if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
        //     h_ratio->GetXaxis()->SetLabelSize(0.250);
        // }
        c->GetPad(1)->RedrawAxis();
        c->GetPad(2)->RedrawAxis();
        
    } else {
        hs->GetXaxis()->SetLabelFont(42);   //Default: 62
        if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
            hs->GetXaxis()->SetLabelSize(0.05); //Default: 0.04
        } else {
            hs->GetXaxis()->SetLabelSize(0.04); //Default: 0.04
        }

        c->GetPad(1)->RedrawAxis();
    }

    c->cd();
    draw_lines(pData, pGroup, L_margin, R_margin);

    TString save_format, save_name;

    // save_format = "png";
    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_format.Data());
    // c->Print(save_name,save_format);

    save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type1.Data());
    c->Print(save_name,save_type1);

    // save_format = "pdf";
    // save_format = "eps";
    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_format.Data());
    // c->Print(save_name,save_format);

    save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type2.Data());
    c->Print(save_name,save_type2);

    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type4.Data());
    // c->Print(save_name,save_type4);

    // Print an external legend
    if (ext_leg) {
        // save_name = TString::Format("ext_leg_%s",title.Data());
        save_name = TString::Format("ext_leg_ylds");
        make_external_legend(leg,save_name);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Clean up section
    ////////////////////////////////////////////////////////////////////////////////////////////////
    delete c;
    delete h_data;
    // delete CMSInfoLatex;
    delete leg;
    delete hs;
    delete gr_err;
    delete h_exp_sum;
    for (TH1D* h: proc_hists) {
        delete h;
    }
    if (incl_ratio) {
        delete h_ratio;
        delete h_ratio_base;
        delete h_ratio_band;
    }
    return;
}

void make_overlay_sum_plot(
    TString title,
    std::vector<TLatex*> extra_text,
    PlotData pData,
    PlotGroup pGroup,
    bool incl_ratio,
    bool incl_leg,
    bool ext_leg,
    CMSTextStyle cms_style,
    TString xtitle=""
) {
    bool debug = false;
    int pSize = pData.SR_name.size();

    // Some configuration settings
    Float_t small = 1.e-5;
    const float padding = 1e-5;
    const float xpad = small;   // Pad spacing left to right
    const float ypad = small;   // Pad spacing top to bottom
    const float ygap = 0.11;    // Gap between the main plot and ratio plot
    const float ydiv = 0.3;     // Height of the second pad when making plots with ratios

    HistogramBuilder builder = HistogramBuilder();

    int c_hh = 640;
    int c_ww = 960;

    TCanvas* c = new TCanvas("canv","canv",150,10,c_ww,c_hh);
    // TCanvas* c = new TCanvas("canv","canv",150,10,960*4,640);
    TLegend *leg = new TLegend(0.14,0.75,0.94,0.89);
    THStack *hs = new THStack("hs_category_yield","");

    std::vector<TH1D*> proc_hists;
    TH1D* h_data = builder.buildDataDifferentialHistogram(title,pData,BIN_LABEL_MAP);
    h_data->SetLineWidth(1); // Try a thiner line for the full njet histogram PDFs
    
    //PLOT_PROCS = {"charge_flips","fakes","Diboson","Triboson","convs","ttH","ttll","ttlnu","tllq","tHq","tttt"}; // This is odd, why this vector imported from PlotData.h is empty?
    //cout << "Adding processes....... " << PLOT_PROCS.size() << endl;

    for (TString proc_name: PLOT_PROCS) {
        if (debug) std::cout << "DEBUG: Getting process histogram for " << proc_name << std::endl;
        TH1D* h_proc = builder.buildProcessDifferentialHistogram(title,proc_name,pData,BIN_LABEL_MAP,PROCESS_COLOR_MAP);
        if (debug) std::cout << "DEBUG: Adding process histogram to legend: " << proc_name << std::endl;
        TString legend_name = proc_name;
        if (PROCESS_LABEL_MAP.count(proc_name.Data())) {
            legend_name = PROCESS_LABEL_MAP[proc_name.Data()];
        }
        if (incl_ratio) {
            // Hide the x-axis labels for the stack plot
            // Note: For some reason this can't be done using the THStack histogram
            for (int i=1; i <= h_proc->GetXaxis()->GetNbins(); i++) {
                h_proc->GetXaxis()->SetBinLabel(i,"");
            }
        }
        leg->AddEntry(h_proc,legend_name,"f");
        proc_hists.push_back(h_proc);
    }

    // for (TH1D* h: overlay_hists) {
    //     leg->AddEntry(h,h->GetTitle(),"f");
    // }

    for (TH1D* h: proc_hists) {
        if (debug) std::cout << "DEBUG: Adding histogram to stack: " << h->GetName() << std::endl;
        hs->Add(h);
    }

    // hs->SetTitle(";Category;Events");
    if (incl_ratio) {
        hs->SetTitle(";;Events");
    } else {
        hs->SetTitle(TString::Format(";%s;Events",xtitle.Data()));
    }

    TH1D* h_exp_sum = builder.buildSummedDifferentialHistogram("expected_sum","",pData,BIN_LABEL_MAP);
    TGraphErrors* gr_err = get_error_differential_graph(h_exp_sum,pData);

    leg->AddEntry(gr_err,"Total unc.","f");
    leg->AddEntry(h_data,"Obs.","lp");

    TH1D* h_ratio;
    TH1D* h_ratio_base;
    TGraphAsymmErrors* h_ratio_band;
    if (incl_ratio) {
        TString ratio_name = "r_" + title;
        h_ratio = make_ratio_histogram(ratio_name,h_data,h_exp_sum);
        h_ratio_base = make_ratio_histogram("r_base",h_data,h_data);
        h_ratio_band = make_ratio_error_band(h_data,h_exp_sum,gr_err);

        h_ratio->SetLineColor(kBlack);
        h_ratio->SetMarkerStyle(20);
        h_ratio->SetMarkerSize(0.75);
        h_ratio->GetYaxis()->SetTitleSize(0.1);
        h_ratio->GetYaxis()->SetTitleOffset(0.25);

        h_ratio_base->SetLineColor(kBlack);
        h_ratio_base->SetLineWidth(1);
        h_ratio_base->SetLineStyle(3);
        // h_ratio_base->GetYaxis()->SetRangeUser(0.2,1.8);
        // h_ratio_base->GetYaxis()->SetRangeUser(0.4,1.6);    // Range for nuisfit ratio as per ARC request
        h_ratio_base->GetYaxis()->SetRangeUser(0.0,2.0);    // Range for 35 bin njets histogram as per ARC request
        h_ratio_base->GetYaxis()->SetNdivisions(204,kFALSE);

        // h_ratio_base->GetXaxis()->SetLabelSize(0.230);//0.230
        // h_ratio_base->GetXaxis()->SetLabelOffset(0.020);  // Default is 0.005
        h_ratio_base->GetXaxis()->SetLabelSize(0.270);//0.230
        h_ratio_base->GetXaxis()->SetLabelOffset(0.040);  // Default is 0.005
        if (pSize > 36) {
            h_ratio_base->GetXaxis()->SetLabelSize(0.200);
            h_ratio_base->GetXaxis()->SetLabelOffset(0.015);
        }

        // h_ratio_base->SetTitle(TString::Format(";%s;#frac{Data}{Pred}",xtitle.Data()));
        // h_ratio_base->GetYaxis()->SetTitleSize(0.150);
        // h_ratio_base->GetYaxis()->SetTitleOffset(0.300);  // Default is 1.0
        h_ratio_base->SetTitle(TString::Format(";%s;Obs. / pred.",xtitle.Data()));
        h_ratio_base->GetYaxis()->SetTitleSize(0.180);
        h_ratio_base->GetYaxis()->SetTitleOffset(0.220);  // Default is 1.0
        h_ratio_base->GetYaxis()->SetLabelSize(0.163);// 0.140
        if (pSize > 36) {
            h_ratio_base->GetYaxis()->SetTitleSize(0.180);
            h_ratio_base->GetYaxis()->SetTitleOffset(0.130);
            h_ratio_base->GetYaxis()->SetLabelSize(0.163);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Actual plotting and Drawing section
    ////////////////////////////////////////////////////////////////////////////////////////////////

    if (debug) std::cout << "DEBUG: Edit canvas object" << std::endl;
    gStyle->SetPadBorderMode(0);
    gStyle->SetFrameBorderMode(0);
    gStyle->SetOptStat(0);

    float L = xpad;
    float B = ypad;
    float R = 1-xpad;
    float T = 1-ypad;
    double L_margin = 105.6 / c->GetWw();   // Targets 0.11 at 960 width
    double R_margin =  24.0 / c->GetWw();   // Targets 0.025 at 960 width
    if (incl_ratio) {
        c->Divide(1,2,small,small);
        c->GetPad(1)->SetPad(L,B+ydiv,R,T); // Order: (L B R T)
        c->GetPad(1)->SetLeftMargin(L_margin);
        c->GetPad(1)->SetRightMargin(R_margin);//0.05
        c->GetPad(1)->SetBottomMargin(ygap / 2);
        c->GetPad(1)->Modified();

        c->GetPad(2)->SetPad(L,B,R,ydiv);   // Order: (L B R T)
        c->GetPad(2)->SetTopMargin(ygap / 2);
        c->GetPad(2)->SetLeftMargin(L_margin);
        c->GetPad(2)->SetRightMargin(R_margin);//0.05
        c->GetPad(2)->SetBottomMargin(0.333);//0.3
        c->GetPad(2)->SetGrid(0,1);
        c->GetPad(2)->SetTickx();
        c->GetPad(2)->Modified();
    } else {
        c->Divide(1,1,small,small);
        c->GetPad(1)->SetGrid(0,0);
        c->GetPad(1)->SetLeftMargin(.11);
        c->GetPad(1)->SetRightMargin(.05);
        c->GetPad(1)->SetBottomMargin(.1);

        c->GetPad(1)->SetBottomMargin(.1);
        c->GetPad(1)->Modified();
        c->cd(1);
        gPad->Modified();
    }

    if (debug) std::cout << "DEBUG: Edit legend object" << std::endl;
    leg->SetFillColor(kWhite);
    leg->SetLineColor(kWhite);
    leg->SetShadowColor(kWhite);
    leg->SetTextFont(42);
    leg->SetTextSize(0.035);
    leg->SetNColumns(5);

    if (debug) std::cout << "DEBUG: Making the Latex object" << std::endl;

    // c->cd();
    c->cd(1);

    int max_bin;
    double hmax,max_val,bin_err;

    hmax = 0.0;
    max_bin = h_data->GetMaximumBin();
    max_val = h_data->GetBinContent(max_bin);
    bin_err = h_data->GetBinErrorUp(max_bin);
    hmax = TMath::Max(max_val+bin_err,hmax);

    max_val = hs->GetMaximum();
    hmax = TMath::Max(max_val,hmax);

    // for (TH1D* h: overlay_hists) {
    //     max_bin = h->GetMaximumBin();
    //     max_val = h->GetBinContent(max_bin);
    //     hmax = TMath::Max(max_val,hmax);
    // }

    if (incl_leg) {
        h_data->SetMaximum(hmax*1.5);
        hs->SetMaximum(hmax*1.5);
    } else {
        h_data->SetMaximum(hmax*1.01);
        hs->SetMaximum(hmax*1.01);
    }

    if (incl_ratio) {
        // hs->SetMinimum(0.01);   // This will avoid drawing the 0 on the y-axis
        hs->SetMinimum(0.0);
    } else {
        hs->SetMinimum(0.0);
        h_data->SetMinimum(0.0);
    }

    if (debug) std::cout << "DEBUG: Drawing stuff" << std::endl;

    hs->Draw("hist");   // draws the stacked histogram
    // h_exp_sum->Draw("hist"); // draws the summed histogram (no process samples shown)
    //h_exp_sum->Draw("same,e");
    if (incl_leg) leg->Draw();
    extra_text.at(0)->Draw();

    h_data->Draw("same,e,p");
    gr_err->Draw("same,2");
    // for (TH1D* h: overlay_hists) h->Draw("same,hist");

    add_cms_text((TPad*)c->GetPad(1),cms_style);
    if (incl_ratio) {
        c->cd(1);

        hs->GetYaxis()->SetTitleSize(0.08);
        hs->GetYaxis()->SetTitleOffset(0.63);
        hs->GetYaxis()->SetLabelSize(0.070);
        if (pSize > 36) {
            hs->GetYaxis()->SetTitleSize(0.08);
            hs->GetYaxis()->SetTitleOffset(0.30);
            hs->GetYaxis()->SetLabelSize(0.070);
        }

        c->cd(2);

        h_ratio_base->Draw();
        h_ratio_band->Draw("same,2");
        h_ratio->Draw("same,e,p");

        // The x-axis labeling is determined by the ratio plot
        // if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
        //     h_ratio->GetXaxis()->SetLabelSize(0.250);
        // }

        c->GetPad(1)->RedrawAxis();
        c->GetPad(2)->RedrawAxis();
    } else {
        hs->GetXaxis()->SetLabelFont(42);   //Default: 62
        if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
            hs->GetXaxis()->SetLabelSize(0.05); //Default: 0.04
        } else {
            hs->GetXaxis()->SetLabelSize(0.04); //Default: 0.04
        }

        c->GetPad(1)->RedrawAxis();
    }

    c->cd();
    draw_lines(pData, pGroup, L_margin, R_margin, false, 0.015);

    TString save_format, save_name;

    // save_format = "png";
    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_format.Data());
    // c->Print(save_name,save_format);

    save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type1.Data());
    c->Print(save_name,save_type1);

    // save_format = "pdf";
    // save_format = "eps";
    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_format.Data());
    // c->Print(save_name,save_format);

    save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type2.Data());
    c->Print(save_name,save_type2);

    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type4.Data());
    // c->Print(save_name,save_type4);

    // Print an external legend
    if (ext_leg) {
        // save_name = TString::Format("ext_leg_%s",title.Data());
        save_name = TString::Format("ext_leg_ylds");
        make_external_legend(leg,save_name);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Clean up section
    ////////////////////////////////////////////////////////////////////////////////////////////////
    delete c;
    delete h_data;
    // delete CMSInfoLatex;
    delete leg;
    delete hs;
    delete gr_err;
    delete h_exp_sum;
    for (TH1D* h: proc_hists) {
        delete h;
    }
    if (incl_ratio) {
        delete h_ratio;
        delete h_ratio_base;
        delete h_ratio_band;
    }
    return;
}


void make_overlay_mega_plot(
    TString title,
    std::vector<TLatex*> extra_text,
    PlotData pData,
    PlotGroup pGroup,
    bool incl_ratio,
    bool incl_leg,
    bool ext_leg,
    CMSTextStyle cms_style,
    TString xtitle="",
    bool do_log = false
) {
    bool debug = false;
    int pSize = pData.SR_name.size();

    // Some configuration settings
    Float_t small = 1.e-5;
    const float padding = 1e-5;
    const float xpad = small;   // Pad spacing left to right
    const float ypad = small;   // Pad spacing top to bottom
    const float ygap = 0.11;    // Gap between the main plot and ratio plot
    const float ydiv = 0.3;     // Height of the second pad when making plots with ratios

    HistogramBuilder builder = HistogramBuilder();

    int c_hh = 640;
    int c_ww = 1920;

    TCanvas* c = new TCanvas("canv","canv",150,10,c_ww,c_hh);
    // TCanvas* c = new TCanvas("canv","canv",150,10,960*4,640);
    TLegend *leg = new TLegend(0.14,0.75,0.94,0.89);
    THStack *hs = new THStack("hs_category_yield","");

    std::vector<TH1D*> proc_hists;
    TH1D* h_data = builder.buildDataDifferentialHistogram(title,pData,BIN_LABEL_MAP);
    h_data->SetLineWidth(1); // Try a thiner line for the full njet histogram PDFs
    
    //PLOT_PROCS = {"charge_flips","fakes","Diboson","Triboson","convs","ttH","ttll","ttlnu","tllq","tHq","tttt"}; // This is odd, why this vector imported from PlotData.h is empty?
    //cout << "Adding processes....... " << PLOT_PROCS.size() << endl;

    for (TString proc_name: PLOT_PROCS) {
        if (debug) std::cout << "DEBUG: Getting process histogram for " << proc_name << std::endl;
        TH1D* h_proc = builder.buildProcessDifferentialHistogram(title,proc_name,pData,BIN_LABEL_MAP,PROCESS_COLOR_MAP);
        if (debug) std::cout << "DEBUG: Adding process histogram to legend: " << proc_name << std::endl;
        TString legend_name = proc_name;
        if (PROCESS_LABEL_MAP.count(proc_name.Data())) {
            legend_name = PROCESS_LABEL_MAP[proc_name.Data()];
        }
        if (incl_ratio) {
            // Hide the x-axis labels for the stack plot
            // Note: For some reason this can't be done using the THStack histogram
            for (int i=1; i <= h_proc->GetXaxis()->GetNbins(); i++) {
                h_proc->GetXaxis()->SetBinLabel(i,"");
            }
        }
        leg->AddEntry(h_proc,legend_name,"f");
        proc_hists.push_back(h_proc);
    }

    // for (TH1D* h: overlay_hists) {
    //     leg->AddEntry(h,h->GetTitle(),"f");
    // }

    for (TH1D* h: proc_hists) {
        if (debug) std::cout << "DEBUG: Adding histogram to stack: " << h->GetName() << std::endl;
        hs->Add(h);
    }

    // hs->SetTitle(";Category;Events");
    if (incl_ratio) {
        hs->SetTitle(";;Events");
    } else {
        hs->SetTitle(TString::Format(";%s;Events",xtitle.Data()));
    }

    TH1D* h_exp_sum = builder.buildSummedDifferentialHistogram("expected_sum","",pData,BIN_LABEL_MAP);
    TGraphErrors* gr_err = get_error_differential_graph(h_exp_sum,pData);

    leg->AddEntry(gr_err,"Total unc.","f");
    leg->AddEntry(h_data,"Obs.","lp");

    TH1D* h_ratio;
    TH1D* h_ratio_base;
    TGraphAsymmErrors* h_ratio_band;
    if (incl_ratio) {
        TString ratio_name = "r_" + title;
        h_ratio = make_ratio_histogram(ratio_name,h_data,h_exp_sum);
        h_ratio_base = make_ratio_histogram("r_base",h_data,h_data);
        h_ratio_band = make_ratio_error_band(h_data,h_exp_sum,gr_err);

        h_ratio->SetLineColor(kBlack);
        h_ratio->SetMarkerStyle(20);
        h_ratio->SetMarkerSize(0.75);
        h_ratio->GetYaxis()->SetTitleSize(0.1);
        h_ratio->GetYaxis()->SetTitleOffset(0.25);

        h_ratio_base->SetLineColor(kBlack);
        h_ratio_base->SetLineWidth(1);
        h_ratio_base->SetLineStyle(3);
        // h_ratio_base->GetYaxis()->SetRangeUser(0.2,1.8);
        // h_ratio_base->GetYaxis()->SetRangeUser(0.4,1.6);    // Range for nuisfit ratio as per ARC request
        h_ratio_base->GetYaxis()->SetRangeUser(0.0,2.0);    // Range for 35 bin njets histogram as per ARC request
        h_ratio_base->GetYaxis()->SetNdivisions(204,kFALSE);

        // h_ratio_base->GetXaxis()->SetLabelSize(0.230);//0.230
        // h_ratio_base->GetXaxis()->SetLabelOffset(0.020);  // Default is 0.005
        h_ratio_base->GetXaxis()->SetLabelSize(0.270);//0.230
        h_ratio_base->GetXaxis()->SetLabelOffset(0.040);  // Default is 0.005
        if (pSize > 36) {
            h_ratio_base->GetXaxis()->SetLabelSize(0.200);
            h_ratio_base->GetXaxis()->SetLabelOffset(0.015);
        }

        // h_ratio_base->SetTitle(TString::Format(";%s;#frac{Data}{Pred}",xtitle.Data()));
        // h_ratio_base->GetYaxis()->SetTitleSize(0.150);
        // h_ratio_base->GetYaxis()->SetTitleOffset(0.300);  // Default is 1.0
        h_ratio_base->SetTitle(TString::Format(";%s;Obs. / pred.",xtitle.Data()));
        h_ratio_base->GetYaxis()->SetTitleSize(0.180);
        h_ratio_base->GetYaxis()->SetTitleOffset(0.220);  // Default is 1.0
        h_ratio_base->GetYaxis()->SetLabelSize(0.163);// 0.140
        if (pSize > 36) {
            h_ratio_base->GetYaxis()->SetTitleSize(0.180);
            h_ratio_base->GetYaxis()->SetTitleOffset(0.130);
            h_ratio_base->GetYaxis()->SetLabelSize(0.163);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Actual plotting and Drawing section
    ////////////////////////////////////////////////////////////////////////////////////////////////

    if (debug) std::cout << "DEBUG: Edit canvas object" << std::endl;
    gStyle->SetPadBorderMode(0);
    gStyle->SetFrameBorderMode(0);
    gStyle->SetOptStat(0);

    float L = xpad;
    float B = ypad;
    float R = 1-xpad;
    float T = 1-ypad;
    double L_margin = 105.6 / c->GetWw();   // Targets 0.11 at 960 width
    double R_margin =  24.0 / c->GetWw();   // Targets 0.025 at 960 width
    if (incl_ratio) {
        c->Divide(1,2,small,small);
        c->GetPad(1)->SetPad(L,B+ydiv,R,T); // Order: (L B R T)
        c->GetPad(1)->SetLeftMargin(L_margin);
        c->GetPad(1)->SetRightMargin(R_margin);//0.05
        c->GetPad(1)->SetBottomMargin(ygap / 2);
        c->GetPad(1)->Modified();        

        c->GetPad(2)->SetPad(L,B,R,ydiv);   // Order: (L B R T)
        c->GetPad(2)->SetTopMargin(ygap / 2);
        c->GetPad(2)->SetLeftMargin(L_margin);
        c->GetPad(2)->SetRightMargin(R_margin);//0.05
        c->GetPad(2)->SetBottomMargin(0.333);//0.3
        c->GetPad(2)->SetGrid(0,1);
        c->GetPad(2)->SetTickx();
        c->GetPad(2)->Modified();
    } else {
        c->Divide(1,1,small,small);
        c->GetPad(1)->SetGrid(0,0);
        c->GetPad(1)->SetLeftMargin(.11);
        c->GetPad(1)->SetRightMargin(.05);
        c->GetPad(1)->SetBottomMargin(.1);

        c->GetPad(1)->SetBottomMargin(.1);
        c->GetPad(1)->Modified();
        c->cd(1);
        gPad->Modified();
    }

    if (debug) std::cout << "DEBUG: Edit legend object" << std::endl;
    leg->SetFillColor(kWhite);
    leg->SetLineColor(kWhite);
    leg->SetShadowColor(kWhite);
    leg->SetTextFont(42);
    leg->SetTextSize(0.035);
    leg->SetNColumns(5);

    if (debug) std::cout << "DEBUG: Making the Latex object" << std::endl;
    c->cd(1);
    // c->cd();

    int max_bin;
    double hmax,max_val,bin_err;

    hmax = 0.0;
    max_bin = h_data->GetMaximumBin();
    max_val = h_data->GetBinContent(max_bin);
    bin_err = h_data->GetBinErrorUp(max_bin);
    hmax = TMath::Max(max_val+bin_err,hmax);

    max_val = hs->GetMaximum();
    hmax = TMath::Max(max_val,hmax);

    // for (TH1D* h: overlay_hists) {
    //     max_bin = h->GetMaximumBin();
    //     max_val = h->GetBinContent(max_bin);
    //     hmax = TMath::Max(max_val,hmax);
    // }

    if (incl_leg) {
        h_data->SetMaximum(hmax*1.5);
        hs->SetMaximum(hmax*1.5);
    } else {
        h_data->SetMaximum(hmax*1.01);
        hs->SetMaximum(hmax*1.01);
    }

    if (incl_ratio) {
        hs->SetMinimum(0.0);   // This will avoid drawing the 0 on the y-axis
        // hs->SetMinimum(0.0);
    } else {
        hs->SetMinimum(0.0);
        h_data->SetMinimum(0.0);
    }
    if (do_log) {
        hs->SetMaximum(hmax*10);
        hs->SetMinimum(0.1);
        ((TPad*)c->GetPad(1))->SetLogy();
    }

    if (debug) std::cout << "DEBUG: Drawing stuff" << std::endl;

    hs->Draw("hist");   // draws the stacked histogram
    // h_exp_sum->Draw("hist"); // draws the summed histogram (no process samples shown)
    //h_exp_sum->Draw("same,e");
    if (incl_leg) leg->Draw();
    extra_text.at(0)->Draw();

    h_data->Draw("same,e,p");
    gr_err->Draw("same,2");
    // for (TH1D* h: overlay_hists) h->Draw("same,hist");

    add_cms_text((TPad*)c->GetPad(1),cms_style);
    if (incl_ratio) {
        c->cd(1);
        //((TPad*)c->GetPad(1))->SetLogy();

        hs->GetYaxis()->SetTitleSize(0.08);
        hs->GetYaxis()->SetTitleOffset(0.63);
        hs->GetYaxis()->SetLabelSize(0.070);
        if (pSize > 36) {
            hs->GetYaxis()->SetTitleSize(0.08);
            hs->GetYaxis()->SetTitleOffset(0.30);
            hs->GetYaxis()->SetLabelSize(0.070);
        }

        c->cd(2);

        h_ratio_base->Draw();
        h_ratio_band->Draw("same,2");
        h_ratio->Draw("same,e,p");

        // The x-axis labeling is determined by the ratio plot
        // if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
        //     h_ratio->GetXaxis()->SetLabelSize(0.250);
        // }

        c->GetPad(1)->RedrawAxis();
        c->GetPad(2)->RedrawAxis();
    } else {
        hs->GetXaxis()->SetLabelFont(42);   //Default: 62
        if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
            hs->GetXaxis()->SetLabelSize(0.05); //Default: 0.04
        } else {
            hs->GetXaxis()->SetLabelSize(0.04); //Default: 0.04
        }

        c->GetPad(1)->RedrawAxis();
    }

    c->cd();
    draw_lines(pData, pGroup, L_margin, R_margin, true, 0.035);

    TString save_format, save_name;

    // save_format = "png";
    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_format.Data());
    // c->Print(save_name,save_format);

    save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type1.Data());
    c->Print(save_name,save_type1);

    // save_format = "pdf";
    // save_format = "eps";
    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_format.Data());
    // c->Print(save_name,save_format);

    save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type2.Data());
    c->Print(save_name,save_type2);

    save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type3.Data());
    c->Print(save_name,save_type3);
    TFile f(save_name, "recreate");
    h_data->SetDirectory(&f);
    h_data->Write();
    for (TH1D* h: proc_hists) {
        h->SetDirectory(&f);
        h->Write();
    }
    h_exp_sum->SetDirectory(&f);
    h_exp_sum->Write();
    gr_err->Write();

    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_type4.Data());
    // c->Print(save_name,save_type4);

    // Print an external legend
    if (ext_leg) {
        // save_name = TString::Format("ext_leg_%s",title.Data());
        save_name = TString::Format("ext_leg_ylds");
        make_external_legend(leg,save_name);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Clean up section
    ////////////////////////////////////////////////////////////////////////////////////////////////
    delete c;
    delete h_data;
    // delete CMSInfoLatex;
    delete leg;
    delete hs;
    delete gr_err;
    delete h_exp_sum;
    for (TH1D* h: proc_hists) {
        delete h;
    }
    if (incl_ratio) {
        delete h_ratio;
        delete h_ratio_base;
        delete h_ratio_band;
    }
    return;
}

void make_overlay_sub_plots(
    TString title,
    std::vector<TLatex*> extra_text,
    PlotData pData_arranged,
    PlotGroup megaGroup,
    vTStr refSR,
    bool incl_ratio,
    bool incl_leg,
    bool ext_leg,
    CMSTextStyle cms_style,
    std::string year="all",
    TString xtitle=""
) {
    bool debug = false;

    std::unordered_map<std::string,std::vector<TString> > BINNING {
        {"lj0pt", {"0","1.5","2.5","5"}},
        {"ptz"  , {"0","2","3","4","5"}},
        {"ptbl" , {"0","100","200","400"}},
        {"bl0pt", {"0","100","200","400"}},
        //{"ht"   , {"0","300","500","800"}},
        {"ht"   , {"0","1","2","3","4","6","8"}},
    };

    bool do_binning = true;
    bool do_main_binning = false;
    std::string kin;
    TString subtitle = title(title.Index("_")+1,title.Length());
    if (subtitle.Index("_") == TString::kNPOS) do_main_binning = true; // It's either lj0pt or ptz
    else if (subtitle.Index("_", subtitle.Index("_")+1) == TString::kNPOS) kin = subtitle(subtitle.Index("_")+1, subtitle.Length());
    else kin = subtitle(subtitle.Index("_")+1, subtitle.Index("_", subtitle.Index("_")+1) - (subtitle.Index("_")+1));
    if (BINNING.find(kin)==BINNING.end() & !do_main_binning) do_binning = false;

    cout << kin << endl;
    cout << do_binning << endl;

    // Some configuration settings
    Float_t small = 1.e-5;
    const float padding = 1e-5;
    const float xpad = small;   // Pad spacing left to right
    const float ypad = small;   // Pad spacing top to bottom
    const float ygap = 0.11;    // Gap between the main plot and ratio plot
    const float ydiv = 0.3;     // Height of the second pad when making plots with ratios

    HistogramBuilder builder = HistogramBuilder();

    int c_hh = 640;
    int c_ww = 960;
    int idx  = 0;
    
    PlotGroup repartGroup = SRRepartition(pData_arranged, megaGroup, refSR);
    std::vector<int> divider = repartGroup.gbins;
    std::vector<PlotData> pList = divide(pData_arranged, divider);

    TLatex* latex_holder = new TLatex(*extra_text.at(0));

    for (PlotData pData: pList) {

        cout << pData.SR_name.at(0) << endl;
        cout << pData.SR_name.size() << endl;

    if (do_main_binning) {
        TString sr0 = pData.SR_name[0];
        int sr_size = 0;
        for (TString sr: pData.SR_name) {
            if (sr != sr0) break;
            sr_size++;
        }
        cout << "bin size: " << sr_size << endl;
        if (sr_size == 4) kin = "lj0pt";      // lj0pt has 4 bins
        else if (sr_size == 5) kin = "ptz";   // ptz has 5 bins
        else {
            cout << "[WARNING]Unknown kinematic with bin size " << pData.SR_name.size() << endl;
            do_binning = false;
        }
        // Replace the kinematic label with either lj0pt or ptz
        if (do_binning) {
            TLatex* latex2 = extra_text.at(1);
            double x_latex2 = latex2->GetX();
            double y_latex2 = latex2->GetY();
            latex2->SetText(x_latex2, y_latex2, KIN_LABEL_MAP[kin].c_str());
            extra_text.at(1) = latex2;
        }
    }

    int pSize = pData.SR_name.size();
    TCanvas* c = new TCanvas("canv","canv",150,10,c_ww,c_hh);
    // TCanvas* c = new TCanvas("canv","canv",150,10,960*4,640);
    TLegend *leg = new TLegend(0.14,0.75,0.94,0.89);
    THStack *hs = new THStack("hs_category_yield","");

    std::vector<TH1D*> proc_hists;
    TH1D* h_data = builder.buildDataDifferentialHistogram(title,pData,BIN_LABEL_MAP);
    h_data->SetLineWidth(1); // Try a thiner line for the full njet histogram PDFs
    
    //PLOT_PROCS = {"charge_flips","fakes","Diboson","Triboson","convs","ttH","ttll","ttlnu","tllq","tHq","tttt"}; // This is odd, why this vector imported from PlotData.h is empty?
    //cout << "Adding processes....... " << PLOT_PROCS.size() << endl;

    for (TString proc_name: PLOT_PROCS) {
        if (debug) std::cout << "DEBUG: Getting process histogram for " << proc_name << std::endl;
        TH1D* h_proc = builder.buildProcessDifferentialHistogram(title,proc_name,pData,BIN_LABEL_MAP,PROCESS_COLOR_MAP);
        if (debug) std::cout << "DEBUG: Adding process histogram to legend: " << proc_name << std::endl;
        TString legend_name = proc_name;
        if (PROCESS_LABEL_MAP.count(proc_name.Data())) {
            legend_name = PROCESS_LABEL_MAP[proc_name.Data()];
        }
        if (incl_ratio) {
            // Hide the x-axis labels for the stack plot
            // Note: For some reason this can't be done using the THStack histogram
            for (int i=1; i <= h_proc->GetXaxis()->GetNbins(); i++) {
                h_proc->GetXaxis()->SetBinLabel(i,"");
            }
        }
        leg->AddEntry(h_proc,legend_name,"f");
        proc_hists.push_back(h_proc);
    }

    // for (TH1D* h: overlay_hists) {
    //     leg->AddEntry(h,h->GetTitle(),"f");
    // }

    for (TH1D* h: proc_hists) {
        if (debug) std::cout << "DEBUG: Adding histogram to stack: " << h->GetName() << std::endl;
        hs->Add(h);
    }

    // hs->SetTitle(";Category;Events");
    if (incl_ratio) {
        hs->SetTitle(";;Events");
    } else {
        hs->SetTitle(TString::Format(";%s;Events",xtitle.Data()));
    }

    TH1D* h_exp_sum = builder.buildSummedDifferentialHistogram("expected_sum","",pData,BIN_LABEL_MAP);
    TGraphErrors* gr_err = get_error_differential_graph(h_exp_sum,pData);

    leg->AddEntry(gr_err,"Total unc.","f");
    leg->AddEntry(h_data,"Obs.","lp");

    TH1D* h_ratio;
    TH1D* h_ratio_base;
    TGraphAsymmErrors* h_ratio_band;
    if (incl_ratio) {
        TString ratio_name = "r_" + title;
        h_ratio = make_ratio_histogram(ratio_name,h_data,h_exp_sum);
        h_ratio_base = make_ratio_histogram("r_base",h_data,h_data);
        h_ratio_band = make_ratio_error_band(h_data,h_exp_sum,gr_err);

        h_ratio->SetLineColor(kBlack);
        h_ratio->SetMarkerStyle(20);
        h_ratio->SetMarkerSize(0.75);
        h_ratio->GetYaxis()->SetTitleSize(0.1);
        h_ratio->GetYaxis()->SetTitleOffset(0.25);

        h_ratio_base->SetLineColor(kBlack);
        h_ratio_base->SetLineWidth(1);
        h_ratio_base->SetLineStyle(3);
        // h_ratio_base->GetYaxis()->SetRangeUser(0.2,1.8);
        // h_ratio_base->GetYaxis()->SetRangeUser(0.4,1.6);    // Range for nuisfit ratio as per ARC request
        h_ratio_base->GetYaxis()->SetRangeUser(0.0,2.0);    // Range for 35 bin njets histogram as per ARC request
        h_ratio_base->GetYaxis()->SetNdivisions(204,kFALSE);

        // h_ratio_base->GetXaxis()->SetLabelSize(0.230);//0.230
        // h_ratio_base->GetXaxis()->SetLabelOffset(0.020);  // Default is 0.005
        h_ratio_base->GetXaxis()->SetLabelSize(0.270);//0.230
        h_ratio_base->GetXaxis()->SetLabelOffset(0.040);  // Default is 0.005
        if (pSize > 36) {
            h_ratio_base->GetXaxis()->SetLabelSize(0.200);
            h_ratio_base->GetXaxis()->SetLabelOffset(0.015);
        }

        // h_ratio_base->SetTitle(TString::Format(";%s;#frac{Data}{Pred}",xtitle.Data()));
        // h_ratio_base->GetYaxis()->SetTitleSize(0.150);
        // h_ratio_base->GetYaxis()->SetTitleOffset(0.300);  // Default is 1.0
        h_ratio_base->SetTitle(TString::Format(";%s;Obs. / pred.",xtitle.Data()));
        h_ratio_base->GetYaxis()->SetTitleSize(0.180);
        h_ratio_base->GetYaxis()->SetTitleOffset(0.220);  // Default is 1.0
        h_ratio_base->GetYaxis()->SetLabelSize(0.163);// 0.140
        if (pSize > 36) {
            h_ratio_base->GetYaxis()->SetTitleSize(0.180);
            h_ratio_base->GetYaxis()->SetTitleOffset(0.130);
            h_ratio_base->GetYaxis()->SetLabelSize(0.163);
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Actual plotting and Drawing section
    ////////////////////////////////////////////////////////////////////////////////////////////////

    if (debug) std::cout << "DEBUG: Edit canvas object" << std::endl;
    gStyle->SetPadBorderMode(0);
    gStyle->SetFrameBorderMode(0);
    gStyle->SetOptStat(0);

    float L = xpad;
    float B = ypad;
    float R = 1-xpad;
    float T = 1-ypad;
    double L_margin = 105.6 / c->GetWw();   // Targets 0.11 at 960 width
    double R_margin =  24.0 / c->GetWw();   // Targets 0.025 at 960 width
    if (incl_ratio) {
        c->Divide(1,2,small,small);
        c->GetPad(1)->SetPad(L,B+ydiv,R,T); // Order: (L B R T)
        c->GetPad(1)->SetLeftMargin(L_margin);
        c->GetPad(1)->SetRightMargin(R_margin);//0.05
        c->GetPad(1)->SetBottomMargin(ygap / 2);
        c->GetPad(1)->Modified();

        c->GetPad(2)->SetPad(L,B,R,ydiv);   // Order: (L B R T)
        c->GetPad(2)->SetTopMargin(ygap / 2);
        c->GetPad(2)->SetLeftMargin(L_margin);
        c->GetPad(2)->SetRightMargin(R_margin);//0.05
        c->GetPad(2)->SetBottomMargin(0.333);//0.3
        c->GetPad(2)->SetGrid(0,1);
        c->GetPad(2)->SetTickx();
        c->GetPad(2)->Modified();
    } else {
        c->Divide(1,1,small,small);
        c->GetPad(1)->SetGrid(0,0);
        c->GetPad(1)->SetLeftMargin(.11);
        c->GetPad(1)->SetRightMargin(.05);
        c->GetPad(1)->SetBottomMargin(.1);

        c->GetPad(1)->SetBottomMargin(.1);
        c->GetPad(1)->Modified();
        c->cd(1);
        gPad->Modified();
    }

    if (debug) std::cout << "DEBUG: Edit legend object" << std::endl;
    leg->SetFillColor(kWhite);
    leg->SetLineColor(kWhite);
    leg->SetShadowColor(kWhite);
    leg->SetTextFont(42);
    leg->SetTextSize(0.035);
    leg->SetNColumns(5);

    if (debug) std::cout << "DEBUG: Making the Latex object" << std::endl;

    // c->cd();
    c->cd(1);

    int max_bin;
    double hmax,max_val,bin_err;

    hmax = 0.0;
    max_bin = h_data->GetMaximumBin();
    max_val = h_data->GetBinContent(max_bin);
    bin_err = h_data->GetBinErrorUp(max_bin);
    hmax = TMath::Max(max_val+bin_err,hmax);

    max_val = hs->GetMaximum();
    hmax = TMath::Max(max_val,hmax);

    // for (TH1D* h: overlay_hists) {
    //     max_bin = h->GetMaximumBin();
    //     max_val = h->GetBinContent(max_bin);
    //     hmax = TMath::Max(max_val,hmax);
    // }

    if (incl_leg) {
        h_data->SetMaximum(hmax*1.5);
        hs->SetMaximum(hmax*1.5);
    } else {
        h_data->SetMaximum(hmax*1.01);
        hs->SetMaximum(hmax*1.01);
    }

    if (incl_ratio) {
        // hs->SetMinimum(0.01);   // This will avoid drawing the 0 on the y-axis
        hs->SetMinimum(0.0);
    } else {
        hs->SetMinimum(0.0);
        h_data->SetMinimum(0.0);
    }

    if (debug) std::cout << "DEBUG: Drawing stuff" << std::endl;

    hs->Draw("hist");   // draws the stacked histogram
    // h_exp_sum->Draw("hist"); // draws the summed histogram (no process samples shown)
    //h_exp_sum->Draw("same,e");
    if (incl_leg) leg->Draw();

    extra_text.at(0)->SetX(0.5);
    // cout << extra_text.at(0)->GetX() << endl;
    // cout << extra_text.at(0)->GetY() << endl;
    // latex_holder->Draw();
    extra_text.at(0)->Draw();

    h_data->Draw("same,e,p");
    gr_err->Draw("same,2");
    // for (TH1D* h: overlay_hists) h->Draw("same,hist");

    add_cms_text((TPad*)c->GetPad(1),cms_style,year);
    if (incl_ratio) {
        c->cd(1);

        hs->GetYaxis()->SetTitleSize(0.08);
        hs->GetYaxis()->SetTitleOffset(0.63);
        hs->GetYaxis()->SetLabelSize(0.070);
        if (pSize > 36) {
            hs->GetYaxis()->SetTitleSize(0.08);
            hs->GetYaxis()->SetTitleOffset(0.30);
            hs->GetYaxis()->SetLabelSize(0.070);
        }

        c->cd(2);

        h_ratio_base->Draw();
        h_ratio_band->Draw("same,2");
        h_ratio_base->Draw("same");
        h_ratio->Draw("same,e,p");

        // The x-axis labeling is determined by the ratio plot
        // if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
        //     h_ratio->GetXaxis()->SetLabelSize(0.250);
        // }

        c->GetPad(1)->RedrawAxis();
        c->GetPad(2)->RedrawAxis();
    } else {
        hs->GetXaxis()->SetLabelFont(42);   //Default: 62
        if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
            hs->GetXaxis()->SetLabelSize(0.05); //Default: 0.04
        } else {
            hs->GetXaxis()->SetLabelSize(0.04); //Default: 0.04
        }

        c->GetPad(1)->RedrawAxis();
    }

    c->cd();
    if (incl_ratio) extra_text.at(1)->Draw();
    if (do_binning) draw_labels(BINNING[kin], pData, L_margin, R_margin);

    TLatex testsign(0.99, 0.09, "\\times100");
    testsign.SetTextSize(0.035);
    if (kin == "ht") testsign.SetTextSize(0.0275);
    testsign.SetTextAlign(33); // right+top
    testsign.SetTextFont(42);
    // if (kin == "lj0pt" | kin == "ptz" | kin == "ht") testsign.Draw();

    // Drawing the channel label
    std::string ch_label = BIN_LABEL_MAP[refSR[idx].Data()];
    double ch_size = 0.045;
    TLatex clabel(0.97, 0.92, ch_label.c_str());
    clabel.SetTextSize(ch_size);
    // if(ch_label.find("2j3j")!=-1 | ch_label.find("4j5j")!=-1) {
    //     clabel.SetTextSize(ch_size*1.4);
    // }
    clabel.SetTextAlign(33); // right+top
    clabel.SetTextFont(42);
    clabel.Draw();

    TString save_format, save_name;

    // save_format = "png";
    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_format.Data());
    // c->Print(save_name,save_format);

    save_name = TString::Format("plots/%s_%s.%s",title.Data(),refSR[idx].Data(),save_type1.Data());
    c->Print(save_name,save_type1);

    // save_format = "pdf";
    // save_format = "eps";
    // save_name = TString::Format("plots/overlayed_%s.%s",title.Data(),save_format.Data());
    // c->Print(save_name,save_format);

    save_name = TString::Format("plots/%s_%s.%s",title.Data(),refSR[idx].Data(),save_type2.Data());
    c->Print(save_name,save_type2);

    // save_name = TString::Format("plots/%s_%s.%s",title.Data(),refSR[idx].Data(),save_type4.Data());
    // c->Print(save_name,save_type4);

    // Print an external legend
    if (ext_leg) {
        // save_name = TString::Format("ext_leg_%s",title.Data());
        save_name = TString::Format("ext_leg_ylds");
        make_external_legend(leg,save_name);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Clean up section
    ////////////////////////////////////////////////////////////////////////////////////////////////
    delete c;
    delete h_data;
    // delete CMSInfoLatex;
    delete leg;
    delete hs;
    delete gr_err;
    delete h_exp_sum;
    for (TH1D* h: proc_hists) {
        delete h;
    }
    if (incl_ratio) {
        delete h_ratio;
        delete h_ratio_base;
        delete h_ratio_band;
    }
    idx++;
    }
    return;
}

// When calling this function, passing postfix as the arg. The postfix is used in the folder name like "SR_xxx" 
void plot_maker(std::string postfix = "") {
    std::string in_dir  = "/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/test/fit_results/";
    std::string out_dir = "/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/test/fit_results/";
    
    //TString fpath_datacard = "/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/test/card_ub/combinedcard.txt";
    TString fpath_datacard = "/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/test/card_anatest25/combinedcard.txt";

    std::map<std::string,TString> ch_map = get_channel_map( fpath_datacard.Data(), true); // map from to long string jet subcategory name to the short channel name
    std::map<std::string,std::string> kin_map = {}; // map the name of channel to the name of kinamtic it uses
    for (const auto & [lstring, ch] : ch_map) {
        int counter = 0;
        for(int i = 0; i < lstring.length(); i++) {
            if(lstring[i] == '_') {
                counter = i;
            }
        }
        std::string chstring = lstring.substr(0, counter);  // remove the last segment of the channel name, like "_lj0pt"
        kin_map[ch.Data()] = lstring.substr(counter+1, lstring.length()); // after the underscore to the end of the long string

        auto nodeHandler = ch_map.extract(lstring);
        nodeHandler.key() = chstring;
        ch_map.insert(std::move(nodeHandler));
    }
    
    // Plot options
    bool incl_mega_plots = true;
    bool incl_njet_plots = true;
    bool incl_sub_plots  = true;
    bool incl_sum_plots  = true;
    
    // Plot layout options
    bool incl_ratio = true;
    bool incl_leg = false;
    bool incl_ext_leg = true;
    
    // Which data-taking year
    std::string year = "all";
    
    // Fit types
    bool do_postfit = true; // true: do postfit, false: do prefit
    std::string fit_type;
    if (do_postfit) fit_type = "postfit";
    else fit_type = "prefit";
    fit_type = fit_type + postfix;

    std::string fit_type2 = fit_type.substr(0, fit_type.find("_"));
    std::string kin_type = fit_type.substr(fit_type.find("_")+1, fit_type.find("_", fit_type.find("_")+1)-fit_type.find("_")-1);
    // fit_type2 = "NP only fit";

    if (postfix.find("step") != -1) {
        int step = int(postfix.back())-48;
        fit_type2 = TString::Format("%d%s", step-2, "\\sigma").Data();
    }
    cout << fit_type2 << endl;
    cout << kin_type << endl;
    
    std::string pData_path = TString::Format("%sSR_%s/", in_dir.c_str(), fit_type.c_str()).Data();
    std::vector<std::string> files = all_files(pData_path);
    
    PlotData pData_raw = read_PlotData_from_file(files);
    PlotData pData;
    if (fit_type.find("ht") != -1) pData = pData_raw;
    else pData = removeEmptyBins(pData_raw);
    
    
    PlotData pData_arranged = rearrange(pData, ch_map, kin_map);
    PlotData pData_arranged2 = rearrange(pData, ch_map, {}, SR_list);
    PlotData pData_aggregated = aggregateDifferential(pData_arranged2);
    
    cout << pData.SR_name.size() << endl;
    cout << pData_arranged.SR_name.size() << endl;
    cout << pData_aggregated.SR_name.size() << endl;
    
    PlotGroup megaGroup = autoPartition(pData_arranged, ch_map);
    PlotGroup njetGroup = SRPartition(pData_aggregated);
    PlotGroup repartGroup = SRRepartition(pData_arranged, megaGroup);

    PlotData pSum_aggregated;
    PlotGroup sumGroup;
    if (incl_sum_plots) {
        std::string pData_sum_path = TString::Format("%sSR_sum_%s/", in_dir.c_str(), fit_type.c_str()).Data();
        std::vector<std::string> files_sum = all_files(pData_sum_path);
        PlotData pSum_raw = read_PlotData_from_file(files_sum);
        PlotData pSum = rearrange(pSum_raw, SR_list);
        pSum_aggregated = aggregateDifferential(pSum);
        sumGroup = autoPartition(pSum_aggregated);
    }

    double cms_txt_xpos = 0.12;
    double cms_txt_ypos = 0.94;
    double extra_txt_xoffset  = 0.13;
    double extra_txt_xoffset2 = 0.86;
    double extra_txt_yoffset  =-0.02;
    double extra_txt_yoffset2 =-0.89;
    int extra_txt_align = 11;

    // specify prefit or postfit
    TLatex* latex = new TLatex();
    latex->SetNDC();
    latex->SetTextFont(42);
    latex->SetTextSize(0.080);
    latex->SetTextAlign(extra_txt_align);
    latex->SetText(cms_txt_xpos + extra_txt_xoffset, cms_txt_ypos + extra_txt_yoffset, fit_type2.c_str());

    // specify kinematic
    TLatex* latex2 = new TLatex(); // The coordinate of this latex is relative to the entire canvas (main plot + ratio plot)
    latex2->SetNDC();
    latex2->SetTextFont(42);
    latex2->SetTextSize(0.040);
    latex2->SetTextAlign(33);
    latex2->SetText(cms_txt_xpos + extra_txt_xoffset2, cms_txt_ypos + extra_txt_yoffset2, KIN_LABEL_MAP[kin_type].c_str());

    // specify category (which SR)
    //TLatex* cat_label = new TLatex(R_margin, 32, BIN_LABEL_MAP[refSR[idx].Data()].c_str());

    std::vector<TLatex*> extra_text;
    extra_text.push_back(latex);
    extra_text.push_back(latex2);

    CMSTextStyle cms_style_pre;
    cms_style_pre.cms_size  = 0.90;//0.85;
    cms_style_pre.lumi_size = 0.80;
    // cms_style.extra_text = "";
    cms_style_pre.extra_text = "Preliminary";
    cms_style_pre.cms_frame_loc = 0;
    cms_style_pre.extra_over_cms_text_size = 0.80;//0.76

    CMSTextStyle cms_style_supp(cms_style_pre);
    cms_style_supp.extra_text = "Supplementary";
    
    if (incl_mega_plots) {
        // make_overlay_mega_plot(TString::Format("mega_%s_layout1", fit_type.c_str()), extra_text, pData_arranged, megaGroup,   incl_ratio, incl_leg, incl_ext_leg, cms_style, "", true);
        make_overlay_mega_plot(TString::Format("mega_%s_layout2", fit_type.c_str()), extra_text, pData_arranged, repartGroup, incl_ratio, incl_leg, incl_ext_leg, cms_style_pre, "", true);
    }
    
    if (incl_njet_plots) {
        make_overlay_njet_plot(TString::Format("njet_%s", fit_type.c_str()), extra_text, pData_aggregated, njetGroup, incl_ratio, incl_leg, incl_ext_leg, cms_style_supp);
    }
    if (incl_sub_plots) {
        // Change SR_list to SR_list_2 to split up 3l onZ 2b category.
        make_overlay_sub_plots(TString::Format("sub_%s", fit_type.c_str()), extra_text, pData_arranged, megaGroup, SR_list_2, incl_ratio, incl_leg, incl_ext_leg, cms_style_pre, year); // Names of the files are hard-coded in the function.
    }
    if (incl_sum_plots) {
        make_overlay_sum_plot(TString::Format("sum_%s", fit_type.c_str()), extra_text, pSum_aggregated, sumGroup, incl_ratio, incl_leg, incl_ext_leg, cms_style_pre);
    }
    return;
}
