// #include "workspace_helper.h"
// #include "plotmaker.h"

#include "EFTFit/Fitter/interface/WSHelper.h"
#include "EFTFit/Fitter/interface/PlotMaker.h"
#include "EFTFit/Fitter/interface/AnalysisCategory.h"

// #include "tdrstyle.C"

/*
Desc:
    Monolithic ROOT macro for producing analysis plots/graphs/tables. It takes as input a directory
    that contains a root file with a RooWorkspace object inside of it, assumed to be called '16D.root'
    for an EFT workspace and 'SMWorkspace.root' for a SM workspace. The directory is semi-optionally
    expected to have other root files that contain a RooFitResult object, which is obtained from doing
    a particular combine fit using the associated RooWorkspace. Almost all of these files were generated
    by making use of the 'combine_helper.py' python script

    The bulk of the file reading and macro configuration occurs in the 'runit' function, which takes
    care of reading and loading the relevant .root files located in the input directory that you
    specified.

    There are a number of boolean flags for easily turning off and on which plots/tables
    you want to have made.

    runit Flags:
        incl_print_info
        incl_summary_plots
        incl_summary_gif_plots
        incl_njets_plots
        incl_fluct_plots

Important Note 1:
    The code for making WC fluctuation plots rely heavily on being given a directory containing
    files with RooFitResult objects, which are named in a very specific way. This supplementary
    directory is currently just hardcoded and is not determined in any way based on the user given
    input directory for reading the normal RooWorkspace root files. For specifics on how these specially
    made RooFitResult objects are read/used, please take a look at the 'get_extremum_fitresult' function
    which handles getting all of the information needed to produce the WC fluctuation plots.

    Currently, the hardcoded directory is pointing to an area in Andrew's AFS area, which should
    be accessible to anyone running from earth.

Important Note 2:
    The root files in the hardcoded supplementary directory were produced using a specific RooWorkspace,
    which means that to be fully consistent you want to make sure that the RooWorkspace file in the
    user specified input directory (in this case the '16D.root' file) is made in a consistent way as
    the one used to produce the RooFitResult objects from the hardcoded supplementary directory.

    Pracically speaking, this just means that the combine datacards used to make the RooWorkspace
    file are the same and that no yield manipulation was done (e.g. switching over to using the asmiov
    dataset). However, if the format of the datacards changes (e.g. adding/removing certain categories),
    then this will likely introduce an inconsistency between the hardcoded supplementary files and those
    made in the input directory you specified

Important Note 3:
    All output files will be produced in whatever directory you run the script from, i.e. the 'out_dir'
    variable currently does nothing
*/

typedef std::vector<TString> vTStr;
typedef std::vector<RooAddition*> vRooAdd;
typedef std::vector<RooCatType*> vRooCat;
typedef std::pair<TString,double> pTStrDbl;
typedef std::pair<TString,TString> pTStrTStr;
typedef std::unordered_map<std::string,double> umapStrDbl;  // Apparently a TString isn't a 'hashable' type

// Container for info found by the 'get_extremum_fitresult' function from a particular AnalysisCategory
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

// Fancy structure for containing the info needed to plot an 'off-scale' point in the ratio fluct plots 
struct OffScalePoint {
    double nom_val;
    double hi_val;
    double lo_val;
    double bin_center;
    double axis_max;
    int hist_bin;
    int direction;  // should be +1 (up) or -1 (down)
    Color_t clr;
    TArrow* arrow;
    TLatex* latex;
};

// This determines the ordering of the THStack histograms
vTStr ALL_PROCS {
    "charge_flips","fakes",
    "Diboson","Triboson",
    // "ttGJets",   // This got renamed to 'convs'
    "convs",
    //"WZ","ZZ","WW",
    //"WWW","WWZ","WZZ","ZZZ",
    //"singlet_tWchan","singletbar_tWchan",
    "ttH","ttll","ttlnu","tllq","tHq"
    // "ttlnu","ttll","ttH","tllq","tHq"
};

vTStr YIELD_TABLE_ORDER {
    "Diboson","Triboson","charge_flips","fakes","convs",
    "ttlnu","ttll","ttH","tllq","tHq"
};

vTStr SIG_PROCS {
    "ttlnu","ttll","ttH","tllq","tHq"
};

vTStr BKGD_PROCS {
    "Diboson","Triboson","charge_flips","fakes","convs",
};

// How to name bin categories in histograms
std::unordered_map<std::string,std::string> BIN_LABEL_MAP {
    {"2lss_m","2lss(-)"},
    {"2lss_p","2lss(+)"},
    {"3l_p_nsfz_1b","3l(+)1b"},
    {"3l_m_nsfz_1b","3l(-)1b"},
    {"3l_p_nsfz_2b","3l(+)2b"},
    {"3l_m_nsfz_2b","3l(-)2b"},
    // {"3l_sfz_1b","3l SFZ 1b"},
    {"3l_sfz_1b","SFZ1b"},
    // {"3l_sfz_2b","3l SFZ 2b"},
    {"3l_sfz_2b","SFZ2b"},

    {"C_2lss_p_2b_4j","4j"},
    {"C_2lss_p_2b_5j","5j"},
    {"C_2lss_p_2b_6j","6j"},
    {"C_2lss_p_2b_ge7j","ge7j"},

    {"C_2lss_m_2b_4j","4j"},
    {"C_2lss_m_2b_5j","5j"},
    {"C_2lss_m_2b_6j","6j"},
    {"C_2lss_m_2b_ge7j","ge7j"},

    {"C_3l_mix_p_1b_2j","2j"},
    {"C_3l_mix_p_1b_3j","3j"},
    {"C_3l_mix_p_1b_4j","4j"},
    {"C_3l_mix_p_1b_ge5j","ge5j"},

    {"C_3l_mix_m_1b_2j","2j"},
    {"C_3l_mix_m_1b_3j","3j"},
    {"C_3l_mix_m_1b_4j","4j"},
    {"C_3l_mix_m_1b_ge5j","ge5j"},

    {"C_3l_mix_p_2b_2j","2j"},
    {"C_3l_mix_p_2b_3j","3j"},
    {"C_3l_mix_p_2b_4j","4j"},
    {"C_3l_mix_p_2b_ge5j","ge5j"},

    {"C_3l_mix_m_2b_2j","2j"},
    {"C_3l_mix_m_2b_3j","3j"},
    {"C_3l_mix_m_2b_4j","4j"},
    {"C_3l_mix_m_2b_ge5j","ge5j"},

    {"C_3l_mix_sfz_1b_2j","2j"},
    {"C_3l_mix_sfz_1b_3j","3j"},
    {"C_3l_mix_sfz_1b_4j","4j"},
    {"C_3l_mix_sfz_1b_ge5j","ge5j"},

    {"C_3l_mix_sfz_2b_2j","2j"},
    {"C_3l_mix_sfz_2b_3j","3j"},
    {"C_3l_mix_sfz_2b_4j","4j"},
    {"C_3l_mix_sfz_2b_ge5j","ge5j"},

    {"C_4l_2b_2j","2j"},
    {"C_4l_2b_3j","3j"},
    {"C_4l_2b_ge4j","ge4j"},
};

// How to color code the processes
std::unordered_map<std::string,Color_t> PROCESS_COLOR_MAP {
    {"ttlnu",kBlue},
    {"ttll",kGreen+1},
    {"ttH",kRed+1},
    {"tllq",kPink+1},
    // {"tHq",kCyan},
    {"tHq",kCyan+1},
    {"charge_flips",kAzure-9},
    {"fakes",kYellow-7},
    {"Diboson",kMagenta},
    {"Triboson",kSpring+1},
    {"convs",kGreen}
};

// What marker to use for each process
std::unordered_map<std::string,int> PROCESS_MARKER_MAP {
    {"ttlnu",kFullCircle},      // kFullCircle
    {"ttll",kFullSquare},       // kFullSquare
    {"ttH",kFullTriangleUp},  // kFullTriangleUp
    {"tllq",kFullTriangleDown}, // kFullTriangleDown
    {"tHq",kFullDiamond}   // kFullDiamond
    // {"charge_flips",},
    // {"fakes",},
    // {"Diboson",},
    // {"Triboson",},
    // {"convs",}
};

// What marker to use for each process
std::unordered_map<std::string,int> PROCESS_MARKER_SIZE_MAP {
    {"ttlnu",1},
    {"ttll" ,1},
    {"ttH"  ,1},
    {"tllq" ,1},
    {"tHq"  ,1},

    {"charge_flips",1},
    {"fakes",1},
    {"Diboson",1},
    {"Triboson",1},
    {"convs",1}
};

// How the processes should be labeled in the legend
std::unordered_map<std::string,std::string> PROCESS_LABEL_MAP {
    {"ttlnu","ttl#nu"},
    {"charge_flips","ChargeFlips"},
    {"fakes","Fakes"},
    {"convs","Convs"}
};

// How the processes should be named in the latex yield table
std::unordered_map<std::string,std::string> YIELD_LABEL_MAP {
    {"ttH","\\ttH"},
    {"tHq","\\tHq"},
    {"ttll","\\ttll"},
    {"tllq","\\tllq"},
    {"ttlnu","\\ttlnu"},
    {"charge_flips","Charge Flips"},
    {"fakes","Fakes"},
    {"convs","Conversions"}
};


// How the WCs (w/o Lambda fraction) should be latex styled in the plots
std::unordered_map<std::string,std::string> WC_LABEL_MAP {
    {"ctW"  , "#it{c}_{tW}"},
    {"ctZ"  , "#it{c}_{tZ}"},
    {"ctp"  , "#it{c}_{t#varphi}"},
    {"cpQM" , "#it{c}^{-}_{#varphiQ}"},
    {"ctG"  , "#it{c}_{tG}"},
    {"cbW"  , "#it{c}_{bW}"},
    {"cpQ3" , "#it{c}^{3(#it{l})}_{#varphiQ}"},
    {"cptb" , "#it{c}_{#varphitb}"},
    {"cpt"  , "#it{c}_{#varphit}"},
    {"cQl3i", "#it{c}^{3(#it{l})}_{Ql}"},
    {"cQlMi", "#it{c}^{-(#it{l})}_{Ql}"},
    {"cQei" , "#it{c}^{(#it{l})}_{Qe}"},
    {"ctli" , "#it{c}^{(#it{l})}_{tl}"},
    {"ctei" , "#it{c}^{(#it{l})}_{te}"},
    {"ctlSi", "#it{c}^{S(#it{l})}_{t}"},
    {"ctlTi", "#it{c}^{T(#it{l})}_{t}"}
};

// How the WCs (w/o Lambda fraction) should be latex styled in the plots
std::unordered_map<std::string,std::string> WC_LAMBDA_LABEL_MAP {
    {"ctW"  , "#it{c}_{tW}/#Lambda^{2}"},
    {"ctZ"  , "#it{c}_{tZ}/#Lambda^{2}"},
    {"ctp"  , "#it{c}_{t#varphi}/#Lambda^{2}"},
    {"cpQM" , "#it{c}^{-}_{#varphiQ}/#Lambda^{2}"},
    {"ctG"  , "#it{c}_{tG}/#Lambda^{2}"},
    {"cbW"  , "#it{c}_{bW}/#Lambda^{2}"},
    {"cpQ3" , "#it{c}^{3(#it{l})}_{#varphiQ}/#Lambda^{2}"},
    {"cptb" , "#it{c}_{#varphitb}/#Lambda^{2}"},
    {"cpt"  , "#it{c}_{#varphit}/#Lambda^{2}"},
    {"cQl3i", "#it{c}^{3(#it{l})}_{Ql}/#Lambda^{2}"},
    {"cQlMi", "#it{c}^{-(#it{l})}_{Ql}/#Lambda^{2}"},
    {"cQei" , "#it{c}^{(#it{l})}_{Qe}/#Lambda^{2}"},
    {"ctli" , "#it{c}^{(#it{l})}_{tl}/#Lambda^{2}"},
    {"ctei" , "#it{c}^{(#it{l})}_{te}/#Lambda^{2}"},
    {"ctlSi", "#it{c}^{S(#it{l})}_{t}/#Lambda^{2}"},
    {"ctlTi", "#it{c}^{T(#it{l})}_{t}/#Lambda^{2}"}
};

// How the WCs (with Lambda and latex fraction) should be latex styled in the plots
std::unordered_map<std::string,std::string> WC_LATEX_FRACTION_LABEL_MAP {
    {"ctW"  , "#frac{#it{c}_{tW}}{#Lambda^{2}}"},
    {"ctZ"  , "#frac{#it{c}_{tZ}}{#Lambda^{2}}"},
    {"ctp"  , "#frac{#it{c}_{t#varphi}}{#Lambda^{2}}"},
    {"cpQM" , "#frac{#it{c}^{-}_{#varphiQ}}{#Lambda^{2}}"},
    {"ctG"  , "#frac{#it{c}_{tG}}{#Lambda^{2}}"},
    {"cbW"  , "#frac{#it{c}_{bW}}{#Lambda^{2}}"},
    {"cpQ3" , "#frac{#it{c}^{3(#it{l})}_{#varphiQ}}{#Lambda^{2}}"},
    {"cptb" , "#frac{#it{c}_{#varphitb}}{#Lambda^{2}}"},
    {"cpt"  , "#frac{#it{c}_{#varphit}}{#Lambda^{2}}"},
    {"cQl3i", "#frac{#it{c}^{3(#it{l})}_{Ql}}{#Lambda^{2}}"},
    {"cQlMi", "#frac{#it{c}^{-(#it{l})}_{Ql}}{#Lambda^{2}}"},
    {"cQei" , "#frac{#it{c}^{(#it{l})}_{Qe}}{#Lambda^{2}}"},
    {"ctli" , "#frac{#it{c}^{(#it{l})}_{tl}}{#Lambda^{2}}"},
    {"ctei" , "#frac{#it{c}^{(#it{l})}_{te}}{#Lambda^{2}}"},
    {"ctlSi", "#frac{#it{c}^{S(#it{l})}_{t}}{#Lambda^{2}}"},
    {"ctlTi", "#frac{#it{c}^{T(#it{l})}_{t}}{#Lambda^{2}}"}
};


// Scale the ratio histograms for certain process when doing 'make_fluct_compare_plots' plots
std::unordered_map<std::string,double> SCALE_PROCESS_RATIO_FLUCT {
    {"tHq",15}
};

