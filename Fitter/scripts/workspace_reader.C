//#include "TString.h"
//#include "TCanvas.h"
//#include "TH1D.h"
//#include "TTree.h"
//#include "TFile.h"
//#include "TList.h"

//#include "RooWorkspace.h"
//#include "RooFitResult.h"
//#include "RooProdPdf.h"
//#include "RooAddition.h"
//#include "RooRealVar.h"

//#include <vector>

#include "EFTFit/Fitter/interface/WSHelper.h"
#include "EFTFit/Fitter/interface/PlotMaker.h"

void iter_print(RooArgSet set,Int_t contents) {
    RooAbsArg *next = 0;
    RooFIter it = set.fwdIterator();
    while ((next=it.next())) {
        TString name = next->GetName();
        //if (!name.Contains("C_2lss_p_ee_2b_4j")) {
        //    continue;
        //} else if (!name.Contains("ttH")) {
        //    continue;
        //}

        //if (!name.BeginsWith("pdfbins_binC")) {
        //    continue;
        //}

        //if (!name.BeginsWith("pdf_binC_")) {
        //    continue;
        //}

        if (name.BeginsWith("n_exp_binC_")) {
            continue;
        }

        //if (name != "CMS_fakeObs") {
        //    continue;
        //}

        RooRealVar* rrv = dynamic_cast<RooRealVar *>(next);

        //next->printClassName(std::cout); std::cout << "::";
        //std::cout << name << std::endl;

        //next->Print();
        rrv->Print();
        rrv->getBinning().printArgs(std::cout); std::cout << std::endl;
        rrv->getBinning().printTitle(std::cout);

        std::cout << "Bins: " << rrv->getBinning().numBins() << std::endl;
        std::cout << "Err: " << rrv->getError() << std::endl;

        //next->Print("s");
        //next->Print("t");
        //next->Print("v");
        //next->printMultiline(std::cout,contents);
        //next->printTree(std::cout);
        //std::cout << "------------------------------------------------------------------------------" << std::endl;
    }
}

void iter_print(std::list<RooAbsData*> lst,Int_t contents) {
    for (auto d: lst) {
        TString name = d->GetName();
        std::cout << name << std::endl;
        d->Print();
        d->printMultiline(std::cout,contents);
    }
}


