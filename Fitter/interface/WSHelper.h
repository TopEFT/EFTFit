#ifndef WSHELPER_H_
#define WSHELPER_H_

#include <vector>
#include <set>
#include <stdio.h>

#include "TString.h"
#include "TIterator.h"

#include "RooWorkspace.h"
#include "RooCategory.h"
#include "RooFitResult.h"
#include "RooProdPdf.h"
#include "RooAddition.h"
#include "RooRealVar.h"

// Helper class for working with and manipulating RooWorkspace objects
class WSHelper {
    private:
        typedef std::vector<TString> vTStr;
        typedef std::pair<TString,double> pTStrDbl;
        TString n_exp_search_str = "n_exp_bin";
        TString n_exp_search_str_pdf = "shape";        
    public:
        WSHelper();
        ~WSHelper();
        RooArgSet getPOIs(RooWorkspace* ws);
        RooArgSet getNuisances(RooWorkspace* ws);
        std::vector<TString> getProcesses(RooWorkspace* ws);
        std::vector<RooCatType*>    getTypes(RooWorkspace* ws,TString name="CMS_channel");
        std::vector<RooAbsReal*>    getExpCatFuncs(RooWorkspace* ws,RooCatType* cat_type);
        std::vector<RooAbsReal*>    getExpCatFuncs(RooWorkspace* ws,std::vector<RooCatType*> cat_types);
        std::vector<RooAbsPdf*>     getPdfs(RooWorkspace* ws,
                                        bool bkg_only=0,
                                        bool nuis_pdfs=0,
                                        bool other_pdfs=0,
                                        bool all_pdfs=0);
        std::vector<RooAbsData*>    getObsData(RooWorkspace* ws,
                                        TString n1,
                                        TString n2,
                                        std::vector<RooCatType*> cat_types);
        std::vector<RooAddition*>   getSummedCats(std::vector<RooAbsReal*> funcs,
                                        std::vector<RooCatType*> cat_types,
                                        vTStr procs={},
                                        TString override="");
        std::vector<pTStrDbl>       mergeDataBins(std::vector<RooAbsData*> datasets,
                                        TString merge_name,
                                        std::vector<RooCatType*> cats,
                                        vTStr sub_cats);
        std::vector<RooAddition*>   mergeSubCats(std::vector<RooAbsReal*> funcs,
                                        TString merge_name,
                                        vTStr procs,
                                        vTStr sub_cats);
        double sumObsDataByCats(RooWorkspace* ws,
            TString n1, TString n2,
            std::vector<RooCatType*> cat_types);
        void printSnapshot(RooWorkspace* ws,TString name);
        std::vector<RooAddition*> toRooAdd(std::vector<RooAbsReal*> funcs);
        std::vector<TString> toCatStr(std::vector<RooCatType*> cats);
        TString searchPdf(RooWorkspace* ws, TString name);

        // Define the templated member functions inline

        // Returns the expected events summed over all processes for a particular category
        template<typename T>
        RooAddition* sumProcesses(std::vector<T> funcs, TString cat_name, vTStr procs={}, TString override="") {
            TString name = cat_name;
            if (override.Length() > 0) {
                name = override;
            }
            std::vector<TRegexp> re_exps;
            if (procs.size()) {
                // Matches to: "*{cat_name}_proc_{p1,p2,...}"
                for (TString p: procs) {
                    re_exps.push_back(cat_name+"_proc_"+p+"$"); // Ensure exact matches to the process
                }
            } else {
                // Matches to: "*{cat_name}_proc_*"
                re_exps.push_back(TRegexp(cat_name+"_proc_"));  // Merge all processes
            }
            std::vector<T> subset = this->filter(funcs,re_exps);
            return this->merge(subset,name);
        }