// Basically the null hypothesis
std::unordered_map<std::string,double> SM_POIS {
    {"ctW"   ,0.0},
    {"ctZ"   ,0.0},
    {"ctp"   ,0.0},
    {"cpQM"  ,0.0},
    {"ctG"   ,0.0},
    {"cbW"   ,0.0},
    {"cpQ3"  ,0.0},
    {"cptb"  ,0.0},
    {"cpt"   ,0.0},
    {"cQl3i" ,0.0},
    {"cQlMi" ,0.0},
    {"cQei"  ,0.0},
    {"ctli"  ,0.0},
    {"ctei"  ,0.0},
    {"ctlSi" ,0.0},
    {"ctlTi" ,0.0}
};

// Come from Brent's 1D grid scans (other WCs floating)
std::unordered_map<std::string,double> BEST_FIT_POIS {
    {"ctW"  ,-0.58}, //-0.860;
    {"ctZ"  ,-0.68}, //-0.957;
    // {"ctp"  ,-7.85}, // From other scans (i.e. profiled)
    {"ctp"  ,25.50}, //26.167; // From dedicated 1D scan
    {"cpQM" ,-1.07}, //0.000;
    {"ctG"  ,-0.85}, //-0.750;
    {"cbW"  , 3.23}, //2.633;
    {"cpQ3" ,-1.60}, //-1.280;
    {"cptb" , 0.13}, //0.133;
    {"cpt"  ,-3.72}, //-2.083;
    {"cQl3i",-4.20}, //-4.200;
    {"cQlMi", 0.51}, //0.510;
    {"cQei" , 0.05}, //0.053;
    {"ctli" , 0.20}, //0.200;
    {"ctei" , 0.33}, //0.333;
    {"ctlSi",-0.07}, //-0.073;
    {"ctlTi",-0.01}, //-0.013;
};

// Come from the AN (other WCs floating)
std::unordered_map<std::string,double> HI_POIS {
    {"ctW"  , 2.79}, //2.74;
    {"ctZ"  , 3.14}, //3.16;
    {"ctp"  ,44.51}, //44.68;
    {"cpQM" ,21.26}, //21.72;
    {"ctG"  , 1.18}, //1.16;
    {"cbW"  , 4.98}, //4.78;
    {"cpQ3" , 3.43}, //3.54;
    {"cptb" ,12.49}, //12.68;
    {"cpt"  ,12.37}, //12.52;
    {"cQl3i", 9.04}, //8.44;
    {"cQlMi", 4.87}, //4.90;
    {"cQei" , 4.48}, //4.34;
    {"ctli" , 4.71}, //4.70;
    {"ctei" , 4.74}, //4.72;
    {"ctlSi", 6.31}, //6.37;
    {"ctlTi", 0.81}, //0.82;
};

// Come from the AN (other WCs floating)
std::unordered_map<std::string,double> LO_POIS {
    {"ctW"  , -2.98}, //-2.96;
    {"ctZ"  , -3.31}, //-3.33;
    {"ctp"  ,-17.09}, //-16.87;
    {"cpQM" , -7.65}, //-7.81;
    {"ctG"  , -1.39}, //-1.37;
    {"cbW"  , -4.96}, //-4.77;
    {"cpQ3" , -7.36}, //-7.00;
    {"cptb" ,-12.58}, //-12.77;
    {"cpt"  ,-18.89}, //-18.60;
    {"cQl3i", -9.66}, //-9.16;
    {"cQlMi", -3.90}, //-3.77;
    {"cQei" , -4.27}, //-4.28;
    {"ctli" , -4.17}, //-4.10;
    {"ctei" , -4.11}, //-4.11;
    {"ctlSi", -6.31}, //-6.37;
    {"ctlTi", -0.81}, //-0.82;
};

TString CMSSW_BASE = "/afs/crc.nd.edu/user/a/awightma/CMSSW_Releases/CMSSW_8_1_0/";
TString EFTFIT_TEST_DIR = CMSSW_BASE + "src/EFTFit/Fitter/test/";

TString FR_MDKEY = "fit_mdf";   // The name of the key for the fit result object from a multidimfit file
TString FR_DIAGKEY = "nuisances_prefit_res";    // Same thing, but for a fitDiagnostics file

// Should return a string padded on left and right to give a centered string (if possible)
TString centerTStr(TString str, int width) {
    TString s = str;
    if (s.Length() >= width) {
        return s;
    }
    int tpad = width - s.Length();  // The total amount of padding we have to work with
    int lpad = tpad / 2;    // Padding to add to the right of the string
    int rpad = tpad - lpad; // Padding to add to the left of the string
    s = TString::Format("%*s%s%*s",lpad,"",s.Data(),rpad,"");
    return s;
}

// Prints the yields for categories which have been summed over certain processes
template<typename T>
void printYields(std::vector<T> yields,RooFitResult *fr) {
    TString indent = "    ";

    std::cout << "Yields:" << std::endl;
    int dMax = 0;
    for (auto y: yields) {
        TString n = y->GetName();
        dMax = (dMax > n.Length()) ? dMax : n.Length();
    }

    for (auto y: yields) {
        TString n  = y->GetName();
        double val = y->getVal();
        double err = y->getPropagatedError(*(fr));

        std::cout << indent << std::left << std::setw(dMax) << n << ": "
                  << std::setw(8) << val << " +/- "
                  << std::setw(9) << err << std::endl;
    }
}

// Prints various values for a single RooRealVar
void printRRV(RooRealVar* rrv) {
    const char* indent = "  ";
    std::string name = rrv->GetName();
    double nom_var  = rrv->getVal();
    TString fstr = "";
    fstr += TString::Format("%s\n",rrv->GetName());
    fstr += TString::Format("%sVal: %.2f +/- %.2f\n",indent,rrv->getVal(),rrv->getError());
    // fstr += TString::Format("%sErr: %.2f\n",indent,rrv->getError());
    fstr += TString::Format("%s(ErrLo,ErrHi):   (%.2f,%.2f)\n",indent,rrv->getErrorLo(),rrv->getErrorHi());
    fstr += TString::Format("%s(AsymLo,AsymHi): (%.2f,%.2f)\n",indent,rrv->getAsymErrorLo(),rrv->getAsymErrorHi());
    fstr += TString::Format("%sRange: [%.2f,%.2f]",indent,rrv->getMin(),rrv->getMax());
    std::cout << fstr << std::endl;
}

// Prints a single RRV from the given RooArgSet
void printRRV(TString name, RooArgSet& pois) {
    RooRealVar* rrv = (RooRealVar*)pois.find(name);
    if (!rrv) {
        std::cout << TString::Format("Unknown RRV: %s",name.Data()) << std::endl;
        return;
    }
    printRRV(rrv);
}

// Prints various values for each element in the RooArgSet
void printRRVs(RooArgSet pois) {
    RooLinkedListIter iterP = pois.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        printRRV(rrv);
    }
}

void printNuisParams(RooArgList lst) {
    int w1 = 0;
    int w2 = 0;
    int w3 = 0;
    int sz = 0;
    std::string str;
    for (int i = 0; i < lst.getSize(); i++) {
        RooRealVar const* rrv = dynamic_cast<RooRealVar const*>(lst.at(i));
        str  = rrv->GetName();
        sz = str.size();
        w1 = TMath::Max(w1,sz);

        str = std::to_string(rrv->getVal());
        sz  = str.size();
        w2  = TMath::Max(w2,sz);

        str = "(" + std::to_string(rrv->getErrorLo()) + "," + std::to_string(rrv->getErrorLo()) + ")";
        sz  = str.size();
        w3  = TMath::Max(w3,sz);

    }
    std::cout << TString::Format("%*s : %*s +/- %*s %s",-1*w1,"Name",-1*w2,"Nominal",-1*w3," Asym. Error","Sym. Error") << std::endl;
    for (int i = 0; i < lst.getSize(); i++) {
        RooRealVar const* rrv = dynamic_cast<RooRealVar const*>(lst.at(i));
        std::string name = rrv->GetName();
        double nom_val = rrv->getVal();
        double err = rrv->getError();
        double err_d = rrv->getErrorLo();
        double err_u = rrv->getErrorHi();
        str = "(" + std::to_string(err_d) + "," + std::to_string(err_u) + ")";
        std::cout << std::left << std::setw(w1) << name << " : "
                  << std::right << std::setw(w2) << std::to_string(nom_val)
                  << " +/- " << std::left << std::setw(w3) << str
                  << " " << err
                  << std::endl;
    }
}

void printPOICorrelations(RooArgSet pois, RooFitResult* fr) {
    int counter = 0;
    auto it1 = pois.createIterator();
    for (RooRealVar* rrv1 = (RooRealVar*) it1->Next(); rrv1 != 0; rrv1 = (RooRealVar*) it1->Next()) {
        auto it2 = pois.createIterator();
        std::string n1 = rrv1->GetName();
        for (RooRealVar* rrv2 = (RooRealVar*) it2->Next(); rrv2 != 0; rrv2 = (RooRealVar*) it2->Next()) {
            std::string n2 = rrv2->GetName();
            double corr_val = fr->correlation(n1.c_str(),n2.c_str());
            //double corr_val = fr->correlation(&rrv1,&rrv2);
            std::string s1 = " <" + n1 + "," + n2 + "> ";
            std::string s2 = std::to_string(corr_val);
            if (corr_val > 0) {
                s2 = " " + s2;
            }
            std::cout << std::left << std::setw(15) << s1 << s2 << std::endl;
            counter++;
        }
        //std::cout << std::endl;
    }
}

void printLatexYieldTable(std::vector<AnalysisCategory*> cats, vTStr sgnls, vTStr bkgds, RooFitResult* fr) {
    std::string cr = "\\\\";            // carrige return
    std::string col    = " & ";         // column identifier
    std::string hline  = "\\hline";     // insert horizontal line

    bool for_paper = false;  // Changes the sig figs of the output for use in the AN or Paper
    bool skip_header = false;

    TString last_bkgd_name, last_sgnl_name;
    TString bkgd_sum_name = "Sum Bkgd.";
    TString sgnl_sum_name = "Sum Sgnl.";
    TString tot_exp_name = "Total Exp.";
    TString data_name = "Data";

    if (for_paper) {
        skip_header = true;
        bkgd_sum_name = "Sum Background";
        sgnl_sum_name = "Sum Signal";
        tot_exp_name = "Total Expected";
    }

    std::vector<int> col_widths(cats.size()+1,0);   // The +1 is for the process name column
    std::vector<double> sum_bkgds(cats.size(),0);
    std::vector<double> sum_sgnls(cats.size(),0);

    std::vector<std::vector<TString> > rows;
    std::vector<TString> row;

    ////////////////////////////////////////////////
    // Add in a header row
    ////////////////////////////////////////////////
    if (!skip_header) {
        row.clear();
        row.push_back("");
        col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
        for (uint i=0; i < cats.size(); i++) {
            AnalysisCategory* cat = cats.at(i);
            TString str = cat->getName();
            if (BIN_LABEL_MAP.count(str.Data())) {
                str = BIN_LABEL_MAP[str.Data()];
            }
            col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
            row.push_back(str);
        }
        rows.push_back(row);
    }

    ////////////////////////////////////////////////
    // Add in the background process rows
    ////////////////////////////////////////////////
    for (uint i=0; i < bkgds.size(); i++) {
        row.clear();
        TString proc = bkgds.at(i);
        TString row_name = proc;
        if (for_paper) {
            if (YIELD_LABEL_MAP.count(proc.Data())) {
                row_name = YIELD_LABEL_MAP[proc.Data()];
            }
            last_bkgd_name = row_name;
        }
        row.push_back(row_name);
        col_widths.at(0) = std::max(col_widths.at(0),row_name.Length());

        for (uint j=0; j < cats.size(); j++) {
            AnalysisCategory* cat = cats.at(j);
            double val = cat->getExpProc(proc);
            TString str = TString::Format("%.2f",val);
            if (for_paper) {
                str = TString::Format("%.1f",val);
            }
            sum_bkgds.at(j) += val;
            row.push_back(str);
            col_widths.at(j+1) = std::max(col_widths.at(j+1),str.Length());
        }
        rows.push_back(row);
    }

    row.clear();
    row.push_back(bkgd_sum_name);
    col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
    for (uint i=0; i < sum_bkgds.size(); i++) {
        double val = sum_bkgds.at(i);
        TString str = TString::Format("%.2f",val);
        if (for_paper) {
            str = TString::Format("%.1f",val);
        }
        row.push_back(str);
        col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
    }
    rows.push_back(row);

    ////////////////////////////////////////////////
    // Add in the signal process rows
    ////////////////////////////////////////////////
    for (uint i=0; i < sgnls.size(); i++) {
        row.clear();
        TString proc = sgnls.at(i);
        TString row_name = proc;
        if (for_paper) {
            if (YIELD_LABEL_MAP.count(proc.Data())) {
                row_name = YIELD_LABEL_MAP[proc.Data()];
            }
            last_sgnl_name = row_name;
        }
        row.push_back(row_name);
        col_widths.at(0) = std::max(col_widths.at(0),row_name.Length());

        for (uint j=0; j < cats.size(); j++) {
            AnalysisCategory* cat = cats.at(j);
            double val = cat->getExpProc(proc);
            TString str = TString::Format("%.2f",val);
            if (for_paper) {
                str = TString::Format("%.1f",val);
            }
            sum_sgnls.at(j) += val;
            row.push_back(str);
            col_widths.at(j+1) = std::max(col_widths.at(j+1),str.Length());
        }
        rows.push_back(row);
    }

    row.clear();
    row.push_back(sgnl_sum_name);
    col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
    for (uint i=0; i < sum_sgnls.size(); i++) {
        double val = sum_sgnls.at(i);
        TString str = TString::Format("%.2f",val);
        if (for_paper) {
            str = TString::Format("%.1f",val);
        }
        row.push_back(str);
        col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
    }
    rows.push_back(row);

    ////////////////////////////////////////////////
    // Add in the total expected row
    ////////////////////////////////////////////////
    row.clear();
    row.push_back(tot_exp_name);
    col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
    for (uint i=0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        double val = cat->getExpSum();
        double err = cat->getExpSumError(fr);
        TString str = TString::Format("%.2f \\pm %.2f",val,err);
        if (for_paper) {
            str = TString::Format("$%.0f \\pm %.0f$",val,err);
        } else {
            // Only update the col widths here b/c this row is an outlier in terms of length
            col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
        }
        row.push_back(str);
    }
    rows.push_back(row);

    ////////////////////////////////////////////////
    // Add in the data observed row
    ////////////////////////////////////////////////
    row.clear();
    row.push_back(data_name);
    col_widths.at(0) = std::max(col_widths.at(0),row.at(0).Length());
    for (uint i=0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        double val = cat->getData();
        TString str = TString::Format("%.0f",val);
        col_widths.at(i+1) = std::max(col_widths.at(i+1),str.Length());
        row.push_back(str);
    }
    rows.push_back(row);

    ////////////////////////////////////////////////
    // Construct the entire table row-by-row
    ////////////////////////////////////////////////
    std::stringstream ss;
    for (uint i=0; i < rows.size(); i++) {
        std::vector<TString> row = rows.at(i);
        for (uint j=0; j < row.size(); j++) {
            TString entry = row.at(j);
            int colw = col_widths.at(j);

            if (j == 0) { // left-justify
                ss << TString::Format("%*s",-1*colw,entry.Data());
            } else { // right-justify
                ss << TString::Format("%*s",colw,entry.Data());
            }
            if (j < row.size() - 1) {
                ss << col;
            } else {
                ss << " " << cr;
            }
        }
        if (for_paper) {
            // Add in the \hline for latex
            if (row.at(0) == bkgd_sum_name  || row.at(0) == sgnl_sum_name ||
                row.at(0) == tot_exp_name   || row.at(0) == data_name ||
                row.at(0) == last_bkgd_name || row.at(0) == last_sgnl_name) {
                ss << " " << hline;
            }
        }
        ss << "\n";
    }
    std::cout << ss.str() << std::endl;
}