void runit(TString ws_fname, TString lim_fname, TString prefit_fname, TString full_fname, TString stat_fname) {
    TH1::SetDefaultSumw2(1);

    Int_t contents = RooPrintable::kName|RooPrintable::kClassName|RooPrintable::kArgs|RooPrintable::kValue;
    TString line_break = "--------------------------------------------------";

    TString OUTPUT_DIR = "src/EFTFit/Fitter/test/";

    std::vector<TString> all_procs {
        //"WZ","ZZ","WW",
        //"WWW","WWZ","WZZ","ZZZ",
        "Diboson","Triboson",
        //"singlet_tWchan","singletbar_tWchan",
        "charge_flips","fakes","ttGJets",
        "ttH","ttll","ttlnu","tllq","tHq"
    };
    std::vector<TString> sig_procs {"ttH","ttll","ttlnu","tllq","tHq"};
    //std::vector<TString> bkg_procs {"charge_flips","fakes","ttGJets","WZ","ZZ","WW","WWW","WWZ","WZZ","ZZZ"};
    std::vector<TString> bkg_procs {"charge_flips","fakes","convs","Diboson","Triboson"};
    std::vector<TString> diboson_procs {"Diboson"};
    //std::vector<TString> triboson_procs {"WWW","WWZ","WZZ","ZZZ"};
    //std::vector<TString> diboson_procs {"WZ","ZZ","WW"};
    std::vector<TString> triboson_procs {"Triboson"};
    std::vector<TString> syst_bkgs {"charge_flips","fakes"};
    
    TString fr_mdkey = "fit_mdf";
    TString fr_diagkey = "nuisances_prefit_res";

    TFile* ws_file        = TFile::Open(ws_fname);
    // TFile* limit_file     = TFile::Open(lim_fname);
    TFile* fr_prefit_file = TFile::Open(prefit_fname);
    //TFile* fr_full_file   = TFile::Open(full_fname);
    // TFile* fr_stat_file   = TFile::Open(stat_fname);

    // Workspace related objects
    RooWorkspace* ws = (RooWorkspace*) ws_file->Get("w");
    // Fit Result related objects
    RooFitResult* fr_prefit = (RooFitResult*) fr_prefit_file->Get(fr_diagkey);
    //RooFitResult* fr_full   = (RooFitResult*) fr_full_file->Get(fr_mdkey);
    // RooFitResult* fr_stat   = (RooFitResult*) fr_stat_file->Get(fr_mdkey);

    //ws->Print("t");

    WSHelper ws_helper = WSHelper();
    PlotMaker plot_maker = PlotMaker(ws,".","pdf");

    std::vector<RooAbsPdf*> all_pdfs      = ws_helper.getPdfs(ws,0,0,0,1);
    std::vector<RooAbsPdf*> other_pdfs    = ws_helper.getPdfs(ws,0,0,1,0);
    std::vector<RooAbsPdf*> sig_pdfs      = ws_helper.getPdfs(ws,0,0);
    std::vector<RooAbsPdf*> sig_nuis_pdfs = ws_helper.getPdfs(ws,0,1);
    std::vector<RooAbsPdf*> bkg_pdfs      = ws_helper.getPdfs(ws,1,0);
    std::vector<RooAbsPdf*> bkg_nuis_pdfs = ws_helper.getPdfs(ws,1,1);

    other_pdfs = ws_helper.filter(other_pdfs,"^shapeSig_C_",1);
    other_pdfs = ws_helper.filter(other_pdfs,"^shapeBkg_C_",1);
    other_pdfs = ws_helper.filter(other_pdfs,"^pdfbins_binC_",1);

    RooSimultaneous* model_s = (RooSimultaneous*)ws->pdf("model_s");
    RooSimultaneous* model_b = (RooSimultaneous*)ws->pdf("model_b");

    RooCategory* CMS_channel = ws->cat("CMS_channel");

    //for (RooAbsPdf* pdf: bkg_pdfs) std::cout << pdf->GetName() << std::endl;
    //std::cout << line_break << std::endl;
    //for (RooAbsPdf* pdf: sig_pdfs) std::cout << pdf->GetName() << std::endl;
    //std::cout << line_break << std::endl;
    //for (RooAbsPdf* pdf: other_pdfs) std::cout << pdf->GetName() << std::endl;

    std::vector<RooCatType*> all_cat_types = ws_helper.getTypes(ws,"CMS_channel");       // The categories used in the analysis
    std::vector<RooAbsReal*> all_exp_funcs = ws_helper.getExpCatFuncs(ws,all_cat_types); // These are the expected rate values from the datacard

    // Category names, grouped together by lepton count
    std::vector<RooCatType*> cats_2lss = ws_helper.filter(all_cat_types,"C_2lss");
    //std::vector<TRegexp> my_regs {".*p_ee_2b_ge7j",".*p_ee_2b_4j"};
    //cats_2lss = ws_helper.filter(cats_2lss,my_regs);
    std::vector<RooCatType*> cats_3l   = ws_helper.filter(all_cat_types,"C_3l");
    std::vector<RooCatType*> cats_4l   = ws_helper.filter(all_cat_types,"C_4l");

    std::vector<RooCatType*> cats_3l_sfz  = ws_helper.filter(cats_3l,"_sfz_",false);
    std::vector<RooCatType*> cats_3l_nsfz = ws_helper.filter(cats_3l,"_sfz_",true);
    
    std::vector<RooCatType*> cats_2lss_p = ws_helper.filter(cats_2lss,"p");
    std::vector<RooCatType*> cats_2lss_m = ws_helper.filter(cats_2lss,"m");
    std::vector<RooCatType*> cats_3l_nsfz_p_1b = ws_helper.filter(cats_3l_nsfz,"p_1b");
    std::vector<RooCatType*> cats_3l_nsfz_m_1b = ws_helper.filter(cats_3l_nsfz,"m_1b");
    std::vector<RooCatType*> cats_3l_nsfz_p_2b = ws_helper.filter(cats_3l_nsfz,"p_2b");
    std::vector<RooCatType*> cats_3l_nsfz_m_2b = ws_helper.filter(cats_3l_nsfz,"m_2b");
    std::vector<RooCatType*> cats_3l_sfz_1b = ws_helper.filter(cats_3l_sfz,"1b");
    std::vector<RooCatType*> cats_3l_sfz_2b = ws_helper.filter(cats_3l_sfz,"2b");

    // Expected events, grouped together by lepton count
    std::vector<RooAbsReal*> exp_2lss = ws_helper.getExpCatFuncs(ws,cats_2lss);
    std::vector<RooAbsReal*> exp_3l   = ws_helper.getExpCatFuncs(ws,cats_3l);
    std::vector<RooAbsReal*> exp_4l   = ws_helper.getExpCatFuncs(ws,cats_4l);

    std::vector<RooAbsReal*> exp_3l_sfz  = ws_helper.getExpCatFuncs(ws,cats_3l_sfz);
    std::vector<RooAbsReal*> exp_3l_nsfz = ws_helper.getExpCatFuncs(ws,cats_3l_nsfz);
    
    std::vector<RooAbsReal*> exp_2lss_p  = ws_helper.getExpCatFuncs(ws,cats_2lss_p);
    std::vector<RooAbsReal*> exp_2lss_m  = ws_helper.getExpCatFuncs(ws,cats_2lss_m);
    std::vector<RooAbsReal*> exp_3l_nsfz_p_1b  = ws_helper.getExpCatFuncs(ws,cats_3l_nsfz_p_1b);
    std::vector<RooAbsReal*> exp_3l_nsfz_m_1b  = ws_helper.getExpCatFuncs(ws,cats_3l_nsfz_m_1b);
    std::vector<RooAbsReal*> exp_3l_nsfz_p_2b  = ws_helper.getExpCatFuncs(ws,cats_3l_nsfz_p_2b);
    std::vector<RooAbsReal*> exp_3l_nsfz_m_2b  = ws_helper.getExpCatFuncs(ws,cats_3l_nsfz_m_2b);
    std::vector<RooAbsReal*> exp_3l_sfz_1b  = ws_helper.getExpCatFuncs(ws,cats_3l_sfz_1b);
    std::vector<RooAbsReal*> exp_3l_sfz_2b  = ws_helper.getExpCatFuncs(ws,cats_3l_sfz_2b);

    // Grouped expected events, summed over all processes
    std::vector<RooAddition*> summed_2lss = ws_helper.getSummedCats(exp_2lss,cats_2lss,all_procs);
    std::vector<RooAddition*> summed_3l   = ws_helper.getSummedCats(exp_3l,cats_3l,all_procs);
    std::vector<RooAddition*> summed_4l   = ws_helper.getSummedCats(exp_4l,cats_4l,all_procs);

    // Observed data yields grouped by lepton count
    std::vector<RooAbsData*> obs_data_2lss = ws_helper.getObsData(ws,"data_obs","CMS_channel",cats_2lss);
    std::vector<RooAbsData*> obs_data_3l   = ws_helper.getObsData(ws,"data_obs","CMS_channel",cats_3l);
    std::vector<RooAbsData*> obs_data_4l   = ws_helper.getObsData(ws,"data_obs","CMS_channel",cats_4l);

    // Examples to merge certain groups of categories into a single object
    std::vector<TString> subcats_2lss {
        //"p_ee","p_emu","p_mumu",
        //"m_ee","m_emu","m_mumu",
        "p","m"
    };
    std::vector<TString> subcats_3l_nsfz {
        //"ppp","mmm","mix"
        "mix_m_1b","mix_p_1b","mix_m_2b","mix_p_2b"
    };
    std::vector<TString> subcats_3l_sfz {
        "mix_sfz_1b","mix_sfz_2b"
    };
    std::vector<TString> subcats_4l {
        ""
    };

    std::vector<std::pair<TString,double> > data_all,data_2lss,data_3l,data_4l;
    for (auto d: obs_data_2lss) {
        TString name = d->GetName();
        double sum = d->sumEntries();
        data_all.push_back(std::make_pair(name,sum));
        data_2lss.push_back(std::make_pair(name,sum));
    }
    for (auto d: obs_data_3l) {
        TString name = d->GetName();
        double sum = d->sumEntries();
        data_all.push_back(std::make_pair(name,sum));
        data_3l.push_back(std::make_pair(name,sum));
    }
    for (auto d: obs_data_4l) {
        TString name = d->GetName();
        double sum = d->sumEntries();
        data_all.push_back(std::make_pair(name,sum));
        data_4l.push_back(std::make_pair(name,sum));
    }

    std::vector<std::pair<TString,double> > merged_data,mdata_2lss,mdata_3l_sfz,mdata_3l_nsfz,mdata_4l;

    mdata_2lss    = ws_helper.mergeDataBins(obs_data_2lss,"2lss",cats_2lss   ,subcats_2lss);
    mdata_3l_nsfz = ws_helper.mergeDataBins(obs_data_3l  ,"3l"  ,cats_3l_nsfz,subcats_3l_nsfz);
    mdata_3l_sfz  = ws_helper.mergeDataBins(obs_data_3l  ,"3l"  ,cats_3l_sfz ,subcats_3l_sfz);
    mdata_4l      = ws_helper.mergeDataBins(obs_data_4l  ,"4l"  ,cats_4l     ,subcats_4l);

    //merged_data.insert(merged_data.end(),mdata_2lss.begin(),mdata_2lss.end());
    //merged_data.insert(merged_data.end(),mdata_3l_sfz.begin(),mdata_3l_sfz.end());
    //merged_data.insert(merged_data.end(),mdata_3l_nsfz.begin(),mdata_3l_nsfz.end());
    //merged_data.insert(merged_data.end(),mdata_4l.begin(),mdata_4l.end());
    for (auto d: mdata_2lss) merged_data.push_back(d);
    for (auto d: mdata_3l_sfz) merged_data.push_back(d);
    for (auto d: mdata_3l_nsfz) merged_data.push_back(d);
    for (auto d: mdata_4l) merged_data.push_back(d);

    std::vector<TString> yield_procs = all_procs;//{"WW","WZ","ZZ","WWW","WWZ","WZZ","ZZZ"};//{"ttH","ttll","ttlnu"};

    std::vector<RooAddition*> yields_all,yields_2lss,yields_3l,yields_3l_non_sfz,yields_3l_sfz,yields_4l;
    std::vector<RooAddition*> yields_2lss_p,yields_2lss_m,yields_3l_nsfz_p_1b,yields_3l_nsfz_m_1b,yields_3l_nsfz_p_2b,yields_3l_nsfz_m_2b,yields_3l_sfz_1b,yields_3l_sfz_2b;
    std::vector<RooAddition*> merged_yields,merged_2lss,merged_3l_nsfz,merged_3l_sfz,merged_4l;
    merged_2lss    = ws_helper.mergeSubCats(exp_2lss   ,"2lss",yield_procs,subcats_2lss);
    merged_3l_sfz  = ws_helper.mergeSubCats(exp_3l_sfz ,"3l"  ,yield_procs,subcats_3l_sfz);
    merged_3l_nsfz = ws_helper.mergeSubCats(exp_3l_nsfz,"3l"  ,yield_procs,subcats_3l_nsfz);
    merged_4l      = ws_helper.mergeSubCats(exp_4l     ,"4l"  ,yield_procs,subcats_4l);


    // This will create summed yield bins grouped in a specific way
    //merged_yields.insert(merged_yields.end(),merged_2lss.begin(),merged_2lss.end());
    //merged_yields.insert(merged_yields.end(),merged_3l_sfz.begin(),merged_3l_sfz.end());
    //merged_yields.insert(merged_yields.end(),merged_3l_nsfz.begin(),merged_3l_nsfz.end());
    //merged_yields.insert(merged_yields.end(),merged_4l.begin(),merged_2lss.end());
    for (RooAddition* f: merged_2lss) merged_yields.push_back(f);
    for (RooAddition* f: merged_3l_nsfz) merged_yields.push_back(f);
    for (RooAddition* f: merged_3l_sfz) merged_yields.push_back(f);
    for (RooAddition* f: merged_4l) merged_yields.push_back(f);

    // This will create a yield bin for every bin in the workspace
    // Note: The categories will be prepended with "n_exp_bin"
    for (RooAbsReal* f: exp_2lss) {
        yields_all.push_back((RooAddition*)f);
        yields_2lss.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_3l_sfz) {
        yields_all.push_back((RooAddition*)f);
        yields_3l_sfz.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_3l_nsfz) {
        yields_all.push_back((RooAddition*)f);
        yields_3l_non_sfz.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_4l) {
        yields_all.push_back((RooAddition*)f);
        yields_4l.push_back((RooAddition*)f);
    }
    
    for (RooAbsReal* f: exp_2lss_p) {
        yields_2lss_p.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_2lss_m) {
        yields_2lss_m.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_3l_nsfz_p_1b) {
        yields_3l_nsfz_p_1b.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_3l_nsfz_m_1b) {
        yields_3l_nsfz_m_1b.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_3l_nsfz_p_2b) {
        yields_3l_nsfz_p_2b.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_3l_nsfz_m_2b) {
        yields_3l_nsfz_m_2b.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_3l_sfz_1b) {
        yields_3l_sfz_1b.push_back((RooAddition*)f);
    }
    for (RooAbsReal* f: exp_3l_sfz_2b) {
        yields_3l_sfz_2b.push_back((RooAddition*)f);
    }

    RooArgSet pdfs = ws->allPdfs();
    RooArgSet cats = ws->allCats();
    RooArgSet vars = ws->allVars();
    RooArgSet funcs = ws->allFunctions();
    RooArgSet cat_funcs = ws->allCatFunctions(); // Seems to be empty

    //iter_print(vars,contents);

    //std::list<RooAbsData*> data = ws->allData();
    //std::list<RooAbsData*> emb_data = ws->allEmbeddedData();    // Seems to be empty

    // Post-fit related objects
    //TDirectoryFile* toys = (TDirectoryFile*)limit_file->Get("toys"); // This appears to be empty
    //TTree* lim = (TTree*)limit_file->Get("limit");
    //toys->GetListOfKeys()->Print();
    //lim->Dump();
    //lim->GetListOfBranches()->Print();
    //lim->Scan("limit:limitErr:syst:iToy:iSeed:iChannel:ctW:ctZ");

    gStyle->SetOptStat(0);

    //plot_maker.makeCorrelationPlot("fr_prefit_corr",fr_prefit);
    //plot_maker.makeCorrelationPlot("fr_postfit_corr",fr_full);
    //plot_maker.makeCorrelationPlot("fr_stats_corr",fr_stat);

    //RooArgSet pars_init  = fr_full->floatParsInit();
    //RooArgSet pars_final = fr_full->floatParsFinal();
    //RooArgSet pars_const = fr_full->constPars();

    // For the prefit, the initial and final param values are the same
    RooArgSet prefit_pars_init  = fr_prefit->floatParsInit();
    RooArgSet prefit_pars_final = fr_prefit->floatParsFinal();

    //RooArgSet postfit_pars_init  = fr_full->floatParsInit();
    //RooArgSet postfit_pars_final = fr_full->floatParsFinal();

    ws->saveSnapshot("prefit_pars",prefit_pars_init,kTRUE);
    //ws->saveSnapshot("prefit_pars" ,postfit_pars_init,kTRUE);
    //ws->saveSnapshot("postfit_pars",postfit_pars_final,kTRUE);

    //ws->saveSnapshot("pars_init" ,pars_init,kTRUE);
    //ws->saveSnapshot("pars_final",pars_final,kTRUE);

    // RooRealVar* rrv_ctW = (RooRealVar*)pars_init.find("ctW");
    // RooRealVar* rrv_ctZ = (RooRealVar*)pars_init.find("ctZ");

    ////////////////////////////////////////////////////////////////////////////////////////////////

    plot_maker.setFitResult(fr_prefit,fr_prefit);
    plot_maker.noratio = true;
    plot_maker.isfakedata = false;
    plot_maker.splitunc = false;
    plot_maker.nodata = false;

    ws->loadSnapshot("prefit_pars");
    //plot_maker.makeYieldsPlot(merged_data,merged_yields   ,yield_procs,"yields_prefit_merged");
    //plot_maker.makeYieldsPlot(data_all,yields_all         ,yield_procs,"yields_prefit_all");
    //plot_maker.makeYieldsPlot(data_all,yields_2lss        ,yield_procs,"yields_prefit_2lss");
    //plot_maker.makeYieldsPlot(data_all,yields_3l_sfz      ,yield_procs,"yields_prefit_3l_sfz");
    //plot_maker.makeYieldsPlot(data_all,yields_3l_non_sfz  ,yield_procs,"yields_prefit_3l_non_sfz");
    plot_maker.makeYieldsPlot(data_all,yields_2lss_p      ,yield_procs,"yields_prefit_2lss_p");
    plot_maker.makeYieldsPlot(data_all,yields_2lss_m      ,yield_procs,"yields_prefit_2lss_m");
    plot_maker.makeYieldsPlot(data_all,yields_3l_nsfz_p_1b,yield_procs,"yields_prefit_3l_nsfz_p_1b");
    plot_maker.makeYieldsPlot(data_all,yields_3l_nsfz_m_1b,yield_procs,"yields_prefit_3l_nsfz_m_1b");
    plot_maker.makeYieldsPlot(data_all,yields_3l_nsfz_p_2b,yield_procs,"yields_prefit_3l_nsfz_p_2b");
    plot_maker.makeYieldsPlot(data_all,yields_3l_nsfz_m_2b,yield_procs,"yields_prefit_3l_nsfz_m_2b");
    plot_maker.makeYieldsPlot(data_all,yields_3l_sfz_1b   ,yield_procs,"yields_prefit_3l_sfz_1b");
    plot_maker.makeYieldsPlot(data_all,yields_3l_sfz_2b   ,yield_procs,"yields_prefit_3l_sfz_2b");
    plot_maker.makeYieldsPlot(data_all,yields_4l          ,yield_procs,"yields_prefit_4l");

    std::cout << line_break << std::endl;

    // plot_maker.nodata = false;
    //plot_maker.setFitResult(fr_full,fr_full);

    //ws->loadSnapshot("postfit_pars");
    //plot_maker.makeYieldsPlot(merged_data,merged_yields ,yield_procs,"yields_postfit_merged");
    //plot_maker.makeYieldsPlot(data_all,yields_all       ,yield_procs,"yields_postfit_all");
    //plot_maker.makeYieldsPlot(data_all,yields_2lss      ,yield_procs,"yields_postfit_2lss");
    //plot_maker.makeYieldsPlot(data_all,yields_3l_sfz    ,yield_procs,"yields_postfit_3l_sfz");
    //plot_maker.makeYieldsPlot(data_all,yields_3l_non_sfz,yield_procs,"yields_postfit_3l_non_sfz");
    //plot_maker.makeYieldsPlot(data_all,yields_4l        ,yield_procs,"yields_postfit_4l");

    ////////////////////////////////////////////////////////////////////////////////////////////////

    //Roo1DTable* my_table = ws->data("data_obs")->table(*(ws->cat("CMS_channel")));
}