        //TODO: Need to figure out how to handle the override option
        // Note: This is effectively identical to the 'getSummedCats' member function, except takes
        //      a vector of TStrings instead.
        template<typename T>
        std::vector<RooAddition*> sumProcesses(std::vector<T> funcs, vTStr cats, vTStr procs={}, TString override="") {
            std::vector<RooAddition*> ret;
            for (TString cat: cats) {
                TString name_override = "";
                if (override.Length() > 0) {
                    //TODO: This is not a good solution, need to come up with a better method
                    name_override = cat + override;
                }
                ret.push_back(this->sumProcesses(funcs,cat,procs,name_override));
            }
            return ret;
        }
        // Filters the collection by comparing to list of patterns
        // Note: Works with any objects T which have a GetName() member function
        template<typename T>
        std::vector<T> filter(std::vector<T> vec,std::vector<TRegexp> pats,bool mode=0) {
            // mode = 0 --> whitelist mode
            // mode = 1 --> blacklist mode
            std::vector<T> subset;
            for (auto v: vec) {
                TString name = v->GetName();
                bool add_it = mode;  // false for whitelist mode, true for blacklist mode
                for (auto pat: pats) {
                    Ssiz_t len = name.Length();
                    bool chk = (pat.Index(name,&len) > -1);
                    if (chk) {
                        //In either case, break on first match (i.e wl any match passes, bl any match fails)
                        add_it = !mode;
                        break;
                    }
                }
                if (add_it) {
                    subset.push_back(v);
                }
            }
            return subset;
        }
        // Overloaded version to handle single patterns
        template<typename T>
        std::vector<T> filter(std::vector<T> vec,TRegexp pat,bool mode=0) {
            std::vector<TRegexp> tvec {pat};
            return this->filter(vec,tvec,mode);
        }
        // Add functions together which match any of the specified strings
        template<typename T>
        RooAddition* merge(std::vector<T> funcs,TString merged_name,vTStr pats={},bool mode=0) {
            // mode = 0 --> whitelist mode
            // mode = 1 --> blacklist mode
            RooArgSet args;
            for (auto f: funcs) {
                TString str = f->GetName();
                if (pats.size() != 0) {
                    bool add_it = mode;
                    for (auto pat: pats) {
                        bool chk = str.Contains(pat);
                        if (chk) {
                            add_it = !mode; // In either case, break on first match (i.e wl any match passes, bl any match fails)
                            break;
                        }
                    }
                    if (add_it) {
                        args.add(*f);
                    }
                } else {
                    // No pattern --> merge all functions together
                    args.add(*f);
                }
            }
            RooAddition* roo_add = new RooAddition(merged_name,merged_name,args);
            return roo_add;
        }
        // Overloaded version to handle single patterns
        template<typename T>
        RooAddition* merge(std::vector<T> funcs,TString merged_name,TString pat,bool mode=0) {
            std::vector<TRegexp> tvec {pat};
            return this->merge(funcs,merged_name,tvec,mode);
        }
        // Strip process name from name and return resulting substr
        template<typename T>
        TString stripProcessName(T func) {
            TString sub_str = "";
            TString s = func->GetName();
            int idx = s.Index("_proc_");
            if (idx < 0) {
                return s;
            }
            sub_str = s(0,idx);
            return sub_str;
        }
        // Iterates over the functions, strips the process info and returns a unique list of TString results
        //TODO: This function needs to be renamed to better reflect its purpose
        template<typename T>
        vTStr stripProcessName(std::vector<T> funcs) {
            std::set<TString> tmp;
            vTStr ret;
            for (auto f: funcs) {
                TString sub_str = this->stripProcessName(f);
                if (sub_str.Length() == 0) {
                    continue;
                } else if (tmp.count(sub_str)) {
                    continue;
                } else {
                    tmp.insert(sub_str);
                    ret.push_back(sub_str);
                }
            }
            return ret;
        }
};

WSHelper::WSHelper() {}
WSHelper::~WSHelper() {}

// Returns all POIs from the workspace as a RooArgSet
RooArgSet WSHelper::getPOIs(RooWorkspace* ws) {
    RooStats::ModelConfig* mc_s = dynamic_cast<RooStats::ModelConfig *>(ws->genobj("ModelConfig"));
    RooArgSet pois(*mc_s->GetParametersOfInterest());
    return pois;
}

RooArgSet WSHelper::getNuisances(RooWorkspace* ws) {
    RooStats::ModelConfig* mc_s = dynamic_cast<RooStats::ModelConfig *>(ws->genobj("ModelConfig"));
    RooArgSet nuis(*mc_s->GetNuisanceParameters());
    return nuis;
}