// Iterates over the RooArgSet and sets their values to +/- values based on 'type'
void adjustRRVs(RooArgSet pois,TString type,double sigma=1.0,std::set<std::string> skip={},std::set<std::string> keep={}) {
    RooLinkedListIter iterP = pois.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        std::string name = rrv->GetName();
        rrv->removeRange();     // We don't care about limiting the range of values at this point
        if (skip.size() && skip.count(name)) {
            continue;
        }
        if (keep.size() && !keep.count(name)) {
            continue;
        }
        double nom_var  = rrv->getVal();
        double down_var = rrv->getVal() + rrv->getErrorLo()*sigma;
        double up_var   = rrv->getVal() + rrv->getErrorHi()*sigma;
        //std::cout << name << " Up: " << up_var << std::endl;
        if (type == "up") {
            rrv->setVal(up_var);
        } else if (type == "down") {
            rrv->setVal(down_var);
        } else if (type == "nom") {
            rrv->setVal(nom_var);
        } else {
            rrv->setVal(nom_var);
        }
    }
}

// Sets the specified RRV to the specified value
void setRRV(RooArgSet pois, std::string name, double val) {
    RooLinkedListIter iterP = pois.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        std::string rrv_name = rrv->GetName();
        if (rrv_name != name) continue;
        rrv->setVal(val);
    }
}

// Sets the RooRealVar error values
void setRRVError(RooArgSet pois, std::string name, double val_hi, double val_lo=0.0) {
    RooLinkedListIter iterP = pois.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        std::string rrv_name = rrv->GetName();
        if (rrv_name != name) continue;
        if (val_lo != 0.0) {
            rrv->setAsymError(val_lo,val_hi);
        } else {
            rrv->setError(val_hi);
        }
    }
}

// Find a specific RooRealVar from a RooArgList
double getRRV(RooArgList lst, std::string name) {
    RooLinkedListIter iterP = lst.iterator();
    for (RooRealVar* rrv = (RooRealVar*) iterP.Next(); rrv != 0; rrv = (RooRealVar*) iterP.Next()) {
        std::string rrv_name = rrv->GetName();
        if (rrv_name == name) {
            return rrv->getVal();
        }
    }
    return -1;
}

// Iterates over the first set and removes errors from ones which appear in the second set
void removeErrors(RooArgSet pars,RooArgSet pois) {
    RooLinkedListIter it1 = pars.iterator();
    for (RooRealVar* rrv = (RooRealVar*) it1.Next(); rrv != 0; rrv = (RooRealVar*) it1.Next()) {
        std::string n1 = rrv->GetName();
        RooLinkedListIter it2 = pois.iterator();
        for (RooRealVar* poi = (RooRealVar*) it2.Next(); poi !=0; poi = (RooRealVar*) it2.Next()) {
            std::string n2 = poi->GetName();
            if (n1 == n2) {            
                rrv->removeAsymError();
                rrv->removeError();
                break;
            }        
        }
    }
}

// Adds the CMS luminosity text to a given pad object
void add_cms_text(TPad* pad, float cmsTextSize=0.75, float lumiTextSize=0.60) {
    //////////////////////
    // Define some constants
    //////////////////////
    TString cmsText     = "CMS";
    float cmsTextFont   = 61;  // default is helvetic-bold

    TString extraText   = "";   // For Paper plots
    // TString extraText   = "Preliminary";
    // TString extraText   = "Supplementary";
    float extraTextFont = 52;  // default is helvetica-italics

    // TString lumiText = "#sqrt{s} = 13 TeV, L = 41.5 fb^{-1}";
    TString lumiText = "41.5 fb^{-1} (13 TeV)";
    float lumiTextFont = 42;

    //////////////////////
    // text sizes and text offsets with respect to the top frame
    // in unit of the top margin size
    //////////////////////
    // float lumiTextSize     = 0.80;   // 0.60 is tdrstyle default
    float lumiTextOffset   = 0.20;   // Percentage of some margin (currently just top margin) to shift text
    // float cmsTextSize      = 0.85;   // 0.75 is tdrstyle default
    // float cmsTextOffset    = 0.1;  // only used in outOfFrame version
    float cmsTextOffset    = 0.10;  // This will need to be adjusted if 'lumiText' is changed

    //////////////////////
    // also text sizes and text offsets with respect to frame margins
    // in unit of the margin size
    //////////////////////
    // float relPosX = 0.08;   // Controls where the 'extraText' gets placed relative to 'cmsText'
    float relPosX = 0.045;
    float relPosY = 0.100;//0.035;

    //////////////////////
    // ratio of "CMS" and extra text size
    //////////////////////
    float extraOverCmsTextSize  = 0.76;
    float extraTextSize = extraOverCmsTextSize*cmsTextSize;

    //////////////////////
    // Add the text
    //////////////////////

    float posX = 0.0;
    float posY = 0.0;
    int align  = 11;

    float H = pad->GetWh();
    float W = pad->GetWw();
    float l = pad->GetLeftMargin();
    float t = pad->GetTopMargin();
    float r = pad->GetRightMargin();
    float b = pad->GetBottomMargin();

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
    latex.SetTextFont(42);
    latex.SetTextAlign(31);
    latex.SetTextSize(lumiTextSize*t);
    std::cout << TString::Format("lumiText:  (%.2f,%.2f), Size: %.2f",posX,posY,lumiTextSize*t) << std::endl;
    latex.DrawLatex(posX,posY,lumiText);

    //////////////////////
    // Draw the CMS text
    //////////////////////

    //////////////////////
    // Out of frame top middle-ish
    //////////////////////
    // posX  = l + cmsTextOffset;
    // posY  = 1-t+lumiTextOffset*t;
    // align = 11;

    //////////////////////
    // In frame top-left
    //////////////////////
    posX  =   l + relPosX*(1-l-r);
    posY  = 1-t - relPosY*(1-t-b);
    align = 11;

    latex.SetTextFont(cmsTextFont);
    latex.SetTextAlign(align); 
    latex.SetTextSize(cmsTextSize*t);
    std::cout << TString::Format("cmsText:   (%.2f,%.2f), Size: %.2f",posX,posY,cmsTextSize*t) << std::endl;
    latex.DrawLatex(posX,posY,cmsText);

    //////////////////////
    // Draw the extra text (i.e. 'Preliminary')
    //////////////////////

    //////////////////////
    // Out of frame top middle-ish
    //////////////////////
    // posX  = l + cmsTextOffset + relPosX;
    // posY  = 1-t+lumiTextOffset*t;
    // align = 11;

    //////////////////////
    // In frame and inline with "CMS" text
    //////////////////////
    posX  = l + cmsTextOffset + relPosX*(1-l-r);
    posY  = 1-t - relPosY*(1-t-b);
    align = 11;

    latex.SetTextFont(extraTextFont);
    latex.SetTextSize(extraTextSize*t);
    latex.SetTextAlign(align);
    // std::cout << TString::Format("extraText: (%.2f,%.2f)",posX,posY) << std::endl;
    latex.DrawLatex(posX,posY,extraText);

    return;
}

// Returns a histogram that is the ratio of h1/h2
// Used in: make_overlay_plot_v2
TH1D* make_ratio_histogram(TString name, TH1D* h1, TH1D* h2) {
    if (h1->GetXaxis()->GetNbins() != h2->GetXaxis()->GetNbins()) {
        std::cout << "[Error] makeRatioHistogram() - bin mismatch between ratio of hists" << std::endl;
        throw;
    }
    TAxis* xaxis = h1->GetXaxis();
    int bins = xaxis->GetNbins();
    Double_t low = xaxis->GetXmin();
    Double_t high = xaxis->GetXmax();

    TAxis* yaxis = h1->GetYaxis();
    Double_t yaxis_sz = yaxis->GetLabelSize();

    // std::cout << "Ratio Name: " << name << std::endl;
    TH1D* h_ratio = new TH1D(name,"",bins,low,high);    // Make sure the title is empty!

    // This is to fix the y-axis label size (I think)
    // Note: If done after making x-axis alphanumeric, this does nothing for some reason
    h_ratio->GetYaxis()->SetLabelSize(yaxis_sz*1.5);
    // Change the x-axis label size
    if (bins <= 4) {// Likely an njet histogram
        h_ratio->GetXaxis()->SetLabelSize(yaxis_sz*3.5);
    } else {
        h_ratio->GetXaxis()->SetLabelSize(yaxis_sz*2.5);
    }

    for (int i = 1; i <= bins; i++) {
        // if (xaxis->IsAlphanumeric()) {
        //     TString bin_label = xaxis->GetBinLabel(i);
        //     h_ratio->GetXaxis()->SetBinLabel(i,bin_label);
        // }
        // Apparently in ROOT 6.06 'IsAlphanumeric()' is a private member function...
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
        // Note: If you set this to 0, the horizontal line doesn't get drawn, b/c ROOT is the fucking
        //       stupidest piece of shit I have ever had to deal with
        if (h1->GetName() == h2->GetName()) {
            ratio_err = 0.001;    // Ignore the error for now (makes the y-axis errors tiny)
        } else {
            ratio_err = h1->GetBinError(i) / h1->GetBinContent(i);
        }
        h_ratio->SetBinContent(i,ratio);
        h_ratio->SetBinError(i,ratio_err);
    }
    h_ratio->GetYaxis()->SetRangeUser(0.0,2.0);// was 1.8
    h_ratio->GetYaxis()->SetNdivisions(205,kFALSE); // The kFALSE is important as otherwise it will
                                                    // 'optimize' the tick marks and likely just ignore
                                                    //  w/e option you choose
    return h_ratio;
}

// For filling the TGraphAsymmErrors See:
//   https://github.com/bryates/TopLJets2015/blob/master/TopAnalysis/scripts/plotter.py#L695-L714
// Used in: make_overlay_plot_v2
TGraphAsymmErrors* make_ratio_error_band(TH1D* h_data, TH1D* h_mc, TGraphErrors* err_mc) {
    TGraphAsymmErrors* gr_err = new TGraphAsymmErrors(h_mc);
    for (uint i = 0; i < gr_err->GetN(); i++) {
        int bin_idx = i + 1;
        double x_val, y_val;
        double err_up,err_lo;
        gr_err->GetPoint(i,x_val,y_val);    // GetPointX doesn't exist in ROOT 6.06
        double data_up = h_data->GetBinErrorUp(i);
        double data_down = h_data->GetBinErrorLow(i);
        // double diff_up = err_mc->GetErrorYHigh(i);
        // double diff_down = err_mc->GetErrorYLow(i);
        double diff_up = err_mc->GetErrorY(i);
        double diff_down = err_mc->GetErrorY(i);

        err_up = sqrt(data_up*data_up + diff_up*diff_up);
        err_lo = sqrt(data_down*data_down + diff_down*diff_down);

        err_up = err_up / h_mc->GetBinContent(bin_idx);
        err_lo = err_lo / h_mc->GetBinContent(bin_idx);


        // std::cout << TString::Format("Bin %d",i) << std::endl;
        // std::cout << TString::Format("MC nom: %.1f",h_mc->GetBinContent(bin_idx)) << std::endl;
        // std::cout << TString::Format("data nom: %.1f",h_data->GetBinContent(bin_idx)) << std::endl;
        // std::cout << TString::Format("data hi: %.1f",data_up) << std::endl;
        // std::cout << TString::Format("data lo: %.1f",data_down) << std::endl;
        // std::cout << TString::Format("diff hi: %.1f",diff_up) << std::endl;
        // std::cout << TString::Format("diff lo: %.1f",diff_down) << std::endl;
        // std::cout << std::endl;

        gr_err->SetPoint(i,x_val,1.0);
        gr_err->SetPointEYlow(i,err_lo);
        gr_err->SetPointEYhigh(i,err_up);
    }

    gr_err->SetLineColor(kWhite);
    // gr_err->SetFillStyle(3001); // Hashed stylings
    // gr_err->SetFillColor(kBlack);
    gr_err->SetFillStyle(1001); // Solid color
    // gr_err->SetFillColor(kGreen);
    gr_err->SetFillColor(kGray+1);
    // gr_err->SetFillColorAlpha(kBlack,0.25); // Don't really seem to work
    // gr_err->SetFillColorAlpha(kBlack,0.65); // Don't really seem to work

    return gr_err;
}

