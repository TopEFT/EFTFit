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

typedef std::vector<TString> vTStr;
typedef std::vector<RooAddition*> vRooAdd;
typedef std::vector<RooCatType*> vRooCat;
typedef std::pair<TString,double> pTStrDbl;
typedef std::pair<TString,TString> pTStrTStr;
typedef std::unordered_map<std::string,double> umapStrDbl;  // Apparently a TString isn't a 'hashable' type

TString FR_MDKEY = "fit_mdf";   // The name of the key for the fit result object from a multidimfit file
TString FR_DIAGKEY = "fit_s";    // Same thing, but for a fitDiagnostics file

RooFitResult* load_fitresult(TString fpath, TString fr_key, TFile* f) {
    RooFitResult* fr = nullptr;
    f = TFile::Open(fpath);
    if (!f) {
        std::cout << TString::Format("[WARNING] %s not found",fpath.Data()) << std::endl;
        return nullptr;
    }
    fr = (RooFitResult*) f->Get(fr_key);
    if (!fr) {
        std::cout << TString::Format("[WARNING] Missing fitresult: %s",fr_key.Data()) << std::endl;
        return nullptr;
    }
    return fr;
}

void struct_maker(int SR_selector) {
    //TFile* ws_file = TFile::Open("/scratch365/kmohrman/forFurong/ptz-lj0pt_fullR2_anatest18v07_withAutostats_withSys/ptz-lj0pt_fullR2_anatest18v07_withAutostats_withSys.root");
    std::string in_dir = "/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/test/card_ht_anatest25/";
    std::string out_dir = "/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/test/fit_results/";

    TString fpath_workspace = TString::Format("%s%s", in_dir.c_str(), "wps.root");
    TFile* ws_file = TFile::Open(fpath_workspace);
    
    RooWorkspace* ws = (RooWorkspace*) ws_file->Get("w");
    AnalysisCategory::th1x = ws->var("CMS_th1x");
    int bin_size = AnalysisCategory::th1x->numBins();
    for (uint i=0; i < bin_size; i++) {
        double half_int = i + 0.5;
        AnalysisCategory::index_mapping.push_back(half_int);
    }
    AnalysisCategory::roo_counter = 0;
    bool do_postfit = false; // true: do postfit, false: do prefit
    
    //TString fpath_datacard = "/afs/crc.nd.edu/user/f/fyan2/macrotesting/CMSSW_10_2_13/src/EFTFit/Fitter/test/card_ub_2017/combinedcard.txt";  // hard-coded path for the datacard for now.
    TString fpath_datacard = TString::Format("%s%s", in_dir.c_str(), "combinedcard.txt");
    std::map<std::string,TString> ch_map = get_channel_map( fpath_datacard.Data(), true);
    
    for (const auto & [lstring, ch] : ch_map) {
        int counter = 0;
        for(int i = 0; i < lstring.length(); i++) {
            if(lstring[i] == '_') {
                counter = i;
            }
        }
        std::string chstring = lstring.substr(0, counter);  // remove the last segment of the channel name, like "_lj0pt"
        auto nodeHandler = ch_map.extract(lstring);
        nodeHandler.key() = chstring;
        ch_map.insert(std::move(nodeHandler));
    }
    
    TFile* prefit_file = nullptr;
    TFile* postfit_file = nullptr;
    RooFitResult* prefit = nullptr;
    RooFitResult* postfit = nullptr;
    
    if (do_postfit) {
        postfit = load_fitresult(in_dir + "multidimfit.root", FR_MDKEY, postfit_file);
        ws->saveSnapshot("postfit_i",postfit->floatParsInit(),kTRUE);
        ws->saveSnapshot("postfit_f",postfit->floatParsFinal(),kTRUE);
    }
    else {
        prefit  = load_fitresult(in_dir + "prefit.root", FR_DIAGKEY, prefit_file);//"multidimfitNPonly.root", FR_MDKEY
        ws->saveSnapshot("prefit_i",prefit->floatParsInit(),kTRUE);
        ws->saveSnapshot("prefit_f",prefit->floatParsFinal(),kTRUE);        
    }
    
    // Create instances of our helper classes
    WSHelper ws_helper = WSHelper();
    RooArgSet pois = ws_helper.getPOIs(ws);

    std::vector<int> SR_index = {};
    SR_index.push_back(SR_selector); // The selector ranges from 0 to 10.
    std::vector<std::string> file_names = {};
    
    RooFitResult* fr;
    std::string folder_suffix;
    if (do_postfit) {
        ws->loadSnapshot("postfit_f");
        fr = postfit;
        folder_suffix = "postfit_ht_7bins";
    }
    else {
        ws->loadSnapshot("prefit_i");
        fr = prefit;
        folder_suffix = "prefit_ht_7bins";
    }
    std::string file_path = TString::Format("%sSR_%s/", out_dir.c_str(), folder_suffix.c_str()).Data();
    std::string file_path_sum = TString::Format("%sSR_sum_%s/", out_dir.c_str(), folder_suffix.c_str()).Data();
    
    cout << "After loading:" << endl;
    ws->allVars().Print("V");
    
    for (int idx: SR_index) 
    {
        TString SR = SR_list[idx];
        std::string file_name = TString::Format("SR%d", idx).Data();
        file_name = file_path + file_name;
        std::string file_name_sum = TString::Format("SR%d_sum", idx).Data();
        file_name_sum = file_path_sum + file_name_sum;
        
        cout << "Output file: " << file_name << endl;
        
        file_names.push_back(file_name);
        
        std::vector<TString> ch_to_plot = {};
        for (TString cat_name: cat_groups[SR.Data()]) {
            for (auto const& x : ch_map) {
                if (x.first == cat_name) {
                    ch_to_plot.push_back(x.second);
                    //cout << x.second << " added for the SR " << SR << endl;
                }
            }
        }
        CategoryManager cat_manager = CategoryManager(ws, ws_helper, ch_to_plot, YIELD_TABLE_ORDER);
        
        // Set up the child categories and merge them into the parent category
        std::vector<TString> mrg_groups = {};
        for (TString cat_name: cat_groups[SR.Data()]) {
            for (auto const& x : ch_map) {
                if (x.first == cat_name) {
                    mrg_groups.push_back(x.second);
                    //cout << x.second << endl;
                }
            }
        }
        //cat_manager.mergeCategories(SR.Data(), mrg_groups, YIELD_TABLE_ORDER);  // We don't merge the categories any more, instead we read them out individually.
        
        //////////////////////
        // Create some merged processes, i.e. create a new process which is the merger of all
        //  sub-processes of the corresponding 'cat_groups' entry
        //////////////////////
        for (TString mrg_name: ALL_PROCS) {
            cat_manager.mergeProcesses(mrg_name,mrg_name.Data());
        }
        /*
        cout << "Test starts!" << endl;
        AnalysisCategory* cat_test = cat_manager.getCategory(TString::Format("ch15"));
        cat_test->mergeAllProcesses();
        cat_test->mergeAllUnusedProcesses();
        cout << "Unused error: " << cat_test->allUnusedProcs->getPropagatedError(*fr) << endl;
        cout << "Used error: " << cat_test->allProcs->getPropagatedError(*fr) << endl;
        */
        // These are basically the bins of the histogram we want to make
        std::vector<AnalysisCategory*> cats_to_plot = cat_manager.getCategories(mrg_groups);
        
        PlotData data_to_plot;
        for (AnalysisCategory* ana_cat: cats_to_plot) {
            //cout << ana_cat->getName() << endl;

            for (uint idx=0; idx < bin_size; idx++) {
                data_to_plot.SR_name.push_back(ana_cat->getName());
                data_to_plot.data.push_back(ana_cat->getDataBin(idx));
                data_to_plot.sum.push_back(ana_cat->getExpSumBin(idx));
                data_to_plot.err.push_back(ana_cat->getExpSumErrorBin(idx, fr));

                for (TString proc: ALL_PROCS) {
                    // cout << "Getting per process yields for process " << proc << endl;

                    data_to_plot.procs[proc.Data()].push_back(ana_cat->getExpProcBin(proc, idx));
                    //data_to_plot.procs_error[proc.Data()].push_back(ana_cat->getExpProcErrorBin(proc, idx, fr));
                }
            }
        }

        cout << "Writing data..." << endl;
        write_PlotData_to_file(data_to_plot, file_name);
        cout << "Done writing data!" << endl;
        
        // Make PlotData struct of the merged categories (SRs) for the summary plots.
        cat_manager.mergeCategories(SR.Data(), mrg_groups, YIELD_TABLE_ORDER);
        std::vector<TString> SR_groups = {};
        SR_groups.push_back(SR);
        
        std::vector<AnalysisCategory*> SRs_to_plot = cat_manager.getCategories(SR_groups);
        PlotData sum_to_plot;
        for (AnalysisCategory* ana_cat: SRs_to_plot) {
            //cout << ana_cat->getName() << endl;
            //ana_cat->Print(fr);
            
            for (TString mrg_name: ALL_PROCS) {
                ana_cat->mergeProcesses(mrg_name,mrg_name.Data());
            }
            
            for (uint idx=0; idx < bin_size; idx++) {
                sum_to_plot.SR_name.push_back(ana_cat->getName());
                sum_to_plot.data.push_back(ana_cat->getDataBin(idx));
                sum_to_plot.sum.push_back(ana_cat->getExpSumBin(idx));
                sum_to_plot.err.push_back(ana_cat->getExpSumErrorBin(idx, fr));
                for (TString proc: ALL_PROCS) {
                    sum_to_plot.procs[proc.Data()].push_back(ana_cat->getExpProcBin(proc, idx));
                    //sum_to_plot.procs_error[proc.Data()].push_back(ana_cat->getExpProcErrorBin(proc, idx, fr));
                }
            }
        
            // std::cout << ana_cat->getName() << " " << ana_cat->getData() <<  " " << ana_cat->getExpSum() <<  " " << ana_cat->getExpSumError() << " ";
            // for (TString proc: ALL_PROCS) {
            //     std::cout << ana_cat->getExpProc(proc) << " ";
            // }
            // for (TString proc: ALL_PROCS) {
            //     std::cout << ana_cat->getExpProcError(proc, fr) << " ";
            // }
        
        }

        write_PlotData_to_file(sum_to_plot, file_name_sum);
    }    
    return;
}