void workspace_reader() {
    // TString base_dir = "/afs/crc.nd.edu/user/a/awightma/CMSSW_Releases/CMSSW_8_1_0/src/EFTFit/Fitter/test/fromTony/";
    TString base_dir = "/afs/crc.nd.edu/user/a/awightma/CMSSW_Releases/CMSSW_8_1_0/src/EFTFit/Fitter/test/";
    // TString tony_dir = "/afs/crc.nd.edu/user/a/alefeld/Public/ForAndrew/";
    // TString in_dir  = "src/EFTFit/Fitter/test/ana12asimov_dir/";
    // TString in_dir  = "src/EFTFit/Fitter/test/anatest12_Jan18btagReqs/16D_AllSysts_AllFits_SMdata/";

    // Naming based on output from combine_helper.py
    // TString ws_fname    = "16D.root";    // Made from text2workspace.py, which converts a datacard to a RooWorkspace
    TString ws_fname = "SMWorkspace.root";  // Made from text2workspace.py, using SM signals as POIs
    TString limit_fname = "higgsCombinePostfit.MultiDimFit.mH120.root";  // Made by combine running on pre-fit workspace ('16D.root')
    TString fr_prefit_fname = "fitDiagnosticsPrefit.root";
    TString fr_full_fname = "multidimfitPostfit.root";
    TString fr_stat_fname = "multidimfitStats.root";

    // Other names
    //TString fr_full_fname = "fitDiagnosticsEFT.root";   // Made by combine running on pre-fit workspace ('16D.root')
    //TString fr_key = "nuisances_prefit_res";

    // File names from Tony
    // ws_fname = "SMWorkspace.root";
    // fr_full_fname = "multidimfit.SM.Private.Float.Oct9.FullJES.root";
    // fr_full_fname = "multidimfit.SM.Central.Float.Oct9.FullJES.root";

    // TString ws_fpath     = base_dir + "SM_impacts_2019-10-10_1959_ana24_private_test_cminDefaultMinimizerStategy-0/" + ws_fname;
    // TString ws_fpath     = "/afs/crc.nd.edu/user/a/alefeld/Private/EFT/CMSSW_8_1_0/src/EFTFit/Fitter/test/16DWorkspace.root";
    // TString lim_fpath    = "";
    // TString prefit_fpath = "/afs/crc.nd.edu/user/a/alefeld/Private/EFT/CMSSW_8_1_0/src/EFTFit/Fitter/test/fitDiagnosticsEFTFD.root";
    // TString full_fpath = "/afs/crc.nd.edu/user/a/alefeld/Private/EFT/CMSSW_8_1_0/src/EFTFit/Fitter/test/fitDiagnosticsEFTFD.root";
    // TString full_fpath   = tony_dir + fr_full_fname;
    // TString full_fpath   = "";
    // TString stat_fpath   = "";

    TString sub_dir = "data2017v1/SM_fitting_2019-12-06_ana32_private/";
    TString ws_fpath     = base_dir + sub_dir + ws_fname;
    TString prefit_fpath = base_dir + sub_dir + fr_prefit_fname;
    TString full_fpath   = base_dir + sub_dir + fr_full_fname;
    TString lim_fpath  = "";
    TString stat_fpath = "";

    runit(ws_fpath,lim_fpath,prefit_fpath,full_fpath,stat_fpath);
}