/*
Note:
    Since the hi/lo points aren't really error bars per-se, we need to use a lot of extra logic
    to try and make preserve relative orientations (currently WIP)
*/
TGraphAsymmErrors* make_ratio_fluct(TH1D* h_nom, TH1D* h_lo, TH1D* h_hi) {
    TGraphAsymmErrors* gr = new TGraphAsymmErrors(h_nom);
    for (uint i = 0; i < gr->GetN(); i++) {
        int bin_idx = i + 1;
        double x_val, y_val;
        double bin_lo,bin_hi;
        double val_nom,val_hi,val_lo;
        gr->GetPoint(i,x_val,y_val);    // GetPointX doesn't exist in ROOT 6.06

        val_nom = h_nom->GetBinContent(bin_idx);

        // val_lo = abs(h_lo->GetBinContent(bin_idx) - y_val);
        // val_hi = abs(h_hi->GetBinContent(bin_idx) - y_val);

        // val_lo = h_lo->GetBinContent(bin_idx) - y_val;
        // val_hi = h_hi->GetBinContent(bin_idx) - y_val;

        bin_lo = h_lo->GetBinContent(bin_idx);
        bin_hi = h_hi->GetBinContent(bin_idx);

        val_lo = std::min(val_nom,bin_lo);
        val_lo = std::min(val_lo,bin_hi);

        val_hi = std::max(val_nom,bin_hi);
        val_hi = std::max(val_hi,bin_lo);

        if (val_nom == val_lo) {// The nominal point is a minimum
            val_lo = 0.0;
            val_hi = std::max(bin_lo,bin_hi);
            val_hi = abs(val_hi - val_nom);
        } else if (val_nom == val_hi) {// The nominal point is a maximum
            val_hi = 0.0;
            val_lo = std::min(bin_lo,bin_hi);
            val_lo = abs(val_lo - val_nom);
        } else {// The nominal point is between lo and hi
            val_lo = std::min(bin_lo,bin_hi);
            val_hi = std::max(bin_lo,bin_hi);

            val_lo = abs(val_lo - val_nom);
            val_hi = abs(val_hi - val_nom);
        }

        /*
        if (val_lo > val_nom) {
            val_lo = -1*abs(val_lo - val_nom);
        } else {
            val_lo = abs(val_lo - val_nom);
        }

        if (val_hi < val_nom) {
            val_hi = -1*abs(val_hi - val_nom);
        } else {
            val_hi = abs(val_hi - val_nom);
        }
        */

        // val_lo = std::max(val_lo,0.001);
        // val_hi = std::max(val_hi,0.001);

        gr->SetPoint(i,x_val,val_nom);
        gr->SetPointEXlow(i,0.0);
        gr->SetPointEXhigh(i,0.0);

        gr->SetPointEYlow(i,val_lo);
        gr->SetPointEYhigh(i,val_hi);

        // std::cout << TString::Format("x-val: %.1f",x_val) << std::endl;
        // std::cout << TString::Format("\tNom: %.3f",val_nom) << std::endl;
        // std::cout << TString::Format("\tLo: %.3f (%.3f)",val_lo,bin_lo) << std::endl;
        // std::cout << TString::Format("\tHi: %.3f (%.3f)",val_hi,bin_hi) << std::endl;
    }

    Color_t clr = h_nom->GetFillColor();

    gr->SetLineColor(clr);
    gr->SetLineWidth(2);
    gr->SetFillColor(0);

    // gr->SetLineColor(kWhite);
    // gr->SetFillStyle(1001); // Solid color
    // gr->SetFillColor(kGray+1);

    return gr;
}

// For error bars see: https://twiki.cern.ch/twiki/bin/view/CMS/PoissonErrorBars
// Used in: make_overlay_plot_v2
TH1D* get_data_histogram(TString title,std::vector<AnalysisCategory*> cats) {
    TString plot_title = TString::Format("%s;category;Events",title.Data());
    // TH1D* h_data = new TH1D("data_yield",plot_title,cats.size(),0.0,1.0);
    TH1D* h_data = new TH1D("data_yield",plot_title,cats.size(),0.0,cats.size());
    h_data->SetLineColor(1);
    h_data->SetLineWidth(2);
    h_data->SetMarkerStyle(20);
    // h_data->SetMarkerSize(0.75);
    h_data->SetMarkerSize(1.00);
    h_data->GetYaxis()->SetTitleSize(0.05);
    h_data->GetYaxis()->SetTitleOffset(1.1);
    h_data->GetYaxis()->SetLabelSize(0.05);

    h_data->Sumw2(kFALSE);
    // h_data->Sumw2(false);

    // Fill and label the data histogram
    for (uint i = 0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        int bin_idx = i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        double bin_val = cat->getData();
        h_data->SetBinContent(bin_idx,bin_val);
        TString bin_label = cat->getName();
        if (BIN_LABEL_MAP.count(bin_label.Data())) {
            bin_label = BIN_LABEL_MAP[bin_label.Data()];
        }
        h_data->GetXaxis()->SetBinLabel(bin_idx,bin_label);
    }
    h_data->SetBinErrorOption(TH1::kPoisson);

    return h_data;  
}

// Not needed yet...
// TGraphAsymmErrors get_poisson_error_graph(TH1D* h) {

// }