// Returns all processes from the workspace (not in any particular order)
std::vector<TString> WSHelper::getProcesses(RooWorkspace* ws) {
    std::vector<RooCatType*> all_cats = this->getTypes(ws,"CMS_channel");
    std::vector<RooAbsReal*> all_exp = this->getExpCatFuncs(ws,all_cats);

    std::set<std::string> set_procs;
    std::vector<TString> procs;

    TString search = "_proc_";
    for (auto f: all_exp) {
        TString name = f->GetName();
        Ssiz_t idx = name.Index(search);
        if (idx == TString::kNPOS) {
            continue;
        }
        name = name(idx+search.Length(),name.Length());
        std::string p = name.Data();
        if (!set_procs.count(p)) {
            procs.push_back(name);
        }
        set_procs.insert(p);
    }

    return procs;
}

// Returns all type states for the specified category in the workspace
std::vector<RooCatType*> WSHelper::getTypes(RooWorkspace* ws,TString name="CMS_channel") {
    std::vector<RooCatType*> r;
    RooCategory* c = ws->cat(name);
    RooCatType* next = 0;
    TIterator* it = c->typeIterator();
    while((next=(RooCatType*)it->Next())) {
        r.push_back(next);
    }
    return r;
}

// Overloaded function to allow for passing a single category instead of a vector
std::vector<RooAbsReal*> WSHelper::getExpCatFuncs(RooWorkspace* ws,RooCatType* cat_type) {
    std::vector<RooCatType*> tmp_v {cat_type};
    return this->getExpCatFuncs(ws,tmp_v);
}

// Returns all function names for the expected events in a set of categories from the workspace
std::vector<RooAbsReal*> WSHelper::getExpCatFuncs(RooWorkspace* ws,std::vector<RooCatType*> cat_types) {
    std::vector<RooAbsReal*> r;
    RooArgSet funcs = ws->allFunctions();
    RooFIter it = funcs.fwdIterator();
    RooAbsArg* next = 0;
    while ((next=it.next())) {
        TString str = next->GetName();
        if (!str.BeginsWith(this->n_exp_search_str)) {
            continue;
        }
        for (auto ctype: cat_types) {
            TString match = TString::Format("_bin%s_",ctype->GetName());
              if (str.Contains(match)) {
                RooAbsReal* f = ws->function(str);
                r.push_back(f);
            }
        }
    }

    // If a process is made as a constant, it won't show up in allFunctions(), but rather all_Vars()
    RooArgSet vars = ws->allVars();
    it = vars.fwdIterator();
    next = 0;
    while ((next=it.next())) {
        TString str = next->GetName();
        if (!str.BeginsWith(this->n_exp_search_str)) {
            continue;
        }
        for (auto ctype: cat_types) {
            TString match = TString::Format("_bin%s_",ctype->GetName());
              if (str.Contains(match)) {
                RooAbsReal* f = ws->function(str);
                r.push_back(f);
            }
        }
    }

    return r;
}

// Return specified ws pdf objects in a std::vector container
std::vector<RooAbsPdf*> WSHelper::getPdfs(RooWorkspace* ws,
    bool bkg_pdfs=0,
    bool nuis_pdfs=0,
    bool other_pdfs=0,//others
    bool all_pdfs=0
) {
    // Note: All filter options result in mutually exlusive sets (only exception being the 'all' option)
    // 0 0 0 1 --> all pdfs
    // 0 0 1 0 --> other pdfs
    // 0 0 0 0 --> sig pdfs
    // 0 1 0 0 --> sig_nuis pdfs
    // 1 0 0 0 --> bkg pdfs
    // 1 1 0 0 --> bkg_nuis pdfs
    std::vector<RooAbsPdf*> tmp;
    RooArgSet pdfs = ws->allPdfs();
    RooFIter it = pdfs.fwdIterator();
    RooAbsArg *next = 0;
    while ((next=it.next())) {// Convert the RooArgSet into a std::vector container
        TString s = next->GetName();
        RooAbsPdf* pdf = ws->pdf(s);
        tmp.push_back(pdf);
    }

    if (all_pdfs) {
        return tmp;
    }

    // Note: The inconsistent negation of the typing bools is b/c wlst == 0 and blst == 1
    std::vector<TRegexp> others_re = {"^pdf_binC_"};
    std::vector<TRegexp> bkg_re {"_bonly$","_bonly_"};
    std::vector<TRegexp> nuis_re {"_nuis$"};

    tmp = this->filter(tmp,others_re,other_pdfs);   // Note: No negation on the bool here
    if (other_pdfs) {
        // All 'other' type pdfs will fail the bkg/nuis filters --> Don't bother checking them
        return tmp;
    }

    // Note: bkg_pdfs and nuis_pdfs filters >both< get applied (i.e. logical AND)!
    tmp = this->filter(tmp,bkg_re,!bkg_pdfs);
    tmp = this->filter(tmp,nuis_re,!nuis_pdfs);

    return tmp;
}