// Turns a vector of AnalysisCategory objects into a histogram for a particular process with one bin per category
// Used in: make_overlay_plot_v2, make_fluct_compare_plots
TH1D* get_process_histogram(TString title, TString proc, std::vector<AnalysisCategory*> cats) {
    TString plot_title = TString::Format("%s;category;Events",proc.Data());
    // TH1D* h = new TH1D(proc+"_yield",plot_title,cats.size(),0.0,1.0);
    TString hname = TString::Format("%s_%s_yield",title.Data(),proc.Data());
    TH1D* h = new TH1D(hname,plot_title,cats.size(),0.0,cats.size());
    h->GetYaxis()->SetTitleSize(0.05);
    h->GetYaxis()->SetTitleOffset(1.1);
    h->GetYaxis()->SetLabelSize(0.05);

    Color_t h_clr = kBlack;
    if (PROCESS_COLOR_MAP.count(proc.Data())) {
        h_clr = PROCESS_COLOR_MAP[proc.Data()];
    }
    // h->SetFillColor(h_clr);
    // h->SetLineColor(h_clr);
    // h->SetLineWidth(0);

    h->SetFillColor(h_clr);
    h->SetLineColor(kBlack);
    h->SetLineWidth(1);

    // Fill and label the histogram
    for (uint i = 0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        int bin_idx = i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        TString bin_label = cat->getName();
        if (BIN_LABEL_MAP.count(bin_label.Data())) {
            bin_label = BIN_LABEL_MAP[bin_label.Data()];
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

// Turns a vector of ExtremumPoint structs into a histogram for a particular process
// Note: The histogram style here should attempt to be kept in sync with 'get_process_histogram'
TH1D* get_extremum_histogram(TString title, TString proc, std::vector<ExtremumPoint> pts, TString pt_type) {
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
        std::cout << TString::Format("ERROR: Invalid point type passed to 'get_extremum_histogram': %s",pt_type.Data()) << std::endl;
        return nullptr;
    }

    TString plot_title = TString::Format("%s;category;Events",proc.Data());
    TString hname = TString::Format("%s_%s_yield",title.Data(),proc.Data());
    TH1D* h = new TH1D(hname,plot_title,pts.size(),0.0,pts.size());
    h->GetYaxis()->SetTitleSize(0.05);
    h->GetYaxis()->SetTitleOffset(1.1);
    h->GetYaxis()->SetLabelSize(0.05);

    Color_t h_clr = kBlack;
    if (PROCESS_COLOR_MAP.count(proc.Data())) {
        h_clr = PROCESS_COLOR_MAP[proc.Data()];
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
        if (BIN_LABEL_MAP.count(bin_label.Data())) {
            bin_label = BIN_LABEL_MAP[bin_label.Data()];
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

// Returns a histogram built from the vector of categories, summed over all processes
// Used in: make_overlay_plot_v2
TH1D* get_summed_histogram(TString name,TString title, std::vector<AnalysisCategory*> cats) {
    // TH1D* h = new TH1D(name,title,cats.size(),0.0,1.0);
    TH1D* h = new TH1D(name,title,cats.size(),0.0,cats.size());
    h->SetFillColor(0);
    h->SetLineWidth(1);
    // Fill and label the histogram
    for (uint i = 0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        int bin_idx = i + 1;    // Histogram bins are offset by 1, since idx 0 is underflow bin
        TString bin_label = cat->getName();
        if (BIN_LABEL_MAP.count(bin_label.Data())) {
            bin_label = BIN_LABEL_MAP[bin_label.Data()];
        }
        h->GetXaxis()->SetBinLabel(bin_idx,bin_label);
        h->SetBinContent(bin_idx,cat->getExpSum());
    }
    return h;
}

// Used in: make_overlay_plot_v2
TGraphErrors* get_error_graph(TH1D* base_hist, std::vector<AnalysisCategory*> cats, RooFitResult* fr) {
    // TGraphAsymmErrors* gr_err = new TGraphAsymmErrors(base_hist);
    TGraphErrors* gr_err = new TGraphErrors(base_hist);
    for (uint i = 0; i < cats.size(); i++) {
        AnalysisCategory* cat = cats.at(i);
        int bin_idx = i + 1;
        double x_val,y_val;
        double x_err,y_err;
        gr_err->GetPoint(i,x_val,y_val);
        y_val = cat->getExpSum();
        x_err = gr_err->GetErrorX(i);
        y_err = cat->getExpSumError(fr);

        // std::cout << "Bin idx: " << bin_idx << std::endl;
        // std::cout << TString::Format("Point: (%.2f,%.2f)",x_val,y_val) << std::endl;
        // std::cout << TString::Format("Error: (%.2f,%.2f)",x_err,y_err) << std::endl;

        gr_err->SetPoint(i,x_val,y_val);
        gr_err->SetPointError(i,x_err,y_err);
    }

    gr_err->SetLineColor(kWhite);
    // gr_err->SetFillStyle(3001);
    gr_err->SetFillStyle(3254);
    gr_err->SetFillColor(kBlack);
    // gr_err->SetFillColorAlpha(kBlack,0.25);
    // gr_err->SetFillColorAlpha(kBlack,0.65);

    return gr_err;
}

std::vector<TString> get_files(const char *dirname, const char *ext=".root") {
    TSystemDirectory dir(dirname, dirname);
    TList *files = dir.GetListOfFiles();
    std::vector<TString> ret;
    if (files) {
        TSystemFile *file;
        TString fname;
        TIter next(files);
        while ((file=(TSystemFile*)next())) {
            fname = file->GetName();
            if (!file->IsDirectory() && fname.EndsWith(ext)) {
                ret.push_back(fname);
            }
        }
    }
    return ret;
}

/*
    tdir: The directory with *ALL* of the fitresult files
    wc_name: The name of the WC which you want to find the extremum of
    proc: The Signal process you want to find the extremum of
    ana_cat: The analysis category used to determine the bin yield
    returns: An ExtremumPoint struct, which contains all of the info related to the hi/lo extremes for a given category

    Note:
        This creates a workspace snapshot, so should only ever be called once, otherwise you will create
        duplicate named snapshots, which I don't know if that is problematic or not
*/
ExtremumPoint get_extremum_fitresult(
    TString tdir,
    TString wc_name,
    std::vector<TString> procs,
    AnalysisCategory* ana_cat,
    RooWorkspace* ws,
    RooArgSet pois
) {
    ExtremumPoint pt;

    TString cat_name = ana_cat->getName();

    pt.cat_name = cat_name;
    pt.wc_name = wc_name;

    TString ext = ".root";
    std::vector<TString> fnames = get_files(tdir.Data(),ext.Data());

    TString search = TString::Format("multidimfit_%s_",wc_name.Data());

    TString lo_str;
    TString hi_str;

    double lo_yld;
    double hi_yld;

    for (TString p: procs) {
        pt.procs.push_back(p);
        pt.lo_fnames.push_back("");
        pt.hi_fnames.push_back("");
        pt.lo_snps.push_back("");
        pt.hi_snps.push_back("");
        pt.lo_ylds.push_back(-999);
        pt.hi_ylds.push_back(-999);
        pt.lo_vals.push_back(-999);
        pt.hi_vals.push_back(-999);

        pt.nom_snp = "";
        pt.base_snp = "";
        pt.nom_ylds.push_back(-999);
        pt.base_ylds.push_back(-999);
    }

    pt.sum_lo_fname = "";
    pt.sum_hi_fname = "";
    pt.sum_lo_snp = "";
    pt.sum_hi_snp = "";
    pt.sum_lo_yld = -999;
    pt.sum_hi_yld = -999;
    pt.sum_lo_val = -999;
    pt.sum_hi_val = -999;

    int f_count = 0;
    for (TString fn: fnames) {
        // if (f_count >= 20) break;
        if (!fn.BeginsWith(search)) continue;

        int len_diff = fn.Length() - search.Length() - ext.Length();
        TString val_str = fn(search.Length(),len_diff);
        double wc_val = std::stod(val_str.Data());

        TString fpath = TString::Format("%s/%s",tdir.Data(),fn.Data());
        TFile* f = TFile::Open(fpath,"READ");
        RooFitResult* fr = (RooFitResult*) f->Get(FR_MDKEY);

        TString snapshot_name = TString::Format("fr_%s_%s_%.2f",cat_name.Data(),wc_name.Data(),wc_val);

        ws->saveSnapshot(snapshot_name,fr->floatParsFinal(),kTRUE);
        ws->loadSnapshot(snapshot_name);
        setRRV(pois,wc_name.Data(),wc_val); // Needed b/c the 1D scans don't include the fixed point in the final RooArgSet

        double sum_exp_yld = 0.0;
        for (uint i=0; i < procs.size(); i++) {
            TString proc = procs.at(i);
            double exp_yld = ana_cat->getExpProc(proc);
            sum_exp_yld += exp_yld;
            lo_yld = pt.lo_ylds.at(i);
            hi_yld = pt.hi_ylds.at(i);
            if (lo_yld == -999 || hi_yld == -999) {
                pt.lo_fnames.at(i) = fn;
                pt.hi_fnames.at(i) = fn;
                pt.lo_ylds.at(i) = exp_yld;
                pt.hi_ylds.at(i) = exp_yld;
                pt.lo_vals.at(i) = wc_val;
                pt.hi_vals.at(i) = wc_val;
                pt.lo_snps.at(i) = snapshot_name;
                pt.hi_snps.at(i) = snapshot_name;
            }
            if (exp_yld < lo_yld) {
                pt.lo_fnames.at(i) = fn;
                pt.lo_ylds.at(i) = exp_yld;
                pt.lo_vals.at(i) = wc_val;
                pt.lo_snps.at(i) = snapshot_name;
            }
            if (exp_yld > hi_yld) {
                pt.hi_fnames.at(i) = fn;
                pt.hi_ylds.at(i) = exp_yld;
                pt.hi_vals.at(i) = wc_val;
                pt.hi_snps.at(i) = snapshot_name;
            }
        }

        lo_yld = pt.sum_lo_yld;
        hi_yld = pt.sum_hi_yld;
        if (lo_yld == -999 || hi_yld == -999) {
            pt.sum_lo_fname = fn;
            pt.sum_hi_fname = fn;
            pt.sum_lo_snp = snapshot_name;
            pt.sum_hi_snp = snapshot_name;
            pt.sum_lo_yld = sum_exp_yld;
            pt.sum_hi_yld = sum_exp_yld;
            pt.sum_lo_val = wc_val;
            pt.sum_hi_val = wc_val;
        }
        if (sum_exp_yld < lo_yld) {
            pt.sum_lo_fname = fn;
            pt.sum_lo_snp = snapshot_name;
            pt.sum_lo_yld = sum_exp_yld;
            pt.sum_lo_val = wc_val;
        }
        if (sum_exp_yld > hi_yld) {
            pt.sum_hi_fname = fn;
            pt.sum_hi_snp = snapshot_name;
            pt.sum_hi_yld = sum_exp_yld;
            pt.sum_hi_val = wc_val;
        }

        f->Close();
        f_count += 1;
    }

    return pt;
}

/*
Desc:
    Takes an ExtremumPoint (EP) and creates a new one by replacing all of the vector data with the values
    stored in the 'sum_*' data members. The result of this is that all of the data vectors of the new
    EP will have a length of exactly one. The reason for doing it this way, is to make it trivial to
    construct the fluctuation plots, which operate on the data vectors and their sizes
Note:
    Since this also merges the values of the 'nom_ylds' and 'base_ylds' data, this function must come
    after those entries have already been filled!
*/
ExtremumPoint merge_extremum_processes(
    TString new_name,
    ExtremumPoint pt
) {
    ExtremumPoint new_pt;

    new_pt.wc_name = pt.wc_name;
    new_pt.cat_name = pt.cat_name;

    TString lo_fname = pt.sum_lo_fname;
    TString hi_fname = pt.sum_hi_fname;
    TString lo_snp = pt.sum_lo_snp;
    TString hi_snp = pt.sum_hi_snp;
    double lo_yld = pt.sum_lo_yld;
    double hi_yld = pt.sum_hi_yld;
    double lo_val = pt.sum_lo_val;
    double hi_val = pt.sum_hi_val;

    new_pt.procs.push_back(new_name);
    new_pt.lo_fnames.push_back(lo_fname);
    new_pt.hi_fnames.push_back(hi_fname);
    new_pt.lo_snps.push_back(lo_snp);
    new_pt.hi_snps.push_back(hi_snp);
    new_pt.lo_ylds.push_back(lo_yld);
    new_pt.hi_ylds.push_back(hi_yld);
    new_pt.lo_vals.push_back(lo_val);
    new_pt.hi_vals.push_back(hi_val);

    // These entries don't need a special 'sum_*' data members b/c they come from a specific phase space point
    new_pt.nom_snp = pt.nom_snp;
    new_pt.base_snp = pt.base_snp;

    double nom_yld = 0.0;
    double base_yld = 0.0;
    for (uint i=0; i < pt.procs.size(); i++) {
        nom_yld += pt.nom_ylds.at(i);
        base_yld += pt.base_ylds.at(i);
    }
    new_pt.nom_ylds.push_back(nom_yld);
    new_pt.base_ylds.push_back(base_yld);

    return new_pt;
}

void get_offscale_arrow(OffScalePoint& pt) {
    double x1,x2,y1,y2;

    x1 = pt.bin_center;
    x2 = pt.bin_center;
    y1 = (pt.axis_max - 0.0)*(1.0 - 0.05);  // Make the arrow length 5% of the axis length;
    if (pt.lo_val < pt.axis_max) {
        y1 = pt.lo_val; // Make the arrow extend down to the corresponding low point
    }
    y2 = pt.axis_max;
    TArrow* arrow = new TArrow(x1,y1,x2,y2);
    arrow->SetFillColor(pt.clr);
    arrow->SetLineColor(pt.clr);
    arrow->SetLineWidth(2);
    arrow->SetArrowSize(0.02);

    double e_hi = pt.hi_val - pt.nom_val;
    double e_lo = pt.lo_val - pt.nom_val;

    if (pt.lo_val < pt.axis_max) {
        arrow->SetLineWidth(3);
        y1 = (pt.axis_max - 0.0)*(1.0 - 0.07);  // Make the text at 7% of the axis length;
        // y1 = pt.axis_max;
    }

    TString text = TString::Format("%.1f^{%+.1f}_{%.1f}",pt.nom_val,e_hi,e_lo);
    TLatex* latex = new TLatex(x1,y1,text.Data());

    // latex->SetTextAlign(23); // Top adjusted
    // latex->SetTextAlign(13); // Left+Top adjusted
    latex->SetTextAlign(33); // Left+Top adjusted
    latex->SetTextSize(0.05);

    pt.arrow = arrow;
    pt.latex = latex;
}

// This might end up being a bad idea, if we can't make a 'one size fits all' external legend for some reason
void make_external_legend(TLegend* leg, TString title) {
    int n_entries = leg->GetListOfPrimitives()->GetEntries();

    TCanvas* ext_canv;
    int ww; // the canvas size in pixels along X
    int wh; // the canvas size in pixels along Y

    double txt_sz;

    int max_cols = 6;
    int cols = std::min(n_entries,max_cols);

    // This monstrosity calculates the number of rows in the legend
    int n_rows = (n_entries / max_cols) + int(n_entries % max_cols != 0);
    n_rows = std::max(1,n_rows);

    std::cout << "n_rows: " << n_rows << std::endl;

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

    std::cout << "n_entries: " << n_entries << std::endl;


    if (n_entries < max_cols) {
        leg->SetNColumns(n_entries);
        leg->SetColumnSeparation(0.45);  // looks pretty decent with 750 canvas width 5 cols and 1 row
    } else {
        leg->SetNColumns(max_cols);
    }

    leg->Draw();

    
    TString save_format;
    TString save_name;

    save_format = "png";
    save_name = TString::Format("%s.%s",title.Data(),save_format.Data());
    ext_canv->Print(save_name,save_format);

    save_format = "pdf";
    save_name = TString::Format("%s.%s",title.Data(),save_format.Data());
    ext_canv->Print(save_name,save_format);

    // delete ext_canv;
}

/*
Desc:
    Creates a stack plot of yield histograms taken from the input vector of categories and also displays
    the data yields in those categories. The overlay_hists vector will plot each histogram ontop of the
    stack+data histograms. The legend entry for the overlay histograms is determined by the TH1D title
    and should be set (along with any other drawing options) prior to being passed to this function.
    If the incl_ratio flag is set to true, then the data/MC ratio will be included
Note:
    This can modify the value of the 'ext_leg' variable!
*/
void make_overlay_plot_v2(
    TString title,
    std::vector<TLatex*> extra_text,
    std::vector<AnalysisCategory*> cats,
    RooFitResult* fr,
    bool incl_ratio,
    bool incl_leg,
    bool ext_leg,
    // int ext_leg,
    TString xtitle="",
    std::vector<TH1D*> overlay_hists={}
) {
    bool debug = false;
    TCanvas* c = new TCanvas("canv","canv",150,10,960,640);// was 700
    TLegend *leg = new TLegend(0.14,0.75,0.94,0.89);
    THStack *hs = new THStack("hs_category_yield","");

    std::vector<TH1D*> proc_hists;
    TH1D* h_data = get_data_histogram(title,cats);

    for (TString proc_name: ALL_PROCS) {
        if (debug) std::cout << "DEBUG: Getting process histogram for " << proc_name << std::endl;
        TH1D* h_proc = get_process_histogram(title,proc_name,cats);
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

    for (TH1D* h: overlay_hists) {
        leg->AddEntry(h,h->GetTitle(),"f");
    }

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

    TH1D* h_exp_sum = get_summed_histogram("expected_sum","",cats);
    TGraphErrors* gr_err = get_error_graph(h_exp_sum,cats,fr);

    leg->AddEntry(gr_err,"Total unc.","f");
    leg->AddEntry(h_data,"Data","lp");

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
        // h_ratio->SetTitle(";;data/MC");
        // h_ratio->SetTitle(";;Data/MC");
        // h_ratio->SetTitle(TString::Format(";%s;Data/MC",xtitle.Data()));
        // h_ratio->SetTitle(TString::Format(";%s;data/pred.",xtitle.Data()));

        h_ratio_base->SetTitle(TString::Format(";%s;data / pred.",xtitle.Data()));
        h_ratio_base->SetLineColor(kRed);
        h_ratio_base->SetLineWidth(2);
        h_ratio_base->GetYaxis()->SetRangeUser(0.4,1.6);
        h_ratio_base->GetYaxis()->SetNdivisions(204,kFALSE);

        h_ratio_base->GetXaxis()->SetLabelSize(0.200);
        h_ratio_base->GetXaxis()->SetLabelOffset(0.020);  // Default is 0.005
        h_ratio_base->GetYaxis()->SetTitleSize(0.150);
        h_ratio_base->GetYaxis()->SetTitleOffset(0.270);  // Default is 1.0
        h_ratio_base->GetYaxis()->SetLabelSize(0.140);

        std::cout << "X-Label Offset: " << h_ratio_base->GetXaxis()->GetLabelOffset() << std::endl;
        std::cout << "Y-Title Offset: " << h_ratio_base->GetYaxis()->GetTitleOffset() << std::endl;
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Actual plotting and Drawing section
    ////////////////////////////////////////////////////////////////////////////////////////////////

    if (debug) std::cout << "DEBUG: Edit canvas object" << std::endl;
    // TCanvas* c = new TCanvas("canv","canv",150,10,960,700);
    gStyle->SetPadBorderMode(0);
    gStyle->SetFrameBorderMode(0);

    Float_t small = 1.e-5;
    const float padding = 1e-5;
    const float xpad = small;    // Pad spacing left to right
    const float ypad = small;    // Pad spacing top to bottom
    const float ygap = 0.07;
    if (incl_ratio) {
        const float ydiv = 0.3; // Height of the second pad
        // float L = padding;
        // float B = padding;
        // float R = 1-padding;
        // float T = 1-padding;
        float L = xpad;
        float B = ypad;
        float R = 1-xpad;
        float T = 1-ypad;
        c->Divide(1,2,small,small);
        // c->GetPad(1)->SetPad(padding,ydiv+padding,1-padding,1-padding); // Order: (L B R T)
        c->GetPad(1)->SetPad(L,B+ydiv,R,T); // Order: (L B R T)
        c->GetPad(1)->SetLeftMargin(.11);
        c->GetPad(1)->SetRightMargin(.05);
        // c->GetPad(1)->SetBottomMargin(.3);
        // c->GetPad(1)->SetBottomMargin(small);
        c->GetPad(1)->SetBottomMargin(ygap / 2);
        c->GetPad(1)->Modified();

        // c->GetPad(2)->SetPad(padding,padding,1-padding,ydiv-padding);
        c->GetPad(2)->SetPad(L,B,R,ydiv);   // Order: (L B R T)
        // c->GetPad(2)->SetTopMargin(small);
        c->GetPad(2)->SetTopMargin(ygap / 2);
        c->GetPad(2)->SetLeftMargin(.11);
        c->GetPad(2)->SetRightMargin(.05);
        c->GetPad(2)->SetBottomMargin(.3);
        c->GetPad(2)->SetGrid(0,1);
        c->GetPad(2)->SetTickx();
        c->GetPad(2)->Modified();

        // c->cd(1);
        // gPad->SetBottomMargin(small);
        // gPad->Modified();

        // c->cd(2);
        // gPad->SetTopMargin(small);
        // gPad->SetTickx();
        // gPad->Modified();
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

    for (TH1D* h: overlay_hists) {
        max_bin = h->GetMaximumBin();
        max_val = h->GetBinContent(max_bin);
        hmax = TMath::Max(max_val,hmax);
    }

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

    // h_data->Draw("hist,e,p");
    // hs->Draw("hist,same");
    hs->Draw("hist");
    if (incl_leg) {
        leg->Draw();
    }
    // CMSInfoLatex->Draw();
    for (TLatex* latex: extra_text) {
        latex->Draw();
    }
    h_data->Draw("same,e,p");
    gr_err->Draw("same,2");
    for (TH1D* h: overlay_hists) h->Draw("same,hist");

    // 3rd argument makes the lumi text slightly bigger then default (0.60)
    add_cms_text((TPad*)c->GetPad(1),0.85,0.80);
    if (incl_ratio) {
        c->cd(1);

        hs->GetYaxis()->SetTitleSize(0.08);
        hs->GetYaxis()->SetTitleOffset(0.63);//0.53

        // hs->GetYaxis()->SetLabelSize(0.060);
        hs->GetYaxis()->SetLabelSize(0.070);

        c->cd(2);
        // h_ratio->Draw("e,p");
        // h_ratio_base->Draw("same");
        // h_ratio_band->Draw("same,2");

        h_ratio_base->Draw();
        // h_ratio_base->GetXaxis()->SetLabelSize(0.200);
        // h_ratio_base->GetYaxis()->SetLabelSize(0.140);

        h_ratio_band->Draw("same,2");
        h_ratio->Draw("same,e,p");


        // h_ratio->GetYaxis()->SetTitleSize(0.15);
        // h_ratio->GetYaxis()->SetTitleOffset(0.22);

        // h_ratio->GetYaxis()->SetLabelSize(0.110);
        // h_ratio->GetXaxis()->SetLabelSize(0.200);
        // h_ratio->GetXaxis()->SetLabelSize(0.500);
        if (hs->GetXaxis()->GetNbins() <= 4) {// Likely an njet histogram
            h_ratio->GetXaxis()->SetLabelSize(0.250);
        }

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

    TString save_format, save_name;

    save_format = "png";
    save_name = TString::Format("overlayed_%s.%s",title.Data(),save_format.Data());
    c->Print(save_name,save_format);

    save_format = "pdf";
    save_name = TString::Format("overlayed_%s.%s",title.Data(),save_format.Data());
    c->Print(save_name,save_format);

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

/*
Desc:
    Creates ratio style histograms from event yields computed by combine fits with WCs scanned to find
    maximal ranges the yields can cover
Note:
    Trying to use the pass-by-reference trick to produce only a single external legend causes all sorts
    of black magic fuckery to go down, resulting in random plots not getting created properly. As a
    result I've removed the variable and just decided to create the external legend with the same exact
    name and overwrite the output file each time. I've not checked if this crazy bug also affects
    'make_overlay_plot_2' as well, but I suspect it does.
*/
void make_fluct_compare_plots(
    TString title,
    // TString heading_str,
    std::vector<TLatex*> extra_text,
    TString wc_name,
    std::vector<ExtremumPoint> pts
) {
    bool debug = false;
    TCanvas* c = new TCanvas("canv","canv",150,10,960,640);// was 700
    // TCanvas* c = new TCanvas("canv","canv",150,10,800,600);
    // TCanvas* c = new TCanvas("canv","canv",150,10,800,800);
    TLegend* leg = new TLegend(0.14,0.75,0.94,0.89);
    THStack* hs = new THStack("hs_category_yield","");

    // TLatex* heading = new TLatex(0.11,1 - 0.06,heading_str.Data());
    // TLatex* heading = new TLatex(0.11,1 - 0.05,heading_str.Data());
    // heading->SetTextSize(0.070);
    // heading->SetTextSize(0.065);
    // heading->SetTextSize(0.060);
    // heading->SetNDC();
    // heading->SetTextFont(42);

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Get Histograms
    ////////////////////////////////////////////////////////////////////////////////////////////////

    std::vector<TString> pt_procs = pts.at(0).procs;

    std::vector<TH1D*> base_hists;
    std::vector<TH1D*> nom_hists;
    std::vector<TH1D*> lo_hists;
    std::vector<TH1D*> hi_hists;
    // for (TString proc_name: SIG_PROCS) {
    for (TString proc_name: pt_procs) {
        TH1D* h_proc;
        TString hname;

        hname = TString::Format("%s_base",title.Data());
        h_proc = get_extremum_histogram(hname,proc_name,pts,"base");
        base_hists.push_back(h_proc);

        hname = TString::Format("%s_nom",title.Data());
        h_proc = get_extremum_histogram(hname,proc_name,pts,"nom");
        nom_hists.push_back(h_proc);

        hname = TString::Format("%s_flcLo",title.Data());
        h_proc = get_extremum_histogram(hname,proc_name,pts,"lo");
        lo_hists.push_back(h_proc);

        hname = TString::Format("%s_flcHi",title.Data());
        h_proc = get_extremum_histogram(hname,proc_name,pts,"hi");
        hi_hists.push_back(h_proc);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Make Ratio Histograms
    ////////////////////////////////////////////////////////////////////////////////////////////////

    double hmin,hmax = 0;
    std::vector<TH1D*> rat_nom_hists;
    std::vector<TH1D*> rat_lo_hists;
    std::vector<TH1D*> rat_hi_hists;
    for (uint i=0; i < base_hists.size(); i++) {
        // TString proc_name = SIG_PROCS.at(i);    // This should be the exact same order as the other
        //                                         // nom and flc histogram vectors
        TString proc_name = pt_procs.at(i);

        TString legend_name = proc_name;
        if (PROCESS_LABEL_MAP.count(proc_name.Data())) {// Rename a process for display in the legend
            legend_name = PROCESS_LABEL_MAP[proc_name.Data()];
        }

        TString hname;

        hname = TString::Format("%s_nom_ratio",proc_name.Data());
        TH1D* h_nom = (TH1D*)nom_hists.at(i)->Clone(hname);

        hname = TString::Format("%s_lo_ratio",proc_name.Data());
        TH1D* h_lo = (TH1D*)lo_hists.at(i)->Clone(hname);

        hname = TString::Format("%s_hi_ratio",proc_name.Data());
        TH1D* h_hi = (TH1D*)hi_hists.at(i)->Clone(hname);

        TH1D* h_unit = (TH1D*)h_nom->Clone("tmp_hist");
        h_unit->Divide(h_unit);

        h_nom->Divide(base_hists.at(i));
        h_lo->Divide(base_hists.at(i));
        h_hi->Divide(base_hists.at(i));

        h_nom->Add(h_unit,-1);
        h_lo->Add(h_unit,-1);
        h_hi->Add(h_unit,-1);

        // Default settings
        h_nom->SetMarkerStyle(kFullCircle);
        h_nom->SetMarkerSize(1);
        h_nom->SetMarkerColor(kBlack);
        h_nom->SetLineColor(kBlack);
        if (PROCESS_MARKER_MAP.count(proc_name.Data())) {
            int mark_sty = PROCESS_MARKER_MAP[proc_name.Data()];
            int mark_sz = PROCESS_MARKER_SIZE_MAP[proc_name.Data()];
            Color_t clr = h_nom->GetFillColor();
            h_nom->SetMarkerStyle(mark_sty);
            h_nom->SetMarkerSize(mark_sz);
            h_nom->SetMarkerColor(clr);
            h_nom->SetLineColor(clr);

        }
        if (SCALE_PROCESS_RATIO_FLUCT.count(proc_name.Data())) {
            double scale_val = SCALE_PROCESS_RATIO_FLUCT[proc_name.Data()];
            h_nom->Scale(1. / scale_val);
            h_lo->Scale(1. / scale_val);
            h_hi->Scale(1. / scale_val);
            legend_name = TString::Format("%s#divide%.0f",legend_name.Data(),scale_val);
            // legend_name = TString::Format("%s#times%.2f",legend_name.Data(),scale_val);
        }

        hmin = std::min(hmin,h_nom->GetMinimum());
        hmin = std::min(hmin,h_lo->GetMinimum());
        hmin = std::min(hmin,h_hi->GetMinimum());

        for (int bin=1; bin <= h_nom->GetXaxis()->GetNbins(); bin++) {
            if (h_nom->GetBinContent(bin) < 5.0) {
                hmax = std::max(hmax,h_nom->GetBinContent(bin));
                hmax = std::max(hmax,h_lo->GetBinContent(bin));
                hmax = std::max(hmax,h_hi->GetBinContent(bin));
            }
        }

        // hmax = std::max(hmax,h_nom->GetMaximum());
        // hmax = std::max(hmax,h_lo->GetMaximum());
        // hmax = std::max(hmax,h_hi->GetMaximum());

        // double bar_width  = 0.95 / base_hists.size();
        // double bar_offset = (1 - 0.95)/2 + bar_width*i;
        // h_nom->SetBarWidth(bar_width);
        // h_nom->SetBarOffset(bar_offset);

        // leg->AddEntry(h_nom,legend_name,"f");
        leg->AddEntry(h_nom,legend_name,"lp");

        // h_nom->SetMinimum(-2.0);
        // h_nom->SetMaximum(2.0);

        rat_nom_hists.push_back(h_nom);
        rat_lo_hists.push_back(h_lo);
        rat_hi_hists.push_back(h_hi);

        delete h_unit;
    }

    // hmax = std::min(8.0,hmax);


    TH1D* h_frame = (TH1D*)rat_nom_hists.at(0)->Clone("h_frame");
    h_frame->SetTitle(";;");
    for (int i=1; i <= h_frame->GetXaxis()->GetNbins(); i++) {
        h_frame->SetBinContent(i,0.0);
    }
    h_frame->SetLineColor(kBlack);
    h_frame->SetLineWidth(1);

    TString xtitle = "";
    // TString ytitle = "1/prefit";
    // TString ytitle = TString::Format("#frac{fit - prefit}{prefit}");
    TString ytitle = TString::Format("#frac{#Delta Yield}{prefit}");
    TString frame_title = ";" + xtitle + ";" + ytitle;
    h_frame->SetTitle(frame_title);

    // h_frame->GetXaxis()->SetLabelSize(0.045);
    // h_frame->GetYaxis()->SetTitleSize(0.08);
    // h_frame->GetYaxis()->SetTitleOffset(1.50);
    // h_frame->GetYaxis()->SetLabelSize(0.055);

    h_frame->GetXaxis()->SetLabelSize(0.065);
    h_frame->GetYaxis()->SetTitleSize(0.045);
    h_frame->GetYaxis()->SetTitleOffset(1.10);
    h_frame->GetYaxis()->SetLabelSize(0.055);

    hmax = 1.2*hmax;
    hmin = 1.2*hmin;

    h_frame->SetMinimum(hmin);
    h_frame->SetMaximum(hmax);

    std::vector<OffScalePoint> off_scale_pts;

    // Remake the Ratio Histograms with offset binning to make nice side-by-side comparisons for a category
    int n_procs = rat_nom_hists.size();
    int n_cats = pts.size();
    std::vector<TH1D*> subbinned_nom_hists;
    std::vector<TH1D*> subbinned_lo_hists;
    std::vector<TH1D*> subbinned_hi_hists;
    std::vector<TGraphAsymmErrors*> fluct_hists;
    for (uint i=0; i < base_hists.size(); i++) {
        TH1D* h_parent = rat_nom_hists.at(i);
        Color_t line_clr = h_parent->GetLineColor();
        Color_t fill_clr = h_parent->GetFillColor();
        Style_t mark_sty = h_parent->GetMarkerStyle();
        int mark_sz = h_parent->GetMarkerSize();

        TString hname = TString::Format("%s_nom_proc_%d",wc_name.Data(),i);
        TH1D* h_nom = new TH1D(hname,";;",n_procs*n_cats,0.0,n_cats);
        h_nom->SetLineColor(line_clr);
        h_nom->SetFillColor(fill_clr);
        h_nom->SetMarkerStyle(mark_sty);
        h_nom->SetMarkerColor(fill_clr);
        h_nom->SetMarkerSize(mark_sz);

        hname = TString::Format("%s_lo_proc_%d",wc_name.Data(),i);
        TH1D* h_lo = (TH1D*)h_nom->Clone(hname);

        hname = TString::Format("%s_hi_proc_%d",wc_name.Data(),i);
        TH1D* h_hi = (TH1D*)h_nom->Clone(hname);

        // Crude workaround to 'hide' the unfilled bins...
        for (int bin=1; bin <= h_nom->GetXaxis()->GetNbins(); bin++) {
            h_nom->SetBinContent(bin,-999);
            h_lo->SetBinContent(bin,-999);
            h_hi->SetBinContent(bin,-999);
        }

        for (int bin=0; bin < h_parent->GetXaxis()->GetNbins(); bin++) {
            double nom_val = h_parent->GetBinContent(bin+1);
            double lo_val = rat_lo_hists.at(i)->GetBinContent(bin+1);
            double hi_val = rat_hi_hists.at(i)->GetBinContent(bin+1);
            int sub_bin = (i+1) + bin*n_procs;

            h_nom->SetBinContent(sub_bin,nom_val);
            h_lo->SetBinContent(sub_bin,lo_val);
            h_hi->SetBinContent(sub_bin,hi_val);

            if (nom_val > hmax) {
                OffScalePoint off_scale_pt;
                off_scale_pt.direction = 1;
                off_scale_pt.hist_bin = sub_bin;
                off_scale_pt.bin_center = h_nom->GetXaxis()->GetBinCenter(sub_bin);
                off_scale_pt.axis_max = hmax;
                off_scale_pt.nom_val = nom_val;
                off_scale_pt.lo_val = lo_val;
                off_scale_pt.hi_val = hi_val;
                off_scale_pt.clr = fill_clr;


                off_scale_pts.push_back(off_scale_pt);

                // Hide the off-scale bin markers
                h_nom->SetBinContent(sub_bin,-999);
                h_lo->SetBinContent(sub_bin,-999);
                h_hi->SetBinContent(sub_bin,-999);
            }

            // Another crude workaround to try and hide the tllq 4l entry for being way out of range
            // if (bin_val > hmax) {
            //     bin_val = -999;
            // } else if (bin_val < hmin) {
            //     bin_val = -999;
            // }
        }

        TGraphAsymmErrors* gr = make_ratio_fluct(h_nom,h_lo,h_hi);

        subbinned_nom_hists.push_back(h_nom);
        subbinned_lo_hists.push_back(h_lo);
        subbinned_hi_hists.push_back(h_hi);

        fluct_hists.push_back(gr);
    }
    ////////////////////////////////////////////////////////////////////////////////////////////////


    std::vector<TArrow*> arrows;
    for (OffScalePoint& pt: off_scale_pts) {
        get_offscale_arrow(pt);
        // TArrow* arrow = get_offscale_arrow(pt);
        // arrows.push_back(arrow);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Configure the TCanvas
    ////////////////////////////////////////////////////////////////////////////////////////////////

    c->cd(1);

    gStyle->SetPadBorderMode(0);
    gStyle->SetFrameBorderMode(0);

    Float_t small = 1.e-5;
    const float padding = 1e-5;
    const float xpad = small;    // Pad spacing left to right
    const float ypad = small;    // Pad spacing top to bottom

    const float ydiv = 0.3; // Height of the second pad
    const float ygap = 0.07;
    float L = xpad;
    float B = ypad;
    float R = 1-xpad;
    float T = 1-ypad;
    // c->Divide(1,2,small,small);
    c->Divide(1,1,small,small);
    // c->GetPad(1)->SetPad(padding,ydiv+padding,1-padding,1-padding); // Order: (L B R T)
    // c->GetPad(1)->SetPad(L,B+ydiv,R,T); // Order: (L B R T)
    c->GetPad(1)->SetPad(L,B,R,T); // Order: (L B R T)
    
    // Original margins
    c->GetPad(1)->SetTopMargin(.07);
    c->GetPad(1)->SetLeftMargin(.11);    
    c->GetPad(1)->SetRightMargin(.025);
    c->GetPad(1)->SetBottomMargin(0.1);

    // New Margins
    // c->GetPad(1)->SetTopMargin(0.08);
    // c->GetPad(1)->SetLeftMargin(0.16);    
    // c->GetPad(1)->SetRightMargin(0.02);
    // c->GetPad(1)->SetBottomMargin(0.08);
    
    c->GetPad(1)->Modified();

    c->cd(1);

    ////////////////////////////////////////////////////////////////////////////////////////////////

    h_frame->Draw();
    for (TGraphAsymmErrors* gr: fluct_hists) {
        gr->Draw("same,P,Z");
    }
    for (TH1D* h: subbinned_nom_hists) {
        // h->SetMarkerColor(kBlack);
        h->Draw("same,hist,P");
    }
    // heading->Draw();
    for (TLatex* latex: extra_text) {
        latex->Draw();
    }

    for (OffScalePoint pt: off_scale_pts) {
        pt.arrow->Draw();
        pt.latex->Draw();
    }

    // 2nd argument makes the CMS text slightly bigger then default (0.75)
    add_cms_text((TPad*)c->GetPad(1),0.85,0.80);

    TString base_str, save_format, save_name;
    base_str = "fluct_compare";

    save_format = "png";
    save_name = TString::Format("%s_%s.%s",base_str.Data(),title.Data(),save_format.Data());
    c->Print(save_name,save_format);

    save_format = "pdf";
    save_name = TString::Format("%s_%s.%s",base_str.Data(),title.Data(),save_format.Data());
    c->Print(save_name,save_format);

    save_name = TString::Format("ext_leg_flc");
    make_external_legend(leg,save_name);

    delete c;
    delete leg;
    // delete heading;
    for (TH1D* h: base_hists) delete h;
    for (TH1D* h: nom_hists) delete h;
    for (TH1D* h: lo_hists) delete h;
    for (TH1D* h: hi_hists) delete h;
    for (TH1D* h: rat_nom_hists) delete h;
    for (TH1D* h: rat_lo_hists) delete h;
    for (TH1D* h: rat_hi_hists) delete h;
    for (TH1D* h: subbinned_nom_hists) delete h;
    for (TH1D* h: subbinned_lo_hists) delete h;
    for (TH1D* h: subbinned_hi_hists) delete h;
    for (TGraphAsymmErrors* h: fluct_hists) delete h;
    for (OffScalePoint pt: off_scale_pts) delete pt.arrow;

    std::cout << std::endl;

    return;
}


void runit(TString in_dir,TString out_dir,std::set<std::string> skip_wcs,std::set<std::string> keep_wcs) {
    TH1::SetDefaultSumw2(1);
    gStyle->SetOptStat(0);

    if (!in_dir.EndsWith("/")) {
        in_dir += "/";
    }

    if (!out_dir.EndsWith("/")) {
        out_dir += "/";
    }

    std::cout << "Reading from: " << in_dir << std::endl;
    std::cout << "Output Dir:   " << out_dir << std::endl;

    // Read in objects from various files
    TFile* ws_file = TFile::Open(in_dir + "16D.root");
    if (!ws_file) {
        // Try looking for the SM workspace version (a directory should only have one or the other not both!)
        ws_file = TFile::Open(in_dir + "SMWorkspace.root");
    }
    RooWorkspace* ws = (RooWorkspace*) ws_file->Get("w");

    // A fitresult for getting the prefit uncertainties coming from the NP
    TString prefit_fname = "fitDiagnosticsPrefit.root";
    TFile* prefit_file   = TFile::Open(in_dir + prefit_fname);
    RooFitResult* prefit = 0;
    if (prefit_file) {
        prefit = (RooFitResult*) prefit_file->Get(FR_DIAGKEY);
    }
    
    // The fitresult from starting at SM
    TString postfit_fname = "multidimfitPostfit.root";
    TFile* postfit_file   = TFile::Open(in_dir + postfit_fname);
    RooFitResult* postfit = 0;
    if (postfit_file) {
        postfit = (RooFitResult*) postfit_file->Get(FR_MDKEY);
    }

    // The fitresult from starting at a 'bestfit' point (e.g. from 1d profiled scans)
    TString bestfit_fname = "multidimfitBestfit.root";
    TFile* bestfit_file   = TFile::Open(in_dir + bestfit_fname);
    RooFitResult* bestfit = 0;
    if (bestfit_file) {
        bestfit = (RooFitResult*) bestfit_file->Get(FR_MDKEY);
    }

    // The fitresult from freezing all POIs to SM values (i.e. NP only fit)
    TString nuisfit_fname = "multidimfitNuisOnly.root";
    TFile* nuisfit_file   = TFile::Open(in_dir + nuisfit_fname);
    RooFitResult* nuisfit = 0;
    if (nuisfit_file) {
        nuisfit = (RooFitResult*) nuisfit_file->Get(FR_MDKEY);
    }

    // The fitresult from freezing all POIs to a 'bestfit' point
    TString freeze_nom_fname = "multidimfitFreezeNom.root";
    // TString freeze_nom_fname = "multidimfitFreeze.root";
    TFile* freeze_nom_file   = TFile::Open(in_dir + freeze_nom_fname);
    RooFitResult* freezefit_nom = 0;
    if (freeze_nom_file) {
        freezefit_nom = (RooFitResult*) freeze_nom_file->Get(FR_MDKEY);
    }

    // The fitresult from freezing all POIs to the +1sigma 'bestfit' point
    TString freeze_up_fname = "multidimfitFreezeUp.root";
    TFile* freeze_up_file   = TFile::Open(in_dir + freeze_up_fname);
    RooFitResult* freezefit_up = 0;
    if (freeze_up_file) {
        freezefit_up = (RooFitResult*) freeze_up_file->Get(FR_MDKEY);
    }

    // The fitresult from freezing all POIs to the -1sigma 'bestfit' point
    TString freeze_down_fname = "multidimfitFreezeDown.root";
    TFile* freeze_down_file   = TFile::Open(in_dir + freeze_down_fname);
    RooFitResult* freezefit_down = 0;
    if (freeze_down_file) {
        freezefit_down = (RooFitResult*) freeze_down_file->Get(FR_MDKEY);
    }

    // Note: The prefit RooFitResult only contains the nuis. parameters, so uncertainties from the
    //          POIs are not included when calculating the propagated error
    if (prefit) {
        ws->saveSnapshot("prefit_i",prefit->floatParsInit(),kTRUE);
    }
    if (postfit) {    
        ws->saveSnapshot("postfit_i",postfit->floatParsInit(),kTRUE);
        ws->saveSnapshot("postfit_f",postfit->floatParsFinal(),kTRUE);
    }
    if (bestfit) {
        ws->saveSnapshot("bestfit_i",bestfit->floatParsInit(),kTRUE);
        ws->saveSnapshot("bestfit_f",bestfit->floatParsFinal(),kTRUE);
    }
    if (nuisfit) {
        ws->saveSnapshot("nuisfit_i",nuisfit->floatParsInit(),kTRUE);
        ws->saveSnapshot("nuisfit_f",nuisfit->floatParsFinal(),kTRUE);
    }
    if (freezefit_nom) {    
        ws->saveSnapshot("freeze_nom_i",freezefit_nom->floatParsInit(),kTRUE);
        ws->saveSnapshot("freeze_nom_f",freezefit_nom->floatParsFinal(),kTRUE);
    }

    // Create instances of our helper classes
    WSHelper ws_helper = WSHelper();

    RooArgSet pois = ws_helper.getPOIs(ws);
    RooArgSet nuis = ws_helper.getNuisances(ws);

    std::vector<TString> cat_names;
    // NOTE: second part of the map needs to be a ptr, otherwise the map ctor fails horribly!
    std::unordered_map<std::string,AnalysisCategory*> all_cats;
    for (RooCatType* c: ws_helper.getTypes(ws)) {
        TString cat_name(c->GetName());
        AnalysisCategory* ana_cat = new AnalysisCategory(c->GetName(),ws);
        all_cats[cat_name.Data()] = ana_cat;
        cat_names.push_back(cat_name);
        // std::cout << "cat_name: " << cat_name << std::endl;
    }

    // All of these categories are built from 'fundamental' categories
    std::unordered_map<std::string,std::vector<TString> > cat_groups;
    cat_groups["all"] = {
        "C_2lss_p_2b_4j",
        "C_2lss_p_2b_5j",
        "C_2lss_p_2b_6j",
        "C_2lss_p_2b_ge7j",
        "C_2lss_m_2b_4j",
        "C_2lss_m_2b_5j",
        "C_2lss_m_2b_6j",
        "C_2lss_m_2b_ge7j",
        "C_3l_mix_p_1b_2j",
        "C_3l_mix_p_1b_3j",
        "C_3l_mix_p_1b_4j",
        "C_3l_mix_p_1b_ge5j",
        "C_3l_mix_m_1b_2j",
        "C_3l_mix_m_1b_3j",
        "C_3l_mix_m_1b_4j",
        "C_3l_mix_m_1b_ge5j",
        "C_3l_mix_p_2b_2j",
        "C_3l_mix_p_2b_3j",
        "C_3l_mix_p_2b_4j",
        "C_3l_mix_p_2b_ge5j",
        "C_3l_mix_m_2b_2j",
        "C_3l_mix_m_2b_3j",
        "C_3l_mix_m_2b_4j",
        "C_3l_mix_m_2b_ge5j",
        "C_3l_mix_sfz_1b_2j",
        "C_3l_mix_sfz_1b_3j",
        "C_3l_mix_sfz_1b_4j",
        "C_3l_mix_sfz_1b_ge5j",
        "C_3l_mix_sfz_2b_2j",
        "C_3l_mix_sfz_2b_3j",
        "C_3l_mix_sfz_2b_4j",
        "C_3l_mix_sfz_2b_ge5j",
        "C_4l_2b_2j",
        "C_4l_2b_3j",
        "C_4l_2b_ge4j",
    };
    cat_groups["2lss_m"] = {
        "C_2lss_m_2b_4j",
        "C_2lss_m_2b_5j",
        "C_2lss_m_2b_6j",
        "C_2lss_m_2b_ge7j"
    };
    cat_groups["2lss_p"] = {
        "C_2lss_p_2b_4j",
        "C_2lss_p_2b_5j",
        "C_2lss_p_2b_6j",
        "C_2lss_p_2b_ge7j",
    };
    cat_groups["3l_p_nsfz_1b"] = {
        "C_3l_mix_p_1b_2j",
        "C_3l_mix_p_1b_3j",
        "C_3l_mix_p_1b_4j",
        "C_3l_mix_p_1b_ge5j",
    };
    cat_groups["3l_m_nsfz_1b"] = {
        "C_3l_mix_m_1b_2j",
        "C_3l_mix_m_1b_3j",
        "C_3l_mix_m_1b_4j",
        "C_3l_mix_m_1b_ge5j",
    };
    cat_groups["3l_p_nsfz_2b"] = {
        "C_3l_mix_p_2b_2j",
        "C_3l_mix_p_2b_3j",
        "C_3l_mix_p_2b_4j",
        "C_3l_mix_p_2b_ge5j",
    };
    cat_groups["3l_m_nsfz_2b"] = {
        "C_3l_mix_m_2b_2j",
        "C_3l_mix_m_2b_3j",
        "C_3l_mix_m_2b_4j",
        "C_3l_mix_m_2b_ge5j",
    };
    cat_groups["3l_sfz_1b"] = {
        "C_3l_mix_sfz_1b_2j",
        "C_3l_mix_sfz_1b_3j",
        "C_3l_mix_sfz_1b_4j",
        "C_3l_mix_sfz_1b_ge5j",
    };
    cat_groups["3l_sfz_2b"] = {
        "C_3l_mix_sfz_2b_2j",
        "C_3l_mix_sfz_2b_3j",
        "C_3l_mix_sfz_2b_4j",
        "C_3l_mix_sfz_2b_ge5j",
    };
    cat_groups["4l"] = {
        "C_4l_2b_2j",
        "C_4l_2b_3j",
        "C_4l_2b_ge4j",
    };

    // Can of course have groups of any arbitrary combination
    cat_groups["wacky"] = {
        "C_3l_mix_p_1b_2j",
        "C_4l_2b_3j",
        "C_2lss_m_2b_5j"
    };

    // For the njet merged plots, this determines the bin order
    std::vector<TString> cat_group_names {
        "2lss_p",
        "2lss_m",
        "3l_p_nsfz_1b",
        "3l_m_nsfz_1b",
        "3l_p_nsfz_2b",
        "3l_m_nsfz_2b",
        "3l_sfz_1b",
        "3l_sfz_2b",
        "4l",

        // "wacky",
        // "all",
    };

    //////////////////////
    // Create some merged categories, i.e. create a new category which is the merger of all
    //  sub-categories of the corresponding 'cat_groups' entry
    //////////////////////
    std::unordered_map<std::string,AnalysisCategory*> merged_cats;
    for (TString mrg_name: cat_group_names) {
        std::vector<AnalysisCategory*> to_merge;
        for (TString s: cat_groups[mrg_name.Data()]) {
            // TODO: Should probably add a check to make sure the category key actually exists...
            to_merge.push_back(all_cats[s.Data()]);
        }
        merged_cats[mrg_name.Data()] = new AnalysisCategory(mrg_name,to_merge);
        merged_cats[mrg_name.Data()]->setProcOrder(YIELD_TABLE_ORDER);
        // TODO: Should probably add a check to make sure the new category name doesn't already exist...
        all_cats[mrg_name.Data()] = merged_cats[mrg_name.Data()];   // This might be a bit spicy...
    }

    std::vector<AnalysisCategory*> cats_to_plot;    // These are basically the bins of the histogram we want to make
    // Plot the merged categories as the bins
    for (TString cat_name: cat_group_names) {
        cats_to_plot.push_back(all_cats[cat_name.Data()]);
    }

    //////////////////////
    // Print some stuff
    //////////////////////

    bool incl_print_info = false;

    if (incl_print_info) {
        std::cout << "--------------" << std::endl;
        std::cout << "--- prefit ---" << std::endl;
        std::cout << "--------------" << std::endl;
        ws->loadSnapshot("postfit_i");
        printLatexYieldTable(cats_to_plot,SIG_PROCS,BKGD_PROCS,prefit);

        std::cout << "---------------" << std::endl;
        std::cout << "--- nuisfit ---" << std::endl;
        std::cout << "---------------" << std::endl;
        if (nuisfit) {
            ws->loadSnapshot("nuisfit_f");
            printLatexYieldTable(cats_to_plot,SIG_PROCS,BKGD_PROCS,nuisfit);
        } else {
            std::cout << "WARNING: Missing nuisfit" << std::endl;
        }

        std::cout << "---------------" << std::endl;
        std::cout << "--- postfit ---" << std::endl;
        std::cout << "---------------" << std::endl;
        ws->loadSnapshot("postfit_f");
        printLatexYieldTable(cats_to_plot,SIG_PROCS,BKGD_PROCS,postfit);

        // for (AnalysisCategory* ana_cat: cats_to_plot) ana_cat->Print(prefit);
        // prefit->Print("v");
    }

    // nuisfit->Print("v");
    // postfit->Print("v");

    std::vector<TFile*> fluct_files;
    std::vector<RooFitResult*> fluct_fits;

    //////////////////////
    // Make some plots
    //////////////////////

    // Options for which plots to make
    bool incl_summary_plots = true;
    bool incl_summary_gif_plots = false;
    bool incl_njets_plots = false;
    bool incl_fluct_plots = false;

    // Plot layout options
    bool incl_ratio = true;
    bool incl_leg = false;
    bool incl_ext_leg = true;
    // int incl_ext_leg = 0;
    
    // Note: Irrelevant if not making fluctuation plots
    // std::vector<TString> wc_to_fluctuate {};
    // std::vector<TString> wc_to_fluctuate {"ctG","ctW","ctZ","ctp","cpQM","cbW"};
    std::vector<TString> wc_to_fluctuate {"cbW","ctZ"};

    // This is kind of a really stupid way to do this, I'm just being lazy and don't want to have to
    //  constantly clear the std::vector a bunch of times and refill it with a fresh TLatex object
    //  everytime
    TLatex* latex = new TLatex();
    std::vector<TLatex*> extra_text;
    extra_text.push_back(latex);

    // Plot the (potentially merged) categories from 'cats_to_plot' as the bins
    if (incl_summary_plots) {

        // Make the prefit histogram stack plot
        ws->loadSnapshot("postfit_i");
        latex->SetNDC();
        latex->SetTextFont(42);
        latex->SetTextSize(0.080);  // Was 0.070
        latex->SetTextAlign(13);
        latex->SetText(0.15,0.78,"Prefit");
        make_overlay_plot_v2("noflucts_prefit",extra_text,cats_to_plot,prefit,incl_ratio,incl_leg,incl_ext_leg);
        // Make the postfit histogram stack plot
        ws->loadSnapshot("postfit_f");
        latex->SetNDC();
        latex->SetTextFont(42);
        latex->SetTextSize(0.080);  // Was 0.070
        latex->SetTextAlign(13);
        latex->SetText(0.15,0.78,"Postfit");
        for (auto& kv: BEST_FIT_POIS) {
            std::string rrv_poi_name = kv.first;
            double rrv_value = kv.second;
            setRRV(pois,rrv_poi_name,rrv_value);
        }
        make_overlay_plot_v2("noflucts_postfit",extra_text,cats_to_plot,freezefit_nom,incl_ratio,incl_leg,incl_ext_leg);

        ws->loadSnapshot("nuisfit_f");
        latex->SetNDC();
        latex->SetTextFont(42);
        latex->SetTextSize(0.080);  // Was 0.070
        latex->SetTextAlign(13);
        latex->SetText(0.15,0.78,"NuisOnly");
        for (auto& kv: BEST_FIT_POIS) {
            std::string rrv_poi_name = kv.first;
            double rrv_value = 0.0;
            setRRV(pois,rrv_poi_name,rrv_value);
        }
        make_overlay_plot_v2("noflucts_nuisfit",extra_text,cats_to_plot,nuisfit,incl_ratio,incl_leg,incl_ext_leg);

        ////////////////////////////////////////////////////////////////////////////////////
        // Note: We now make these plots via the dedicated 'make_fluct_compare_plots' function,
        //       kept around for posterity sake
        ////////////////////////////////////////////////////////////////////////////////////
        /*
        if (incl_fluct_plots) {
            // Make the postfit WC 2sigma Up/Down fluctuation histogram stack plots
            for (TString wc_name: wc_to_fluctuate) {
                TString snapshot_name;
                TString plot_name, head_name, styled_name;
                double rrv_val;

                styled_name = wc_name;
                if (WC_LABEL_MAP.count(wc_name.Data())) {
                    styled_name = WC_LABEL_MAP[wc_name.Data()];
                }

                // Note: Hardcoded path here!!!
                TString dumb_path = "/afs/crc.nd.edu/user/a/awightma/CMSSW_Releases/CMSSW_8_1_0/src/EFTFit/Fitter/test/profiled_fitresults";
                TString dumb_fname_up = TString::Format("%s/multidimfit%sUpFitResult.root",dumb_path.Data(),wc_name.Data());
                TString dumb_fname_down = TString::Format("%s/multidimfit%sDownFitResult.root",dumb_path.Data(),wc_name.Data());
                TFile* fluct_file_up = TFile::Open(dumb_fname_up);
                TFile* fluct_file_down = TFile::Open(dumb_fname_down);

                fluct_files.push_back(fluct_file_up);
                fluct_files.push_back(fluct_file_down);

                ////////////////////////////////////////////////////////////////////////////////////
                // Note: These fitresults were created by freezing a particular WC to a specific value
                //       so they don't have that specific WC in the 'floatParsFinal()' object and won't
                //       get set via a 'loadSnapshot' call, need to make sure to set its value explicitly
                ////////////////////////////////////////////////////////////////////////////////////
                
                RooFitResult* fluct_fit_up   = (RooFitResult*)fluct_file_up->Get(FR_MDKEY);
                RooFitResult* fluct_fit_down = (RooFitResult*)fluct_file_down->Get(FR_MDKEY);

                fluct_fits.push_back(fluct_fit_up);
                fluct_fits.push_back(fluct_fit_down);

                ////////////////////////////////////////////////////////////////////////////////////
                // Make the up variation overlaid plots
                ////////////////////////////////////////////////////////////////////////////////////
                snapshot_name = TString::Format("%s_up_profiled_f",wc_name.Data());
                plot_name = TString::Format("%s_up_postfit",wc_name.Data());
                head_name = TString::Format("%s Up",styled_name.Data());
                ws->saveSnapshot(snapshot_name,fluct_fit_up->floatParsFinal(),kTRUE);
                ws->loadSnapshot(snapshot_name);
                rrv_val = getRRV(fluct_fit_up->constPars(),wc_name.Data());
                std::cout << TString::Format("%s Up Value: %.2f",wc_name.Data(),rrv_val) << std::endl;
                setRRV(pois,wc_name.Data(),rrv_val);
                latex->SetNDC();
                latex->SetTextFont(42);
                latex->SetTextSize(0.070);
                latex->SetText(0.11,0.91,head_name.Data());
                make_overlay_plot_v2(plot_name,extra_text,cats_to_plot,fluct_fit_up,incl_ratio,incl_leg,incl_ext_leg);
                
                ////////////////////////////////////////////////////////////////////////////////////
                // Make the down variation overlaid plots
                ////////////////////////////////////////////////////////////////////////////////////
                snapshot_name = TString::Format("%s_down_profiled_f",wc_name.Data());
                plot_name = TString::Format("%s_down_postfit",wc_name.Data());
                head_name = TString::Format("%s Down",styled_name.Data());
                ws->saveSnapshot(snapshot_name,fluct_fit_down->floatParsFinal(),kTRUE);
                ws->loadSnapshot(snapshot_name);
                rrv_val = getRRV(fluct_fit_down->constPars(),wc_name.Data());
                std::cout << TString::Format("%s Down Value: %.2f",wc_name.Data(),rrv_val) << std::endl;
                setRRV(pois,wc_name.Data(),rrv_val);
                latex->SetNDC();
                latex->SetTextFont(42);
                latex->SetTextSize(0.070);
                latex->SetText(0.11,0.91,head_name.Data());
                make_overlay_plot_v2(plot_name,extra_text,cats_to_plot,fluct_fit_down,incl_ratio,incl_leg,incl_ext_leg);
            }
        }
        */
    }

    if (incl_summary_gif_plots) {
        int num_steps = 6;
        for (int i = 0; i <= num_steps; i++) {
            latex->SetNDC();
            latex->SetTextFont(42);
            latex->SetTextSize(0.080);
            latex->SetTextAlign(13);
            // latex->SetText(0.15,0.78,"Postfit");
            latex->SetText(0.15,0.78,"");
            ws->loadSnapshot("postfit_f");
            for (auto& kv: BEST_FIT_POIS) {
                std::string rrv_poi_name = kv.first;
                double rrv_value = i*kv.second / num_steps;
                setRRV(pois,rrv_poi_name,rrv_value);
            }
            TString name_prefix = TString::Format("summary_gif_%02d",i);
            make_overlay_plot_v2(name_prefix,extra_text,cats_to_plot,freezefit_nom,incl_ratio,incl_leg,incl_ext_leg);
        }
    }
    
    // Make the fancier postfit WC 2sigma Up/Down fluctuation histogram stack plots
    if (incl_fluct_plots) {
        for (TString wc_name: wc_to_fluctuate) {
            ////////////////////////////////////////////////////////////////////////////////////////
            // Note: Currently hardcoded path to the directory containing the dedicated fits at all
            //       of the corresponding scan points
            ////////////////////////////////////////////////////////////////////////////////////////
            TString tdir = "/afs/crc.nd.edu/user/a/awightma/CMSSW_Releases/CMSSW_8_1_0/src/EFTFit/Fitter/test/extracted_combine_scans";
            std::vector<ExtremumPoint> extremum_pts;
            std::vector<ExtremumPoint> sum_extremum_pts;
            for (AnalysisCategory* ana_cat: cats_to_plot) {
                ExtremumPoint pt = get_extremum_fitresult(tdir,wc_name,SIG_PROCS,ana_cat,ws,pois);
                // Fill in the 'extra' info for the ExtremumPoint
                pt.base_snp = "postfit_i";
                pt.nom_snp = "postfit_f";
                for (uint i=0; i < pt.procs.size(); i++) {
                    TString p = pt.procs.at(i);
                    TString lo_fn = pt.lo_fnames.at(i);
                    TString hi_fn = pt.hi_fnames.at(i);

                    double lo_yld = pt.lo_ylds.at(i);
                    double hi_yld = pt.hi_ylds.at(i);

                    ws->loadSnapshot(pt.base_snp);
                    double base_yld = ana_cat->getExpProc(p);
                    pt.base_ylds.at(i) = base_yld;

                    ws->loadSnapshot(pt.nom_snp);
                    double nom_yld = ana_cat->getExpProc(p);
                    pt.nom_ylds.at(i) = nom_yld;
                }
                extremum_pts.push_back(pt);

                ExtremumPoint sum_pt = merge_extremum_processes("sum",pt);
                sum_extremum_pts.push_back(sum_pt);
            }
            TString plot_name, head_name, styled_name;

            styled_name = wc_name;
            if (WC_LABEL_MAP.count(wc_name.Data())) {
                styled_name = WC_LABEL_MAP[wc_name.Data()];
            }

            plot_name = TString::Format("%s_flc",wc_name.Data());
            head_name = TString::Format("Coefficient: %s",styled_name.Data());

            latex->SetNDC();
            latex->SetTextSize(0.060);
            latex->SetTextFont(42);
            latex->SetTextAlign(13);
            latex->SetText(0.15,0.85,head_name.Data());

            // latex->SetTextSize(0.050);
            // latex->SetTextFont(42);
            // latex->SetTextAlign(13);
            // latex->SetText(0.20,0.83,head_name.Data());

            make_fluct_compare_plots(plot_name,extra_text,wc_name,extremum_pts);

            // Make the 'summed process' version of these plots
            plot_name = TString::Format("sum_%s_flc",wc_name.Data());
            // make_fluct_compare_plots(plot_name,extra_text,wc_name,sum_extremum_pts);
        }
    }


    // Plot a specific category with njets as the bins
    if (incl_njets_plots) {
        for (TString cat_group_name: cat_group_names) {
            TString plot_name, heading_name;

            cats_to_plot.clear();    
            for (TString cat_name: cat_groups[cat_group_name.Data()]) {
                cats_to_plot.push_back(all_cats[cat_name.Data()]);
            }

            ws->loadSnapshot("postfit_i");
            // for (auto& kv: SM_POIS) setRRV(pois,kv.first,kv.second);
            plot_name = TString::Format("%s_prefit",cat_group_name.Data());
            heading_name = TString::Format("Prefit: %s",cat_group_name.Data());
            if (BIN_LABEL_MAP.count(cat_group_name.Data())) {
                heading_name = TString::Format("Prefit: %s",BIN_LABEL_MAP[cat_group_name.Data()].c_str());
            }
            latex->SetNDC();
            latex->SetTextFont(42);
            latex->SetTextSize(0.070);
            latex->SetText(0.11,0.91,heading_name.Data());
            make_overlay_plot_v2(plot_name,extra_text,cats_to_plot,prefit,incl_ratio,incl_leg,incl_ext_leg);

            ws->loadSnapshot("bestfit_f");
            // for (auto& kv: BEST_FIT_POIS) setRRV(pois,kv.first,kv.second);
            plot_name = TString::Format("%s_postfit",cat_group_name.Data());
            heading_name = TString::Format("Postfit: %s",cat_group_name.Data());
            if (BIN_LABEL_MAP.count(cat_group_name.Data())) {
                heading_name = TString::Format("Postfit: %s",BIN_LABEL_MAP[cat_group_name.Data()].c_str());
            }
            latex->SetNDC();
            latex->SetTextFont(42);
            latex->SetTextSize(0.070);
            latex->SetText(0.11,0.91,heading_name.Data());
            make_overlay_plot_v2(plot_name,extra_text,cats_to_plot,bestfit,incl_ratio,incl_leg,incl_ext_leg);

            if (incl_fluct_plots) {
                // Make plots of njets with the WC Up/Down fluctuations
                for (TString wc_name: wc_to_fluctuate) {
                    continue; // Skip the njets fluct plots for now
                    
                    TString styled_name = wc_name;
                    if (WC_LABEL_MAP.count(wc_name.Data())) {
                        styled_name = WC_LABEL_MAP[wc_name.Data()];
                    }

                    ws->loadSnapshot("postfit_f");
                    for (auto& kv: BEST_FIT_POIS) setRRV(pois,kv.first,kv.second);
                    setRRV(pois,wc_name.Data(),HI_POIS[wc_name.Data()]);
                    plot_name = TString::Format("%s_%s_up_postfit",cat_group_name.Data(),wc_name.Data());
                    heading_name = TString::Format("Postfit: %s %s Up",cat_group_name.Data(),styled_name.Data());
                    if (BIN_LABEL_MAP.count(cat_group_name.Data())) {
                        heading_name = TString::Format("Postfit: %s %s Up",BIN_LABEL_MAP[cat_group_name.Data()].c_str(),styled_name.Data());
                    }
                    latex->SetNDC();
                    latex->SetTextFont(42);
                    latex->SetTextSize(0.070);
                    latex->SetText(0.11,0.91,heading_name.Data());
                    make_overlay_plot_v2(plot_name,extra_text,cats_to_plot,prefit,incl_ratio,incl_leg,incl_ext_leg);

                    ws->loadSnapshot("postfit_f");
                    for (auto& kv: BEST_FIT_POIS) setRRV(pois,kv.first,kv.second);
                    setRRV(pois,wc_name.Data(),LO_POIS[wc_name.Data()]);
                    plot_name = TString::Format("%s_%s_down_postfit",cat_group_name.Data(),wc_name.Data());
                    heading_name = TString::Format("Postfit: %s %s Down",cat_group_name.Data(),styled_name.Data());
                    if (BIN_LABEL_MAP.count(cat_group_name.Data())) {
                        heading_name = TString::Format("Postfit: %s %s Down",BIN_LABEL_MAP[cat_group_name.Data()].c_str(),styled_name.Data());
                    }
                    latex->SetNDC();
                    latex->SetTextFont(42);
                    latex->SetTextSize(0.070);
                    latex->SetText(0.11,0.91,heading_name.Data());
                    make_overlay_plot_v2(plot_name,extra_text,cats_to_plot,prefit,incl_ratio,incl_leg,incl_ext_leg);
                }
            }
        }
    }
    return;
}


void overlay_operator_variations(TString input_dir, TString output_dir) {
    // gROOT->LoadMacro("tdrstyle.C");
    // setTDRStyle();

    // gEnv->Print();

    // These do nothing currently...
    std::set<std::string> skip {};  // Dummy sets
    std::set<std::string> keep {"ctlTi"};  // Dummy sets

    runit(input_dir,output_dir,skip,keep);
}
////////////////////////////////////////////////////////////////////////////////////////////////////