// Splits the dataset into multiples each containing a particular state from the specified category
//Note: The weight error will be equal to the square of the entries, which might not be correct
std::vector<RooAbsData*> WSHelper::getObsData(
    RooWorkspace* ws,
    TString n1,TString n2,
    std::vector<RooCatType*> cat_types
) {
    std::vector<RooAbsData*> r;
    RooAbsData* data = ws->data(n1);
    RooCategory* cat = ws->cat(n2);
    if (!data || !cat) {
        return r;
    }
    TList* split_data = data->split(*cat);
    for (const auto&& a: *split_data) {
        RooAbsData* d = (RooAbsData*)a;
        TString str = d->GetName();
        for (auto ctype: cat_types) {
            if (str.EqualTo(ctype->GetName())) {
                r.push_back(d);
            }
        }
    }
    return r;
}

// Sums the specified category types which appear in the dataset
double WSHelper::sumObsDataByCats(
    RooWorkspace* ws,
    TString n1, TString n2,
    std::vector<RooCatType*> cat_types
) {
    double sum = 0.0;
    RooDataSet* unbinned_data = (RooDataSet*) ws->data(n1);
    const RooArgSet* obs = unbinned_data->get();
    RooCategory* cat = (RooCategory*)obs->find(n2);
    for (Int_t i = 0; i < unbinned_data->numEntries(); i++) {
        unbinned_data->get(i);
        TString s1 = cat->getLabel();
        for (RooCatType* sum_cat: cat_types) {
            TString s2 = sum_cat->GetName();
            if (s1 == s2) {// Need to compare TString to TString otherwise it fails to match
                sum += unbinned_data->weight();
                break;
            }
        }
    }
    return sum;
}

// For each category sum over specified processes
std::vector<RooAddition*> WSHelper::getSummedCats(
    std::vector<RooAbsReal*> funcs,
    std::vector<RooCatType*> cat_types,
    vTStr procs={},
    TString override=""
) {
    std::vector<RooAddition*> r;
    for (auto c: cat_types) {
        TString name = "";
        if (override.Length() > 0) {
            // This might not be the best way to handle it, but makes naming consistent with the 'n_exp_bin' functions
            name = override+c->GetName();
        }
        RooAddition* roo_add = this->sumProcesses(funcs,c->GetName(),procs,name);
        r.push_back(roo_add);
    }
    return r;
}

std::vector<WSHelper::pTStrDbl> WSHelper::mergeDataBins(
    std::vector<RooAbsData*> datasets,
    TString merge_name,
    std::vector<RooCatType*> cats,
    vTStr sub_cats
) {
    std::vector<pTStrDbl> merged_datasets;
    for (TString subcat_str: sub_cats) {
        double sum = 0;
        TString name = merge_name + "_" + subcat_str;
        std::vector<RooCatType*> pruned_cats;
        if (subcat_str.Length() == 0) {// Occurs when we want to merge all objects into a single category
            name = merge_name;
            pruned_cats = cats;
        } else {// Only get categories which match the sub-category
            pruned_cats = this->filter(cats,subcat_str);
        }
        if (pruned_cats.size() == 0) {
            continue;
        }
        for (RooAbsData* ds: datasets) {
            TString s1 = ds->GetName();
            for (RooCatType* cmp_cat: pruned_cats) {
                TString s2 = cmp_cat->GetName();
                if (s1 == s2) {
                    sum += ds->sumEntries();
                    break;
                }
            }
        }
        merged_datasets.push_back(std::make_pair(name,sum));
    }
    return merged_datasets;
}

// Takes a vector of Roo objects, splits them by process and sub_category then merges the results 
//  and returns the merged objects
//TODO: This function makes some basic assumptions about the naming structure of the input functions, 
//      might want to disentangle this
std::vector<RooAddition*> WSHelper::mergeSubCats(
    std::vector<RooAbsReal*> funcs,
    TString merge_name,
    vTStr procs,
    vTStr sub_cats
) {
    std::vector<RooAddition*> merged_subcats;
    for (auto p: procs) {
        TString s1 = "proc_"+p+"$"; // Makes sure we only get the exact process name
        // This collection only has functions from a single process
        std::vector<RooAbsReal*> p_filter = this->filter(funcs,s1);
        for (auto cat: sub_cats) {
            TString s2 = cat;
            // This collection only has functions from a single sub_category
            std::vector<RooAbsReal*> cat_filter;
            if (cat.Length() == 0) {
                // Merge all items
                cat_filter = p_filter;
            } else {
                cat_filter = this->filter(p_filter,cat);
            }
            if (cat_filter.size()) {
                TString name = merge_name + "_" + cat + "_proc_" + p;
                if (cat.Length() == 0) {
                    // Occurs when we want to merge all functions into a single category
                    name = merge_name + "_proc_" + p;
                }
                RooAddition* merged_f = this->merge(cat_filter,name);
                merged_subcats.push_back(merged_f);
                //std::cout << name << " & " << merged_f->getVal() << std::endl;
                printf("%s & %.2f\n", name.Data(), merged_f->getVal());
            }
        }
    }
    return merged_subcats;
}

// Type casts a bunch of RooAbsReal* objects to RooAddition* objects
std::vector<RooAddition*> WSHelper::toRooAdd(std::vector<RooAbsReal*> funcs) {
    std::vector<RooAddition*> r;
    for (auto f: funcs) r.push_back((RooAddition*)f);
    return r;
}

// Converts the RooCatType* objects to vector of strings
std::vector<TString> WSHelper::toCatStr(std::vector<RooCatType*> cats) {
    std::vector<TString> r;
    for (auto c: cats) r.push_back(c->GetName());
    return r;
}

TString WSHelper::searchPdf(RooWorkspace* ws, TString name) {
    RooArgSet Pdfs = ws->allPdfs();
    RooFIter it = Pdfs.fwdIterator();
    RooAbsArg* next = 0;
    while ((next=it.next())) {
        TString str = next->GetName();
        if (!str.BeginsWith(this->n_exp_search_str_pdf)) {
            continue;
        }
        if (str.Contains(name)) {
            return ws->function(str)->GetName();
        }
    }
    std::cout << TString::Format("[WARNING] Unable to find PDF %s",name.Data()) << std::endl;
    throw;
}

void WSHelper::printSnapshot(RooWorkspace* ws, TString name) {
    TString indent = "    ";
    const RooArgSet* snap = ws->getSnapshot(name);
    if (!snap) {
        return;
    }

    std::cout << "Snapshot: " << name << std::endl;
    TIterator* nextArg(snap->createIterator());
    for (TObject *a = nextArg->Next(); a != 0; a = nextArg->Next()) {
        RooRealVar *rrv = dynamic_cast<RooRealVar *>(a);
        double val = rrv->getVal();
        double err = rrv->getError();
        double asym_lo = rrv->getAsymErrorLo();
        double asym_hi = rrv->getAsymErrorHi();
        double lim_lo  = rrv->getMin();
        double lim_hi  = rrv->getMax();
        //std::cout << "RRV Name: " << rrv->GetName()
        //    << ":\n\tvalue = " << rrv->getVal()
        //    << "\n\terror = " << rrv->getError()
        //    << "\n\tAsymErrLo = " << rrv->getAsymErrorLo()
        //    << "\n\tAsymErrHi = " << rrv->getAsymErrorHi()
        //    << "\n\tMin = " << rrv->getMin()
        //    << "\n\tMax = " << rrv->getMax()
        //    << std::endl;


        std::cout << "RRV Name: " << rrv->GetName() << std::endl;
        std::cout << indent << "Value: " << val << " +/- " << err << std::endl;
        std::cout << indent << "Asym: [" << asym_lo << "," << asym_hi << "]" << std::endl;
        std::cout << indent << "Lims: [" << lim_lo << "," << lim_hi << "]" << std::endl;

    }
}

#endif
/* WSHELPER */
